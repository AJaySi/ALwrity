"""
Keyword Utilities

Utility functions for keyword processing, validation, and normalization.
"""

from typing import Dict, Any, List, Optional, Set
from collections import Counter
import re
from loguru import logger

from ..constants import (
    MIN_KEYWORD_LENGTH,
    MAX_KEYWORD_LENGTH,
    DEFAULT_SEARCH_VOLUME_BASE,
    SEARCH_VOLUME_RANGE,
    DIFFICULTY_MAX,
    HASH_BASE_RELEVANCE,
    HASH_RELEVANCE_RANGE
)
from ..enums import IntentType, CompetitionLevel


def validate_keyword(keyword: str) -> bool:
    """
    Validate if a keyword meets basic criteria.
    
    Args:
        keyword: The keyword to validate
        
    Returns:
        True if keyword is valid, False otherwise
    """
    if not keyword or not isinstance(keyword, str):
        return False
    
    keyword = keyword.strip()
    
    # Check length constraints
    if len(keyword) < MIN_KEYWORD_LENGTH or len(keyword) > MAX_KEYWORD_LENGTH:
        return False
    
    # Check for invalid characters
    if re.match(r'^[^\w\s\-]+$', keyword):
        return False
    
    # Check if it's not just numbers or special characters
    if not re.search(r'[a-zA-Z]', keyword):
        return False
    
    return True


def normalize_keyword(keyword: str) -> str:
    """
    Normalize a keyword for consistent processing.
    
    Args:
        keyword: The keyword to normalize
        
    Returns:
        Normalized keyword
    """
    if not keyword:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = keyword.lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove special characters except hyphens and spaces
    normalized = re.sub(r'[^\w\s\-]', '', normalized)
    
    return normalized


def generate_keyword_variations(seed_keyword: str, industry: str) -> List[str]:
    """
    Generate keyword variations from a seed keyword.
    
    Args:
        seed_keyword: The base keyword
        industry: The industry context
        
    Returns:
        List of keyword variations
    """
    variations = [
        f"{seed_keyword} guide",
        f"best {seed_keyword}",
        f"how to {seed_keyword}",
        f"{seed_keyword} tips",
        f"{seed_keyword} tutorial",
        f"{seed_keyword} examples",
        f"{seed_keyword} vs",
        f"{seed_keyword} review",
        f"{seed_keyword} comparison",
        f"{industry} {seed_keyword}",
        f"{seed_keyword} {industry}",
        f"{seed_keyword} strategies",
        f"{seed_keyword} techniques",
        f"{seed_keyword} tools"
    ]
    
    # Filter and normalize variations
    normalized_variations = []
    for variation in variations:
        normalized = normalize_keyword(variation)
        if validate_keyword(normalized):
            normalized_variations.append(normalized)
    
    return list(set(normalized_variations))  # Remove duplicates


def generate_long_tail_keywords(seed_keyword: str, industry: str) -> List[str]:
    """
    Generate long-tail keywords from a seed keyword.
    
    Args:
        seed_keyword: The base keyword
        industry: The industry context
        
    Returns:
        List of long-tail keywords
    """
    long_tail = [
        f"how to {seed_keyword} for beginners",
        f"best {seed_keyword} strategies for {industry}",
        f"{seed_keyword} vs alternatives comparison",
        f"advanced {seed_keyword} techniques",
        f"{seed_keyword} case studies examples",
        f"step by step {seed_keyword} guide",
        f"{seed_keyword} best practices 2024",
        f"{seed_keyword} tools and resources",
        f"{seed_keyword} implementation guide",
        f"{seed_keyword} optimization tips"
    ]
    
    # Filter and normalize long-tail keywords
    normalized_long_tail = []
    for keyword in long_tail:
        normalized = normalize_keyword(keyword)
        if validate_keyword(normalized):
            normalized_long_tail.append(normalized)
    
    return list(set(normalized_long_tail))  # Remove duplicates


def generate_semantic_variations(seed_keyword: str, industry: str) -> List[str]:
    """
    Generate semantic variations of a keyword.
    
    Args:
        seed_keyword: The base keyword
        industry: The industry context
        
    Returns:
        List of semantic variations
    """
    semantic = [
        f"{seed_keyword} alternatives",
        f"{seed_keyword} solutions",
        f"{seed_keyword} methods",
        f"{seed_keyword} approaches",
        f"{seed_keyword} systems",
        f"{seed_keyword} platforms",
        f"{seed_keyword} software",
        f"{seed_keyword} tools",
        f"{seed_keyword} services",
        f"{seed_keyword} providers"
    ]
    
    # Filter and normalize semantic variations
    normalized_semantic = []
    for variation in semantic:
        normalized = normalize_keyword(variation)
        if validate_keyword(normalized):
            normalized_semantic.append(normalized)
    
    return list(set(normalized_semantic))  # Remove duplicates


