#!/usr/bin/env python3
"""
Unit tests for the PubMed Paper Finder.
Tests core functionality including API integration, parsing, and filtering.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from paper_finder.fetch import PubMedFetcher
from paper_finder.parser import PubMedParser, Paper, Author
from paper_finder.filter import AffiliationFilter
from paper_finder.output import CSVExporter


class TestPubMedFetcher(unittest.TestCase):
    """Test PubMed API fetching functionality."""
    
    def setUp(self):
        self.fetcher = PubMedFetcher(email="test@example.com")
    
    def test_init(self):
        """Test fetcher initialization."""
        self.assertEqual(self.fetcher.email, "test@example.com")
        self.assertEqual(self.fetcher.tool, "get-papers-list")
    
    @patch('paper_finder.fetch.requests.Session.get')
    def test_search_papers_success(self, mock_get):
        """Test successful paper search."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "esearchresult": {"idlist": ["12345", "67890"]}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.fetcher.search_papers("test query", 10)
        
        self.assertEqual(result, ["12345", "67890"])
        mock_get.assert_called_once()
    
    @patch('paper_finder.fetch.requests.Session.get')
    def test_search_papers_empty_result(self, mock_get):
        """Test search with no results."""
        mock_response = Mock()
        mock_response.json.return_value = {"esearchresult": {"idlist": []}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.fetcher.search_papers("nonexistent query")
        
        self.assertEqual(result, [])


class TestPubMedParser(unittest.TestCase):
    """Test XML parsing functionality."""
    
    def setUp(self):
        self.parser = PubMedParser()
    
    def test_parse_empty_xml(self):
        """Test parsing empty XML."""
        result = self.parser.parse_papers("<PubmedArticleSet></PubmedArticleSet>")
        self.assertEqual(result, [])
    
    def test_author_creation(self):
        """Test Author dataclass creation."""
        author = Author(
            last_name="Smith",
            first_name="John",
            initials="J",
            affiliation="Test University",
            email="john@test.edu"
        )
        
        self.assertEqual(author.last_name, "Smith")
        self.assertEqual(author.email, "john@test.edu")
    
    def test_paper_creation(self):
        """Test Paper dataclass creation."""
        authors = [Author("Smith", "John", "J", "Test University")]
        paper = Paper(
            pubmed_id="12345",
            title="Test Paper",
            publication_date="2024-01-01",
            authors=authors,
            journal="Test Journal"
        )
        
        self.assertEqual(paper.pubmed_id, "12345")
        self.assertEqual(len(paper.authors), 1)


class TestAffiliationFilter(unittest.TestCase):
    """Test author affiliation filtering."""
    
    def setUp(self):
        self.filter = AffiliationFilter(debug=False)
    
    def test_academic_author_identification(self):
        """Test identification of academic authors."""
        academic_author = Author(
            last_name="Smith",
            first_name="John",
            initials="J",
            affiliation="Department of Biology, Harvard University",
            email="john.smith@harvard.edu"
        )
        
        result = self.filter.is_industry_affiliation(academic_author)
        self.assertFalse(result)
    
    def test_industry_author_identification(self):
        """Test identification of industry authors."""
        industry_author = Author(
            last_name="Johnson",
            first_name="Jane",
            initials="J",
            affiliation="Pfizer Inc., Research Division",
            email="jane.johnson@pfizer.com"
        )
        
        result = self.filter.is_industry_affiliation(industry_author)
        self.assertTrue(result)
    
    def test_email_domain_scoring(self):
        """Test email domain scoring algorithm."""
        # Academic email
        academic_score = self.filter._score_email_domain("test@harvard.edu")
        self.assertLess(academic_score, 0)
        
        # Commercial email
        commercial_score = self.filter._score_email_domain("test@pfizer.com")
        self.assertGreater(commercial_score, 0)
    
    def test_affiliation_text_scoring(self):
        """Test affiliation text scoring."""
        # Academic affiliation
        academic_score = self.filter._score_affiliation_text("harvard university department")
        self.assertLess(academic_score, 0)
        
        # Industry affiliation
        industry_score = self.filter._score_affiliation_text("pfizer pharmaceutical company")
        self.assertGreater(industry_score, 0)


class TestCSVExporter(unittest.TestCase):
    """Test CSV export functionality."""
    
    def setUp(self):
        self.exporter = CSVExporter(debug=False)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_csv_export_structure(self):
        """Test CSV export creates correct structure."""
        # Create test data
        authors = [Author("Smith", "John", "J", "Pfizer Inc.", "john@pfizer.com")]
        papers = [Paper("12345", "Test Paper", "2024-01-01", authors, journal="Test Journal")]
        
        output_file = os.path.join(self.temp_dir, "test_output.csv")
        self.exporter.export_papers(papers, output_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Verify CSV structure
        df = pd.read_csv(output_file)
        expected_columns = [
            "PubmedID", "Title", "Publication Date", "Non-academic Author(s)",
            "Company Affiliation(s)", "Corresponding Author Email", "Journal",
            "Total Authors", "Industry Authors Count"
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns)
    
    def test_author_formatting(self):
        """Test author name formatting."""
        authors = [
            Author("Smith", "John", "J", "Test Affiliation"),
            Author("Doe", "", "J.D.", "Test Affiliation")
        ]
        
        result = self.exporter._format_authors(authors)
        
        self.assertIn("Smith, John", result)
        self.assertIn("Doe, J.D.", result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test complete workflow with mock data."""
        # Create test components
        fetcher = PubMedFetcher()
        parser = PubMedParser()
        filter_obj = AffiliationFilter()
        exporter = CSVExporter()
        
        # Create test data
        authors = [
            Author("Smith", "John", "J", "Harvard University", "john@harvard.edu"),
            Author("Johnson", "Jane", "J", "Pfizer Inc.", "jane@pfizer.com")
        ]
        papers = [Paper("12345", "Test Paper", "2024-01-01", authors)]
        
        # Filter for industry authors
        papers_with_industry = filter_obj.filter_papers_with_industry_authors(papers)
        
        # Export results
        output_file = os.path.join(self.temp_dir, "integration_test.csv")
        exporter.export_papers(papers_with_industry, output_file)
        
        # Verify results
        self.assertTrue(os.path.exists(output_file))
        df = pd.read_csv(output_file)
        self.assertGreater(len(df), 0)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
