"""
Visual Data Extractor for Image Generation Prompts.

This module provides intelligent extraction of visual-relevant data from blog sections
and research data to generate contextually relevant image prompts.

Key Features:
- Statistics extraction with regex patterns
- Domain-specific visual concept detection
- Research source mining for visual data
- Deduplication and data cleaning
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


# Pre-compiled regex patterns for performance
_STATISTICAL_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ('percentage', re.compile(r'\d+[\d,]*%', re.IGNORECASE)),
    ('currency', re.compile(r'\$[\d,]+(?:\.\d{2})?', re.IGNORECASE)),
    ('multiplier', re.compile(r'\d+[\d,]*x', re.IGNORECASE)),
    ('large_number', re.compile(r'\d+[\d,]*\s*(?:million|billion|thousand|trillion)s?', re.IGNORECASE)),
    ('range', re.compile(r'\d+\s*-\s*\d+%', re.IGNORECASE)),
    ('change_up', re.compile(r'up\s+by\s+\d+%', re.IGNORECASE)),
    ('change_down', re.compile(r'down\s+by\s+\d+%', re.IGNORECASE)),
    ('growth', re.compile(r'(?:increased|decreased|grew|declined)\s*[\d%]+', re.IGNORECASE)),
    ('cagr', re.compile(r'cagr\s+of\s+[\d.]+%', re.IGNORECASE)),
]

_VISUAL_DATA_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ('times', re.compile(r'\d+\s*(?:times|folds?)', re.IGNORECASE)),
    ('ranking', re.compile(r'rank(?:ed|ing)?\s*(?:#?\d+|first|second|third|top|bottom)', re.IGNORECASE)),
    ('comparison', re.compile(r'(?:vs|versus|compared\s+to|compared\s+with)', re.IGNORECASE)),
    ('chart_mention', re.compile(r'(?:chart|graph|diagram|visual|infographic)', re.IGNORECASE)),
    ('superlative', re.compile(r'(?:best|worst|leading|top|highest|lowest)', re.IGNORECASE)),
]

_TREND_KEYWORDS: Set[str] = {
    'increase', 'decrease', 'growth', 'trend', 'pattern', 'comparison',
    'ranking', 'versus', 'vs', 'rise', 'fall', 'growth', 'decline',
    'surge', 'drop', 'climb', 'jump', 'plummet', 'soar', 'fluctuate'
}


# Domain-specific visual concepts mapping
DOMAIN_VISUAL_CONCEPTS: Dict[str, List[str]] = {
    "tech": [
        "circuit board patterns", "digital interface", "data stream", "network nodes",
        "server racks", "silicon chips", "binary code", "cloud computing",
        "artificial intelligence", "machine learning model", "software code",
        "technology innovation", "digital transformation"
    ],
    "healthcare": [
        "stethoscope", "medical chart", "hospital equipment", "DNA helix",
        "heart rate monitor", "medical cross", "prescription", "patient care",
        "healthcare professional", "medical research", "wellness", "health metrics"
    ],
    "finance": [
        "stock chart", "dollar signs", "investment growth", "banking",
        "pie chart", "financial graph", "portfolio", "market trends",
        "cryptocurrency", "blockchain", "financial analysis", "wealth management"
    ],
    "marketing": [
        "digital marketing", "social media", "content strategy", "audience growth",
        "brand awareness", "conversion funnel", "engagement metrics", "ROI chart",
        "marketing analytics", "customer acquisition", "viral content"
    ],
    "education": [
        "classroom", "graduation cap", "books", "learning curve",
        "knowledge growth", "student achievement", "online learning", "curriculum",
        "educational technology", "academic success", "skill development"
    ],
    "ecommerce": [
        "shopping cart", "product display", "checkout flow", "conversion",
        "customer journey", "inventory", "shipping", "discount tags",
        "online store", "e-commerce analytics", "retail technology"
    ],
    "real_estate": [
        "building", "house", "property", "real estate market",
        "mortgage", "home ownership", "apartment complex", "construction",
        "property investment", "housing market", "architecture"
    ],
    "food": [
        "restaurant", "cooking", "ingredients", "food preparation",
        "recipe", "menu", "dining experience", "culinary arts",
        "gourmet", "food photography", "healthy eating"
    ],
    "travel": [
        "airplane", "destination", "map", "luggage", "passport",
        "tourist", "hotel", "beach resort", "adventure", "travel planning",
        "vacation", "world exploration"
    ],
    "fitness": [
        "gym", "workout", "exercise", "muscle", "weight loss",
        "nutrition", "running", "yoga", "healthy lifestyle", "fitness tracking",
        "sports training", "wellness"
    ],
    "fashion": [
        "clothing", "wardrobe", "style", "runway", "designer",
        "outfit", "accessories", "fashion trends", "personal style", "apparel"
    ],
    "entertainment": [
        "movie reel", "music note", "concert", "celebrity", "streaming",
        "gaming", "content creation", "media production", "creative arts", "performance"
    ],
    "business": [
        "office", "meeting", "presentation", "business growth", "strategy",
        "team collaboration", "enterprise", "corporate", "leadership", "productivity"
    ],
    "science": [
        "laboratory", "microscope", "experiment", "data analysis", "research",
        "scientific method", "discovery", "innovation", "technology development"
    ],
    "sports": [
        "stadium", "athlete", "scoreboard", "trophy", "team",
        "competition", "fitness", "championship", "sports analytics", "training"
    ],
    "legal": [
        "gavel", "courthouse", "legal documents", "scales of justice",
        "law books", "legal contract", "attorney", "courtroom", "compliance"
    ],
    "environmental": [
        "renewable energy", "solar panels", "wind turbines", "green technology",
        "sustainability", "climate change", "eco-friendly", "nature conservation"
    ],
}


@dataclass
class ExtractedVisualData:
    """Data class for extracted visual data."""
    visual_keywords: List[str] = field(default_factory=list)
    data_points: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    statistics: List[str] = field(default_factory=list)
    domain_concepts: List[str] = field(default_factory=list)
    visual_metaphors: List[str] = field(default_factory=list)
    detected_domains: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary for serialization."""
        return {
            "visual_keywords": self.visual_keywords,
            "data_points": self.data_points,
            "concepts": self.concepts,
            "statistics": self.statistics,
            "domain_concepts": self.domain_concepts,
            "visual_metaphors": self.visual_metaphors,
            "detected_domains": self.detected_domains,
        }
    
    def has_statistics(self) -> bool:
        """Check if any statistics were extracted."""
        return bool(self.statistics)
    
    def has_data_points(self) -> bool:
        """Check if any data points were extracted."""
        return bool(self.data_points)
    
    def has_domain_concepts(self) -> bool:
        """Check if any domain concepts were extracted."""
        return bool(self.domain_concepts)
    
    def is_data_heavy(self) -> bool:
        """Check if content is data-heavy (statistics or data points)."""
        return self.has_statistics() or self.has_data_points()
    
    def get_recommended_image_type(self) -> str:
        """Get recommended image type based on extracted data."""
        if self.has_statistics() or self.has_data_points():
            return "infographic" if self.has_domain_concepts() else "chart"
        elif self.has_domain_concepts():
            return "conceptual"
        return "conceptual"


