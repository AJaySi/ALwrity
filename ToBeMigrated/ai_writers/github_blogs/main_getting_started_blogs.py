"""
Enhanced GitHub Blog Generator

This module provides comprehensive content generation from GitHub repositories,
including technical documentation, tutorials, case studies, and more.
"""

import os
import sys
import datetime
import json
from typing import Dict, List, Optional
from pathlib import Path

from loguru import logger
logger.remove()
logger.add(sys.stdout,
          colorize=True,
          format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}")

from .scrape_github_readme import GitHubScraper, GitHubContent
from .scrape_github_readme import get_gh_details_vision, get_readme_content
from .scrape_github_readme import research_github_topics, check_if_already_written
from .github_getting_started import (
    generate_technical_documentation,
    generate_getting_started_guide,
    generate_tutorial_series,
    generate_comparison_analysis,
    generate_case_studies,
    generate_contribution_guide,
    generate_security_guide,
    generate_performance_guide
)


class GitHubBlogGenerator:
    """Generator for various types of GitHub-related content."""
    
    def __init__(self, cache_dir: str = ".github_cache", ttl_hours: int = 24):
        """Initialize the blog generator."""
        self.cache_dir = Path(cache_dir)
        self.scraper = GitHubScraper(cache_dir, ttl_hours)
        self.output_dir = Path("generated_content")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_content(self, github_url: str, content_types: List[str] = None) -> Dict[str, str]:
        """Generate various types of content from a GitHub repository."""
        if content_types is None:
            content_types = ["getting_started", "technical_docs", "tutorials"]
        
        try:
            # Scrape GitHub content
            repo_content = await self.scraper.scrape_github_content(github_url)
            
            # Generate different types of content
            generated_content = {}
            
            for content_type in content_types:
                if content_type == "getting_started":
                    content = generate_getting_started_guide(repo_content.dict())
                elif content_type == "technical_docs":
                    content = generate_technical_documentation(repo_content.dict())
                elif content_type == "tutorials":
                    content = generate_tutorial_series(repo_content.dict())
                elif content_type == "comparison":
                    content = generate_comparison_analysis(repo_content.dict())
                elif content_type == "case_studies":
                    content = generate_case_studies(repo_content.dict())
                elif content_type == "contribution":
                    content = generate_contribution_guide(repo_content.dict())
                elif content_type == "security":
                    content = generate_security_guide(repo_content.dict())
                elif content_type == "performance":
                    content = generate_performance_guide(repo_content.dict())
                else:
                    logger.warning(f"Unknown content type: {content_type}")
                    continue
                
                generated_content[content_type] = content
            
            # Generate FAQs from online research
            try:
                research_report = do_online_research(repo_content.title, "gemini", github_url)
                faqs = generate_blog_faq(research_report, "gemini")
                generated_content["faqs"] = faqs
            except Exception as err:
                logger.error(f"Failed to generate FAQs: {err}")
            
            return generated_content
            
        except Exception as err:
            logger.error(f"Failed to generate content: {err}")
            raise
    
    def save_content(self, content: Dict[str, str], base_filename: str):
        """Save generated content to files."""
        try:
            for content_type, content_text in content.items():
                # Generate metadata for each content type
                title, meta_desc, tags, categories = blog_metadata(content_text, "gemini")
                
                # Create filename with content type
                filename = f"{base_filename}_{content_type}.md"
                
                # Save content to file
                save_blog_to_file(
                    content_text,
                    title,
                    meta_desc,
                    tags,
                    categories,
                    None  # No image path for now
                )
                
                logger.info(f"Saved {content_type} content to {filename}")
                
        except Exception as err:
            logger.error(f"Failed to save content: {err}")
            raise

async def main():
    """Example usage of the GitHub blog generator."""
    generator = GitHubBlogGenerator()
    
    # Example GitHub URLs
    urls = [
        "https://github.com/owner/repo",
        "https://github.com/owner/another-repo"
    ]
    
    content_types = [
        "getting_started",
        "technical_docs",
        "tutorials",
        "comparison",
        "case_studies",
        "contribution",
        "security",
        "performance"
    ]
    
    for url in urls:
        try:
            # Generate content
            content = await generator.generate_content(url, content_types)
            
            # Create base filename from URL
            base_filename = url.split("/")[-1]
            
            # Save content
            generator.save_content(content, base_filename)
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
