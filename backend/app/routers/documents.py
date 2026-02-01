"""
API routes for document management.
Handles listing, retrieving, and syncing SEC documents.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timezone
from uuid import UUID

from ..database import get_db
from ..schemas import (
    Document,
    DocumentWithText,
    DocumentList,
    DocumentUpdate,
    FilingType,
    SyncRequest,
    SyncResponse,
    ChunkStatus,
    HealthCheck
)
from ..schemas import DocumentCreate
from .. import main

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    Verifies API, Supabase, and Weaviate connectivity.
    """
    supabase_connected = False
    weaviate_connected = False
    
    try:
        # Test Supabase connection
        db.execute("SELECT 1")
        supabase_connected = True
    except:
        pass
    
    try:
        # Test Weaviate connection
        weaviate_connected = main.weaviate_service.is_connected()
    except:
        pass
    
    status = "healthy" if (supabase_connected and weaviate_connected) else "degraded"
    
    return HealthCheck(
        status=status,
        supabase_connected=supabase_connected,
        weaviate_connected=weaviate_connected,
        timestamp=datetime.now(timezone.utc)
    )


@router.get("/documents", response_model=DocumentList)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    filing_type: Optional[str] = Query(None, description="Filter by filing type"),
    company_name: Optional[str] = Query(None, description="Filter by company name"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    search: Optional[str] = Query(None, description="Search across company name and description"),
    db: Session = Depends(get_db)
):
    """
    List documents with optional filtering and pagination.
    """
    documents, total = main.document_service.list_documents(
        db=db,
        skip=skip,
        limit=limit,
        filing_type=filing_type,
        company_name=company_name,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    return DocumentList(
        items=documents,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/documents/{document_id}", response_model=DocumentWithText)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a single document by ID, including full text.
    """
    document = main.document_service.get_document_by_id(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/documents/{document_id}/chunks/status", response_model=ChunkStatus)
async def get_chunk_status(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Check the chunking status of a document.
    """
    document = main.document_service.get_document_by_id(db, document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get actual count from Weaviate
    weaviate_count = None
    if document.is_chunked:
        try:
            weaviate_count = main.weaviate_service.get_chunk_count(str(document_id))
        except:
            pass
    
    return ChunkStatus(
        document_id=document_id,
        is_chunked=document.is_chunked,
        chunk_count=document.chunk_count,
        weaviate_chunk_count=weaviate_count
    )


@router.post("/documents/sync", response_model=SyncResponse)
async def sync_documents(
    request: SyncRequest,
    db: Session = Depends(get_db)
):
    """
    Sync SEC filings from Edgar API.
    Fetches documents, stores in Supabase, chunks text, and stores in Weaviate.
    """
    documents_created = 0
    documents_updated = 0
    chunks_created = 0
    
    try:
        # Ensure Weaviate schema exists
        if main.weaviate_service.is_connected():
            main.weaviate_service.create_schema()
        
        # Fetch filings from SEC
        filings = await main.sec_service.sync_companies(
            ciks=request.ciks,
            max_filings_per_company=request.max_filings_per_company,
            fetch_markdown=True
        )
        
        # Process each filing
        for filing_data in filings:
            try:
                # Check if document already exists
                existing_doc = main.document_service.get_document_by_accession(
                    db, filing_data["accession_number"]
                )
                
                if existing_doc:
                    documents_updated += 1
                    document_id = existing_doc.id
                    # Skip if already chunked
                    if existing_doc.is_chunked:
                        continue
                else:
                    # Create new document
                    doc_create = DocumentCreate(**filing_data)
                    new_doc = main.document_service.create_document(db, doc_create)
                    documents_created += 1
                    document_id = new_doc.id
                    logger.info(f"Created document: {filing_data['company_name']} - {filing_data['filing_type']}")
                
                # Chunk the document if we have markdown content
                markdown_content = filing_data.get("markdown_content")
                if markdown_content and main.weaviate_service.is_connected():
                    logger.info(f"Processing markdown for chunking...")
                    # Prepare metadata for chunking
                    metadata = {
                        "document_id": document_id,
                        "accession_number": filing_data["accession_number"],
                        "company_name": filing_data["company_name"],
                        "filing_type": filing_data["filing_type"],
                        "filing_date": filing_data["filing_date"],
                        "document_url": filing_data["document_url"],
                        "created_at": datetime.now(timezone.utc)
                    }
                    
                    # Chunk the markdown content
                    chunks = main.chunking_service.chunk_document(markdown_content, metadata)
                    
                    # Store chunks in Weaviate
                    if chunks:
                        num_added = main.weaviate_service.add_chunks(chunks)
                        chunks_created += num_added
                        
                        # Update document status
                        update = DocumentUpdate(
                            is_chunked=True,
                            chunk_count=len(chunks)
                        )
                        main.document_service.update_document(db, document_id, update)
                
            except Exception as e:
                logger.error(f"Error processing filing {filing_data.get('accession_number')}: {e}")
                continue
        
        return SyncResponse(
            success=True,
            message=f"Successfully synced {len(filings)} filings",
            documents_created=documents_created,
            documents_updated=documents_updated,
            chunks_created=chunks_created
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing documents: {str(e)}"
        )


@router.get("/filing-types", response_model=list[FilingType])
async def list_filing_types(db: Session = Depends(get_db)):
    """
    List all available filing types.
    """
    return main.document_service.get_filing_types(db)

