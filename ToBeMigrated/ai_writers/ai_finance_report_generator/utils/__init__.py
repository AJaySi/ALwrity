"""
Utility functions and helpers for the AI Finance Report Generator.
"""

from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def validate_symbol(symbol: str) -> bool:
    """
    Validate if the given symbol is in correct format.
    
    Args:
        symbol (str): Stock symbol to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(symbol, str):
        return False
    return len(symbol.strip()) > 0

def format_currency(value: float) -> str:
    """
    Format number as currency.
    
    Args:
        value (float): Number to format
        
    Returns:
        str: Formatted currency string
    """
    return f"${value:,.2f}"

def get_feature_status(feature_name: str) -> Dict[str, Any]:
    """
    Get the status of a feature.
    
    Args:
        feature_name (str): Name of the feature
        
    Returns:
        Dict[str, Any]: Feature status information
    """
    # This will be expanded as we implement more features
    implemented_features = {
        "technical_analysis": True,
        "options_analysis": True,
    }
    
    return {
        "name": feature_name,
        "implemented": implemented_features.get(feature_name, False),
        "coming_soon": not implemented_features.get(feature_name, False)
    } 