def _extract_statistic_with_context(text: str) -> Optional[str]:
    """
    Extract a statistic with surrounding context from text.
    
    Args:
        text: Input text to search
        
    Returns:
        Statistic with context (up to 60 chars before + statistic + 30 chars after),
        or None if no statistic found
    """
    for pattern_name, pattern in _STATISTICAL_PATTERNS:
        match = pattern.search(text)
        if match:
            idx = match.start()
            context_start = max(0, idx - 60)
            context_end = min(len(text), match.end() + 30)
            context = text[context_start:context_end].strip()
            # Clean up to word boundaries
            if context_start > 0:
                # Find first space in context
                first_space = context.find(' ')
                if first_space > 0 and first_space < 20:
                    context = context[first_space + 1:]
            return context
    return None


def _has_visual_mention(text: str) -> bool:
    """
    Check if text contains mentions of visual concepts.
    
    Args:
        text: Input text to check
        
    Returns:
        True if text contains visual data patterns
    """
    for pattern_name, pattern in _VISUAL_DATA_PATTERNS:
        if pattern.search(text):
            return True
    return False


def _has_trend_keyword(text: str) -> bool:
    """
    Check if text contains trend/comparison keywords.
    
    Args:
        text: Input text to check
        
    Returns:
        True if text contains trend keywords
    """
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in _TREND_KEYWORDS)


