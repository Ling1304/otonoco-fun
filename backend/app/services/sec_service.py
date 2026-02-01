"""
SEC Edgar API service for fetching regulatory filings.
Handles API calls, rate limiting, and parsing of SEC data.
"""
import httpx
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from bs4 import BeautifulSoup
from markitdown import MarkItDown
import io
from ..config import settings


class SECService:
    """Service for interacting with SEC Edgar API."""
    
    # Default companies to fetch (major tech companies)
    DEFAULT_CIKS = [
        "0000320193",  # Apple Inc.
        "0000789019",  # Microsoft Corporation
        "0001318605",  # Tesla, Inc.
        "0001018724",  # Amazon.com, Inc.
        "0001652044",  # Alphabet Inc. (Google)
    ]
    
    BASE_URL = "https://data.sec.gov"
    RATE_LIMIT_DELAY = 0.1  # 10 requests per second max
    
    def __init__(self):
        """Initialize SEC service with proper headers."""
        # Headers for API calls (data.sec.gov)
        self.api_headers = {
            "User-Agent": f"{settings.sec_api_user_agent} ({settings.sec_api_email})",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        
        # Headers for document fetches (www.sec.gov)
        self.doc_headers = {
            "User-Agent": f"{settings.sec_api_user_agent} ({settings.sec_api_email})",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        
        self.md_converter = MarkItDown()
        self.logger = logging.getLogger(__name__)
    
    def clean_sec_html(self, html_input: str) -> str:
        """
        Clean SEC HTML by removing XBRL headers and hidden elements.
        
        Args:
            html_input: Raw HTML from SEC document
            
        Returns:
            Cleaned HTML string
        """
        soup = BeautifulSoup(html_input, 'html.parser')
        
        # 1. Remove the entire XBRL header
        for header in soup.find_all(['ix:header', 'xbrl']):
            header.decompose()
        
        # 2. Remove hidden elements
        for hidden in soup.find_all(style=lambda value: value and 'display:none' in value.replace(' ', '')):
            hidden.decompose()
        
        # 3. Unwrap 'Inline XBRL' tags (keep text, remove tag)
        for ix_tag in soup.find_all(lambda tag: tag.name and tag.name.startswith('ix:')):
            ix_tag.unwrap()
        
        return str(soup)
    
    def convert_html_to_markdown(self, html_content: str) -> str:
        """
        Convert cleaned HTML to markdown using MarkItDown.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Markdown formatted text
        """
        try:
            # Clean the HTML first
            clean_html = self.clean_sec_html(html_content)
            
            # Convert to markdown
            clean_html_stream = io.BytesIO(clean_html.encode("utf-8"))
            result = self.md_converter.convert_stream(clean_html_stream, file_extension=".html")
            
            return result.markdown
        except Exception as e:
            self.logger.error(f"Error converting HTML to markdown: {e}")
            # Fallback: return cleaned HTML if markdown conversion fails
            return self.clean_sec_html(html_content)
    
    async def fetch_company_filings(
        self,
        cik: str,
        max_filings: int = 10
    ) -> List[Dict]:
        """
        Fetch recent filings for a specific company.
        
        Args:
            cik: 10-digit CIK number
            max_filings: Maximum number of recent filings to return
            
        Returns:
            List of filing dictionaries with metadata
        """
        # Ensure CIK is 10 digits with leading zeros
        cik = cik.zfill(10)
        
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Rate limiting
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                
                response = await client.get(url, headers=self.api_headers)
                response.raise_for_status()
                data = response.json()
                
                # Extract company info and recent filings
                company_name = data.get("name", "Unknown Company")
                filings = data.get("filings", {}).get("recent", {})
                
                # Parse filings
                result = []
                accession_numbers = filings.get("accessionNumber", [])
                filing_dates = filings.get("filingDate", [])
                forms = filings.get("form", [])
                primary_documents = filings.get("primaryDocument", [])
                descriptions = filings.get("primaryDocDescription", [])
                
                # Combine data from parallel arrays
                today = date.today()
                
                for i in range(len(accession_numbers)):
                    # Filter for common filing types
                    form = forms[i]
                    if form not in ["10-K", "10-Q", "8-K", "20-F", "S-1", "DEF 14A"]:
                        continue
                    
                    # Parse filing date and skip future filings
                    filing_date = filing_dates[i]
                    filing_date_obj = datetime.strptime(filing_date, "%Y-%m-%d").date()
                    
                    # Skip filings from the future or very recent (last 30 days)
                    # Recent filings might not have HTML available yet
                    if filing_date_obj >= (today - timedelta(days=30)):
                        continue
                    
                    accession = accession_numbers[i].replace("-", "")
                    primary_doc = primary_documents[i]
                    
                    # Construct document URL
                    doc_url = (
                        f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/"
                        f"{accession}/{primary_doc}"
                    )
                    
                    result.append({
                        "accession_number": accession_numbers[i],
                        "company_name": company_name,
                        "company_cik": cik,
                        "filing_type": form,
                        "filing_date": filing_date_obj,
                        "description": descriptions[i] if i < len(descriptions) else form,
                        "document_url": doc_url
                    })
                    
                    # Stop once we have enough valid filings
                    if len(result) >= max_filings:
                        break
                
                return result
                
            except httpx.HTTPError as e:
                self.logger.error(f"Error fetching SEC data for CIK {cik}: {e}")
                return []
    
    async def fetch_document_text(self, document_url: str) -> Optional[str]:
        """
        Fetch HTML content and convert to markdown.
        
        Args:
            document_url: URL to the SEC filing document
            
        Returns:
            Markdown formatted content or None if failed
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Rate limiting
                await asyncio.sleep(self.RATE_LIMIT_DELAY)
                
                response = await client.get(document_url, headers=self.doc_headers)
                response.raise_for_status()
                
                # Convert HTML to markdown
                if response.text:
                    markdown_content = self.convert_html_to_markdown(response.text)
                    return markdown_content
                return None
                
            except Exception as e:
                self.logger.error(f"Error fetching document text from {document_url}: {e}")
                return None
    
    async def sync_companies(
        self,
        ciks: Optional[List[str]] = None,
        max_filings_per_company: int = 10,
        fetch_markdown: bool = True
    ) -> List[Dict]:
        """
        Sync filings for multiple companies.
        
        Args:
            ciks: List of CIK numbers (uses defaults if None)
            max_filings_per_company: Max filings per company
            fetch_markdown: Whether to fetch and convert document to markdown
            
        Returns:
            List of all filing dictionaries
        """
        if ciks is None:
            ciks = self.DEFAULT_CIKS
        
        all_filings = []
        
        for cik in ciks:
            self.logger.info(f"Fetching filings for CIK: {cik}")
            filings = await self.fetch_company_filings(cik, max_filings_per_company)
            
            # Optionally fetch and convert to markdown for each filing
            if fetch_markdown:
                for filing in filings:
                    self.logger.info(f"  Fetching and converting to markdown: {filing['filing_type']} - {filing['accession_number']}")
                    markdown_content = await self.fetch_document_text(filing["document_url"])
                    if markdown_content:
                        filing["markdown_content"] = markdown_content
                        self.logger.info(f"    ✓ Successfully converted to markdown ({len(markdown_content)} chars)")
                    else:
                        filing["markdown_content"] = None
                        self.logger.warning(f"    ✗ Failed to fetch/convert (will store metadata only)")
            
            all_filings.extend(filings)
        
        return all_filings

