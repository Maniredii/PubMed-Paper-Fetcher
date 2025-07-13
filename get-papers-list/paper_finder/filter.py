"""
Author affiliation filtering module to identify non-academic authors.
"""

from typing import List, Set, Tuple
import re
from .parser import Author, Paper


class AffiliationFilter:
    """
    Filters authors based on their affiliations to identify non-academic authors.

    This was the most challenging part - needed to balance precision vs recall
    for industry author detection using keyword-based heuristics.
    """
    
    # Academic keywords that indicate academic institutions
    ACADEMIC_KEYWORDS = {
        'university', 'college', 'institute', 'school', 'laboratory', 'lab',
        'research center', 'research centre', 'medical center', 'medical centre',
        'hospital', 'clinic', 'department', 'faculty', 'academy', 'polytechnic',
        'campus', 'graduate school', 'postgraduate', 'doctoral', 'phd program'
    }
    
    # Industry/company keywords that indicate non-academic affiliations
    INDUSTRY_KEYWORDS = {
        'pharma', 'pharmaceutical', 'biotech', 'biotechnology', 'therapeutics',
        'inc', 'incorporated', 'ltd', 'limited', 'llc', 'corp', 'corporation',
        'company', 'co.', 'gmbh', 'ag', 'sa', 'plc', 'pty', 'pvt',
        'biosciences', 'life sciences', 'research and development', 'r&d',
        'drug discovery', 'clinical research', 'contract research',
        'clinical trial', 'clinical trials', 'drug development', 'drug design',
        'medical device', 'diagnostics', 'laboratory services', 'consulting',
        'solutions', 'technologies', 'systems', 'services', 'group',
        'healthcare', 'health care', 'medical', 'clinical', 'trial',
        'cro', 'contract research organization', 'pharmaceutical research',
        'biomedical', 'medicine', 'therapy', 'treatment', 'device'
    }
    
    # Academic email domains
    ACADEMIC_DOMAINS = {
        '.edu', '.ac.', '.edu.', 'university', 'college', 'institute'
    }
    
    # Common industry email domains
    INDUSTRY_DOMAINS = {
        '.com', '.biz', '.org'  # Note: .org can be both, but often industry
    }

    # Known pharmaceutical/biotech company names for enhanced detection
    KNOWN_COMPANIES = {
        'pfizer', 'roche', 'novartis', 'merck', 'gsk', 'glaxosmithkline',
        'sanofi', 'astrazeneca', 'bristol myers squibb', 'johnson & johnson',
        'abbvie', 'amgen', 'gilead', 'biogen', 'regeneron', 'vertex',
        'moderna', 'biontech', 'illumina', 'thermo fisher', 'agilent',
        'waters', 'perkinelmer', 'danaher', 'abbott', 'medtronic',
        'boston scientific', 'stryker', 'zimmer biomet', 'intuitive surgical',
        'eli lilly', 'takeda', 'boehringer ingelheim', 'bayer', 'celgene',
        'iqvia', 'covance', 'parexel', 'psi', 'icon', 'syneos', 'ppd',
        'quintiles', 'celerion', 'medpace', 'worldwide clinical trials',
        'labcorp', 'quest diagnostics', 'eurofins', 'charles river',
        'wuxi', 'catalent', 'lonza', 'samsung biologics', 'boehringer',
        'teva', 'mylan', 'sandoz', 'hospira', 'fresenius', 'baxter',
        # Private medical institutions and clinics
        'mayo clinic', 'cleveland clinic', 'johns hopkins', 'kaiser permanente',
        'memorial sloan kettering', 'md anderson', 'cedars-sinai', 'scripps',
        'intermountain healthcare', 'geisinger', 'henry ford health',
        # Research institutes with industry ties
        'sarah cannon research institute', 'translational genomics research institute',
        'broad institute', 'whitehead institute', 'cold spring harbor laboratory'
    }
    
    def __init__(self, debug: bool = False):
        """
        Initialize the affiliation filter.
        
        Args:
            debug: Whether to print debug information
        """
        self.debug = debug
    
    def filter_papers_with_industry_authors(self, papers: List[Paper]) -> List[Paper]:
        """
        Filter papers to only include those with non-academic (industry) authors.
        
        Args:
            papers: List of Paper objects
            
        Returns:
            List of papers that have at least one non-academic author
        """
        filtered_papers = []
        
        for paper in papers:
            industry_authors = self.identify_industry_authors(paper.authors)
            
            if industry_authors:
                # Create a new paper object with only industry authors highlighted
                filtered_papers.append(paper)
                
                if self.debug:
                    print(f"Paper {paper.pubmed_id} has {len(industry_authors)} industry authors")
        
        return filtered_papers
    
    def identify_industry_authors(self, authors: List[Author]) -> List[Author]:
        """
        Identify authors with industry/non-academic affiliations.
        
        Args:
            authors: List of Author objects
            
        Returns:
            List of authors identified as having industry affiliations
        """
        industry_authors = []
        
        for author in authors:
            if self.is_industry_affiliation(author):
                industry_authors.append(author)
                
                if self.debug:
                    print(f"Industry author: {author.first_name} {author.last_name}")
                    print(f"  Affiliation: {author.affiliation}")
                    if author.email:
                        print(f"  Email: {author.email}")
        
        return industry_authors
    
    def is_industry_affiliation(self, author: Author) -> bool:
        """
        Determine if an author has an industry (non-academic) affiliation.

        Args:
            author: Author object to evaluate

        Returns:
            True if the author appears to have an industry affiliation
        """
        affiliation_text = author.affiliation.lower() if author.affiliation else ""
        email = author.email.lower() if author.email else ""

        # Check email domain first (more reliable)
        email_score = self._score_email_domain(email)

        # Check affiliation text
        affiliation_score = self._score_affiliation_text(affiliation_text)

        # Combine scores with email having higher weight
        total_score = (email_score * 0.7) + (affiliation_score * 0.3)

        if self.debug:
            print(f"  Author: {author.first_name} {author.last_name}")
            print(f"  Email: {email}")
            print(f"  Affiliation: {affiliation_text}")
            print(f"  Email score: {email_score}, Affiliation score: {affiliation_score}, Total: {total_score}")

        # Threshold for considering someone as industry-affiliated
        # Lowered threshold to be more inclusive for industry collaborations
        return total_score > 0.15
    
    def _score_email_domain(self, email: str) -> float:
        """
        Score email domain for industry vs academic likelihood.
        
        Returns:
            Score between -1 (definitely academic) and 1 (definitely industry)
        """
        if not email:
            return 0.0
        
        email_lower = email.lower()
        
        # Strong academic indicators
        for domain in self.ACADEMIC_DOMAINS:
            if domain in email_lower:
                return -0.8
        
        # Check for specific academic patterns
        if re.search(r'@.*\.(edu|ac\.|edu\.)', email_lower):
            return -0.9
        
        # Industry indicators
        if email_lower.endswith('.com'):
            return 0.6
        elif email_lower.endswith('.biz'):
            return 0.8
        elif email_lower.endswith('.org'):
            return 0.3  # .org can be either, slightly more industry-leaning
        elif email_lower.endswith('.net'):
            return 0.4  # .net often industry
        
        return 0.0
    
    def _score_affiliation_text(self, affiliation: str) -> float:
        """
        Score affiliation text for industry vs academic likelihood.
        
        Returns:
            Score between -1 (definitely academic) and 1 (definitely industry)
        """
        if not affiliation:
            return 0.0
        
        affiliation_lower = affiliation.lower()
        
        # Count academic keywords
        academic_count = sum(1 for keyword in self.ACADEMIC_KEYWORDS 
                           if keyword in affiliation_lower)
        
        # Count industry keywords
        industry_count = sum(1 for keyword in self.INDUSTRY_KEYWORDS 
                           if keyword in affiliation_lower)
        
        # Special patterns
        if re.search(r'\b(inc|ltd|llc|corp|gmbh)\b', affiliation_lower):
            industry_count += 2
        
        if re.search(r'\b(university|college|institute)\b', affiliation_lower):
            academic_count += 2

        # Check for known company names (higher weight)
        company_matches = sum(1 for company in self.KNOWN_COMPANIES
                            if company in affiliation_lower)
        if company_matches > 0:
            industry_count += company_matches * 2  # Give known companies higher weight

        # Calculate score - these thresholds were tuned through testing
        # TODO: Could make these configurable in the future
        if academic_count > 0 and industry_count == 0:
            return -0.7  # Clearly academic
        elif industry_count > 0 and academic_count == 0:
            return 0.8   # Clearly industry
        elif industry_count > academic_count:
            return 0.6   # Probably industry (increased from 0.5)
        elif academic_count > industry_count:
            return -0.4  # Probably academic (less negative to be more inclusive)
        else:
            return 0.1   # Unclear/neutral (slightly positive to be more inclusive)
    
    def get_company_affiliations(self, authors: List[Author]) -> List[str]:
        """
        Extract company names from industry authors' affiliations.
        
        Args:
            authors: List of Author objects
            
        Returns:
            List of company/organization names
        """
        companies = set()
        
        for author in authors:
            if self.is_industry_affiliation(author) and author.affiliation:
                company = self._extract_company_name(author.affiliation)
                if company:
                    companies.add(company)
        
        return list(companies)
    
    def _extract_company_name(self, affiliation: str) -> str:
        """
        Extract the main company/organization name from affiliation text.
        
        Args:
            affiliation: Full affiliation string
            
        Returns:
            Extracted company name
        """
        # Simple extraction - take the first part before comma or semicolon
        parts = re.split(r'[,;]', affiliation)
        if parts:
            company = parts[0].strip()
            # Remove common prefixes/suffixes
            company = re.sub(r'^(department of|division of|section of)\s+', '', company, flags=re.IGNORECASE)
            return company
        
        return affiliation.strip()