def _detect_domains_in_text(text: str) -> Tuple[List[str], List[str]]:
    """
    Detect industry/domain from text and return relevant visual concepts.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (detected_domain_names, domain_concepts)
    """
    text_lower = text.lower()
    detected_domains: List[str] = []
    all_concepts: List[str] = []
    
    for domain, concepts in DOMAIN_VISUAL_CONCEPTS.items():
        # Check if domain name or any concept keyword is in text
        keywords_to_check = [domain] + concepts[:5]
        if any(keyword in text_lower for keyword in keywords_to_check):
            detected_domains.append(domain)
            # Add top 3 concepts for this domain
            all_concepts.extend(concepts[:3])
    
    return detected_domains, list(set(all_concepts))


def _deduplicate_and_limit(
    items: List[str],
    max_items: int = 10,
    key_length: int = 50
) -> List[str]:
    """
    Deduplicate items by normalized key and limit count.
    
    Args:
        items: List of strings to deduplicate
        max_items: Maximum number of items to return
        key_length: Length of normalized key for comparison
        
    Returns:
        Deduplicated list with max_items items
    """
    seen: Set[str] = set()
    unique_items: List[str] = []
    
    for item in items:
        if not item or not isinstance(item, str):
            continue
        normalized = item.lower().strip()[:key_length]
        if normalized and normalized not in seen and len(unique_items) < max_items:
            seen.add(normalized)
            unique_items.append(item.strip())
    
    return unique_items


def extract_visual_data(
    section: Optional[Dict[str, any]],
    research: Optional[Dict[str, any]]
) -> ExtractedVisualData:
    """
    Intelligently extract visual-relevant data from blog section and research.
    
    This function analyzes section headings, key points, subheadings, keywords,
    and research data to extract statistics, data points, visual concepts,
    and domain-specific visual metaphors.
    
    Args:
        section: Blog section dictionary with optional keys:
            - heading: Section title
            - subheadings: List of subheading strings
            - key_points: List of key point strings
            - keywords: List of keyword strings
        research: Research data dictionary with optional keys:
            - key_facts, highlights: List of fact strings
            - insights, summary: String or list of insight strings
            - sources, references: List of source dictionaries
            - keywords: Dict or list of keywords
            - domain, industry: Domain/industry string
    
    Returns:
        ExtractedVisualData dataclass with extracted information
        
    Example:
        >>> section = {
        ...     "heading": "AI in Healthcare",
        ...     "key_points": ["Market grew 40% in 2023", "Investment reached $5B"]
        ... }
        >>> result = extract_visual_data(section, None)
        >>> result.statistics
        ['Market grew 40% in 2023', 'Investment reached $5B']
        >>> result.domain_concepts
        ['stethoscope', 'medical chart', 'hospital equipment']
    """
    result = ExtractedVisualData()
    
    # Phase 1: Extract from section
    if section:
        _extract_from_section(section, result)
    
    # Phase 2: Extract from research
    if research:
        _extract_from_research(research, result)
    
    # Phase 3: Deduplicate all extracted data
    _deduplicate_results(result)
    
    return result


