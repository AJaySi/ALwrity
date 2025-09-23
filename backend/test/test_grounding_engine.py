"""
Unit tests for GroundingContextEngine.

Tests the enhanced grounding metadata utilization functionality.
"""

import pytest
from typing import List

from models.blog_models import (
    GroundingMetadata,
    GroundingChunk,
    GroundingSupport,
    Citation,
    BlogOutlineSection,
    BlogResearchResponse,
    ResearchSource,
)
from services.blog_writer.outline.grounding_engine import GroundingContextEngine


class TestGroundingContextEngine:
    """Test cases for GroundingContextEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = GroundingContextEngine()
        
        # Create sample grounding chunks
        self.sample_chunks = [
            GroundingChunk(
                title="AI Research Study 2025: Machine Learning Breakthroughs",
                url="https://research.university.edu/ai-study-2025",
                confidence_score=0.95
            ),
            GroundingChunk(
                title="Enterprise AI Implementation Guide",
                url="https://techcorp.com/enterprise-ai-guide",
                confidence_score=0.88
            ),
            GroundingChunk(
                title="Machine Learning Algorithms Explained",
                url="https://blog.datascience.com/ml-algorithms",
                confidence_score=0.82
            ),
            GroundingChunk(
                title="AI Ethics and Responsible Development",
                url="https://ethics.org/ai-responsible-development",
                confidence_score=0.90
            ),
            GroundingChunk(
                title="Personal Opinion on AI Trends",
                url="https://personal-blog.com/ai-opinion",
                confidence_score=0.65
            )
        ]
        
        # Create sample grounding supports
        self.sample_supports = [
            GroundingSupport(
                confidence_scores=[0.92, 0.89],
                grounding_chunk_indices=[0, 1],
                segment_text="Recent research shows that artificial intelligence is transforming enterprise operations with significant improvements in efficiency and decision-making capabilities.",
                start_index=0,
                end_index=150
            ),
            GroundingSupport(
                confidence_scores=[0.85, 0.78],
                grounding_chunk_indices=[2, 3],
                segment_text="Machine learning algorithms are becoming more sophisticated, enabling better pattern recognition and predictive analytics in business applications.",
                start_index=151,
                end_index=300
            ),
            GroundingSupport(
                confidence_scores=[0.45, 0.52],
                grounding_chunk_indices=[4],
                segment_text="Some people think AI is overhyped and won't deliver on its promises.",
                start_index=301,
                end_index=400
            )
        ]
        
        # Create sample citations
        self.sample_citations = [
            Citation(
                citation_type="expert_opinion",
                start_index=0,
                end_index=50,
                text="AI research shows significant improvements in enterprise operations",
                source_indices=[0],
                reference="Source 1"
            ),
            Citation(
                citation_type="statistical_data",
                start_index=51,
                end_index=100,
                text="85% of enterprises report improved efficiency with AI implementation",
                source_indices=[1],
                reference="Source 2"
            ),
            Citation(
                citation_type="research_study",
                start_index=101,
                end_index=150,
                text="University study demonstrates 40% increase in decision-making accuracy",
                source_indices=[0],
                reference="Source 1"
            )
        ]
        
        # Create sample grounding metadata
        self.sample_grounding_metadata = GroundingMetadata(
            grounding_chunks=self.sample_chunks,
            grounding_supports=self.sample_supports,
            citations=self.sample_citations,
            search_entry_point="AI trends and enterprise implementation",
            web_search_queries=[
                "AI trends 2025 enterprise",
                "machine learning business applications",
                "AI implementation best practices"
            ]
        )
        
        # Create sample outline section
        self.sample_section = BlogOutlineSection(
            id="s1",
            heading="AI Implementation in Enterprise",
            subheadings=["Benefits of AI", "Implementation Challenges", "Best Practices"],
            key_points=["Improved efficiency", "Cost reduction", "Better decision making"],
            references=[],
            target_words=400,
            keywords=["AI", "enterprise", "implementation", "machine learning"]
        )
    
    def test_extract_contextual_insights(self):
        """Test extraction of contextual insights from grounding metadata."""
        insights = self.engine.extract_contextual_insights(self.sample_grounding_metadata)
        
        # Should have all insight categories
        expected_categories = [
            'confidence_analysis', 'authority_analysis', 'temporal_analysis',
            'content_relationships', 'citation_insights', 'search_intent_insights',
            'quality_indicators'
        ]
        
        for category in expected_categories:
            assert category in insights
        
        # Test confidence analysis
        confidence_analysis = insights['confidence_analysis']
        assert 'average_confidence' in confidence_analysis
        assert 'high_confidence_count' in confidence_analysis
        assert confidence_analysis['average_confidence'] > 0.0
        
        # Test authority analysis
        authority_analysis = insights['authority_analysis']
        assert 'average_authority' in authority_analysis
        assert 'high_authority_sources' in authority_analysis
        assert 'authority_distribution' in authority_analysis
    
    def test_extract_contextual_insights_empty_metadata(self):
        """Test extraction with empty grounding metadata."""
        insights = self.engine.extract_contextual_insights(None)
        
        # Should return empty insights structure
        assert insights['confidence_analysis']['average_confidence'] == 0.0
        assert insights['authority_analysis']['high_authority_sources'] == 0
        assert insights['temporal_analysis']['recent_content'] == 0
    
    def test_analyze_confidence_patterns(self):
        """Test confidence pattern analysis."""
        confidence_analysis = self.engine._analyze_confidence_patterns(self.sample_grounding_metadata)
        
        assert 'average_confidence' in confidence_analysis
        assert 'high_confidence_count' in confidence_analysis
        assert 'confidence_distribution' in confidence_analysis
        
        # Should have reasonable confidence values
        assert 0.0 <= confidence_analysis['average_confidence'] <= 1.0
        assert confidence_analysis['high_confidence_count'] >= 0
    
    def test_analyze_source_authority(self):
        """Test source authority analysis."""
        authority_analysis = self.engine._analyze_source_authority(self.sample_grounding_metadata)
        
        assert 'average_authority' in authority_analysis
        assert 'high_authority_sources' in authority_analysis
        assert 'authority_distribution' in authority_analysis
        
        # Should have reasonable authority values
        assert 0.0 <= authority_analysis['average_authority'] <= 1.0
        assert authority_analysis['high_authority_sources'] >= 0
    
    def test_analyze_temporal_relevance(self):
        """Test temporal relevance analysis."""
        temporal_analysis = self.engine._analyze_temporal_relevance(self.sample_grounding_metadata)
        
        assert 'recent_content' in temporal_analysis
        assert 'trending_topics' in temporal_analysis
        assert 'evergreen_content' in temporal_analysis
        assert 'temporal_balance' in temporal_analysis
        
        # Should have reasonable temporal values
        assert temporal_analysis['recent_content'] >= 0
        assert temporal_analysis['evergreen_content'] >= 0
        assert temporal_analysis['temporal_balance'] in ['recent_heavy', 'evergreen_heavy', 'balanced', 'unknown']
    
    def test_analyze_content_relationships(self):
        """Test content relationship analysis."""
        relationships = self.engine._analyze_content_relationships(self.sample_grounding_metadata)
        
        assert 'related_concepts' in relationships
        assert 'content_gaps' in relationships
        assert 'concept_coverage' in relationships
        assert 'gap_count' in relationships
        
        # Should have reasonable relationship values
        assert isinstance(relationships['related_concepts'], list)
        assert isinstance(relationships['content_gaps'], list)
        assert relationships['concept_coverage'] >= 0
        assert relationships['gap_count'] >= 0
    
    def test_analyze_citation_patterns(self):
        """Test citation pattern analysis."""
        citation_analysis = self.engine._analyze_citation_patterns(self.sample_grounding_metadata)
        
        assert 'citation_types' in citation_analysis
        assert 'total_citations' in citation_analysis
        assert 'citation_density' in citation_analysis
        assert 'citation_quality' in citation_analysis
        
        # Should have reasonable citation values
        assert citation_analysis['total_citations'] == len(self.sample_citations)
        assert citation_analysis['citation_density'] >= 0.0
        assert 0.0 <= citation_analysis['citation_quality'] <= 1.0
    
    def test_analyze_search_intent(self):
        """Test search intent analysis."""
        intent_analysis = self.engine._analyze_search_intent(self.sample_grounding_metadata)
        
        assert 'intent_signals' in intent_analysis
        assert 'user_questions' in intent_analysis
        assert 'primary_intent' in intent_analysis
        
        # Should have reasonable intent values
        assert isinstance(intent_analysis['intent_signals'], list)
        assert isinstance(intent_analysis['user_questions'], list)
        assert intent_analysis['primary_intent'] in ['informational', 'comparison', 'transactional']
    
    def test_assess_quality_indicators(self):
        """Test quality indicator assessment."""
        quality_indicators = self.engine._assess_quality_indicators(self.sample_grounding_metadata)
        
        assert 'overall_quality' in quality_indicators
        assert 'quality_factors' in quality_indicators
        assert 'quality_grade' in quality_indicators
        
        # Should have reasonable quality values
        assert 0.0 <= quality_indicators['overall_quality'] <= 1.0
        assert isinstance(quality_indicators['quality_factors'], list)
        assert quality_indicators['quality_grade'] in ['A', 'B', 'C', 'D', 'F']
    
    def test_calculate_chunk_authority(self):
        """Test chunk authority calculation."""
        # Test high authority chunk
        high_authority_chunk = self.sample_chunks[0]  # Research study
        authority_score = self.engine._calculate_chunk_authority(high_authority_chunk)
        assert 0.0 <= authority_score <= 1.0
        assert authority_score > 0.5  # Should be high authority
        
        # Test low authority chunk
        low_authority_chunk = self.sample_chunks[4]  # Personal opinion
        authority_score = self.engine._calculate_chunk_authority(low_authority_chunk)
        assert 0.0 <= authority_score <= 1.0
        assert authority_score < 0.7  # Should be lower authority
    
    def test_get_authority_sources(self):
        """Test getting high-authority sources."""
        authority_sources = self.engine.get_authority_sources(self.sample_grounding_metadata)
        
        # Should return list of tuples
        assert isinstance(authority_sources, list)
        
        # Each item should be (chunk, score) tuple
        for chunk, score in authority_sources:
            assert isinstance(chunk, GroundingChunk)
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
        
        # Should be sorted by authority score (descending)
        if len(authority_sources) > 1:
            for i in range(len(authority_sources) - 1):
                assert authority_sources[i][1] >= authority_sources[i + 1][1]
    
    def test_get_high_confidence_insights(self):
        """Test getting high-confidence insights."""
        insights = self.engine.get_high_confidence_insights(self.sample_grounding_metadata)
        
        # Should return list of insights
        assert isinstance(insights, list)
        
        # Each insight should be a string
        for insight in insights:
            assert isinstance(insight, str)
            assert len(insight) > 0
    
    def test_enhance_sections_with_grounding(self):
        """Test section enhancement with grounding insights."""
        sections = [self.sample_section]
        insights = self.engine.extract_contextual_insights(self.sample_grounding_metadata)
        
        enhanced_sections = self.engine.enhance_sections_with_grounding(
            sections, self.sample_grounding_metadata, insights
        )
        
        # Should return same number of sections
        assert len(enhanced_sections) == len(sections)
        
        # Enhanced section should have same basic structure
        enhanced_section = enhanced_sections[0]
        assert enhanced_section.id == self.sample_section.id
        assert enhanced_section.heading == self.sample_section.heading
        
        # Should have enhanced content
        assert len(enhanced_section.subheadings) >= len(self.sample_section.subheadings)
        assert len(enhanced_section.key_points) >= len(self.sample_section.key_points)
        assert len(enhanced_section.keywords) >= len(self.sample_section.keywords)
    
    def test_enhance_sections_with_empty_grounding(self):
        """Test section enhancement with empty grounding metadata."""
        sections = [self.sample_section]
        
        enhanced_sections = self.engine.enhance_sections_with_grounding(
            sections, None, {}
        )
        
        # Should return original sections unchanged
        assert len(enhanced_sections) == len(sections)
        assert enhanced_sections[0].subheadings == self.sample_section.subheadings
        assert enhanced_sections[0].key_points == self.sample_section.key_points
        assert enhanced_sections[0].keywords == self.sample_section.keywords
    
    def test_find_relevant_chunks(self):
        """Test finding relevant chunks for a section."""
        relevant_chunks = self.engine._find_relevant_chunks(
            self.sample_section, self.sample_grounding_metadata
        )
        
        # Should return list of relevant chunks
        assert isinstance(relevant_chunks, list)
        
        # Each chunk should be a GroundingChunk
        for chunk in relevant_chunks:
            assert isinstance(chunk, GroundingChunk)
    
    def test_find_relevant_supports(self):
        """Test finding relevant supports for a section."""
        relevant_supports = self.engine._find_relevant_supports(
            self.sample_section, self.sample_grounding_metadata
        )
        
        # Should return list of relevant supports
        assert isinstance(relevant_supports, list)
        
        # Each support should be a GroundingSupport
        for support in relevant_supports:
            assert isinstance(support, GroundingSupport)
    
    def test_extract_insight_from_segment(self):
        """Test insight extraction from segment text."""
        # Test with valid segment
        segment = "This is a comprehensive analysis of AI trends in enterprise applications."
        insight = self.engine._extract_insight_from_segment(segment)
        assert insight == segment
        
        # Test with short segment
        short_segment = "Short"
        insight = self.engine._extract_insight_from_segment(short_segment)
        assert insight is None
        
        # Test with long segment
        long_segment = "This is a very long segment that exceeds the maximum length limit and should be truncated appropriately to ensure it fits within the expected constraints and provides comprehensive coverage of the topic while maintaining readability and clarity for the intended audience."
        insight = self.engine._extract_insight_from_segment(long_segment)
        assert insight is not None
        assert len(insight) <= 203  # 200 + "..."
        assert insight.endswith("...")
    
    def test_get_confidence_distribution(self):
        """Test confidence distribution calculation."""
        confidences = [0.95, 0.88, 0.82, 0.90, 0.65]
        distribution = self.engine._get_confidence_distribution(confidences)
        
        assert 'high' in distribution
        assert 'medium' in distribution
        assert 'low' in distribution
        
        # Should have reasonable distribution
        total = distribution['high'] + distribution['medium'] + distribution['low']
        assert total == len(confidences)
    
    def test_calculate_temporal_balance(self):
        """Test temporal balance calculation."""
        # Test recent heavy
        balance = self.engine._calculate_temporal_balance(8, 2)
        assert balance == 'recent_heavy'
        
        # Test evergreen heavy
        balance = self.engine._calculate_temporal_balance(2, 8)
        assert balance == 'evergreen_heavy'
        
        # Test balanced
        balance = self.engine._calculate_temporal_balance(5, 5)
        assert balance == 'balanced'
        
        # Test empty
        balance = self.engine._calculate_temporal_balance(0, 0)
        assert balance == 'unknown'
    
    def test_extract_related_concepts(self):
        """Test related concept extraction."""
        text_list = [
            "Artificial Intelligence is transforming Machine Learning applications",
            "Deep Learning algorithms are improving Neural Network performance",
            "Natural Language Processing is advancing AI capabilities"
        ]
        
        concepts = self.engine._extract_related_concepts(text_list)
        
        # Should extract capitalized concepts
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Should contain expected concepts
        expected_concepts = ['Artificial', 'Intelligence', 'Machine', 'Learning', 'Deep', 'Neural', 'Network']
        for concept in expected_concepts:
            assert concept in concepts
    
    def test_identify_content_gaps(self):
        """Test content gap identification."""
        text_list = [
            "The research shows significant improvements in AI applications",
            "However, there is a lack of comprehensive studies on AI ethics",
            "The gap in understanding AI bias remains unexplored",
            "Current research does not cover all aspects of AI implementation"
        ]
        
        gaps = self.engine._identify_content_gaps(text_list)
        
        # Should identify gaps
        assert isinstance(gaps, list)
        assert len(gaps) > 0
    
    def test_assess_citation_quality(self):
        """Test citation quality assessment."""
        quality = self.engine._assess_citation_quality(self.sample_citations)
        
        # Should have reasonable quality score
        assert 0.0 <= quality <= 1.0
        assert quality > 0.0  # Should have some quality
    
    def test_determine_primary_intent(self):
        """Test primary intent determination."""
        # Test informational intent
        intent = self.engine._determine_primary_intent(['informational', 'informational', 'comparison'])
        assert intent == 'informational'
        
        # Test empty signals
        intent = self.engine._determine_primary_intent([])
        assert intent == 'informational'
    
    def test_get_quality_grade(self):
        """Test quality grade calculation."""
        # Test A grade
        grade = self.engine._get_quality_grade(0.95)
        assert grade == 'A'
        
        # Test B grade
        grade = self.engine._get_quality_grade(0.85)
        assert grade == 'B'
        
        # Test C grade
        grade = self.engine._get_quality_grade(0.75)
        assert grade == 'C'
        
        # Test D grade
        grade = self.engine._get_quality_grade(0.65)
        assert grade == 'D'
        
        # Test F grade
        grade = self.engine._get_quality_grade(0.45)
        assert grade == 'F'


if __name__ == '__main__':
    pytest.main([__file__])