def generate_related_keywords(seed_keyword: str, industry: str) -> List[str]:
    """
    Generate related keywords for a seed keyword.
    
    Args:
        seed_keyword: The base keyword
        industry: The industry context
        
    Returns:
        List of related keywords
    """
    related = [
        f"{seed_keyword} optimization",
        f"{seed_keyword} improvement",
        f"{seed_keyword} enhancement",
        f"{seed_keyword} development",
        f"{seed_keyword} implementation",
        f"{seed_keyword} execution",
        f"{seed_keyword} management",
        f"{seed_keyword} planning",
        f"{seed_keyword} strategy",
        f"{seed_keyword} framework"
    ]
    
    # Filter and normalize related keywords
    normalized_related = []
    for keyword in related:
        normalized = normalize_keyword(keyword)
        if validate_keyword(normalized):
            normalized_related.append(normalized)
    
    return list(set(normalized_related))  # Remove duplicates


def categorize_keywords_by_intent(keywords: List[str]) -> Dict[str, List[str]]:
    """
    Categorize keywords by search intent.
    
    Args:
        keywords: List of keywords to categorize
        
    Returns:
        Dictionary with intent types as keys and keyword lists as values
    """
    categories = {
        IntentType.INFORMATIONAL: [],
        IntentType.COMMERCIAL: [],
        IntentType.NAVIGATIONAL: [],
        IntentType.TRANSACTIONAL: []
    }
    
    # Intent classification keywords
    informational_keywords = ['how', 'what', 'why', 'guide', 'tips', 'tutorial', 'learn', 'understand']
    commercial_keywords = ['best', 'top', 'review', 'comparison', 'vs', 'ratings', 'ranking']
    transactional_keywords = ['buy', 'purchase', 'price', 'cost', 'order', 'book', 'deal', 'discount']
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in informational_keywords):
            categories[IntentType.INFORMATIONAL].append(keyword)
        elif any(word in keyword_lower for word in commercial_keywords):
            categories[IntentType.COMMERCIAL].append(keyword)
        elif any(word in keyword_lower for word in transactional_keywords):
            categories[IntentType.TRANSACTIONAL].append(keyword)
        else:
            categories[IntentType.NAVIGATIONAL].append(keyword)
    
    return categories


def analyze_single_keyword_intent(keyword: str) -> Dict[str, Any]:
    """
    Analyze the intent of a single keyword.
    
    Args:
        keyword: The keyword to analyze
        
    Returns:
        Dictionary with intent analysis results
    """
    keyword_lower = keyword.lower()
    
    # Intent classification keywords
    informational_keywords = ['how', 'what', 'why', 'guide', 'tips']
    commercial_keywords = ['best', 'top', 'review', 'comparison']
    transactional_keywords = ['buy', 'purchase', 'price', 'cost']
    
    if any(word in keyword_lower for word in informational_keywords):
        intent_type = IntentType.INFORMATIONAL
        content_type = 'educational'
    elif any(word in keyword_lower for word in commercial_keywords):
        intent_type = IntentType.COMMERCIAL
        content_type = 'comparison'
    elif any(word in keyword_lower for word in transactional_keywords):
        intent_type = IntentType.TRANSACTIONAL
        content_type = 'product'
    else:
        intent_type = IntentType.NAVIGATIONAL
        content_type = 'brand'
    
    return {
        'keyword': keyword,
        'intent_type': intent_type,
        'content_type': content_type,
        'confidence': 0.8
    }


