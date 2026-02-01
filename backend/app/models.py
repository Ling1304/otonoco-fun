"""
SQLAlchemy models for Supabase PostgreSQL database.
Defines document and filing type tables.
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base


class Document(Base):
    """
    Model for SEC filing documents.
    Stores metadata and full text of regulatory filings.
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    accession_number = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    company_cik = Column(String(10), nullable=False, index=True)
    filing_type = Column(String(10), nullable=False, index=True)
    filing_date = Column(Date, nullable=False, index=True)
    description = Column(Text)
    document_url = Column(String(512), nullable=False)
    markdown_content = Column(Text)
    is_chunked = Column(Boolean, default=False, nullable=False)
    chunk_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Document {self.company_name} - {self.filing_type} ({self.filing_date})>"


class FilingType(Base):
    """
    Reference table for SEC filing types.
    Stores common filing type codes and descriptions.
    """
    __tablename__ = "filing_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(10), unique=True, nullable=False)
    description = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<FilingType {self.code}: {self.description}>"

