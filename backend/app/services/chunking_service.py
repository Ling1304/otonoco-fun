"""
Document chunking service for RAG preparation.
Splits documents into manageable chunks for vector storage using LangChain.
"""
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingService:
    """Service for chunking documents using LangChain's RecursiveCharacterTextSplitter."""
    
    def __init__(self):
        """Initialize chunking service with LangChain splitter."""
        # Configure the recursive splitter based on notebook settings
        self.splitter = RecursiveCharacterTextSplitter(
            separators=["---", "\n\n", "\n", " ", ""],
            chunk_size=5000,
            chunk_overlap=2000,
            add_start_index=True,  # Useful for tracking where chunks came from
        )
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks using LangChain's RecursiveCharacterTextSplitter.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Use LangChain's splitter
        chunks = self.splitter.create_documents([text])
        return [chunk.page_content for chunk in chunks]
    
    def chunk_document(
        self,
        markdown_content: str,
        document_metadata: Dict
    ) -> List[Dict]:
        """
        Chunk a document and attach metadata.
        
        Args:
            markdown_content: Complete document markdown content
            document_metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        text_chunks = self.chunk_text(markdown_content)
        
        result = []
        for i, chunk_content in enumerate(text_chunks):
            chunk_data = {
                "chunk_index": i,
                "content": chunk_content,
                "document_id": str(document_metadata.get("document_id")),
                "accession_number": document_metadata.get("accession_number"),
                "company_name": document_metadata.get("company_name"),
                "filing_type": document_metadata.get("filing_type"),
                "filing_date": document_metadata.get("filing_date"),
                "document_url": document_metadata.get("document_url"),
                "created_at": document_metadata.get("created_at"),
                "metadata": {
                    "total_chunks": len(text_chunks),
                    "chunk_position": (i + 1) / len(text_chunks),
                }
            }
            result.append(chunk_data)
        
        return result

