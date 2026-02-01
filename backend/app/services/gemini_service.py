"""
Gemini service for generating natural language answers.
Uses Google's Gemini Flash model for RAG responses.
"""
import logging
from google import genai
from typing import List, Dict
import os
import asyncio
from ..config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating answers using Gemini Flash."""
    
    def __init__(self):
        """Initialize Gemini client with API key from environment."""
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("Warning: GEMINI_API_KEY not set. Gemini service will not work.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
    
    async def answer_query(self, query: str, chunks: List[Dict]) -> str:
        """
        Use Gemini Flash to answer query based on retrieved chunks.
        
        Args:
            query: User's question
            chunks: List of chunk dictionaries with content and metadata
            
        Returns:
            Natural language answer from Gemini
        """
        if not self.client:
            return "Gemini service is not configured. Please set GEMINI_API_KEY environment variable."
        
        if not chunks:
            return "No relevant information found in the SEC filings database. Please try rephrasing your question or search for a different topic."
        
        # Format context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk["metadata"]
            context_parts.append(
                f"[Source {i}] {metadata['company_name']} - {metadata['filing_type']} "
                f"(Filed: {metadata['filing_date']}):\n{chunk['content']}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Create prompt for Gemini
        prompt = f"""You are a financial analyst assistant. Answer the user's question based on the SEC filing excerpts provided below.

SEC Filing Excerpts:
{context}

User Question: {query}

Instructions:
- Provide a clear, accurate answer based only on the information in the excerpts
- Cite which source(s) you're using (e.g., "According to Source 1...")
- If the excerpts don't contain enough information, say so
- Be specific with numbers, dates, and facts when available
- Use a professional but conversational tone

**FORMATTING REQUIREMENTS:**
- Format your response in Markdown
- Use **bold** for emphasis on key terms, numbers, and important facts
- Use ## for section headings if your answer has multiple parts
- Use bullet points (-) for lists
- Use > for important quotes or key findings
- Keep paragraphs concise and well-structured

Answer:"""
        
        try:
            # Call Gemini Flash in a thread pool to avoid blocking
            # The genai library is synchronous, so we run it in a thread
            response = await self.client.aio.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return f"Error generating answer: {str(e)}"