def _extract_from_section(section: Dict, result: ExtractedVisualData) -> None:
    """Extract visual data from blog section."""
    
    # Extract from key points
    key_points = section.get("key_points", []) or []
    for point in key_points[:10]:  # Increased limit
        if not isinstance(point, str):
            continue
            
        # Check for statistics
        stat = _extract_statistic_with_context(point)
        if stat:
            result.statistics.append(stat)
            # Also detect domains in statistical points
            domains, concepts = _detect_domains_in_text(point)
            result.detected_domains.extend(domains)
            result.domain_concepts.extend(concepts)
            continue
        
        # Check for visual mentions or trend keywords
        if _has_visual_mention(point) or _has_trend_keyword(point):
            result.data_points.append(point)
        else:
            result.concepts.append(point)
            # Detect domains in regular concepts too
            domains, concepts = _detect_domains_in_text(point)
            result.detected_domains.extend(domains)
            result.domain_concepts.extend(concepts)
    
    # Extract from subheadings
    subheadings = section.get("subheadings", []) or []
    for subhead in subheadings[:7]:
        if isinstance(subhead, str):
            result.concepts.append(subhead)
            domains, concepts = _detect_domains_in_text(subhead)
            result.detected_domains.extend(domains)
            result.domain_concepts.extend(concepts)
    
    # Extract from keywords
    keywords = section.get("keywords", []) or []
    for kw in keywords[:12]:
        if kw and isinstance(kw, str):
            result.visual_keywords.append(str(kw))
    
    # Detect domain from section heading
    heading = section.get("heading", "")
    if heading and isinstance(heading, str):
        domains, concepts = _detect_domains_in_text(heading)
        result.detected_domains.extend(domains)
        result.domain_concepts.extend(concepts)
        # Also add heading as a concept
        if heading.strip():
            result.concepts.insert(0, heading.strip())


def _extract_from_research(research: Dict, result: ExtractedVisualData) -> None:
    """Extract visual data from research data."""
    
    # Extract from key facts/highlights
    key_facts = research.get("key_facts", []) or research.get("highlights", []) or []
    for fact in key_facts[:7]:
        if isinstance(fact, str):
            stat = _extract_statistic_with_context(fact)
            if stat:
                result.statistics.append(stat)
            else:
                result.data_points.append(fact)
    
    # Extract from insights/summary
    insights = research.get("insights", []) or research.get("summary", "")
    if isinstance(insights, str) and insights:
        sentences = insights.split('.')[:7]
        for sent in sentences:
            sent = sent.strip()
            if sent:
                stat = _extract_statistic_with_context(sent)
                if stat:
                    result.statistics.append(stat)
                else:
                    result.concepts.append(sent)
    elif isinstance(insights, list):
        for insight in insights[:7]:
            if isinstance(insight, str):
                stat = _extract_statistic_with_context(insight)
                if stat:
                    result.statistics.append(stat)
                else:
                    result.concepts.append(insight)
    
    # Extract from research sources
    sources = research.get("sources", []) or research.get("references", []) or []
    for source in sources[:7]:
        if not isinstance(source, dict):
            continue
            
        # Extract from source title
        source_title = source.get("title", "")
        if source_title:
            domains, concepts = _detect_domains_in_text(source_title)
            result.detected_domains.extend(domains)
            result.domain_concepts.extend(concepts)
        
        # Extract from source excerpt/snippet
        source_excerpt = (
            source.get("excerpt", "") 
            or source.get("snippet", "") 
            or source.get("description", "")
        )
        if source_excerpt:
            # Extract statistic
            stat = _extract_statistic_with_context(source_excerpt)
            if stat:
                result.statistics.append(stat)
            
            # Add as data point (limited to 200 chars)
            excerpt_text = source_excerpt[:200] if len(source_excerpt) > 200 else source_excerpt
            result.data_points.append(excerpt_text)
            
            # Check for visual mentions
            if _has_visual_mention(source_excerpt):
                result.data_points.append(source_excerpt[:300])
            
            # Detect domains
            domains, concepts = _detect_domains_in_text(source_excerpt)
            result.detected_domains.extend(domains)
            result.domain_concepts.extend(concepts)
    
    # Extract from research keywords
    research_keywords = research.get("keywords", {})
    if isinstance(research_keywords, dict):
        primary_kw = (
            research_keywords.get("primary_keywords", []) 
            or research_keywords.get("primary", [])
            or []
        )
        for kw in primary_kw[:7]:
            if isinstance(kw, str):
                domains, concepts = _detect_domains_in_text(kw)
                result.detected_domains.extend(domains)
                result.domain_concepts.extend(concepts)
    elif isinstance(research_keywords, list):
        for kw in research_keywords[:7]:
            if isinstance(kw, str):
                domains, concepts = _detect_domains_in_text(kw)
                result.detected_domains.extend(domains)
                result.domain_concepts.extend(concepts)
    
    # Extract from research domain/industry
    research_domain = research.get("domain", "") or research.get("industry", "")
    if research_domain:
        domains, concepts = _detect_domains_in_text(research_domain)
        result.detected_domains.extend(domains)
        result.domain_concepts.extend(concepts)


