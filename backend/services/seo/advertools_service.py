import advertools as adv
import pandas as pd
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import json
import os
import tempfile

class AdvertoolsService:
    """
    Centralized service for leveraging the Advertools library for deep SEO intelligence.
    Provides functions for sitemap analysis, content auditing, and link extraction.
    """
    
    def __init__(self):
        self.logger = logger.bind(service="AdvertoolsService")

    async def analyze_sitemap(self, sitemap_url: str) -> Dict[str, Any]:
        """
        Analyzes a website's sitemap to extract metrics on publishing velocity and freshness.
        """
        try:
            self.logger.info(f"Analyzing sitemap: {sitemap_url}")
            
            # advertools sitemap_to_df is blocking, run in executor
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(None, lambda: adv.sitemap_to_df(sitemap_url))
            
            if df is None or df.empty:
                return {"success": False, "error": "Sitemap is empty or could not be parsed."}

            # Convert lastmod to datetime
            if 'lastmod' in df.columns:
                df['lastmod'] = pd.to_datetime(df['lastmod'], errors='coerce', utc=True)
                
            total_urls = len(df)
            
            # Handle potential empty datetime columns
            if 'lastmod' in df.columns and not df['lastmod'].isna().all():
                now = datetime.now(df['lastmod'].dt.tz)
                thirty_days_ago = now - timedelta(days=30)
                recent_urls = df[df['lastmod'] > thirty_days_ago]
                six_months_ago = now - timedelta(days=180)
                stale_urls = df[df['lastmod'] < six_months_ago]
                
                publishing_velocity = len(recent_urls) / 4.0 # URLs per week
                stale_count = len(stale_urls)
            else:
                publishing_velocity = 0
                stale_count = 0
            
            # Enhanced Content Pillars (Top folder patterns - 3 levels deep)
            def extract_hierarchy(url: str):
                try:
                    parts = urlparse(url).path.strip('/').split('/')
                    if not parts or not parts[0]: return "home"
                    return "/".join(parts[:2]) # Capture top 2 segments
                except:
                    return "other"

            df['pillar'] = df['loc'].apply(extract_hierarchy)
            pillars = df['pillar'].value_counts().head(15).to_dict()

            # Return a sample of URLs for auditing (top 15 most recent if available)
            audit_urls = []
            if 'lastmod' in df.columns and not df['lastmod'].isna().all():
                audit_urls = df.sort_values('lastmod', ascending=False).head(15)['loc'].tolist()
            else:
                audit_urls = df['loc'].head(15).tolist()

            return {
                "success": True,
                "metrics": {
                    "total_urls": total_urls,
                    "publishing_velocity": round(publishing_velocity, 2),
                    "stale_content_count": stale_count,
                    "stale_content_percentage": round((stale_count / total_urls) * 100, 2) if total_urls > 0 else 0,
                    "top_pillars": pillars,
                    "audit_sample_urls": audit_urls
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze sitemap {sitemap_url}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def audit_content(self, url_list: List[str]) -> Dict[str, Any]:
        """
        Performs a shallow crawl and theme analysis using word frequency.
        Uses unique temporary files for thread safety.
        """
        temp_file = None
        try:
            self.logger.info(f"Auditing content for {len(url_list)} URLs")
            
            # Create a unique temporary file
            with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tf:
                temp_file = tf.name

            # advertools crawl is blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: adv.crawl(
                url_list=url_list,
                output_file=temp_file,
                follow_links=False,
                custom_settings={
                    'LOG_LEVEL': 'WARNING',
                    'CLOSESPIDER_PAGECOUNT': 15, # Guardrail: Max 15 pages
                    'DOWNLOAD_TIMEOUT': 30        # Guardrail: 30s timeout per page
                }
            ))
            
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                return {"success": False, "error": "Crawl failed to generate output or output is empty."}

            crawl_df = pd.read_json(temp_file, lines=True)
            
            # Extract themes using word frequency
            text_columns = [col for col in ['body_text', 'h1', 'h2', 'title'] if col in crawl_df.columns]
            if not text_columns:
                 return {"success": False, "error": "No text content found to analyze."}

            all_text = " ".join(crawl_df[text_columns].fillna("").values.flatten())
            
            if not all_text.strip():
                return {"success": False, "error": "Extracted text is empty."}

            word_freq = await loop.run_in_executor(None, lambda: adv.word_frequency([all_text], rm_stopwords=True))
            top_themes = word_freq.head(20).to_dict(orient='records')

            # Additional metrics: Readability, word count
            avg_word_count = 0
            if 'body_text' in crawl_df.columns:
                crawl_df['word_count'] = crawl_df['body_text'].fillna("").str.split().str.len()
                avg_word_count = crawl_df['word_count'].mean()

            return {
                "success": True,
                "themes": top_themes,
                "page_count": len(crawl_df),
                "avg_word_count": round(avg_word_count, 1),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to audit content: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    self.logger.warning(f"Failed to remove temp file {temp_file}: {e}")

    async def extract_communication_style(self, url_list: List[str]) -> Dict[str, Any]:
        """
        Analyzes linking patterns and social media presence using unique temporary files.
        """
        temp_file = None
        try:
            self.logger.info(f"Extracting communication style for {len(url_list)} URLs")
            
            with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tf:
                temp_file = tf.name

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: adv.crawl(
                url_list=url_list,
                output_file=temp_file,
                follow_links=False,
                custom_settings={
                    'LOG_LEVEL': 'WARNING',
                    'CLOSESPIDER_PAGECOUNT': 10,
                    'DOWNLOAD_TIMEOUT': 30
                }
            ))
            
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                return {"success": False, "error": "Link extraction crawl failed."}

            crawl_df = pd.read_json(temp_file, lines=True)
            
            # Extract social links and internal/external stats
            all_links = []
            if 'links_url' in crawl_df.columns:
                for links in crawl_df['links_url'].dropna():
                    if isinstance(links, str):
                        all_links.extend(links.split("@@"))
                    elif isinstance(links, list):
                        all_links.extend(links)

            if not all_links:
                return {"success": True, "social_links": [], "link_stats": {"total_links_found": 0, "unique_domains": 0}}

            # Analyze links
            link_df = adv.url_to_df(all_links)
            
            social_domains = ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 'instagram.com', 'youtube.com', 'github.com']
            social_links = []
            if not link_df.empty and 'netloc' in link_df.columns:
                social_links = link_df[link_df['netloc'].isin(social_domains)]['url'].unique().tolist()
            
            return {
                "success": True,
                "social_links": social_links,
                "link_stats": {
                    "total_links_found": len(all_links),
                    "unique_domains": link_df['netloc'].nunique() if not link_df.empty else 0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to extract communication style: {str(e)}")
            return {"success": False, "error": str(e)}
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    self.logger.warning(f"Failed to remove temp file {temp_file}: {e}")
