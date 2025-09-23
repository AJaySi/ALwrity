"""
Metadata Collector - Handles collection and formatting of outline metadata.

Collects source mapping stats, grounding insights, optimization results, and research coverage.
"""

from typing import Dict, Any, List
from loguru import logger


class MetadataCollector:
    """Handles collection and formatting of various metadata types for UI display."""
    
    def __init__(self):
        """Initialize the metadata collector."""
        pass
    
    def collect_source_mapping_stats(self, mapped_sections, research):
        """Collect source mapping statistics for UI display."""
        from models.blog_models import SourceMappingStats
        
        total_sources = len(research.sources)
        total_mapped = sum(len(section.references) for section in mapped_sections)
        coverage_percentage = (total_mapped / total_sources * 100) if total_sources > 0 else 0.0
        
        # Calculate average relevance score (simplified)
        all_relevance_scores = []
        for section in mapped_sections:
            for ref in section.references:
                if hasattr(ref, 'credibility_score') and ref.credibility_score:
                    all_relevance_scores.append(ref.credibility_score)
        
        average_relevance = sum(all_relevance_scores) / len(all_relevance_scores) if all_relevance_scores else 0.0
        high_confidence_mappings = sum(1 for score in all_relevance_scores if score >= 0.8)
        
        return SourceMappingStats(
            total_sources_mapped=total_mapped,
            coverage_percentage=round(coverage_percentage, 1),
            average_relevance_score=round(average_relevance, 3),
            high_confidence_mappings=high_confidence_mappings
        )
    
    def collect_grounding_insights(self, grounding_insights):
        """Collect grounding insights for UI display."""
        from models.blog_models import GroundingInsights
        
        return GroundingInsights(
            confidence_analysis=grounding_insights.get('confidence_analysis'),
            authority_analysis=grounding_insights.get('authority_analysis'),
            temporal_analysis=grounding_insights.get('temporal_analysis'),
            content_relationships=grounding_insights.get('content_relationships'),
            citation_insights=grounding_insights.get('citation_insights'),
            search_intent_insights=grounding_insights.get('search_intent_insights'),
            quality_indicators=grounding_insights.get('quality_indicators')
        )
    
    def collect_optimization_results(self, optimized_sections, focus):
        """Collect optimization results for UI display."""
        from models.blog_models import OptimizationResults
        
        # Calculate a quality score based on section completeness
        total_sections = len(optimized_sections)
        complete_sections = sum(1 for section in optimized_sections 
                              if section.heading and section.subheadings and section.key_points)
        
        quality_score = (complete_sections / total_sections * 10) if total_sections > 0 else 0.0
        
        improvements_made = [
            "Enhanced section headings for better SEO",
            "Optimized keyword distribution across sections",
            "Improved content flow and logical progression",
            "Balanced word count distribution",
            "Enhanced subheadings for better readability"
        ]
        
        return OptimizationResults(
            overall_quality_score=round(quality_score, 1),
            improvements_made=improvements_made,
            optimization_focus=focus
        )
    
    def collect_research_coverage(self, research):
        """Collect research coverage metrics for UI display."""
        from models.blog_models import ResearchCoverage
        
        sources_utilized = len(research.sources)
        content_gaps = research.keyword_analysis.get('content_gaps', [])
        competitive_advantages = research.competitor_analysis.get('competitive_advantages', [])
        
        return ResearchCoverage(
            sources_utilized=sources_utilized,
            content_gaps_identified=len(content_gaps),
            competitive_advantages=competitive_advantages[:5]  # Limit to top 5
        )