def calculate_keyword_metrics(keyword: str, source: str = 'unknown') -> Dict[str, Any]:
    """
    Calculate simulated metrics for a keyword.
    
    Args:
        keyword: The keyword to calculate metrics for
        source: Source of the keyword (title, meta_description, etc.)
        
    Returns:
        Dictionary with keyword metrics
    """
    # Use hash-based calculation for consistent simulated data
    keyword_hash = hash(keyword)
    
    # Calculate metrics based on hash
    if source == 'title':
        search_volume = DEFAULT_SEARCH_VOLUME_BASE + (keyword_hash % SEARCH_VOLUME_RANGE)
        relevance_base = HASH_BASE_RELEVANCE
    else:  # meta_description
        search_volume = (DEFAULT_SEARCH_VOLUME_BASE // 2) + (keyword_hash % (SEARCH_VOLUME_RANGE // 2))
        relevance_base = HASH_BASE_RELEVANCE - 0.1
    
    return {
        'keyword': keyword,
        'source': source,
        'search_volume': max(100, search_volume),  # Minimum volume of 100
        'difficulty': keyword_hash % DIFFICULTY_MAX,
        'relevance_score': min(1.0, relevance_base + (keyword_hash % HASH_RELEVANCE_RANGE) / 100),
        'content_type': source
    }


def remove_duplicate_keywords(keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate keywords while preserving the highest relevance score.
    
    Args:
        keywords: List of keyword dictionaries
        
    Returns:
        List of unique keywords with highest relevance scores
    """
    unique_keywords = {}
    
    for kw in keywords:
        keyword = kw['keyword']
        if keyword not in unique_keywords:
            unique_keywords[keyword] = kw
        else:
            # Keep the one with higher relevance score
            existing_relevance = unique_keywords[keyword]['relevance_score']
            current_relevance = kw['relevance_score']
            if current_relevance > existing_relevance:
                unique_keywords[keyword] = kw
    
    return list(unique_keywords.values())


def sort_keywords_by_relevance(keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort keywords by relevance score in descending order.
    
    Args:
        keywords: List of keyword dictionaries
        
    Returns:
        Sorted list of keywords
    """
    return sorted(keywords, key=lambda x: x['relevance_score'], reverse=True)


def extract_keywords_from_text(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text content.
    
    Args:
        text: The text to extract keywords from
        min_length: Minimum length for keywords
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Common stop words to filter out
    stop_words = {'the', 'and', 'for', 'with', 'are', 'is', 'was', 'were', 'been', 'have', 'has', 'had', 
                  'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 
                  'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 
                  'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'}
    
    # Split text into words and filter
    words = text.lower().split()
    keywords = []
    
    for word in words:
        # Clean the word
        clean_word = re.sub(r'[^\w]', '', word)
        
        # Check if it meets criteria
        if (len(clean_word) >= min_length and 
            clean_word not in stop_words and 
            validate_keyword(clean_word)):
            keywords.append(clean_word)
    
    return list(set(keywords))  # Remove duplicates


def filter_keywords_by_length(keywords: List[str], min_length: int = 3, max_length: int = 100) -> List[str]:
    """
    Filter keywords by length constraints.
    
    Args:
        keywords: List of keywords to filter
        min_length: Minimum keyword length
        max_length: Maximum keyword length
        
    Returns:
        Filtered list of keywords
    """
    return [kw for kw in keywords if min_length <= len(kw) <= max_length]


def merge_keyword_lists(*keyword_lists: List[str]) -> List[str]:
    """
    Merge multiple keyword lists and remove duplicates.
    
    Args:
        keyword_lists: Variable number of keyword lists
        
    Returns:
        Merged list of unique keywords
    """
    all_keywords = set()
    for keyword_list in keyword_lists:
        all_keywords.update(keyword_list)
    
    return list(all_keywords)


def get_keyword_statistics(keywords: List[str]) -> Dict[str, Any]:
    """
    Get statistics about a list of keywords.
    
    Args:
        keywords: List of keywords to analyze
        
    Returns:
        Dictionary with keyword statistics
    """
    if not keywords:
        return {
            'total_keywords': 0,
            'average_length': 0,
            'unique_keywords': 0,
            'length_distribution': {}
        }
    
    # Basic statistics
    total_keywords = len(keywords)
    unique_keywords = len(set(keywords))
    lengths = [len(kw) for kw in keywords]
    average_length = sum(lengths) / len(lengths)
    
    # Length distribution
    length_distribution = {}
    for length in lengths:
        length_range = f"{length//5*5}-{length//5*5+4}"
        length_distribution[length_range] = length_distribution.get(length_range, 0) + 1
    
    return {
        'total_keywords': total_keywords,
        'average_length': round(average_length, 2),
        'unique_keywords': unique_keywords,
        'length_distribution': length_distribution,
        'shortest_keyword': min(keywords, key=len) if keywords else None,
        'longest_keyword': max(keywords, key=len) if keywords else None
    }
