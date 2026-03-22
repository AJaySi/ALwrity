"""
Enhanced GitHub Content Scraper with Rate Limiting and Caching

This module provides functionality to scrape GitHub repositories, READMEs, and code files
for content marketing purposes. It includes async support, rate limiting, caching,
and comprehensive metadata collection.
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
import requests
from pydantic import BaseModel, Field
import time
import pickle
from pathlib import Path

# Configure logging
logger.remove()
logger.add(sys.stdout,
        colorize=True,
          format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}")

class RateLimiter:
    """Rate limiter for GitHub API requests."""
    
    def __init__(self, calls_per_minute: int = 30):
        self.calls_per_minute = calls_per_minute
        self.interval = 60 / calls_per_minute  # seconds between calls
        self.last_call_time = 0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire rate limit token."""
        async with self.lock:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.interval:
                await asyncio.sleep(self.interval - time_since_last_call)
            
            self.last_call_time = time.time()

class Cache:
    """Cache for GitHub content."""
    
    def __init__(self, cache_dir: str = ".github_cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        return self.cache_dir / f"{hash(key)}.cache"
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached value for key."""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                if datetime.now() - data['timestamp'] > self.ttl:
                    cache_path.unlink()
                    return None
                return data['value']
        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            return None
    
    def set(self, key: str, value: Dict):
        """Set cache value for key."""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'timestamp': datetime.now(),
                    'value': value
                }, f)
        except Exception as e:
            logger.warning(f"Cache write error for {key}: {e}")

class GitHubContent(BaseModel):
    """Model for GitHub content analysis."""
    title: str = Field("", description="Title of the content")
    description: str = Field("", description="Description of the content")
    content: str = Field("", description="Main content")
    language: str = Field("", description="Programming language")
    stars: int = Field(0, description="Number of stars")
    forks: int = Field(0, description="Number of forks")
    watchers: int = Field(0, description="Number of watchers")
    last_updated: str = Field("", description="Last update date")
    topics: List[str] = Field([], description="Repository topics")
    contributors: List[str] = Field([], description="Contributor usernames")
    readme_url: str = Field("", description="URL of the README")
    raw_content_url: str = Field("", description="URL for raw content")
    license: str = Field("", description="Repository license")
    dependencies: List[str] = Field([], description="Project dependencies")
    metadata: Dict = Field({}, description="Additional metadata")

class GitHubScraper:
    """Service for scraping GitHub content with rate limiting and caching."""
    
    def __init__(self, cache_dir: str = ".github_cache", ttl_hours: int = 24, calls_per_minute: int = 30):
        """Initialize the scraper service."""
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.rate_limiter = RateLimiter(calls_per_minute)
        self.cache = Cache(cache_dir, ttl_hours)
    
    async def __aenter__(self):
        """Create aiohttp session when entering context."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context."""
        if self.session:
            await self.session.close()
    
    async def fetch_url(self, url: str, use_cache: bool = True) -> str:
        """Fetch URL content asynchronously with rate limiting and caching."""
        if use_cache:
            cached_content = self.cache.get(url)
            if cached_content:
                logger.debug(f"Cache hit for {url}")
                return cached_content
        
        await self.rate_limiter.acquire()
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    if use_cache:
                        self.cache.set(url, content)
                    return content
                else:
                    error_msg = f"Failed to fetch URL: Status code {response.status}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            raise
    
    def parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract repository information."""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        return {
            'owner': path_parts[0],
            'repo': path_parts[1],
            'branch': path_parts[3] if len(path_parts) > 3 else 'main',
            'path': '/'.join(path_parts[4:]) if len(path_parts) > 4 else ''
        }
    
    async def get_repo_metadata(self, owner: str, repo: str) -> Dict:
        """Get repository metadata from GitHub API with caching."""
        cache_key = f"metadata_{owner}_{repo}"
        cached_metadata = self.cache.get(cache_key)
        if cached_metadata:
            return cached_metadata
        
        await self.rate_limiter.acquire()
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    metadata = await response.json()
                    self.cache.set(cache_key, metadata)
                    return metadata
                else:
                    logger.error(f"Failed to fetch repo metadata: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching repo metadata: {e}")
            return {}
    
    async def get_readme_content(self, owner: str, repo: str, branch: str = 'main') -> Dict:
        """Get README content from GitHub with caching."""
        cache_key = f"readme_{owner}_{repo}_{branch}"
        cached_content = self.cache.get(cache_key)
        if cached_content:
            return cached_content
        
        try:
            # Try to get README from API first
            await self.rate_limiter.acquire()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    readme_data = await response.json()
                    content = {
                        'content': readme_data.get('content', ''),
                        'encoding': readme_data.get('encoding', 'base64'),
                        'url': readme_data.get('html_url', '')
                    }
                    self.cache.set(cache_key, content)
                    return content
            
            # Fallback to scraping if API fails
            readme_url = f"https://github.com/{owner}/{repo}/blob/{branch}/README.md"
            html_content = await self.fetch_url(readme_url, use_cache=True)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the README content
            readme_content = soup.find('div', {'class': 'markdown-body'})
            if readme_content:
                content = {
                    'content': readme_content.get_text(),
                    'encoding': 'text',
                    'url': readme_url
                }
                self.cache.set(cache_key, content)
                return content
            
            return {}
        except Exception as e:
            logger.error(f"Error fetching README: {e}")
            return {}
    
    async def get_file_content(self, owner: str, repo: str, path: str, branch: str = 'main') -> Dict:
        """Get content of a specific file from GitHub with caching."""
        cache_key = f"file_{owner}_{repo}_{path}_{branch}"
        cached_content = self.cache.get(cache_key)
        if cached_content:
            return cached_content
        
        try:
            # Try to get file content from API first
            await self.rate_limiter.acquire()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    file_data = await response.json()
                    content = {
                        'content': file_data.get('content', ''),
                        'encoding': file_data.get('encoding', 'base64'),
                        'url': file_data.get('html_url', '')
                    }
                    self.cache.set(cache_key, content)
                    return content
            
            # Fallback to scraping if API fails
            file_url = f"https://github.com/{owner}/{repo}/blob/{branch}/{path}"
            html_content = await self.fetch_url(file_url, use_cache=True)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the file content
            file_content = soup.find('div', {'class': 'file-content'})
            if file_content:
                content = {
                    'content': file_content.get_text(),
                    'encoding': 'text',
                    'url': file_url
                }
                self.cache.set(cache_key, content)
                return content
            
            return {}
        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            return {}
    
    async def get_repo_topics(self, owner: str, repo: str) -> List[str]:
        """Get repository topics with caching."""
        cache_key = f"topics_{owner}_{repo}"
        cached_topics = self.cache.get(cache_key)
        if cached_topics:
            return cached_topics
        
        try:
            await self.rate_limiter.acquire()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/topics"
            async with self.session.get(api_url, headers={'Accept': 'application/vnd.github.mercy-preview+json'}) as response:
                if response.status == 200:
                    data = await response.json()
                    topics = data.get('names', [])
                    self.cache.set(cache_key, topics)
                    return topics
                return []
        except Exception as e:
            logger.error(f"Error fetching topics: {e}")
            return []
    
    async def get_contributors(self, owner: str, repo: str) -> List[str]:
        """Get repository contributors with caching."""
        cache_key = f"contributors_{owner}_{repo}"
        cached_contributors = self.cache.get(cache_key)
        if cached_contributors:
            return cached_contributors
        
        try:
            await self.rate_limiter.acquire()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    contributors = await response.json()
                    contributor_list = [contributor['login'] for contributor in contributors]
                    self.cache.set(cache_key, contributor_list)
                    return contributor_list
                return []
        except Exception as e:
            logger.error(f"Error fetching contributors: {e}")
            return []
    
    async def scrape_github_content(self, url: str) -> GitHubContent:
        """Main function to scrape GitHub content with caching."""
        cache_key = f"content_{url}"
        cached_content = self.cache.get(cache_key)
        if cached_content:
            return GitHubContent(**cached_content)
        
        try:
            # Parse the GitHub URL
            repo_info = self.parse_github_url(url)
            
            # Get repository metadata
            metadata = await self.get_repo_metadata(repo_info['owner'], repo_info['repo'])
            
            # Get content based on URL type
            if not repo_info['path'] or repo_info['path'].lower() == 'readme.md':
                content_data = await self.get_readme_content(
                    repo_info['owner'], 
                    repo_info['repo'], 
                    repo_info['branch']
                )
            else:
                content_data = await self.get_file_content(
                    repo_info['owner'], 
                    repo_info['repo'], 
                    repo_info['path'], 
                    repo_info['branch']
                )
            
            # Get additional metadata
            topics = await self.get_repo_topics(repo_info['owner'], repo_info['repo'])
            contributors = await self.get_contributors(repo_info['owner'], repo_info['repo'])
            
            # Create GitHubContent object
            content = GitHubContent(
                title=metadata.get('name', ''),
                description=metadata.get('description', ''),
                content=content_data.get('content', ''),
                language=metadata.get('language', ''),
                stars=metadata.get('stargazers_count', 0),
                forks=metadata.get('forks_count', 0),
                watchers=metadata.get('watchers_count', 0),
                last_updated=metadata.get('updated_at', ''),
                topics=topics,
                contributors=contributors,
                readme_url=content_data.get('url', ''),
                raw_content_url=metadata.get('html_url', ''),
                license=metadata.get('license', {}).get('name', ''),
                metadata={
                    'size': metadata.get('size', 0),
                    'open_issues': metadata.get('open_issues_count', 0),
                    'default_branch': metadata.get('default_branch', 'main'),
                    'created_at': metadata.get('created_at', ''),
                    'pushed_at': metadata.get('pushed_at', '')
                }
            )
            
            # Cache the complete content
            self.cache.set(cache_key, content.dict())
            
            return content
            
        except Exception as e:
            logger.error(f"Error scraping GitHub content: {e}")
            raise

async def main():
    """Example usage of the GitHub scraper with rate limiting and caching."""
    scraper = GitHubScraper(
        cache_dir=".github_cache",
        ttl_hours=24,
        calls_per_minute=30
    )
    
    async with scraper:
        # Example URLs
        urls = [
            "https://github.com/owner/repo",
            "https://github.com/owner/repo/blob/main/README.md",
            "https://github.com/owner/repo/blob/main/src/main.py"
        ]
        
        for url in urls:
            try:
                content = await scraper.scrape_github_content(url)
                print(f"Scraped content from {url}:")
                print(json.dumps(content.dict(), indent=2))
            except Exception as e:
                print(f"Error scraping {url}: {e}")


if __name__ == "__main__":
    asyncio.run(main())








