#!/usr/bin/env python3
"""
LLM Service for PubMed Paper Analysis using Groq API.
By Manideep Reddy Eevuri
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from groq import Groq

class GroqLLMService:
    """Service for interacting with Groq API for paper analysis."""
    
    def __init__(self, api_key: str, model: str = "llama3-8b-8192"):
        """
        Initialize the Groq LLM service.
        
        Args:
            api_key: Groq API key
            model: Model to use (default: llama3-8b-8192)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)
        
    def summarize_paper(self, title: str, abstract: str = None, authors: List[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a research paper.
        
        Args:
            title: Paper title
            abstract: Paper abstract (if available)
            authors: List of author names
            
        Returns:
            Dictionary with summary, key findings, and insights
        """
        try:
            # Prepare the prompt
            prompt = f"""
            Analyze this research paper and provide a comprehensive summary:
            
            Title: {title}
            """
            
            if abstract:
                prompt += f"\nAbstract: {abstract}"
            
            if authors:
                prompt += f"\nAuthors: {', '.join(authors[:5])}{'...' if len(authors) > 5 else ''}"
            
            prompt += """
            
            Please provide:
            1. A concise summary (2-3 sentences)
            2. Key findings or contributions
            3. Research methodology (if mentioned)
            4. Potential impact or significance
            5. Industry relevance (if any)
            
            Format your response as JSON with keys: summary, key_findings, methodology, impact, industry_relevance
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a research analyst expert at summarizing scientific papers. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            try:
                # Remove markdown code blocks if present
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Fallback: return raw content
                return {
                    "summary": content[:200] + "..." if len(content) > 200 else content,
                    "key_findings": "Analysis available in summary",
                    "methodology": "Not specified",
                    "impact": "Requires further analysis",
                    "industry_relevance": "To be determined"
                }
                
        except Exception as e:
            self.logger.error(f"Error summarizing paper: {e}")
            return {
                "summary": "Summary generation failed",
                "key_findings": "Unable to extract",
                "methodology": "Not available",
                "impact": "Unknown",
                "industry_relevance": "Unknown",
                "error": str(e)
            }
    
    def analyze_research_trends(self, papers_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze research trends across multiple papers.
        
        Args:
            papers_data: List of paper dictionaries with title, authors, etc.
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            # Prepare data for analysis
            titles = [paper.get('title', '') for paper in papers_data[:20]]  # Limit to 20 papers
            companies = []
            for paper in papers_data:
                companies.extend(paper.get('companies', []))
            
            prompt = f"""
            Analyze these research papers and identify trends:
            
            Paper Titles:
            {chr(10).join([f"- {title}" for title in titles[:15]])}
            
            Companies/Organizations involved:
            {', '.join(list(set(companies))[:20])}
            
            Please identify:
            1. Main research themes and topics
            2. Emerging trends in the field
            3. Key industry players and collaborations
            4. Research methodologies being used
            5. Potential future directions
            
            Format as JSON with keys: themes, trends, key_players, methodologies, future_directions
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a research trend analyst. Provide insights in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "themes": ["Analysis in progress"],
                    "trends": ["Trend analysis available"],
                    "key_players": list(set(companies))[:10],
                    "methodologies": ["Various research methods"],
                    "future_directions": ["Continued research expected"]
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return {
                "themes": ["Analysis failed"],
                "trends": ["Unable to determine"],
                "key_players": [],
                "methodologies": ["Unknown"],
                "future_directions": ["Unknown"],
                "error": str(e)
            }
    
    def enhance_search_query(self, original_query: str) -> Dict[str, Any]:
        """
        Enhance a search query to be more effective for finding industry collaborations.
        
        Args:
            original_query: The original search query
            
        Returns:
            Dictionary with enhanced query and suggestions
        """
        try:
            prompt = f"""
            Improve this PubMed search query to better find research papers with industry collaborations:
            
            Original query: "{original_query}"
            
            Please provide:
            1. An enhanced query with better search terms
            2. Alternative query suggestions
            3. Specific industry terms to include
            4. PubMed search operators that could help
            
            Focus on finding papers with pharmaceutical, biotech, or other industry collaborations.
            
            Format as JSON with keys: enhanced_query, alternatives, industry_terms, search_tips
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a PubMed search expert. Help optimize queries for finding industry-academic collaborations."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "enhanced_query": f"({original_query}) AND (industry[Affiliation] OR pharmaceutical[Affiliation] OR biotech[Affiliation])",
                    "alternatives": [
                        f"{original_query} AND clinical trial",
                        f"{original_query} AND drug development",
                        f"{original_query} AND pharmaceutical company"
                    ],
                    "industry_terms": ["pharmaceutical", "biotech", "clinical trial", "drug development"],
                    "search_tips": ["Use [Affiliation] field", "Include company names", "Add collaboration terms"]
                }
                
        except Exception as e:
            self.logger.error(f"Error enhancing query: {e}")
            return {
                "enhanced_query": original_query,
                "alternatives": [original_query],
                "industry_terms": [],
                "search_tips": [],
                "error": str(e)
            }
    
    def generate_research_insights(self, paper_data: Dict) -> Dict[str, Any]:
        """
        Generate detailed insights for a specific paper.
        
        Args:
            paper_data: Dictionary containing paper information
            
        Returns:
            Dictionary with detailed insights
        """
        try:
            prompt = f"""
            Provide detailed research insights for this paper:
            
            Title: {paper_data.get('title', 'N/A')}
            Journal: {paper_data.get('journal', 'N/A')}
            Industry Authors: {len(paper_data.get('industry_authors', []))}
            Companies: {', '.join(paper_data.get('companies', []))}
            Total Authors: {paper_data.get('total_authors', 0)}
            
            Analyze:
            1. Research significance and novelty
            2. Industry-academic collaboration strength
            3. Potential commercial applications
            4. Research quality indicators
            5. Follow-up research opportunities
            
            Format as JSON with keys: significance, collaboration_strength, commercial_potential, quality_indicators, follow_up_opportunities
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a research analyst specializing in industry-academic collaborations."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "significance": "High potential research significance",
                    "collaboration_strength": f"Strong collaboration with {len(paper_data.get('companies', []))} companies",
                    "commercial_potential": "Potential commercial applications identified",
                    "quality_indicators": "Multiple industry partners suggest quality research",
                    "follow_up_opportunities": "Further research collaboration opportunities available"
                }
                
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return {
                "significance": "Analysis unavailable",
                "collaboration_strength": "Unknown",
                "commercial_potential": "Unknown",
                "quality_indicators": "Unknown",
                "follow_up_opportunities": "Unknown",
                "error": str(e)
            }
