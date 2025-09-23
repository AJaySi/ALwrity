"""
AI Blog Writer Service - Main entry point for blog writing functionality.

This module provides a clean interface to the modular blog writer services.
The actual implementation has been refactored into specialized modules:
- research/ - Research and keyword analysis
- outline/ - Outline generation and optimization  
- core/ - Main service orchestrator
"""

from .core import BlogWriterService