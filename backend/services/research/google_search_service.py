"""
Google Search Service for ALwrity

This service provides real-time industry research using Google Custom Search API,
replacing the mock research system with actual web search capabilities.

Key Features:
- Industry-specific search queries
- Source credibility scoring and ranking
- Content extraction and insight generation
- Real-time information from the last month
- Fallback mechanisms for API failures

Dependencies:
- google-api-python-client
- aiohttp (for async HTTP requests)
- os (for environment variables)
- logging (for debugging)

Author: ALwrity Team
Version: 1.0
Last Updated: January 2025
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

class GoogleSearchService:
    """
    Service for conducting real industry research using Google Custom Search API.
    
    This service replaces the mock research system with actual web search capabilities,
    providing current, relevant industry information for content grounding.
    """
    
    def __init__(self):
        """Initialize the Google Search Service with API credentials."""
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google Search API credentials not configured. Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")
        else:
            self.enabled = True
            logger.info("Google Search Service initialized successfully")
    
    async def search_industry_trends(
        self, 
        topic: str, 
        industry: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for current industry trends and insights.
        
        Args:
            topic: The specific topic to research
            industry: The industry context for the search
            max_results: Maximum number of search results to return
            
        Returns:
            List of search results with credibility scoring
        """
        if not self.enabled:
            raise RuntimeError("Google Search Service is not enabled. Please configure API credentials.")
        
        try:
            # Construct industry-specific search query
            search_query = self._build_search_query(topic, industry)
            logger.info(f"Searching for: {search_query}")
            
            # Perform the search
            search_results = await self._perform_search(search_query, max_results)
            
            # Process and rank results
            processed_results = await self._process_search_results(search_results, topic, industry)
            
            # Extract insights and statistics
            insights = await self._extract_insights(processed_results, topic, industry)
            
            logger.info(f"Search completed successfully. Found {len(processed_results)} relevant sources.")
            
            return {
                "sources": processed_results,
                "key_insights": insights["insights"],
                "statistics": insights["statistics"],
                "grounding_enabled": True,
                "search_query": search_query,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            raise RuntimeError(f"Google search failed: {str(e)}")
    
    def _build_search_query(self, topic: str, industry: str) -> str:
        """
        Build an optimized search query for industry research.
        
        Args:
            topic: The specific topic to research
            industry: The industry context
            
        Returns:
            Optimized search query string
        """
        # Add industry-specific terms and current year for relevance
        current_year = datetime.now().year
        
        # Industry-specific search patterns
        industry_patterns = {
            "Technology": ["trends", "innovations", "developments", "insights"],
            "Healthcare": ["advances", "research", "treatments", "studies"],
            "Finance": ["market analysis", "trends", "reports", "insights"],
            "Marketing": ["strategies", "trends", "best practices", "case studies"],
            "Education": ["innovations", "trends", "research", "best practices"]
        }
        
        # Get industry-specific terms
        industry_terms = industry_patterns.get(industry, ["trends", "insights", "developments"])
        
        # Build the query
        query_components = [
            topic,
            industry,
            f"{current_year}",
            "latest",
            "trends",
            "insights"
        ]
        
        # Add industry-specific terms
        query_components.extend(industry_terms[:2])
        
        return " ".join(query_components)
    
    async def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Perform the actual Google Custom Search API call.
        
        Args:
            query: The search query to execute
            max_results: Maximum number of results to return
            
        Returns:
            Raw search results from Google API
        """
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(max_results, 10),  # Google CSE max is 10 per request
            "dateRestrict": "m1",  # Last month
            "sort": "date",  # Sort by date for current information
            "safe": "active"  # Safe search for professional content
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    error_text = await response.text()
                    logger.error(f"Google Search API error: {response.status} - {error_text}")
                    raise Exception(f"Search API returned status {response.status}")
    
    async def _process_search_results(
        self, 
        raw_results: List[Dict[str, Any]], 
        topic: str, 
        industry: str
    ) -> List[Dict[str, Any]]:
        """
        Process and rank search results by relevance and credibility.
        
        Args:
            raw_results: Raw search results from Google API
            topic: The research topic for relevance scoring
            industry: The industry context for relevance scoring
            
        Returns:
            Processed and ranked search results
        """
        processed_results = []
        
        for result in raw_results:
            try:
                # Extract basic information
                title = result.get("title", "")
                url = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(title, snippet, topic, industry)
                
                # Calculate credibility score
                credibility_score = self._calculate_credibility_score(url, title)
                
                # Extract publication date if available
                publication_date = self._extract_publication_date(result)
                
                # Calculate domain authority
                domain_authority = self._calculate_domain_authority(url)
                
                processed_result = {
                    "title": title,
                    "url": url,
                    "content": snippet,
                    "relevance_score": relevance_score,
                    "credibility_score": credibility_score,
                    "domain_authority": domain_authority,
                    "publication_date": publication_date,
                    "source_type": self._categorize_source(url, title),
                    "raw_result": result
                }
                
                processed_results.append(processed_result)
                
            except Exception as e:
                logger.warning(f"Failed to process search result: {str(e)}")
                continue
        
        # Sort by combined score (relevance + credibility)
        processed_results.sort(
            key=lambda x: (x["relevance_score"] + x["credibility_score"]) / 2,
            reverse=True
        )
        
        return processed_results
    
    def _calculate_relevance_score(self, title: str, snippet: str, topic: str, industry: str) -> float:
        """
        Calculate relevance score based on topic and industry alignment.
        
        Args:
            title: The title of the search result
            snippet: The snippet/description of the result
            topic: The research topic
            industry: The industry context
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        text = f"{title} {snippet}".lower()
        
        # Topic relevance (40% of score)
        topic_words = topic.lower().split()
        topic_matches = sum(1 for word in topic_words if word in text)
        topic_score = min(topic_matches / len(topic_words), 1.0) * 0.4
        
        # Industry relevance (30% of score)
        industry_words = industry.lower().split()
        industry_matches = sum(1 for word in industry_words if word in text)
        industry_score = min(industry_matches / len(industry_words), 1.0) * 0.3
        
        # Content quality indicators (30% of score)
        quality_indicators = [
            "research", "study", "analysis", "report", "insights",
            "trends", "data", "statistics", "findings", "expert"
        ]
        quality_matches = sum(1 for indicator in quality_indicators if indicator in text)
        quality_score = min(quality_matches / len(quality_indicators), 1.0) * 0.3
        
        score = topic_score + industry_score + quality_score
        return round(score, 3)
    
    def _calculate_credibility_score(self, url: str, title: str) -> float:
        """
        Calculate credibility score based on URL and title analysis.
        
        Args:
            url: The URL of the source
            title: The title of the content
            
        Returns:
            Credibility score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Domain credibility indicators
        credible_domains = [
            "harvard.edu", "stanford.edu", "mit.edu", "berkeley.edu",  # Academic
            "forbes.com", "bloomberg.com", "reuters.com", "wsj.com",   # Business
            "nature.com", "science.org", "ieee.org", "acm.org",       # Scientific
            "linkedin.com", "medium.com", "substack.com"              # Professional
        ]
        
        # Check if domain is in credible list
        domain = self._extract_domain(url)
        if any(credible_domain in domain for credible_domain in credible_domains):
            score += 0.3
        
        # Title credibility indicators
        credible_indicators = [
            "research", "study", "analysis", "report", "insights",
            "expert", "professional", "industry", "trends"
        ]
        
        title_lower = title.lower()
        credible_matches = sum(1 for indicator in credible_indicators if indicator in title_lower)
        score += min(credible_matches * 0.1, 0.2)
        
        return round(min(score, 1.0), 3)
    
    def _calculate_domain_authority(self, url: str) -> float:
        """
        Calculate domain authority based on URL analysis.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Domain authority score between 0.0 and 1.0
        """
        domain = self._extract_domain(url)
        
        # High authority domains
        high_authority = [
            "harvard.edu", "stanford.edu", "mit.edu", "berkeley.edu",
            "forbes.com", "bloomberg.com", "reuters.com", "wsj.com",
            "nature.com", "science.org", "ieee.org", "acm.org"
        ]
        
        # Medium authority domains
        medium_authority = [
            "linkedin.com", "medium.com", "substack.com", "techcrunch.com",
            "venturebeat.com", "wired.com", "theverge.com"
        ]
        
        if any(auth_domain in domain for auth_domain in high_authority):
            return 0.9
        elif any(auth_domain in domain for auth_domain in medium_authority):
            return 0.7
        else:
            # Basic scoring for other domains
            return 0.5
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return url.lower()
    
    def _extract_publication_date(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract publication date from search result if available."""
        # Check for various date fields
        date_fields = ["pagemap", "metatags", "date"]
        
        for field in date_fields:
            if field in result:
                date_value = result[field]
                if isinstance(date_value, dict):
                    # Look for common date keys
                    for date_key in ["date", "pubdate", "article:published_time"]:
                        if date_key in date_value:
                            return date_value[date_key]
                elif isinstance(date_value, str):
                    return date_value
        
        return None
    
    def _categorize_source(self, url: str, title: str) -> str:
        """Categorize the source type based on URL and title."""
        domain = self._extract_domain(url)
        title_lower = title.lower()
        
        # Academic sources
        if any(edu in domain for edu in [".edu", "harvard", "stanford", "mit"]):
            return "academic"
        
        # Business/News sources
        if any(biz in domain for biz in ["forbes", "bloomberg", "reuters", "wsj"]):
            return "business_news"
        
        # Professional platforms
        if any(prof in domain for prof in ["linkedin", "medium", "substack"]):
            return "professional_platform"
        
        # Research/Scientific
        if any(research in domain for research in ["nature", "science", "ieee", "acm"]):
            return "research_scientific"
        
        # Industry reports
        if any(report in title_lower for report in ["report", "study", "analysis", "research"]):
            return "industry_report"
        
        return "general"
    
    async def _extract_insights(
        self, 
        sources: List[Dict[str, Any]], 
        topic: str, 
        industry: str
    ) -> Dict[str, List[str]]:
        """
        Extract key insights and statistics from search results.
        
        Args:
            sources: Processed search results
            topic: The research topic
            industry: The industry context
            
        Returns:
            Dictionary containing insights and statistics
        """
        insights = []
        statistics = []
        
        # Extract insights from top sources
        top_sources = sources[:5]  # Top 5 most relevant sources
        
        for source in top_sources:
            content = source.get("content", "")
            
            # Look for insight patterns
            insight_patterns = [
                "shows", "indicates", "suggests", "reveals", "demonstrates",
                "highlights", "emphasizes", "points to", "suggests that"
            ]
            
            for pattern in insight_patterns:
                if pattern in content.lower():
                    # Extract the sentence containing the insight
                    sentences = content.split(". ")
                    for sentence in sentences:
                        if pattern in sentence.lower():
                            insights.append(sentence.strip())
                            break
            
            # Look for statistical patterns
            stat_patterns = [
                r'\d+%',  # Percentages
                r'\d+ percent',  # Written percentages
                r'\$\d+',  # Dollar amounts
                r'\d+ million',  # Millions
                r'\d+ billion',  # Billions
                r'\d+ out of \d+',  # Ratios
            ]
            
            import re
            for pattern in stat_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    statistics.append(f"{match}")
        
        # Limit the number of insights and statistics
        insights = insights[:10]  # Top 10 insights
        statistics = statistics[:10]  # Top 10 statistics
        
        return {
            "insights": insights,
            "statistics": statistics
        }
    
    
    async def test_api_connection(self) -> Dict[str, Any]:
        """
        Test the Google Search API connection.
        
        Returns:
            Test results and status information
        """
        if not self.enabled:
            raise RuntimeError("Google Search Service is not enabled. Please configure API credentials.")
        
        try:
            # Perform a simple test search
            test_query = "AI technology trends 2024"
            test_results = await self._perform_search(test_query, 1)
            
            return {
                "status": "success",
                "message": "Google Search API connection successful",
                "enabled": True,
                "test_results_count": len(test_results),
                "api_key_configured": bool(self.api_key),
                "search_engine_configured": bool(self.search_engine_id)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Google Search API connection failed: {str(e)}",
                "enabled": False,
                "error": str(e)
            }
