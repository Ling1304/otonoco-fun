"""
Search router for RAG-based document search.
Provides endpoints for hybrid search with AI-generated answers.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import SearchRequest, SearchResponse, ChunkResult
from .. import main

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search SEC documents using hybrid search and get AI-generated answer.
    
    - Performs hybrid search (75% semantic vector search, 25% keyword BM25)
    - Uses Weaviate 'like' filter for partial company name matching
    - Filters results with score > 0.75
    - Generates natural language answer using Gemini Flash in Markdown format
    - Returns answer with source chunks and metadata
    """
    # Perform hybrid search with pattern matching for company names
    chunks = main.search_service.hybrid_search(
        query=request.query,
        company_filter=request.company_filter,
        filing_type_filter=request.filing_type_filter,
        limit=request.limit or 5
    )
    
    # Generate answer with Gemini (async operation)
    if chunks:
        answer = await main.gemini_service.answer_query(request.query, chunks)
    else:
        answer = "No relevant information found in the SEC filings database. Please try rephrasing your question or search for a different topic."
    
    # Format response
    chunk_results = [
        ChunkResult(
            content=chunk["content"],
            score=chunk["score"],
            metadata=chunk["metadata"]
        )
        for chunk in chunks
    ]
    
    return SearchResponse(
        query=request.query,
        answer=answer,
        chunks=chunk_results,
        total_chunks=len(chunk_results)
    )

