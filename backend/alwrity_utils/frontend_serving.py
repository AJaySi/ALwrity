"""
Frontend Serving Module
Handles React frontend serving and static file mounting with cache headers.
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from typing import Dict, Any


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add cache headers to static files.
    
    This improves performance by allowing browsers to cache static assets
    (JS, CSS, images) for 1 year, reducing repeat visit load times.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only add cache headers to static files
        if request.url.path.startswith("/static/"):
            path = request.url.path.lower()
            
            # Check if file has a hash in its name (React build pattern: filename.hash.ext)
            # Examples: bundle.abc123.js, main.def456.chunk.js, vendors.789abc.js
            import re
            # Pattern matches: filename.hexhash.ext or filename.hexhash.chunk.ext
            hash_pattern = r'\.[a-f0-9]{8,}\.'
            has_hash = bool(re.search(hash_pattern, path))
            
            # File extensions that should be cached
            cacheable_extensions = ['.js', '.css', '.woff', '.woff2', '.ttf', '.otf', 
                                  '.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico', '.gif']
            is_cacheable_file = any(path.endswith(ext) for ext in cacheable_extensions)
            
            if is_cacheable_file:
                if has_hash:
                    # Immutable files (with hash) - cache for 1 year
                    # These files never change (new hash = new file)
                    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
                    response.headers["Expires"] = "Thu, 31 Dec 2025 23:59:59 GMT"
                else:
                    # Non-hashed files - shorter cache (1 hour)
                    # These might be updated, so cache for shorter time
                    response.headers["Cache-Control"] = "public, max-age=3600"
        
        # Never cache HTML files (index.html)
        elif request.url.path == "/" or request.url.path.endswith(".html"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


class FrontendServing:
    """Manages React frontend serving and static file mounting with cache headers."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.frontend_build_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")
        self.static_path = os.path.join(self.frontend_build_path, "static")
    
    def setup_frontend_serving(self) -> bool:
        """
        Set up React frontend serving and static file mounting with cache headers.
        
        This method:
        1. Adds cache headers middleware for static files
        2. Mounts static files directory
        3. Configures proper caching for performance
        """
        try:
            logger.info("Setting up frontend serving with cache headers...")
            
            # Add cache headers middleware BEFORE mounting static files
            self.app.add_middleware(CacheHeadersMiddleware)
            logger.info("Cache headers middleware added")
            
            # Mount static files for React app (only if directory exists)
            if os.path.exists(self.static_path):
                self.app.mount("/static", StaticFiles(directory=self.static_path), name="static")
                logger.info("Frontend static files mounted successfully with cache headers")
                logger.info("Static files will be cached for 1 year (immutable files) or 1 hour (others)")
                return True
            else:
                logger.info("Frontend build directory not found. Static files not mounted.")
                return False
                
        except Exception as e:
            logger.error(f"Could not mount static files: {e}")
            return False
    
    def serve_frontend(self) -> FileResponse | Dict[str, Any]:
        """
        Serve the React frontend index.html.
        
        Note: index.html is never cached to ensure users always get the latest version.
        Static assets (JS/CSS) are cached separately via middleware.
        """
        try:
            # Check if frontend build exists
            index_html = os.path.join(self.frontend_build_path, "index.html")
            
            if os.path.exists(index_html):
                # Return FileResponse with no-cache headers for HTML
                response = FileResponse(index_html)
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                return response
            else:
                return {
                    "message": "Frontend not built. Please run 'npm run build' in the frontend directory.",
                    "api_docs": "/api/docs"
                }
                
        except Exception as e:
            logger.error(f"Error serving frontend: {e}")
            return {
                "message": "Error serving frontend",
                "error": str(e),
                "api_docs": "/api/docs"
            }
    
    def get_frontend_status(self) -> Dict[str, Any]:
        """Get the status of frontend build and serving."""
        try:
            index_html = os.path.join(self.frontend_build_path, "index.html")
            static_exists = os.path.exists(self.static_path)
            
            return {
                "frontend_build_path": self.frontend_build_path,
                "static_path": self.static_path,
                "index_html_exists": os.path.exists(index_html),
                "static_files_exist": static_exists,
                "frontend_ready": os.path.exists(index_html) and static_exists
            }
            
        except Exception as e:
            logger.error(f"Error checking frontend status: {e}")
            return {
                "error": str(e),
                "frontend_ready": False
            }
