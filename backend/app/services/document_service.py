"""
Document service for CRUD operations on Supabase.
Handles business logic for document management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date
from uuid import UUID

from ..models import Document, FilingType
from ..schemas import DocumentCreate, DocumentUpdate


class DocumentService:
    """Service for document-related operations."""
    
    @staticmethod
    def create_document(db: Session, document_data: DocumentCreate) -> Document:
        """Create a new document in the database."""
        # Check if document already exists
        existing = db.query(Document).filter(
            Document.accession_number == document_data.accession_number
        ).first()
        
        if existing:
            return existing
        
        # Create new document
        db_document = Document(**document_data.model_dump())
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def get_document(db: Session, document_id: UUID) -> Optional[Document]:
        """Get a document by ID."""
        return db.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def get_document_by_accession(db: Session, accession_number: str) -> Optional[Document]:
        """Get a document by accession number."""
        return db.query(Document).filter(
            Document.accession_number == accession_number
        ).first()
    
    @staticmethod
    def list_documents(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        filing_type: Optional[str] = None,
        company_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """
        List documents with optional filtering.
        
        Returns:
            Tuple of (documents list, total count)
        """
        query = db.query(Document)
        
        # Apply filters
        if filing_type:
            query = query.filter(Document.filing_type == filing_type)
        
        if company_name:
            query = query.filter(Document.company_name.ilike(f"%{company_name}%"))
        
        if start_date:
            query = query.filter(Document.filing_date >= start_date)
        
        if end_date:
            query = query.filter(Document.filing_date <= end_date)
        
        if search:
            search_filter = or_(
                Document.company_name.ilike(f"%{search}%"),
                Document.description.ilike(f"%{search}%"),
                Document.filing_type.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        documents = query.order_by(Document.filing_date.desc()).offset(skip).limit(limit).all()
        
        return documents, total
    
    @staticmethod
    def update_document(
        db: Session,
        document_id: UUID,
        update_data: DocumentUpdate
    ) -> Optional[Document]:
        """Update a document."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None
        
        # Update fields
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(document, field, value)
        
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    def get_filing_types(db: Session) -> List[FilingType]:
        """Get all filing types."""
        return db.query(FilingType).all()
    
    @staticmethod
    def create_filing_type(db: Session, code: str, description: str) -> FilingType:
        """Create a filing type."""
        existing = db.query(FilingType).filter(FilingType.code == code).first()
        if existing:
            return existing
        
        filing_type = FilingType(code=code, description=description)
        db.add(filing_type)
        db.commit()
        db.refresh(filing_type)
        return filing_type
    
    @staticmethod
    def initialize_filing_types(db: Session):
        """Initialize common filing types."""
        common_types = [
            ("10-K", "Annual Report"),
            ("10-Q", "Quarterly Report"),
            ("8-K", "Current Report"),
            ("20-F", "Annual Report (Foreign Private Issuer)"),
            ("S-1", "Registration Statement"),
            ("DEF 14A", "Proxy Statement"),
        ]
        
        for code, description in common_types:
            DocumentService.create_filing_type(db, code, description)

