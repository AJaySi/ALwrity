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
        
        # Build search kwargs
        search_kwargs = {
            'type': config.exa_search_type or "auto",
            'num_results': min(config.max_sources, 25),
            'contents': {
                'text': {'max_characters': 1000},
                'summary': {'query': f"Key insights about {topic}"},
                'highlights': {
                    'num_sentences': 2,
                    'highlights_per_url': 3
                }
            }
        }
        
        # Add optional filters
        if category:
            search_kwargs['category'] = category
        if config.exa_include_domains:
            search_kwargs['include_domains'] = config.exa_include_domains
        if config.exa_exclude_domains:
            search_kwargs['exclude_domains'] = config.exa_exclude_domains
        
        logger.info(f"[Exa Research] Executing search: {query}")
        
        # Execute Exa search
        results = self.exa.search_and_contents(query, **search_kwargs)
        
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
                'summary': result.summary if hasattr(result, 'summary') else ''
            })
        
        return sources
    
    def _get_excerpt(self, result):
        """Extract excerpt from Exa result."""
        if hasattr(result, 'text') and result.text:
            return result.text[:500]
        elif hasattr(result, 'summary') and result.summary:
            return result.summary
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
        """Aggregate content from Exa results for LLM analysis."""
        content_parts = []
        
        for idx, result in enumerate(results):
            if hasattr(result, 'summary') and result.summary:
                content_parts.append(f"Source {idx + 1}: {result.summary}")
            elif hasattr(result, 'text') and result.text:
                content_parts.append(f"Source {idx + 1}: {result.text[:1000]}")
        
        return "\n\n".join(content_parts)
    
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

