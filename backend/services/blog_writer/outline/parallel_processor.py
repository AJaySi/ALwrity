"""
Parallel Processor - Handles parallel processing of outline generation tasks.

Manages concurrent execution of source mapping and grounding insights extraction.
"""

import asyncio
from typing import Tuple, Any
from loguru import logger


class ParallelProcessor:
    """Handles parallel processing of outline generation tasks for speed optimization."""
    
    def __init__(self, source_mapper, grounding_engine):
        """Initialize the parallel processor with required dependencies."""
        self.source_mapper = source_mapper
        self.grounding_engine = grounding_engine
    
    async def run_parallel_processing(self, outline_sections, research, task_id: str = None) -> Tuple[Any, Any]:
        """
        Run source mapping and grounding insights extraction in parallel.
        
        Args:
            outline_sections: List of outline sections to process
            research: Research data object
            task_id: Optional task ID for progress updates
            
        Returns:
            Tuple of (mapped_sections, grounding_insights)
        """
        if task_id:
            from api.blog_writer.task_manager import task_manager
            await task_manager.update_progress(task_id, "⚡ Running parallel processing for maximum speed...")
        
        logger.info("Running parallel processing for maximum speed...")
        
        # Run these tasks in parallel to save time
        source_mapping_task = asyncio.create_task(
            self._run_source_mapping(outline_sections, research, task_id)
        )
        
        grounding_insights_task = asyncio.create_task(
            self._run_grounding_insights_extraction(research, task_id)
        )
        
        # Wait for both parallel tasks to complete
        mapped_sections, grounding_insights = await asyncio.gather(
            source_mapping_task,
            grounding_insights_task
        )
        
        return mapped_sections, grounding_insights
    
    async def run_parallel_processing_async(self, outline_sections, research) -> Tuple[Any, Any]:
        """
        Run parallel processing without progress updates (for non-progress methods).
        
        Args:
            outline_sections: List of outline sections to process
            research: Research data object
            
        Returns:
            Tuple of (mapped_sections, grounding_insights)
        """
        logger.info("Running parallel processing for maximum speed...")
        
        # Run these tasks in parallel to save time
        source_mapping_task = asyncio.create_task(
            self._run_source_mapping_async(outline_sections, research)
        )
        
        grounding_insights_task = asyncio.create_task(
            self._run_grounding_insights_extraction_async(research)
        )
        
        # Wait for both parallel tasks to complete
        mapped_sections, grounding_insights = await asyncio.gather(
            source_mapping_task,
            grounding_insights_task
        )
        
        return mapped_sections, grounding_insights
    
    async def _run_source_mapping(self, outline_sections, research, task_id):
        """Run source mapping in parallel."""
        if task_id:
            from api.blog_writer.task_manager import task_manager
            await task_manager.update_progress(task_id, "🔗 Applying intelligent source-to-section mapping...")
        return self.source_mapper.map_sources_to_sections(outline_sections, research)
    
    async def _run_grounding_insights_extraction(self, research, task_id):
        """Run grounding insights extraction in parallel."""
        if task_id:
            from api.blog_writer.task_manager import task_manager
            await task_manager.update_progress(task_id, "🧠 Extracting grounding metadata insights...")
        return self.grounding_engine.extract_contextual_insights(research.grounding_metadata)
    
    async def _run_source_mapping_async(self, outline_sections, research):
        """Run source mapping in parallel (async version without progress updates)."""
        logger.info("Applying intelligent source-to-section mapping...")
        return self.source_mapper.map_sources_to_sections(outline_sections, research)
    
    async def _run_grounding_insights_extraction_async(self, research):
        """Run grounding insights extraction in parallel (async version without progress updates)."""
        logger.info("Extracting grounding metadata insights...")
        return self.grounding_engine.extract_contextual_insights(research.grounding_metadata)
