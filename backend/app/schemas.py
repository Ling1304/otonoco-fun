"""
Pydantic schemas for request/response validation.
Defines data structures for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID


# Filing Type Schemas
class FilingTypeBase(BaseModel):
    code: str
    description: str


class FilingTypeCreate(FilingTypeBase):
    pass


class FilingType(FilingTypeBase):
    id: UUID

    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    accession_number: str
    company_name: str
    company_cik: str
    filing_type: str
    filing_date: date
    description: Optional[str] = None
    document_url: str


class DocumentCreate(DocumentBase):
    markdown_content: Optional[str] = None


class DocumentUpdate(BaseModel):
    is_chunked: Optional[bool] = None
    chunk_count: Optional[int] = None


class Document(DocumentBase):
    id: UUID
    is_chunked: bool
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentWithText(Document):
    """Document schema including markdown content."""
    markdown_content: Optional[str] = None


class DocumentList(BaseModel):
    """Paginated list of documents."""
    items: List[Document]
    total: int
    skip: int
    limit: int


# Sync Request Schema
class SyncRequest(BaseModel):
    """Request schema for syncing SEC filings."""
    ciks: Optional[List[str]] = Field(
        default=None,
        description="List of CIK numbers to sync. If empty, syncs default companies."
    )
    max_filings_per_company: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of recent filings to fetch per company"
    )


class SyncResponse(BaseModel):
    """Response schema for sync operation."""
    success: bool
    message: str
    documents_created: int
    documents_updated: int
    chunks_created: int


# Health Check Schema
class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    supabase_connected: bool
    weaviate_connected: bool
    timestamp: datetime


# Chunk Status Schema
class ChunkStatus(BaseModel):
    """Document chunking status."""
    document_id: UUID
    is_chunked: bool
    chunk_count: int
    weaviate_chunk_count: Optional[int] = None


# Search Schemas
class SearchRequest(BaseModel):
    """Request schema for search endpoint."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    company_filter: Optional[str] = Field(None, description="Filter by company name")
    filing_type_filter: Optional[str] = Field(None, description="Filter by filing type (10-K, 10-Q, etc.)")
    limit: Optional[int] = Field(default=5, ge=1, le=20, description="Maximum number of results")


class ChunkResult(BaseModel):
    """Individual chunk result with score and metadata."""
    content: str
    score: float
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Response schema for search endpoint."""
    query: str
    answer: str
    chunks: List[ChunkResult]
    total_chunks: int

