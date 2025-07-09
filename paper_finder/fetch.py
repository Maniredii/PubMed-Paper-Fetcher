"""
PubMed API integration module for fetching research papers.
"""

import requests
import time
from typing import List, Dict, Optional
from urllib.parse import quote_plus


class PubMedFetcher:
    """Handles interactions with PubMed E-utilities API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: Optional[str] = None, tool: str = "get-papers-list"):
        """
        Initialize PubMed fetcher.
        
        Args:
            email: Contact email for API requests (recommended by NCBI)
            tool: Tool name for API requests
        """
        self.email = email
        self.tool = tool
        self.session = requests.Session()
        
    def _get_common_params(self) -> Dict[str, str]:
        """Get common parameters for API requests."""
        params = {"tool": self.tool}
        if self.email:
            params["email"] = self.email
        return params
    
    def search_papers(self, query: str, max_results: int = 20) -> List[str]:
        """
        Search for papers using PubMed esearch API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        url = f"{self.BASE_URL}/esearch.fcgi"
        params = {
            **self._get_common_params(),
            "db": "pubmed",
            "term": query,
            "retmax": str(max_results),
            "retmode": "json"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            
            return id_list
            
        except requests.RequestException as e:
            raise Exception(f"Error searching PubMed: {e}")
        except KeyError as e:
            raise Exception(f"Unexpected response format from PubMed search: {e}")
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> str:
        """
        Fetch detailed information for papers using PubMed efetch API.
        
        Args:
            pubmed_ids: List of PubMed IDs
            
        Returns:
            XML response containing paper details
        """
        if not pubmed_ids:
            return ""
            
        url = f"{self.BASE_URL}/efetch.fcgi"
        params = {
            **self._get_common_params(),
            "db": "pubmed",
            "id": ",".join(pubmed_ids),
            "retmode": "xml"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            return response.text
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching paper details: {e}")
    
    def fetch_papers_batch(self, pubmed_ids: List[str], batch_size: int = 200) -> List[str]:
        """
        Fetch paper details in batches to handle large result sets.
        
        Args:
            pubmed_ids: List of PubMed IDs
            batch_size: Number of IDs to fetch per batch
            
        Returns:
            List of XML responses
        """
        xml_responses = []
        
        for i in range(0, len(pubmed_ids), batch_size):
            batch = pubmed_ids[i:i + batch_size]
            xml_response = self.fetch_paper_details(batch)
            if xml_response:
                xml_responses.append(xml_response)
            
            # Be respectful to NCBI servers
            if i + batch_size < len(pubmed_ids):
                time.sleep(0.5)
        
        return xml_responses
