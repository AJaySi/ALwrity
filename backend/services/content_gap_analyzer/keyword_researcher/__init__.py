"""
Keyword Researcher Package

Main package initialization for keyword researcher service.
"""

# Import extracted modules
from .models import *
from .config import get_config
from .utils import *
from .dependencies import get_dependencies

# Export configuration and utilities
__all__ = [
    'get_config',
    'get_dependencies',
]

# Add all utility exports
from .utils import __all__ as utils_all
__all__.extend(utils_all)

# Add all model exports
from .models import __all__ as models_all
__all__.extend(models_all)

# Import the main class after avoiding circular import
def get_keyword_researcher():
    """Get KeywordResearcher instance to avoid circular imports."""
    from .keyword_researcher import KeywordResearcher as KR
    return KR()

# Version information
__version__ = "1.0.0"
__description__ = "Keyword researcher service with modular architecture"
