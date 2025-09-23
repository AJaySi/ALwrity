"""
Unit tests for ResearchDataFilter.

Tests the filtering and cleaning functionality for research data.
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from models.blog_models import (
    BlogResearchResponse,
    ResearchSource,
    GroundingMetadata,
    GroundingChunk,
    GroundingSupport,
    Citation,
)
from services.blog_writer.research.data_filter import ResearchDataFilter


class TestResearchDataFilter:
    """Test cases for ResearchDataFilter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.filter = ResearchDataFilter()
        
        # Create sample research sources
        self.sample_sources = [
            ResearchSource(
                title="High Quality AI Article",
                url="https://example.com/ai-article",
                excerpt="This is a comprehensive article about artificial intelligence trends in 2024 with detailed analysis and expert insights.",
                credibility_score=0.95,
                published_at="2025-08-15",
                index=0,
                source_type="web"
            ),
            ResearchSource(
                title="Low Quality Source",
                url="https://example.com/low-quality",
                excerpt="This is a low quality source with very poor credibility score and outdated information from 2020.",
                credibility_score=0.3,
                published_at="2020-01-01",
                index=1,
                source_type="web"
            ),
            ResearchSource(
                title="PDF Document",
                url="https://example.com/document.pdf",
                excerpt="This is a PDF document with research data",
                credibility_score=0.8,
                published_at="2025-08-01",
                index=2,
                source_type="web"
            ),
            ResearchSource(
                title="Recent AI Study",
                url="https://example.com/ai-study",
                excerpt="A recent study on AI adoption shows significant growth in enterprise usage with detailed statistics and case studies.",
                credibility_score=0.9,
                published_at="2025-09-01",
                index=3,
                source_type="web"
            )
        ]
        
        # Create sample grounding metadata
        self.sample_grounding_metadata = GroundingMetadata(
            grounding_chunks=[
                GroundingChunk(
                    title="High Confidence Chunk",
                    url="https://example.com/chunk1",
                    confidence_score=0.95
                ),
                GroundingChunk(
                    title="Low Confidence Chunk",
                    url="https://example.com/chunk2",
                    confidence_score=0.5
                ),
                GroundingChunk(
                    title="Medium Confidence Chunk",
                    url="https://example.com/chunk3",
                    confidence_score=0.8
                )
            ],
            grounding_supports=[
                GroundingSupport(
                    confidence_scores=[0.9, 0.85],
                    grounding_chunk_indices=[0, 1],
                    segment_text="High confidence support text with expert insights"
                ),
                GroundingSupport(
                    confidence_scores=[0.4, 0.3],
                    grounding_chunk_indices=[2, 3],
                    segment_text="Low confidence support text"
                )
            ],
            citations=[
                Citation(
                    citation_type="expert_opinion",
                    start_index=0,
                    end_index=50,
                    text="Expert opinion on AI trends",
                    source_indices=[0],
                    reference="Source 1"
                ),
                Citation(
                    citation_type="statistical_data",
                    start_index=51,
                    end_index=100,
                    text="Statistical data showing AI adoption rates",
                    source_indices=[1],
                    reference="Source 2"
                ),
                Citation(
                    citation_type="inline",
                    start_index=101,
                    end_index=150,
                    text="Generic inline citation",
                    source_indices=[2],
                    reference="Source 3"
                )
            ]
        )
        
        # Create sample research response
        self.sample_research_response = BlogResearchResponse(
            success=True,
            sources=self.sample_sources,
            keyword_analysis={
                'primary': ['artificial intelligence', 'AI trends', 'machine learning'],
                'secondary': ['AI adoption', 'enterprise AI', 'AI technology'],
                'long_tail': ['AI trends 2024', 'enterprise AI adoption rates', 'AI technology benefits'],
                'semantic_keywords': ['artificial intelligence', 'machine learning', 'deep learning'],
                'trending_terms': ['AI 2024', 'generative AI', 'AI automation'],
                'content_gaps': [
                    'AI ethics in small businesses',
                    'AI implementation guide for startups',
                    'AI cost-benefit analysis for SMEs',
                    'general overview',  # Should be filtered out
                    'basics'  # Should be filtered out
                ],
                'search_intent': 'informational',
                'difficulty': 7
            },
            competitor_analysis={
                'top_competitors': ['Competitor A', 'Competitor B', 'Competitor C'],
                'opportunities': ['Market gap 1', 'Market gap 2'],
                'competitive_advantages': ['Advantage 1', 'Advantage 2'],
                'market_positioning': 'Premium positioning'
            },
            suggested_angles=[
                'AI trends in 2024',
                'Enterprise AI adoption',
                'AI implementation strategies'
            ],
            search_widget="<div>Search widget HTML</div>",
            search_queries=["AI trends 2024", "enterprise AI adoption"],
            grounding_metadata=self.sample_grounding_metadata
        )
    
    def test_filter_sources_quality_filtering(self):
        """Test that sources are filtered by quality criteria."""
        filtered_sources = self.filter.filter_sources(self.sample_sources)
        
        # Should filter out low quality source (credibility < 0.6) and PDF document
        assert len(filtered_sources) == 2  # Only high quality and recent AI study should pass
        assert all(source.credibility_score >= 0.6 for source in filtered_sources)
        
        # Should filter out sources with short excerpts
        assert all(len(source.excerpt) >= 50 for source in filtered_sources)
    
    def test_filter_sources_relevance_filtering(self):
        """Test that irrelevant sources are filtered out."""
        filtered_sources = self.filter.filter_sources(self.sample_sources)
        
        # Should filter out PDF document
        pdf_sources = [s for s in filtered_sources if s.url.endswith('.pdf')]
        assert len(pdf_sources) == 0
    
    def test_filter_sources_recency_filtering(self):
        """Test that old sources are filtered out."""
        filtered_sources = self.filter.filter_sources(self.sample_sources)
        
        # Should filter out old source (2020)
        old_sources = [s for s in filtered_sources if s.published_at == "2020-01-01"]
        assert len(old_sources) == 0
    
    def test_filter_sources_max_limit(self):
        """Test that sources are limited to max_sources."""
        # Create more sources than max_sources
        many_sources = self.sample_sources * 5  # 20 sources
        filtered_sources = self.filter.filter_sources(many_sources)
        
        assert len(filtered_sources) <= self.filter.max_sources
    
    def test_filter_grounding_metadata_confidence_filtering(self):
        """Test that grounding metadata is filtered by confidence."""
        filtered_metadata = self.filter.filter_grounding_metadata(self.sample_grounding_metadata)
        
        assert filtered_metadata is not None
        
        # Should filter out low confidence chunks
        assert len(filtered_metadata.grounding_chunks) == 2
        assert all(chunk.confidence_score >= 0.7 for chunk in filtered_metadata.grounding_chunks)
        
        # Should filter out low confidence supports
        assert len(filtered_metadata.grounding_supports) == 1
        assert all(max(support.confidence_scores) >= 0.7 for support in filtered_metadata.grounding_supports)
        
        # Should filter out irrelevant citations
        assert len(filtered_metadata.citations) == 2
        relevant_types = ['expert_opinion', 'statistical_data', 'recent_news', 'research_study']
        assert all(citation.citation_type in relevant_types for citation in filtered_metadata.citations)
    
    def test_clean_keyword_analysis(self):
        """Test that keyword analysis is cleaned and deduplicated."""
        keyword_analysis = {
            'primary': ['AI', 'artificial intelligence', 'AI', 'machine learning', ''],
            'secondary': ['AI adoption', 'enterprise AI', 'ai adoption'],  # Case duplicates
            'long_tail': ['AI trends 2024', 'ai trends 2024', 'AI TRENDS 2024'],  # Case duplicates
            'search_intent': 'informational',
            'difficulty': 7
        }
        
        cleaned_analysis = self.filter.clean_keyword_analysis(keyword_analysis)
        
        # Should remove duplicates and empty strings (keywords are converted to lowercase)
        assert len(cleaned_analysis['primary']) == 3
        assert 'ai' in cleaned_analysis['primary']
        assert 'artificial intelligence' in cleaned_analysis['primary']
        assert 'machine learning' in cleaned_analysis['primary']
        
        # Should handle case-insensitive deduplication
        assert len(cleaned_analysis['secondary']) == 2
        assert len(cleaned_analysis['long_tail']) == 1
        
        # Should preserve other fields
        assert cleaned_analysis['search_intent'] == 'informational'
        assert cleaned_analysis['difficulty'] == 7
    
    def test_filter_content_gaps(self):
        """Test that content gaps are filtered for quality and relevance."""
        content_gaps = [
            'AI ethics in small businesses',
            'AI implementation guide for startups',
            'general overview',  # Should be filtered out
            'basics',  # Should be filtered out
            'a',  # Too short, should be filtered out
            'AI cost-benefit analysis for SMEs'
        ]
        
        filtered_gaps = self.filter.filter_content_gaps(content_gaps, self.sample_research_response)
        
        # Should filter out generic and short gaps
        assert len(filtered_gaps) >= 3  # At least the good ones should pass
        assert 'AI ethics in small businesses' in filtered_gaps
        assert 'AI implementation guide for startups' in filtered_gaps
        assert 'AI cost-benefit analysis for SMEs' in filtered_gaps
        assert 'general overview' not in filtered_gaps
        assert 'basics' not in filtered_gaps
    
    def test_filter_research_data_integration(self):
        """Test the complete filtering pipeline."""
        filtered_research = self.filter.filter_research_data(self.sample_research_response)
        
        # Should maintain success status
        assert filtered_research.success is True
        
        # Should filter sources
        assert len(filtered_research.sources) < len(self.sample_research_response.sources)
        assert len(filtered_research.sources) >= 0  # May be 0 if all sources are filtered out
        
        # Should filter grounding metadata
        if filtered_research.grounding_metadata:
            assert len(filtered_research.grounding_metadata.grounding_chunks) < len(self.sample_grounding_metadata.grounding_chunks)
        
        # Should clean keyword analysis
        assert 'primary' in filtered_research.keyword_analysis
        assert len(filtered_research.keyword_analysis['primary']) <= self.filter.max_keywords_per_category
        
        # Should filter content gaps
        assert len(filtered_research.keyword_analysis['content_gaps']) < len(self.sample_research_response.keyword_analysis['content_gaps'])
        
        # Should preserve other fields
        assert filtered_research.suggested_angles == self.sample_research_response.suggested_angles
        assert filtered_research.search_widget == self.sample_research_response.search_widget
        assert filtered_research.search_queries == self.sample_research_response.search_queries
    
    def test_filter_with_empty_data(self):
        """Test filtering with empty or None data."""
        empty_research = BlogResearchResponse(
            success=True,
            sources=[],
            keyword_analysis={},
            competitor_analysis={},
            suggested_angles=[],
            search_widget="",
            search_queries=[],
            grounding_metadata=None
        )
        
        filtered_research = self.filter.filter_research_data(empty_research)
        
        assert filtered_research.success is True
        assert len(filtered_research.sources) == 0
        assert filtered_research.grounding_metadata is None
        # keyword_analysis may contain content_gaps even if empty
        assert 'content_gaps' in filtered_research.keyword_analysis
    
    def test_parse_date_functionality(self):
        """Test date parsing functionality."""
        # Test various date formats
        test_dates = [
            "2024-01-15",
            "2024-01-15T10:30:00",
            "2024-01-15T10:30:00Z",
            "January 15, 2024",
            "Jan 15, 2024",
            "15 January 2024",
            "01/15/2024",
            "15/01/2024"
        ]
        
        for date_str in test_dates:
            parsed_date = self.filter._parse_date(date_str)
            assert parsed_date is not None
            assert isinstance(parsed_date, datetime)
        
        # Test invalid date
        invalid_date = self.filter._parse_date("invalid date")
        assert invalid_date is None
        
        # Test None date
        none_date = self.filter._parse_date(None)
        assert none_date is None
    
    def test_clean_keyword_list_functionality(self):
        """Test keyword list cleaning functionality."""
        keywords = [
            'AI',
            'artificial intelligence',
            'AI',  # Duplicate
            'the',  # Stop word
            'machine learning',
            '',  # Empty
            '   ',  # Whitespace only
            'MACHINE LEARNING',  # Case duplicate
            'ai'  # Case duplicate
        ]
        
        cleaned_keywords = self.filter._clean_keyword_list(keywords)
        
        # Should remove duplicates, stop words, and empty strings
        assert len(cleaned_keywords) == 3
        assert 'ai' in cleaned_keywords
        assert 'artificial intelligence' in cleaned_keywords
        assert 'machine learning' in cleaned_keywords
        assert 'the' not in cleaned_keywords
        assert '' not in cleaned_keywords


if __name__ == '__main__':
    pytest.main([__file__])
