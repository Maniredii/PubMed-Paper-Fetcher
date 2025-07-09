"""
XML parsing module for PubMed paper data.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from lxml import etree
import re


@dataclass
class Author:
    """Represents an author with their affiliation information."""
    last_name: str
    first_name: str
    initials: str
    affiliation: str
    email: Optional[str] = None


@dataclass
class Paper:
    """Represents a research paper with all relevant information."""
    pubmed_id: str
    title: str
    publication_date: str
    authors: List[Author]
    corresponding_author_email: Optional[str] = None
    journal: str = ""
    abstract: str = ""


class PubMedParser:
    """Parses XML responses from PubMed API."""
    
    def parse_papers(self, xml_content: str) -> List[Paper]:
        """
        Parse XML content and extract paper information.
        
        Args:
            xml_content: XML response from PubMed efetch API
            
        Returns:
            List of Paper objects
        """
        papers = []
        
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Find all PubmedArticle elements
            articles = root.xpath('//PubmedArticle')
            
            for article in articles:
                paper = self._parse_single_paper(article)
                if paper:
                    papers.append(paper)
                    
        except etree.XMLSyntaxError as e:
            raise Exception(f"Error parsing XML: {e}")
        except Exception as e:
            raise Exception(f"Error processing papers: {e}")
        
        return papers
    
    def _parse_single_paper(self, article_element) -> Optional[Paper]:
        """Parse a single PubmedArticle element."""
        try:
            # Extract PubMed ID
            pubmed_id = self._get_text(article_element, './/PMID')
            if not pubmed_id:
                return None
            
            # Extract title
            title = self._get_text(article_element, './/ArticleTitle')
            title = self._clean_text(title)
            
            # Extract publication date
            pub_date = self._extract_publication_date(article_element)
            
            # Extract journal
            journal = self._get_text(article_element, './/Journal/Title')
            
            # Extract abstract
            abstract = self._get_text(article_element, './/Abstract/AbstractText')
            abstract = self._clean_text(abstract)
            
            # Extract authors
            authors = self._extract_authors(article_element)
            
            # Find corresponding author email
            corresponding_email = self._find_corresponding_author_email(authors)
            
            return Paper(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                authors=authors,
                corresponding_author_email=corresponding_email,
                journal=journal,
                abstract=abstract
            )
            
        except Exception as e:
            print(f"Warning: Error parsing paper: {e}")
            return None
    
    def _extract_authors(self, article_element) -> List[Author]:
        """Extract author information from the article."""
        authors = []
        
        author_elements = article_element.xpath('.//AuthorList/Author')
        
        for author_elem in author_elements:
            last_name = self._get_text(author_elem, './LastName', '')
            first_name = self._get_text(author_elem, './ForeName', '')
            initials = self._get_text(author_elem, './Initials', '')
            
            # Extract affiliation
            affiliation = self._get_text(author_elem, './AffiliationInfo/Affiliation', '')
            
            # Look for email in affiliation text
            email = self._extract_email_from_text(affiliation)
            
            author = Author(
                last_name=last_name,
                first_name=first_name,
                initials=initials,
                affiliation=affiliation,
                email=email
            )
            
            authors.append(author)
        
        return authors
    
    def _extract_publication_date(self, article_element) -> str:
        """Extract publication date in YYYY-MM-DD format."""
        # Try different date elements
        date_elements = [
            './/PubDate',
            './/ArticleDate',
            './/DateCompleted'
        ]
        
        for date_xpath in date_elements:
            date_elem = article_element.xpath(date_xpath)
            if date_elem:
                year = self._get_text(date_elem[0], './Year', '')
                month = self._get_text(date_elem[0], './Month', '01')
                day = self._get_text(date_elem[0], './Day', '01')
                
                # Handle month names
                month = self._convert_month_name_to_number(month)
                
                if year:
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return ""
    
    def _convert_month_name_to_number(self, month: str) -> str:
        """Convert month name to number."""
        month_map = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        month_lower = month.lower()[:3]
        return month_map.get(month_lower, month)
    
    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """Extract email address from text using regex."""
        if not text:
            return None
            
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        
        return matches[0] if matches else None
    
    def _find_corresponding_author_email(self, authors: List[Author]) -> Optional[str]:
        """Find the corresponding author's email."""
        for author in authors:
            if author.email:
                return author.email
        return None
    
    def _get_text(self, element, xpath: str, default: str = '') -> str:
        """Safely extract text from XML element."""
        try:
            result = element.xpath(xpath)
            if result and hasattr(result[0], 'text') and result[0].text:
                return result[0].text.strip()
            return default
        except:
            return default
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
