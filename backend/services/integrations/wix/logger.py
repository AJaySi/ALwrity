"""
Intelligent logging utility for Wix operations.
Aggregates and consolidates logs to reduce console noise.
"""
from typing import Dict, Any, Optional, List
from loguru import logger
import json


class WixLogger:
    """Consolidated logger for Wix operations"""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def reset(self):
        """Reset context for new operation"""
        self.context = {}
        self.errors = []
        self.warnings = []
    
    def set_context(self, key: str, value: Any):
        """Store context information"""
        self.context[key] = value
    
    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)
    
    def log_operation_start(self, operation: str, **kwargs):
        """Log start of operation with aggregated context"""
        logger.info(f"🚀 Wix: {operation}")
        if kwargs:
            summary = ", ".join([f"{k}={v}" for k, v in kwargs.items() if v])
            if summary:
                logger.info(f"   {summary}")
    
    def log_operation_result(self, operation: str, success: bool, result: Optional[Dict] = None, error: Optional[str] = None):
        """Log operation result"""
        if success:
            post_id = result.get('draftPost', {}).get('id') if result else None
            if post_id:
                logger.success(f"✅ Wix: {operation} - Post ID: {post_id}")
            else:
                logger.success(f"✅ Wix: {operation} - Success")
        else:
            logger.error(f"❌ Wix: {operation} - {error or 'Failed'}")
    
    def log_api_call(self, method: str, endpoint: str, status_code: int, 
                     payload_summary: Optional[Dict] = None, error_body: Optional[Dict] = None):
        """Log API call with aggregated information"""
        status_emoji = "✅" if status_code < 400 else "❌"
        logger.info(f"{status_emoji} Wix API: {method} {endpoint} → {status_code}")
        
        if payload_summary:
            # Show only key information
            if 'draftPost' in payload_summary:
                dp = payload_summary['draftPost']
                parts = []
                if 'title' in dp:
                    parts.append(f"title='{str(dp['title'])[:50]}...'")
                if 'richContent' in dp:
                    nodes_count = len(dp['richContent'].get('nodes', []))
                    parts.append(f"nodes={nodes_count}")
                if 'seoData' in dp:
                    parts.append("has_seoData")
                if parts:
                    logger.debug(f"   Payload: {', '.join(parts)}")
        
        if error_body and status_code >= 400:
            error_msg = error_body.get('message', 'Unknown error')
            logger.error(f"   Error: {error_msg}")
            if status_code == 500:
                logger.error("   ⚠️ Internal server error - check Wix API status")
            elif status_code == 403:
                logger.error("   ⚠️ Permission denied - verify OAuth app has BLOG.CREATE-DRAFT")
            elif status_code == 401:
                logger.error("   ⚠️ Unauthorized - token may be expired")
    
    def log_token_info(self, token_length: int, has_blog_scope: Optional[bool] = None, 
                       meta_site_id: Optional[str] = None):
        """Log token information (aggregated)"""
        info_parts = [f"Token: {token_length} chars"]
        if has_blog_scope is not None:
            info_parts.append(f"Blog scope: {'✅' if has_blog_scope else '❌'}")
        if meta_site_id:
            info_parts.append(f"Site ID: {meta_site_id[:20]}...")
        logger.debug(f"🔐 Wix Auth: {', '.join(info_parts)}")
    
    def log_ricos_conversion(self, nodes_count: int, method: str = "custom parser"):
        """Log Ricos conversion result"""
        logger.info(f"📝 Wix Ricos: Converted to {nodes_count} nodes ({method})")
    
    def log_seo_data(self, tags_count: int, keywords_count: int):
        """Log SEO data summary"""
        logger.info(f"🔍 Wix SEO: {tags_count} tags, {keywords_count} keywords")
    
    def log_final_summary(self):
        """Log final aggregated summary"""
        if self.errors:
            logger.error(f"⚠️ Wix Operation: {len(self.errors)} error(s)")
            for err in self.errors[-3:]:  # Show last 3 errors
                logger.error(f"   {err}")
        elif self.warnings:
            logger.warning(f"⚠️ Wix Operation: {len(self.warnings)} warning(s)")
        else:
            logger.success("✅ Wix Operation: No issues detected")


# Global instance
wix_logger = WixLogger()

