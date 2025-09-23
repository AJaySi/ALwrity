"""
Outline Generator - AI-powered outline generation from research data.

Generates comprehensive, SEO-optimized outlines using research intelligence.
"""

from typing import Dict, Any, List, Tuple
import asyncio
from loguru import logger

from models.blog_models import (
    BlogOutlineRequest,
    BlogOutlineResponse,
    BlogOutlineSection,
)

from .source_mapper import SourceToSectionMapper
from .section_enhancer import SectionEnhancer
from .outline_optimizer import OutlineOptimizer
from .grounding_engine import GroundingContextEngine
from .title_generator import TitleGenerator
from .metadata_collector import MetadataCollector
from .prompt_builder import PromptBuilder
from .response_processor import ResponseProcessor
from .parallel_processor import ParallelProcessor


class OutlineGenerator:
    """Generates AI-powered outlines from research data."""
    
    def __init__(self):
        """Initialize the outline generator with all enhancement modules."""
        self.source_mapper = SourceToSectionMapper()
        self.section_enhancer = SectionEnhancer()
        self.outline_optimizer = OutlineOptimizer()
        self.grounding_engine = GroundingContextEngine()
        
        # Initialize extracted classes
        self.title_generator = TitleGenerator()
        self.metadata_collector = MetadataCollector()
        self.prompt_builder = PromptBuilder()
        self.response_processor = ResponseProcessor()
        self.parallel_processor = ParallelProcessor(self.source_mapper, self.grounding_engine)
    
    async def generate(self, request: BlogOutlineRequest) -> BlogOutlineResponse:
        """
        Generate AI-powered outline using research results
        """
        # Extract research insights
        research = request.research
        primary_keywords = research.keyword_analysis.get('primary', [])
        secondary_keywords = research.keyword_analysis.get('secondary', [])
        content_angles = research.suggested_angles
        sources = research.sources
        search_intent = research.keyword_analysis.get('search_intent', 'informational')
        
        # Check for custom instructions
        custom_instructions = getattr(request, 'custom_instructions', None)
        
        # Build comprehensive outline generation prompt with rich research data
        outline_prompt = self.prompt_builder.build_outline_prompt(
            primary_keywords, secondary_keywords, content_angles, sources,
            search_intent, request, custom_instructions
        )
        
        logger.info("Generating AI-powered outline using research results")
        
        # Define schema with proper property ordering (critical for Gemini API)
        outline_schema = self.prompt_builder.get_outline_schema()
        
        # Generate outline using structured JSON response with retry logic
        outline_data = await self.response_processor.generate_with_retry(outline_prompt, outline_schema)
        
        # Convert to BlogOutlineSection objects
        outline_sections = self.response_processor.convert_to_sections(outline_data, sources)
        
        # Run parallel processing for speed optimization
        mapped_sections, grounding_insights = await self.parallel_processor.run_parallel_processing_async(
            outline_sections, research
        )
        
        # Enhance sections with grounding insights
        logger.info("Enhancing sections with grounding insights...")
        grounding_enhanced_sections = self.grounding_engine.enhance_sections_with_grounding(
            mapped_sections, research.grounding_metadata, grounding_insights
        )
        
        # Optimize outline for better flow, SEO, and engagement
        logger.info("Optimizing outline for better flow and engagement...")
        optimized_sections = await self.outline_optimizer.optimize(grounding_enhanced_sections, "comprehensive optimization")
        
        # Rebalance word counts for optimal distribution
        target_words = request.word_count or 1500
        balanced_sections = self.outline_optimizer.rebalance_word_counts(optimized_sections, target_words)
        
        # Extract title options - combine AI-generated with content angles
        ai_title_options = outline_data.get('title_options', [])
        content_angle_titles = self.title_generator.extract_content_angle_titles(research)
        
        # Combine AI-generated titles with content angles
        title_options = self.title_generator.combine_title_options(ai_title_options, content_angle_titles, primary_keywords)
        
        logger.info(f"Generated optimized outline with {len(balanced_sections)} sections and {len(title_options)} title options")
        
        # Collect metadata for enhanced UI
        source_mapping_stats = self.metadata_collector.collect_source_mapping_stats(mapped_sections, research)
        grounding_insights_data = self.metadata_collector.collect_grounding_insights(grounding_insights)
        optimization_results = self.metadata_collector.collect_optimization_results(optimized_sections, "comprehensive optimization")
        research_coverage = self.metadata_collector.collect_research_coverage(research)
        
        return BlogOutlineResponse(
            success=True,
            title_options=title_options,
            outline=balanced_sections,
            source_mapping_stats=source_mapping_stats,
            grounding_insights=grounding_insights_data,
            optimization_results=optimization_results,
            research_coverage=research_coverage
        )
    
    async def generate_with_progress(self, request: BlogOutlineRequest, task_id: str) -> BlogOutlineResponse:
        """
        Outline generation method with progress updates for real-time feedback.
        """
        from api.blog_writer.task_manager import task_manager
        
        # Extract research insights
        research = request.research
        primary_keywords = research.keyword_analysis.get('primary', [])
        secondary_keywords = research.keyword_analysis.get('secondary', [])
        content_angles = research.suggested_angles
        sources = research.sources
        search_intent = research.keyword_analysis.get('search_intent', 'informational')
        
        # Check for custom instructions
        custom_instructions = getattr(request, 'custom_instructions', None)
        
        await task_manager.update_progress(task_id, "📊 Analyzing research data and building content strategy...")
        
        # Build comprehensive outline generation prompt with rich research data
        outline_prompt = self.prompt_builder.build_outline_prompt(
            primary_keywords, secondary_keywords, content_angles, sources,
            search_intent, request, custom_instructions
        )
        
        await task_manager.update_progress(task_id, "🤖 Generating AI-powered outline with research insights...")
        
        # Define schema with proper property ordering (critical for Gemini API)
        outline_schema = self.prompt_builder.get_outline_schema()
        
        await task_manager.update_progress(task_id, "🔄 Making AI request to generate structured outline...")
        
        # Generate outline using structured JSON response with retry logic
        outline_data = await self.response_processor.generate_with_retry(outline_prompt, outline_schema, task_id)
        
        await task_manager.update_progress(task_id, "📝 Processing outline structure and validating sections...")
        
        # Convert to BlogOutlineSection objects
        outline_sections = self.response_processor.convert_to_sections(outline_data, sources)
        
        # Run parallel processing for speed optimization
        mapped_sections, grounding_insights = await self.parallel_processor.run_parallel_processing(
            outline_sections, research, task_id
        )
        
        # Enhance sections with grounding insights (depends on both previous tasks)
        await task_manager.update_progress(task_id, "✨ Enhancing sections with grounding insights...")
        grounding_enhanced_sections = self.grounding_engine.enhance_sections_with_grounding(
            mapped_sections, research.grounding_metadata, grounding_insights
        )
        
        # Optimize outline for better flow, SEO, and engagement
        await task_manager.update_progress(task_id, "🎯 Optimizing outline for better flow and engagement...")
        optimized_sections = await self.outline_optimizer.optimize(grounding_enhanced_sections, "comprehensive optimization")
        
        # Rebalance word counts for optimal distribution
        await task_manager.update_progress(task_id, "⚖️ Rebalancing word count distribution...")
        target_words = request.word_count or 1500
        balanced_sections = self.outline_optimizer.rebalance_word_counts(optimized_sections, target_words)
        
        # Extract title options - combine AI-generated with content angles
        ai_title_options = outline_data.get('title_options', [])
        content_angle_titles = self.title_generator.extract_content_angle_titles(research)
        
        # Combine AI-generated titles with content angles
        title_options = self.title_generator.combine_title_options(ai_title_options, content_angle_titles, primary_keywords)
        
        await task_manager.update_progress(task_id, "✅ Outline generation and optimization completed successfully!")
        
        # Collect metadata for enhanced UI
        source_mapping_stats = self.metadata_collector.collect_source_mapping_stats(mapped_sections, research)
        grounding_insights_data = self.metadata_collector.collect_grounding_insights(grounding_insights)
        optimization_results = self.metadata_collector.collect_optimization_results(optimized_sections, "comprehensive optimization")
        research_coverage = self.metadata_collector.collect_research_coverage(research)
        
        return BlogOutlineResponse(
            success=True,
            title_options=title_options,
            outline=balanced_sections,
            source_mapping_stats=source_mapping_stats,
            grounding_insights=grounding_insights_data,
            optimization_results=optimization_results,
            research_coverage=research_coverage
        )
    
    
    
    async def enhance_section(self, section: BlogOutlineSection, focus: str = "general improvement") -> BlogOutlineSection:
        """
        Enhance a single section using AI with research context.
        
        Args:
            section: The section to enhance
            focus: Enhancement focus area (e.g., "SEO optimization", "engagement", "comprehensiveness")
            
        Returns:
            Enhanced section with improved content
        """
        logger.info(f"Enhancing section '{section.heading}' with focus: {focus}")
        enhanced_section = await self.section_enhancer.enhance(section, focus)
        logger.info(f"✅ Section enhancement completed for '{section.heading}'")
        return enhanced_section
    
    async def optimize_outline(self, outline: List[BlogOutlineSection], focus: str = "comprehensive optimization") -> List[BlogOutlineSection]:
        """
        Optimize an entire outline for better flow, SEO, and engagement.
        
        Args:
            outline: List of sections to optimize
            focus: Optimization focus area
            
        Returns:
            Optimized outline with improved flow and engagement
        """
        logger.info(f"Optimizing outline with {len(outline)} sections, focus: {focus}")
        optimized_outline = await self.outline_optimizer.optimize(outline, focus)
        logger.info(f"✅ Outline optimization completed for {len(optimized_outline)} sections")
        return optimized_outline
    
    def rebalance_outline_word_counts(self, outline: List[BlogOutlineSection], target_words: int) -> List[BlogOutlineSection]:
        """
        Rebalance word count distribution across outline sections.
        
        Args:
            outline: List of sections to rebalance
            target_words: Total target word count
            
        Returns:
            Outline with rebalanced word counts
        """
        logger.info(f"Rebalancing word counts for {len(outline)} sections, target: {target_words} words")
        rebalanced_outline = self.outline_optimizer.rebalance_word_counts(outline, target_words)
        logger.info(f"✅ Word count rebalancing completed")
        return rebalanced_outline
    
    def get_grounding_insights(self, research_data) -> Dict[str, Any]:
        """
        Get grounding metadata insights for research data.
        
        Args:
            research_data: Research data with grounding metadata
            
        Returns:
            Dictionary containing grounding insights and analysis
        """
        logger.info("Extracting grounding insights from research data...")
        insights = self.grounding_engine.extract_contextual_insights(research_data.grounding_metadata)
        logger.info(f"✅ Extracted {len(insights)} grounding insight categories")
        return insights
    
    def get_authority_sources(self, research_data) -> List[Tuple]:
        """
        Get high-authority sources from grounding metadata.
        
        Args:
            research_data: Research data with grounding metadata
            
        Returns:
            List of (chunk, authority_score) tuples sorted by authority
        """
        logger.info("Identifying high-authority sources from grounding metadata...")
        authority_sources = self.grounding_engine.get_authority_sources(research_data.grounding_metadata)
        logger.info(f"✅ Identified {len(authority_sources)} high-authority sources")
        return authority_sources
    
    def get_high_confidence_insights(self, research_data) -> List[str]:
        """
        Get high-confidence insights from grounding metadata.
        
        Args:
            research_data: Research data with grounding metadata
            
        Returns:
            List of high-confidence insights
        """
        logger.info("Extracting high-confidence insights from grounding metadata...")
        insights = self.grounding_engine.get_high_confidence_insights(research_data.grounding_metadata)
        logger.info(f"✅ Extracted {len(insights)} high-confidence insights")
        return insights
    
    
    
