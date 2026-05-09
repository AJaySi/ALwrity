"""Image Studio API router package.

Assembled from modular sub-routers. Same prefix and tags as the original monolithic file.
Currently re-exports from the legacy router. Sub-routers will be added in subsequent sessions.
"""

from ..image_studio_router import router

__all__ = ["router"]
