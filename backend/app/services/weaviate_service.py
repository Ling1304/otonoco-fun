"""
Weaviate service for vector database operations.
Handles chunk storage and schema management.
"""
import logging
import weaviate
from weaviate.classes.config import Configure, Property, DataType, Tokenization
from weaviate.classes.query import Filter
from typing import List, Dict, Optional
from datetime import datetime, timezone
from ..config import settings

logger = logging.getLogger(__name__)


class WeaviateService:
    """Service for interacting with Weaviate vector database."""
    
    COLLECTION_NAME = "DocumentChunk"
    
    def __init__(self):
        """Initialize Weaviate client."""
        self.client = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Weaviate."""
        try:
            # Prepare headers for Gemini API key if available
            headers = {}
            if settings.gemini_api_key:
                headers["X-Goog-Studio-Api-Key"] = settings.gemini_api_key
            
            if settings.weaviate_api_key:
                # Weaviate Cloud connection
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=settings.weaviate_url,
                    auth_credentials=weaviate.auth.AuthApiKey(settings.weaviate_api_key),
                    headers=headers if headers else None
                )
            else:
                # Local Weaviate connection
                self.client = weaviate.connect_to_local(
                    host=settings.weaviate_url.replace("http://", "").replace("https://", ""),
                    headers=headers if headers else None
                )
            
            logger.info(f"Connected to Weaviate: {self.client.is_ready()}")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Weaviate is connected."""
        try:
            return self.client is not None and self.client.is_ready()
        except:
            return False
    
    def create_schema(self):
        """
        Create DocumentChunk collection schema if it doesn't exist.
        """
        if not self.client:
            raise Exception("Weaviate client not connected")
        
        try:
            # Check if collection exists
            if self.client.collections.exists(self.COLLECTION_NAME):
                logger.info(f"Collection {self.COLLECTION_NAME} already exists")
                return
            
            # Create collection with Google AI Studio (Gemini) vectorizer
            self.client.collections.create(
                name=self.COLLECTION_NAME,
                vector_config=Configure.Vectors.text2vec_google_gemini(
                    model="gemini-embedding-001",
                    vectorize_collection_name=False,
                    source_properties=["content"],
                    dimensions=3072
                ),
                properties=[
                    Property(
                        name="documentId",
                        data_type=DataType.TEXT,
                        tokenization=Tokenization.WORD,
                        description="UUID of parent document in Supabase"
                    ),
                    Property(
                        name="accessionNumber",
                        data_type=DataType.TEXT,
                        tokenization=Tokenization.WORD,
                        description="SEC accession number"
                    ),
                    Property(
                        name="chunkIndex",
                        data_type=DataType.INT,
                        description="Order of chunk within document"
                    ),
                    Property(
                        name="content",
                        data_type=DataType.TEXT,
                        tokenization=Tokenization.WORD,
                        description="Chunk text content"
                    ),
                    Property(
                        name="companyName",
                        data_type=DataType.TEXT,
                        tokenization=Tokenization.LOWERCASE,
                        description="Company name"
                    ),
                    Property(
                        name="filingType",
                        data_type=DataType.TEXT,
                        tokenization=Tokenization.WORD,
                        description="Filing type (10-K, 10-Q, etc.)"
                    ),
                    Property(
                        name="filingDate",
                        data_type=DataType.DATE,
                        description="Original filing date"
                    ),
                    Property(
                        name="documentUrl",
                        data_type=DataType.TEXT,
                        tokenization=Tokenization.WORD,
                        description="URL to original SEC document"
                    ),
                    Property(
                        name="createdAt",
                        data_type=DataType.DATE,
                        description="When chunk was created"
                    ),
                    Property(
                        name="chunkCharCount",
                        data_type=DataType.INT,
                        description="Length of chunk in characters"
                    ),
                    Property(
                        name="totalChunks",
                        data_type=DataType.INT,
                        description="Total chunks in document"
                    ),
                    Property(
                        name="chunkPosition",
                        data_type=DataType.NUMBER,
                        description="Normalized position in document (0.0-1.0)"
                    ),
                ]
            )
            logger.info(f"Created collection {self.COLLECTION_NAME}")
            
        except Exception as e:
            logger.error(f"Error creating schema: {e}")
            raise
    
    def add_chunks(self, chunks: List[Dict]) -> int:
        """
        Add document chunks to Weaviate.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Number of chunks successfully added
        """
        if not self.client:
            raise Exception("Weaviate client not connected")
        
        if not chunks:
            return 0
        
        try:
            collection = self.client.collections.get(self.COLLECTION_NAME)
            
            # Prepare data objects
            with collection.batch.dynamic() as batch:
                for chunk in chunks:
                    # Convert filing_date to datetime if it's a date object
                    filing_date = chunk.get("filing_date")
                    if filing_date and not isinstance(filing_date, datetime):
                        filing_date = datetime.combine(filing_date, datetime.min.time())
                    
                    # Convert created_at to datetime if it's a date object
                    created_at = chunk.get("created_at")
                    if created_at and not isinstance(created_at, datetime):
                        created_at = datetime.combine(created_at, datetime.min.time())
                    
                    # Get metadata
                    metadata = chunk.get("metadata", {})
                    
                    properties = {
                        "documentId": chunk.get("document_id"),
                        "accessionNumber": chunk.get("accession_number"),
                        "chunkIndex": chunk.get("chunk_index"),
                        "content": chunk.get("content"),
                        "companyName": chunk.get("company_name"),
                        "filingType": chunk.get("filing_type"),
                        "filingDate": filing_date,
                        "documentUrl": chunk.get("document_url"),
                        "createdAt": created_at or datetime.now(timezone.utc),
                        "chunkCharCount": len(chunk.get("content", "")),
                        "totalChunks": metadata.get("total_chunks", 0),
                        "chunkPosition": metadata.get("chunk_position", 0.0),
                    }
                    
                    batch.add_object(properties=properties)
            
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error adding chunks to Weaviate: {e}")
            return 0
    
    def get_chunk_count(self, document_id: str) -> int:
        """
        Get the number of chunks for a document in Weaviate.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Number of chunks found
        """
        if not self.client:
            return 0
        
        try:
            collection = self.client.collections.get(self.COLLECTION_NAME)
            
            response = collection.aggregate.over_all(
                filters=Filter.by_property("documentId").equal(document_id)
            )
            
            return response.total_count if response else 0
            
        except Exception as e:
            logger.error(f"Error getting chunk count: {e}")
            return 0
    
    def delete_chunks(self, document_id: str) -> int:
        """
        Delete all chunks for a document.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Number of chunks deleted
        """
        if not self.client:
            return 0
        
        try:
            collection = self.client.collections.get(self.COLLECTION_NAME)
            
            result = collection.data.delete_many(
                where=Filter.by_property("documentId").equal(document_id)
            )
            
            return result.successful if result else 0
            
        except Exception as e:
            logger.error(f"Error deleting chunks: {e}")
            return 0
    
    def close(self):
        """Close Weaviate connection."""
        if self.client:
            self.client.close()
