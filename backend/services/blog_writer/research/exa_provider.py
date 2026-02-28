"""
Exa Research Provider

Neural search implementation using Exa API for high-quality, citation-rich research.
"""

from exa_py import Exa
import os
from loguru import logger
from models.subscription_models import APIProvider
from .base_provider import ResearchProvider as BaseProvider


class ExaResearchProvider(BaseProvider):
    """Exa neural search provider."""
    
    def __init__(self):
        self.api_key = os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise RuntimeError("EXA_API_KEY not configured")
        self.exa = Exa(self.api_key)
        logger.info("✅ Exa Research Provider initialized")
    
    async def search(self, prompt, topic, industry, target_audience, config, user_id):
        """Execute Exa neural search and return standardized results."""
        # Build Exa query
        query = f"{topic} {industry} {target_audience}"
        
        # Determine category: use exa_category if set, otherwise map from source_types
        category = config.exa_category if config.exa_category else self._map_source_type_to_category(config.source_types)
        
        # Use exa_num_results if available, otherwise fallback to max_sources
        num_results = config.exa_num_results if hasattr(config, 'exa_num_results') and config.exa_num_results else min(config.max_sources, 25)
        # Cap at 100 as per Exa API limits
        num_results = min(num_results, 100)
        
        # Build search kwargs - use correct Exa API format
        search_kwargs = {
            'type': config.exa_search_type or "auto",
            'num_results': num_results,
            'text': {'max_characters': 1000},
            'summary': {'query': f"Key insights about {topic}"},
            'highlights': {
                'num_sentences': 2,
                'highlights_per_url': 3
            }
        }
        
        # Add optional filters
        if category:
            search_kwargs['category'] = category
        if config.exa_include_domains:
            search_kwargs['include_domains'] = config.exa_include_domains
        if config.exa_exclude_domains:
            search_kwargs['exclude_domains'] = config.exa_exclude_domains
        
        # Add date filters if configured
        if hasattr(config, 'exa_date_filter') and config.exa_date_filter:
            search_kwargs['start_published_date'] = config.exa_date_filter
        if hasattr(config, 'exa_end_published_date') and config.exa_end_published_date:
            search_kwargs['end_published_date'] = config.exa_end_published_date
        if hasattr(config, 'exa_start_crawl_date') and config.exa_start_crawl_date:
            search_kwargs['start_crawl_date'] = config.exa_start_crawl_date
        if hasattr(config, 'exa_end_crawl_date') and config.exa_end_crawl_date:
            search_kwargs['end_crawl_date'] = config.exa_end_crawl_date
        
        # Add context if configured (supports boolean or object with maxCharacters)
        if hasattr(config, 'exa_context') and config.exa_context is not None:
            if config.exa_context:
                if hasattr(config, 'exa_context_max_characters') and config.exa_context_max_characters:
                    search_kwargs['context'] = {'maxCharacters': config.exa_context_max_characters}
                else:
                    search_kwargs['context'] = True
            # If False, don't add context parameter (default behavior)
        
        # Add text filters if configured
        if hasattr(config, 'exa_include_text') and config.exa_include_text:
            search_kwargs['include_text'] = config.exa_include_text
        if hasattr(config, 'exa_exclude_text') and config.exa_exclude_text:
            search_kwargs['exclude_text'] = config.exa_exclude_text
        
        logger.info(f"[Exa Research] Executing search: {query}")
        
        # Execute Exa search - pass contents parameters directly, not nested
        try:
            # Build optional parameters dict
            optional_params = {}
            if category:
                optional_params['category'] = category
            if config.exa_include_domains:
                optional_params['include_domains'] = config.exa_include_domains
            if config.exa_exclude_domains:
                optional_params['exclude_domains'] = config.exa_exclude_domains
            if hasattr(config, 'exa_date_filter') and config.exa_date_filter:
                optional_params['start_published_date'] = config.exa_date_filter
            if hasattr(config, 'exa_end_published_date') and config.exa_end_published_date:
                optional_params['end_published_date'] = config.exa_end_published_date
            if hasattr(config, 'exa_start_crawl_date') and config.exa_start_crawl_date:
                optional_params['start_crawl_date'] = config.exa_start_crawl_date
            if hasattr(config, 'exa_end_crawl_date') and config.exa_end_crawl_date:
                optional_params['end_crawl_date'] = config.exa_end_crawl_date
            # Add context if configured (supports boolean or object with maxCharacters)
            if hasattr(config, 'exa_context') and config.exa_context:
                if hasattr(config, 'exa_context_max_characters') and config.exa_context_max_characters:
                    optional_params['context'] = {'maxCharacters': config.exa_context_max_characters}
                else:
                    optional_params['context'] = True
            
            # Add text filters if configured
            if hasattr(config, 'exa_include_text') and config.exa_include_text:
                optional_params['include_text'] = config.exa_include_text
            if hasattr(config, 'exa_exclude_text') and config.exa_exclude_text:
                optional_params['exclude_text'] = config.exa_exclude_text
            
            # Add additional_queries for Deep search (only works with type="deep")
            if config.exa_search_type == 'deep' and hasattr(config, 'exa_additional_queries') and config.exa_additional_queries:
                optional_params['additional_queries'] = config.exa_additional_queries
            
            # Build contents parameters (text, summary, highlights)
            text_params = {}
            if hasattr(config, 'exa_text_max_characters') and config.exa_text_max_characters:
                text_params['max_characters'] = config.exa_text_max_characters
            else:
                text_params['max_characters'] = 1000  # Default
            
            summary_params = {}
            if hasattr(config, 'exa_summary_query') and config.exa_summary_query:
                summary_params['query'] = config.exa_summary_query
            else:
                summary_params['query'] = f"Key insights about {topic}"  # Default
            
            highlights_params = {}
            if hasattr(config, 'exa_highlights') and config.exa_highlights:
                if hasattr(config, 'exa_highlights_num_sentences') and config.exa_highlights_num_sentences:
                    highlights_params['num_sentences'] = config.exa_highlights_num_sentences
                else:
                    highlights_params['num_sentences'] = 2  # Default
                
                if hasattr(config, 'exa_highlights_per_url') and config.exa_highlights_per_url:
                    highlights_params['highlights_per_url'] = config.exa_highlights_per_url
                else:
                    highlights_params['highlights_per_url'] = 3  # Default
            
            results = self.exa.search_and_contents(
                query,
                text=text_params,
                summary=summary_params,
                highlights=highlights_params if highlights_params else None,
                type=config.exa_search_type or "auto",
                num_results=num_results,
                **optional_params
            )
        except Exception as e:
            logger.error(f"[Exa Research] API call failed: {e}")
            # Try simpler call without contents if the above fails
            try:
                logger.info("[Exa Research] Retrying with simplified parameters")
                # Build minimal optional parameters for retry
                optional_params = {}
                if category:
                    optional_params['category'] = category
                if config.exa_include_domains:
                    optional_params['include_domains'] = config.exa_include_domains
                if config.exa_exclude_domains:
                    optional_params['exclude_domains'] = config.exa_exclude_domains
                if hasattr(config, 'exa_date_filter') and config.exa_date_filter:
                    optional_params['start_published_date'] = config.exa_date_filter
                if hasattr(config, 'exa_end_published_date') and config.exa_end_published_date:
                    optional_params['end_published_date'] = config.exa_end_published_date
                if hasattr(config, 'exa_start_crawl_date') and config.exa_start_crawl_date:
                    optional_params['start_crawl_date'] = config.exa_start_crawl_date
                if hasattr(config, 'exa_end_crawl_date') and config.exa_end_crawl_date:
                    optional_params['end_crawl_date'] = config.exa_end_crawl_date
                
                # Add additional_queries for Deep search (only works with type="deep")
                if config.exa_search_type == 'deep' and hasattr(config, 'exa_additional_queries') and config.exa_additional_queries:
                    optional_params['additional_queries'] = config.exa_additional_queries
                
                results = self.exa.search_and_contents(
                    query,
                    type=config.exa_search_type or "auto",
                    num_results=num_results,
                    **optional_params
                )
            except Exception as retry_error:
                logger.error(f"[Exa Research] Retry also failed: {retry_error}")
                raise RuntimeError(f"Exa search failed: {str(retry_error)}") from retry_error
        
        # Transform to standardized format
        sources = self._transform_sources(results.results)
        content = self._aggregate_content(results.results)
        search_type = getattr(results, 'resolvedSearchType', 'neural') if hasattr(results, 'resolvedSearchType') else 'neural'
        
        # Get cost if available
        cost = 0.005  # Default Exa cost for 1-25 results
        if hasattr(results, 'costDollars'):
            if hasattr(results.costDollars, 'total'):
                cost = results.costDollars.total
        
        logger.info(f"[Exa Research] Search completed: {len(sources)} sources, type: {search_type}")
        
        return {
            'sources': sources,
            'content': content,
            'search_type': search_type,
            'provider': 'exa',
            'search_queries': [query],
            'cost': {'total': cost}
        }
    
    def get_provider_enum(self):
        """Return EXA provider enum for subscription tracking."""
        return APIProvider.EXA
    
    def estimate_tokens(self) -> int:
        """Estimate token usage for Exa (not token-based)."""
        return 0  # Exa is per-search, not token-based
    
    def _map_source_type_to_category(self, source_types):
        """Map SourceType enum to Exa category parameter."""
        if not source_types:
            return None
        
        category_map = {
            'research paper': 'research paper',
            'news': 'news',
            'web': 'personal site',
            'industry': 'company',
            'expert': 'linkedin profile'
        }
        
        for st in source_types:
            if st.value in category_map:
                return category_map[st.value]
        
        return None
    
    def _transform_sources(self, results):
        """Transform Exa results to ResearchSource format."""
        sources = []
        for idx, result in enumerate(results):
            source_type = self._determine_source_type(result.url if hasattr(result, 'url') else '')
            
            # Extract image if available (some Exa results include image URL)
            image_url = result.image if hasattr(result, 'image') else None
            
            sources.append({
                'title': result.title if hasattr(result, 'title') else '',
                'url': result.url if hasattr(result, 'url') else '',
                'excerpt': self._get_excerpt(result),
                'credibility_score': 0.85,  # Exa results are high quality
                'published_at': result.publishedDate if hasattr(result, 'publishedDate') else None,
                'index': idx,
                'source_type': source_type,
                'content': result.text if hasattr(result, 'text') else '',
                'highlights': result.highlights if hasattr(result, 'highlights') else [],
                'summary': result.summary if hasattr(result, 'summary') else '',
                'image': image_url,
                'author': result.author if hasattr(result, 'author') else None
            })
        
        return sources
    
    def _get_excerpt(self, result):
        """Extract excerpt from Exa result. Prefer highlights if available."""
        if hasattr(result, 'highlights') and result.highlights and len(result.highlights) > 0:
            return result.highlights[0]
        if hasattr(result, 'summary') and result.summary:
            return result.summary
        if hasattr(result, 'text') and result.text:
            return result.text[:500]
        return ''
    
    def _determine_source_type(self, url):
        """Determine source type from URL."""
        if not url:
            return 'web'
        
        url_lower = url.lower()
        if 'arxiv.org' in url_lower or 'research' in url_lower:
            return 'academic'
        elif any(news in url_lower for news in ['cnn.com', 'bbc.com', 'reuters.com', 'theguardian.com']):
            return 'news'
        elif 'linkedin.com' in url_lower:
            return 'expert'
        else:
            return 'web'
    
    def _aggregate_content(self, results):
        """Aggregate content from Exa results for LLM analysis, including highlights."""
        content_parts = []
        
        for idx, result in enumerate(results):
            part = [f"Source {idx + 1}: {result.title if hasattr(result, 'title') else 'Untitled'}"]
            if hasattr(result, 'url') and result.url:
                part.append(f"URL: {result.url}")
            
            # Add highlights if available (most valuable for LLM)
            if hasattr(result, 'highlights') and result.highlights:
                highlights_text = "\n".join([f"- {h}" for h in result.highlights])
                part.append(f"Key Highlights:\n{highlights_text}")
            
            # Add summary if available
            if hasattr(result, 'summary') and result.summary:
                part.append(f"Summary: {result.summary}")
            
            # Add text snippet if highlights/summary insufficient
            elif hasattr(result, 'text') and result.text:
                part.append(f"Excerpt: {result.text[:1000]}")
                
            content_parts.append("\n".join(part))
        
        return "\n\n---\n\n".join(content_parts)
    
    def track_exa_usage(self, user_id: str, cost: float):
        """Track Exa API usage after successful call."""
        from services.database import get_db
        from services.subscription import PricingService
        from sqlalchemy import text
        
        db = next(get_db())
        try:
            pricing_service = PricingService(db)
            current_period = pricing_service.get_current_billing_period(user_id)
            
            # Update exa_calls and exa_cost via SQL UPDATE
            update_query = text("""
                UPDATE usage_summaries 
                SET exa_calls = COALESCE(exa_calls, 0) + 1,
                    exa_cost = COALESCE(exa_cost, 0) + :cost,
                    total_calls = total_calls + 1,
                    total_cost = total_cost + :cost
                WHERE user_id = :user_id AND billing_period = :period
            """)
            db.execute(update_query, {
                'cost': cost,
                'user_id': user_id,
                'period': current_period
            })
            db.commit()
            
            logger.info(f"[Exa] Tracked usage: user={user_id}, cost=${cost}")
        except Exception as e:
            logger.error(f"[Exa] Failed to track usage: {e}")
            db.rollback()
        finally:
            db.close()