def _deduplicate_results(result: ExtractedVisualData) -> None:
    """Deduplicate all extracted data."""
    result.visual_keywords = _deduplicate_and_limit(result.visual_keywords, 12)
    result.data_points = _deduplicate_and_limit(result.data_points, 10)
    result.concepts = _deduplicate_and_limit(result.concepts, 10)
    result.statistics = _deduplicate_and_limit(result.statistics, 10)
    result.domain_concepts = _deduplicate_and_limit(result.domain_concepts, 10)
    result.detected_domains = list(set(result.detected_domains))


def get_model_recommendation(visual_data: ExtractedVisualData) -> Optional[str]:
    """
    Get model recommendation based on extracted visual data.
    
    Args:
        visual_data: ExtractedVisualData instance
        
    Returns:
        Model recommendation string or None
    """
    if visual_data.is_data_heavy():
        return (
            "\n\nMODEL RECOMMENDATION: This section contains data/statistics. "
            "Consider using:\n"
            "- FLUX Kontext Pro: Best for data visualizations with text labels\n"
            "- GLM-Image: Excellent for infographics and educational diagrams\n"
            "- Ideogram V3 Turbo: Good for simple charts with text overlays"
        )
    elif visual_data.has_domain_concepts():
        return (
            "\n\nMODEL RECOMMENDATION: This section covers domain-specific content. "
            "Consider using:\n"
            "- Qwen Image: Best for abstract conceptual imagery\n"
            "- FLUX Kontext Pro: Good for conceptual imagery with text support\n"
            "- FLUX 2 Flex: Excellent for poster-style conceptual designs"
        )
    return None


def build_visual_summary(visual_data: ExtractedVisualData) -> str:
    """
    Build a text summary from extracted visual data.
    
    Args:
        visual_data: ExtractedVisualData instance
        
    Returns:
        Formatted summary string for use in prompts
    """
    parts: List[str] = []
    
    if visual_data.statistics:
        parts.append(f"Key Statistics: {', '.join(visual_data.statistics[:3])}")
    
    if visual_data.data_points:
        parts.append(f"Data Points: {', '.join(visual_data.data_points[:3])}")
    
    if visual_data.concepts:
        parts.append(f"Visual Concepts: {', '.join(visual_data.concepts[:5])}")
    
    if visual_data.visual_keywords:
        parts.append(f"Keywords: {', '.join(visual_data.visual_keywords[:8])}")
    
    if visual_data.domain_concepts:
        parts.append(f"Domain Visual Concepts: {', '.join(visual_data.domain_concepts[:5])}")
    
    if visual_data.detected_domains:
        parts.append(f"Detected Domains: {', '.join(visual_data.detected_domains)}")
    
    return "\n".join(parts) if parts else ""
