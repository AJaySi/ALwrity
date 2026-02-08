"""
Semantic Harvester Service
Handles deep content acquisition using Exa AI.
Prioritizes Exa for scale (hundreds of URLs) to avoid IP bans.
"""

import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger
from services.research.exa_service import ExaService

class SemanticHarvesterService:
    def __init__(self, api_key: Optional[str] = None):
        self.exa_service = ExaService()
        self._harvest_stats = {
            "total_urls_processed": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "last_harvest_time": None
        }

    async def harvest_website(self, website_url: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Deep crawl a website using Exa AI.
        
        Args:
            website_url: The root URL to crawl.
            limit: Maximum number of pages to retrieve.
            
        Returns:
            List of pages with content and metadata.
        """
        logger.info(f"[SemanticHarvester] Starting harvest for {website_url} (Limit: {limit})")
        
        try:
            # Validate input
            if not website_url or not website_url.strip():
                logger.error(f"[SemanticHarvester] Invalid website URL provided: {website_url}")
                return []
            
            # Normalize URL
            website_url = website_url.strip()
            if not website_url.startswith(('http://', 'https://')):
                website_url = f"https://{website_url}"
                logger.debug(f"[SemanticHarvester] Normalized URL to: {website_url}")
            
            logger.debug(f"[SemanticHarvester] Processing domain: {website_url}")
            
            # Use ExaService to find similar contents (which effectively crawls the site if we search by domain)
            # OR better: Use Exa's search with 'site:' operator or include_domains
            
            # Since ExaService.discover_competitors finds *similar* sites, we need a method to crawl *specific* site.
            # Exa SDK supports searching within a domain.
            
            if not self.exa_service.enabled:
                self.exa_service._try_initialize()
                if not self.exa_service.enabled:
                     logger.warning("[SemanticHarvester] Exa service disabled. Returning placeholder data.")
                     return self._get_placeholder_data(website_url)

            # Use Exa to search for all pages in this domain
            search_response = self.exa_service.exa.search_and_contents(
                query=f"site:{website_url}",
                num_results=min(limit, 50), # Exa limit per request
                text=True,
                highlights=True
            )
            
            results = []
            if search_response and hasattr(search_response, 'results'):
                for result in search_response.results:
                    results.append({
                        "url": getattr(result, 'url', ''),
                        "title": getattr(result, 'title', ''),
                        "content": getattr(result, 'text', '') or getattr(result, 'summary', ''),
                        "metadata": {
                            "published_date": getattr(result, 'published_date', None),
                            "author": getattr(result, 'author', None),
                            "highlights": getattr(result, 'highlights', [])
                        }
                    })
            
            logger.info(f"[SemanticHarvester] Successfully harvested {len(results)} pages from {website_url}")
            return results
            
        except Exception as e:
            logger.error(f"[SemanticHarvester] Failed to harvest {website_url}: {e}")
            logger.error(f"[SemanticHarvester] Full traceback: {traceback.format_exc()}")
            return []

    def _get_placeholder_data(self, website_url: str) -> List[Dict[str, Any]]:
        """Return placeholder data for testing."""
        return [
            {
                "url": f"{website_url}/page1",
                "title": "Sample Page 1",
                "content": "This is sample content from page 1",
                "metadata": {"word_count": 100}
            }
        ]

    async def harvest_competitors(self, competitor_urls: List[str], pages_per_competitor: int = 10) -> List[Dict[str, Any]]:
        """Harvest content from multiple competitors with detailed logging."""
        logger.info(f"[SemanticHarvester] Starting competitor harvest for {len(competitor_urls)} competitors")
        
        if not competitor_urls:
            logger.warning("[SemanticHarvester] No competitor URLs provided")
            return []
        
        all_content = []
        successful_harvests = 0
        failed_harvests = 0
        
        for i, url in enumerate(competitor_urls, 1):
            try:
                logger.debug(f"[SemanticHarvester] Processing competitor {i}/{len(competitor_urls)}: {url}")
                content = await self.harvest_website(url, limit=pages_per_competitor)
                
                if content:
                    all_content.extend(content)
                    successful_harvests += 1
                    logger.debug(f"[SemanticHarvester] Successfully harvested {len(content)} pages from {url}")
                else:
                    failed_harvests += 1
                    logger.warning(f"[SemanticHarvester] No content harvested from {url}")
                    
            except Exception as e:
                failed_harvests += 1
                logger.error(f"[SemanticHarvester] Failed to harvest competitor {url}: {e}")
        
        # Update statistics
        self._harvest_stats["total_urls_processed"] += len(competitor_urls)
        self._harvest_stats["successful_extractions"] += successful_harvests
        self._harvest_stats["failed_extractions"] += failed_harvests
        self._harvest_stats["last_harvest_time"] = datetime.now().isoformat()
        
        logger.info(f"[SemanticHarvester] Competitor harvest completed: {successful_harvests} successful, {failed_harvests} failed")
        logger.info(f"[SemanticHarvester] Total content pieces harvested: {len(all_content)}")
        
        return all_content
    
    def get_harvest_stats(self) -> Dict[str, Any]:
        """Get statistics about harvesting operations."""
        return self._harvest_stats.copy()
