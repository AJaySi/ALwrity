"""
Unit tests for SourceToSectionMapper.

Tests the intelligent source-to-section mapping functionality.
"""

import pytest
from typing import List

from models.blog_models import (
    BlogOutlineSection,
    ResearchSource,
    BlogResearchResponse,
    GroundingMetadata,
)
from services.blog_writer.outline.source_mapper import SourceToSectionMapper


class TestSourceToSectionMapper:
    """Test cases for SourceToSectionMapper."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mapper = SourceToSectionMapper()
        
        # Create sample research sources
        self.sample_sources = [
            ResearchSource(
                title="AI Trends in 2025: Machine Learning Revolution",
                url="https://example.com/ai-trends-2025",
                excerpt="Comprehensive analysis of artificial intelligence trends in 2025, focusing on machine learning advancements, deep learning breakthroughs, and AI automation in enterprise environments.",
                credibility_score=0.95,
                published_at="2025-08-15",
                index=0,
                source_type="web"
            ),
            ResearchSource(
                title="Enterprise AI Implementation Guide",
                url="https://example.com/enterprise-ai-guide",
                excerpt="Step-by-step guide for implementing artificial intelligence solutions in enterprise environments, including best practices, challenges, and success stories from leading companies.",
                credibility_score=0.9,
                published_at="2025-08-01",
                index=1,
                source_type="web"
            ),
            ResearchSource(
                title="Machine Learning Algorithms Explained",
                url="https://example.com/ml-algorithms",
                excerpt="Detailed explanation of various machine learning algorithms including supervised learning, unsupervised learning, and reinforcement learning techniques with practical examples.",
                credibility_score=0.85,
                published_at="2025-07-20",
                index=2,
                source_type="web"
            ),
            ResearchSource(
                title="AI Ethics and Responsible Development",
                url="https://example.com/ai-ethics",
                excerpt="Discussion of ethical considerations in artificial intelligence development, including bias mitigation, transparency, and responsible AI practices for developers and organizations.",
                credibility_score=0.88,
                published_at="2025-07-10",
                index=3,
                source_type="web"
            ),
            ResearchSource(
                title="Deep Learning Neural Networks Tutorial",
                url="https://example.com/deep-learning-tutorial",
                excerpt="Comprehensive tutorial on deep learning neural networks, covering convolutional neural networks, recurrent neural networks, and transformer architectures with code examples.",
                credibility_score=0.92,
                published_at="2025-06-15",
                index=4,
                source_type="web"
            )
        ]
        
        # Create sample outline sections
        self.sample_sections = [
            BlogOutlineSection(
                id="s1",
                heading="Introduction to AI and Machine Learning",
                subheadings=["What is AI?", "Types of Machine Learning", "AI Applications"],
                key_points=["AI definition and scope", "ML vs traditional programming", "Real-world AI examples"],
                references=[],
                target_words=300,
                keywords=["artificial intelligence", "machine learning", "AI basics", "introduction"]
            ),
            BlogOutlineSection(
                id="s2",
                heading="Enterprise AI Implementation Strategies",
                subheadings=["Planning Phase", "Implementation Steps", "Best Practices"],
                key_points=["Strategic planning", "Technology selection", "Change management", "ROI measurement"],
                references=[],
                target_words=400,
                keywords=["enterprise AI", "implementation", "strategies", "business"]
            ),
            BlogOutlineSection(
                id="s3",
                heading="Machine Learning Algorithms Deep Dive",
                subheadings=["Supervised Learning", "Unsupervised Learning", "Deep Learning"],
                key_points=["Algorithm types", "Use cases", "Performance metrics", "Model selection"],
                references=[],
                target_words=500,
                keywords=["machine learning algorithms", "supervised learning", "deep learning", "neural networks"]
            ),
            BlogOutlineSection(
                id="s4",
                heading="AI Ethics and Responsible Development",
                subheadings=["Ethical Considerations", "Bias and Fairness", "Transparency"],
                key_points=["Ethical frameworks", "Bias detection", "Explainable AI", "Regulatory compliance"],
                references=[],
                target_words=350,
                keywords=["AI ethics", "responsible AI", "bias", "transparency"]
            )
        ]
        
        # Create sample research response
        self.sample_research = BlogResearchResponse(
            success=True,
            sources=self.sample_sources,
            keyword_analysis={
                'primary': ['artificial intelligence', 'machine learning', 'AI implementation'],
                'secondary': ['enterprise AI', 'deep learning', 'AI ethics'],
                'long_tail': ['AI trends 2025', 'enterprise AI implementation guide', 'machine learning algorithms explained'],
                'semantic_keywords': ['AI', 'ML', 'neural networks', 'automation'],
                'trending_terms': ['AI 2025', 'generative AI', 'AI automation'],
                'search_intent': 'informational',
                'content_gaps': ['AI implementation challenges', 'ML algorithm comparison']
            },
            competitor_analysis={
                'top_competitors': ['TechCorp AI', 'DataScience Inc', 'AI Solutions Ltd'],
                'opportunities': ['Enterprise market gap', 'SME AI adoption'],
                'competitive_advantages': ['Comprehensive coverage', 'Practical examples']
            },
            suggested_angles=[
                'AI trends in 2025',
                'Enterprise AI implementation',
                'Machine learning fundamentals',
                'AI ethics and responsibility'
            ],
            search_widget="<div>Search widget HTML</div>",
            search_queries=["AI trends 2025", "enterprise AI implementation", "machine learning guide"],
            grounding_metadata=GroundingMetadata(
                grounding_chunks=[],
                grounding_supports=[],
                citations=[],
                search_entry_point="AI trends and implementation",
                web_search_queries=["AI trends 2025", "enterprise AI"]
            )
        )
    
    def test_semantic_similarity_calculation(self):
        """Test semantic similarity calculation between sections and sources."""
        section = self.sample_sections[0]  # AI Introduction section
        source = self.sample_sources[0]    # AI Trends source
        
        similarity = self.mapper._calculate_semantic_similarity(section, source)
        
        # Should have high similarity due to AI-related content
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.3  # Should be reasonably high for AI-related content
    
    def test_keyword_relevance_calculation(self):
        """Test keyword-based relevance calculation."""
        section = self.sample_sections[1]  # Enterprise AI section
        source = self.sample_sources[1]    # Enterprise AI Guide source
        
        relevance = self.mapper._calculate_keyword_relevance(section, source, self.sample_research)
        
        # Should have reasonable relevance due to enterprise AI keywords
        assert 0.0 <= relevance <= 1.0
        assert relevance > 0.1  # Should be reasonable for matching enterprise AI content
    
    def test_contextual_relevance_calculation(self):
        """Test contextual relevance calculation."""
        section = self.sample_sections[2]  # ML Algorithms section
        source = self.sample_sources[2]    # ML Algorithms source
        
        relevance = self.mapper._calculate_contextual_relevance(section, source, self.sample_research)
        
        # Should have high relevance due to matching content angles
        assert 0.0 <= relevance <= 1.0
        assert relevance > 0.2  # Should be reasonable for matching content
    
    def test_algorithmic_source_mapping(self):
        """Test the complete algorithmic mapping process."""
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        # Should have mapping results for all sections
        assert len(mapping_results) == len(self.sample_sections)
        
        # Each section should have some mapped sources
        for section_id, sources in mapping_results.items():
            assert isinstance(sources, list)
            # Each source should be a tuple of (source, score)
            for source, score in sources:
                assert isinstance(source, ResearchSource)
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
    
    def test_source_mapping_quality(self):
        """Test that sources are mapped to relevant sections."""
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        # Enterprise AI section should have enterprise AI source
        enterprise_section = mapping_results["s2"]
        enterprise_source_titles = [source.title for source, score in enterprise_section]
        assert any("Enterprise" in title for title in enterprise_source_titles)
        
        # ML Algorithms section should have ML algorithms source
        ml_section = mapping_results["s3"]
        ml_source_titles = [source.title for source, score in ml_section]
        assert any("Machine Learning" in title or "Algorithms" in title for title in ml_source_titles)
        
        # AI Ethics section should have AI ethics source
        ethics_section = mapping_results["s4"]
        ethics_source_titles = [source.title for source, score in ethics_section]
        assert any("Ethics" in title for title in ethics_source_titles)
    
    def test_complete_mapping_pipeline(self):
        """Test the complete mapping pipeline from sections to mapped sections."""
        mapped_sections = self.mapper.map_sources_to_sections(self.sample_sections, self.sample_research)
        
        # Should return same number of sections
        assert len(mapped_sections) == len(self.sample_sections)
        
        # Each section should have mapped sources
        for section in mapped_sections:
            assert isinstance(section.references, list)
            assert len(section.references) <= self.mapper.max_sources_per_section
            
            # All references should be ResearchSource objects
            for source in section.references:
                assert isinstance(source, ResearchSource)
    
    def test_mapping_with_empty_sources(self):
        """Test mapping behavior with empty sources list."""
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
        
        mapped_sections = self.mapper.map_sources_to_sections(self.sample_sections, empty_research)
        
        # Should return sections with empty references
        for section in mapped_sections:
            assert section.references == []
    
    def test_mapping_with_empty_sections(self):
        """Test mapping behavior with empty sections list."""
        mapped_sections = self.mapper.map_sources_to_sections([], self.sample_research)
        
        # Should return empty list
        assert mapped_sections == []
    
    def test_meaningful_words_extraction(self):
        """Test extraction of meaningful words from text."""
        text = "Artificial Intelligence and Machine Learning are transforming the world of technology and business applications."
        words = self.mapper._extract_meaningful_words(text)
        
        # Should extract meaningful words and remove stop words
        assert "artificial" in words
        assert "intelligence" in words
        assert "machine" in words
        assert "learning" in words
        assert "the" not in words  # Stop word should be removed
        assert "and" not in words  # Stop word should be removed
    
    def test_phrase_similarity_calculation(self):
        """Test phrase similarity calculation."""
        text1 = "machine learning algorithms"
        text2 = "This article covers machine learning algorithms and their applications"
        
        similarity = self.mapper._calculate_phrase_similarity(text1, text2)
        
        # Should find phrase matches
        assert similarity > 0.0
        assert similarity <= 0.3  # Should be capped at 0.3
    
    def test_intent_keywords_extraction(self):
        """Test extraction of intent-specific keywords."""
        informational_keywords = self.mapper._get_intent_keywords("informational")
        transactional_keywords = self.mapper._get_intent_keywords("transactional")
        
        # Should return appropriate keywords for each intent
        assert "what" in informational_keywords
        assert "how" in informational_keywords
        assert "guide" in informational_keywords
        
        assert "buy" in transactional_keywords
        assert "purchase" in transactional_keywords
        assert "price" in transactional_keywords
    
    def test_mapping_statistics(self):
        """Test mapping statistics calculation."""
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        stats = self.mapper.get_mapping_statistics(mapping_results)
        
        # Should have valid statistics
        assert stats['total_sections'] == len(self.sample_sections)
        assert stats['total_mappings'] > 0
        assert stats['sections_with_sources'] > 0
        assert 0.0 <= stats['average_score'] <= 1.0
        assert 0.0 <= stats['max_score'] <= 1.0
        assert 0.0 <= stats['min_score'] <= 1.0
        assert 0.0 <= stats['mapping_coverage'] <= 1.0
    
    def test_source_quality_filtering(self):
        """Test that low-quality sources are filtered out."""
        # Create a low-quality source
        low_quality_source = ResearchSource(
            title="Random Article",
            url="https://example.com/random",
            excerpt="This is a completely unrelated article about cooking recipes and gardening tips.",
            credibility_score=0.3,
            published_at="2025-08-01",
            index=5,
            source_type="web"
        )
        
        # Add to research data
        research_with_low_quality = BlogResearchResponse(
            success=True,
            sources=self.sample_sources + [low_quality_source],
            keyword_analysis=self.sample_research.keyword_analysis,
            competitor_analysis=self.sample_research.competitor_analysis,
            suggested_angles=self.sample_research.suggested_angles,
            search_widget=self.sample_research.search_widget,
            search_queries=self.sample_research.search_queries,
            grounding_metadata=self.sample_research.grounding_metadata
        )
        
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, research_with_low_quality)
        
        # Low-quality source should not be mapped to any section
        all_mapped_sources = []
        for sources in mapping_results.values():
            all_mapped_sources.extend([source for source, score in sources])
        
        assert low_quality_source not in all_mapped_sources
    
    def test_max_sources_per_section_limit(self):
        """Test that the maximum sources per section limit is enforced."""
        # Create many sources
        many_sources = self.sample_sources * 3  # 15 sources
        
        research_with_many_sources = BlogResearchResponse(
            success=True,
            sources=many_sources,
            keyword_analysis=self.sample_research.keyword_analysis,
            competitor_analysis=self.sample_research.competitor_analysis,
            suggested_angles=self.sample_research.suggested_angles,
            search_widget=self.sample_research.search_widget,
            search_queries=self.sample_research.search_queries,
            grounding_metadata=self.sample_research.grounding_metadata
        )
        
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, research_with_many_sources)
        
        # Each section should have at most max_sources_per_section sources
        for section_id, sources in mapping_results.items():
            assert len(sources) <= self.mapper.max_sources_per_section
    
    def test_ai_validation_prompt_building(self):
        """Test AI validation prompt building."""
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        prompt = self.mapper._build_validation_prompt(mapping_results, self.sample_research)
        
        # Should contain key elements
        assert "expert content strategist" in prompt
        assert "Research Topic:" in prompt
        assert "ALGORITHMIC MAPPING RESULTS" in prompt
        assert "AVAILABLE SOURCES" in prompt
        assert "VALIDATION TASK" in prompt
        assert "RESPONSE FORMAT" in prompt
        assert "overall_quality_score" in prompt
        assert "section_improvements" in prompt
    
    def test_ai_validation_response_parsing(self):
        """Test AI validation response parsing."""
        # Mock AI response
        mock_response = """
        Here's my analysis of the source-to-section mapping:

        ```json
        {
            "overall_quality_score": 8,
            "section_improvements": [
                {
                    "section_id": "s1",
                    "current_sources": ["AI Trends in 2025: Machine Learning Revolution"],
                    "recommended_sources": ["AI Trends in 2025: Machine Learning Revolution", "Machine Learning Algorithms Explained"],
                    "reasoning": "Adding ML algorithms source provides more technical depth",
                    "confidence": 0.9
                }
            ],
            "summary": "Good mapping overall, minor improvements suggested"
        }
        ```
        """
        
        original_mapping = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        parsed_mapping = self.mapper._parse_validation_response(mock_response, original_mapping, self.sample_research)
        
        # Should have improved mapping
        assert "s1" in parsed_mapping
        assert len(parsed_mapping["s1"]) > 0
        
        # Should maintain other sections
        assert len(parsed_mapping) == len(original_mapping)
    
    def test_ai_validation_fallback_handling(self):
        """Test AI validation fallback when parsing fails."""
        # Mock invalid AI response
        invalid_response = "This is not a valid JSON response"
        
        original_mapping = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        parsed_mapping = self.mapper._parse_validation_response(invalid_response, original_mapping, self.sample_research)
        
        # Should fallback to original mapping
        assert parsed_mapping == original_mapping
    
    def test_ai_validation_with_missing_sources(self):
        """Test AI validation when recommended sources don't exist."""
        # Mock AI response with non-existent source
        mock_response = """
        ```json
        {
            "overall_quality_score": 7,
            "section_improvements": [
                {
                    "section_id": "s1",
                    "current_sources": ["AI Trends in 2025: Machine Learning Revolution"],
                    "recommended_sources": ["Non-existent Source", "Another Fake Source"],
                    "reasoning": "These sources would be better",
                    "confidence": 0.8
                }
            ],
            "summary": "Suggested improvements"
        }
        ```
        """
        
        original_mapping = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        parsed_mapping = self.mapper._parse_validation_response(mock_response, original_mapping, self.sample_research)
        
        # Should fallback to original mapping for s1 since no valid sources found
        assert parsed_mapping["s1"] == original_mapping["s1"]
    
    def test_ai_validation_integration(self):
        """Test complete AI validation integration (with mocked LLM)."""
        # This test would require mocking the LLM provider
        # For now, we'll test that the method doesn't crash
        mapping_results = self.mapper._algorithmic_source_mapping(self.sample_sections, self.sample_research)
        
        # Test that AI validation method exists and can be called
        # (In real implementation, this would call the actual LLM)
        try:
            # This will fail in test environment due to no LLM, but should not crash
            validated_mapping = self.mapper._ai_validate_mapping(mapping_results, self.sample_research)
            # If it doesn't crash, it should return the original mapping as fallback
            assert validated_mapping == mapping_results
        except Exception as e:
            # Expected to fail in test environment, but should be handled gracefully
            assert "AI validation failed" in str(e) or "Failed to get AI validation response" in str(e)
    
    def test_format_sections_for_prompt(self):
        """Test formatting of sections for AI prompt."""
        sections_info = [
            {
                'id': 's1',
                'sources': [
                    {
                        'title': 'Test Source 1',
                        'algorithmic_score': 0.85
                    }
                ]
            }
        ]
        
        formatted = self.mapper._format_sections_for_prompt(sections_info)
        
        assert "Section s1:" in formatted
        assert "Test Source 1" in formatted
        assert "0.85" in formatted
    
    def test_format_sources_for_prompt(self):
        """Test formatting of sources for AI prompt."""
        sources = [
            {
                'title': 'Test Source',
                'url': 'https://example.com',
                'credibility_score': 0.9,
                'excerpt': 'This is a test excerpt for the source.'
            }
        ]
        
        formatted = self.mapper._format_sources_for_prompt(sources)
        
        assert "Test Source" in formatted
        assert "https://example.com" in formatted
        assert "0.9" in formatted
        assert "This is a test excerpt" in formatted


if __name__ == '__main__':
    pytest.main([__file__])
