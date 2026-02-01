"""
Search service for hybrid search using Weaviate.
Implements semantic + keyword search with score filtering.
"""
import logging
from typing import List, Dict, Optional
import weaviate.classes as wvc

logger = logging.getLogger(__name__)


class SearchService:
    """Service for performing hybrid search on document chunks."""
    
    def __init__(self, weaviate_service):
        """
        Initialize search service.
        
        Args:
            weaviate_service: Instance of WeaviateService
        """
        self.weaviate = weaviate_service
    
    def hybrid_search(
        self,
        query: str,
        company_filter: Optional[str] = None,
        filing_type_filter: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Perform hybrid search with alpha=0.75 (75% vector, 25% BM25).
        Only return chunks with score > 0.75.
        Uses Weaviate's 'like' filter for partial company name matching.
        
        Args:
            query: Search query string
            company_filter: Optional company name filter (supports partial matching with wildcards)
            filing_type_filter: Optional filing type filter (10-K, 10-Q, etc.)
            limit: Maximum number of results to return
            
        Returns:
            List of chunk dictionaries with content, score, and metadata
        """
        if not self.weaviate.is_connected():
            return []
        
        try:
            collection = self.weaviate.client.collections.get(self.weaviate.COLLECTION_NAME)
            
            # Build filters
            filters = []
            
            # Handle company filter with wildcard pattern matching
            if company_filter:
                # Use 'like' filter with wildcards for partial matching
                # Wraps input in wildcards: "Tesla" -> "*Tesla*"
                pattern = f"*{company_filter}*"
                filters.append(
                    wvc.query.Filter.by_property("companyName").like(pattern)
                )
                logger.info(f"Applying Weaviate filter: companyName LIKE '{pattern}'")
            
            if filing_type_filter:
                filters.append(
                    wvc.query.Filter.by_property("filingType").equal(filing_type_filter)
                )
            
            # Combine filters with AND logic
            combined_filter = None
            if filters:
                combined_filter = filters[0]
                for f in filters[1:]:
                    combined_filter = combined_filter & f
            
            # Perform hybrid search with alpha=0.75
            # alpha=0.75 means 75% vector search (semantic), 25% BM25 (keyword)
            response = collection.query.hybrid(
                query=query,
                alpha=0.75,
                limit=limit,
                return_metadata=wvc.query.MetadataQuery(score=True),
                filters=combined_filter
            )
            
            # Filter by score > 0.7 and format results
            results = []
            for obj in response.objects:
                # Only keep results with score > 0.75
                if obj.metadata.score > 0.7:
                    results.append({
                        "content": obj.properties.get("content", ""),
                        "score": obj.metadata.score,
                        "metadata": {
                            "company_name": obj.properties.get("companyName", ""),
                            "filing_type": obj.properties.get("filingType", ""),
                            "filing_date": obj.properties.get("filingDate"),
                            "document_url": obj.properties.get("documentUrl", ""),
                            "chunk_index": obj.properties.get("chunkIndex", 0),
                            "accession_number": obj.properties.get("accessionNumber", ""),
                            "chunk_char_count": obj.properties.get("chunkCharCount", 0),
                            "total_chunks": obj.properties.get("totalChunks", 0),
                        }
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing hybrid search: {e}")
            return []
