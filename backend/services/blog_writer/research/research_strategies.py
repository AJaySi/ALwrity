"""
Research Strategy Pattern Implementation

Different strategies for executing research based on depth and focus.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from loguru import logger

from models.blog_models import BlogResearchRequest, ResearchMode, ResearchConfig
from .keyword_analyzer import KeywordAnalyzer
from .competitor_analyzer import CompetitorAnalyzer
from .content_angle_generator import ContentAngleGenerator


class ResearchStrategy(ABC):
    """Base class for research strategies."""
    
    def __init__(self):
        self.keyword_analyzer = KeywordAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.content_angle_generator = ContentAngleGenerator()
    
    @abstractmethod
    def build_research_prompt(
        self, 
        topic: str, 
        industry: str, 
        target_audience: str,
        config: ResearchConfig
    ) -> str:
        """Build the research prompt for the strategy."""
        pass
    
    @abstractmethod
    def get_mode(self) -> ResearchMode:
        """Return the research mode this strategy handles."""
        pass


class BasicResearchStrategy(ResearchStrategy):
    """Basic research strategy - keyword focused, minimal analysis."""
    
    def get_mode(self) -> ResearchMode:
        return ResearchMode.BASIC
    
    def build_research_prompt(
        self,
        topic: str,
        industry: str,
        target_audience: str,
        config: ResearchConfig
    ) -> str:
        """Build basic research prompt focused on keywords and quick insights."""
        prompt = f"""You are a professional blog content strategist researching for a {industry} blog targeting {target_audience}.

Research Topic: "{topic}"

Provide analysis in this EXACT format:

## CURRENT TRENDS (2024-2025)
- [Trend 1 with specific data and source URL]
- [Trend 2 with specific data and source URL]
- [Trend 3 with specific data and source URL]

## KEY STATISTICS
- [Statistic 1: specific number/percentage with source URL]
- [Statistic 2: specific number/percentage with source URL]
- [Statistic 3: specific number/percentage with source URL]
- [Statistic 4: specific number/percentage with source URL]
- [Statistic 5: specific number/percentage with source URL]

## PRIMARY KEYWORDS
1. "{topic}" (main keyword)
2. [Variation 1]
3. [Variation 2]

## SECONDARY KEYWORDS
[5 related keywords for blog content]

## CONTENT ANGLES (Top 5)
1. [Angle 1: specific unique approach]
2. [Angle 2: specific unique approach]
3. [Angle 3: specific unique approach]
4. [Angle 4: specific unique approach]
5. [Angle 5: specific unique approach]

REQUIREMENTS:
- Cite EVERY claim with authoritative source URLs
- Use 2024-2025 data when available
- Include specific numbers, dates, examples
- Focus on actionable blog insights for {target_audience}"""
        return prompt.strip()


class ComprehensiveResearchStrategy(ResearchStrategy):
    """Comprehensive research strategy - full analysis with all components."""
    
    def get_mode(self) -> ResearchMode:
        return ResearchMode.COMPREHENSIVE
    
    def build_research_prompt(
        self,
        topic: str,
        industry: str,
        target_audience: str,
        config: ResearchConfig
    ) -> str:
        """Build comprehensive research prompt with all analysis components."""
        date_filter = f"\nDate Focus: {config.date_range.value.replace('_', ' ')}" if config.date_range else ""
        source_filter = f"\nPriority Sources: {', '.join([s.value for s in config.source_types])}" if config.source_types else ""
        
        prompt = f"""You are a senior blog content strategist conducting comprehensive research for a {industry} blog targeting {target_audience}.

Research Topic: "{topic}"{date_filter}{source_filter}

Provide COMPLETE analysis in this EXACT format:

## TRENDS AND INSIGHTS (2024-2025)
[5-7 trends with specific data, numbers, and source URLs]

## KEY STATISTICS
[7-10 statistics with exact numbers, percentages, dates, and source URLs]

## EXPERT OPINIONS
[4-5 expert quotes with full attribution and source URLs]

## RECENT DEVELOPMENTS
[5-7 recent news/developments with dates and source URLs]

## MARKET ANALYSIS
[3-5 market insights with data points and source URLs]

## BEST PRACTICES & CASE STUDIES
[3-5 examples with specific outcomes/metrics and source URLs]

## KEYWORD ANALYSIS
Primary Keywords: [3 main variations]
Secondary Keywords: [7-10 related keywords]
Long-Tail Opportunities: [5-7 specific search phrases]

## COMPETITOR ANALYSIS
Top Competitors: [5 competitors with brief descriptions]
Content Gaps: [5 topics competitors are missing]
Competitive Advantages: [5 unique angles we can own]

## CONTENT ANGLES (Exactly 5)
1. [Unique angle with reasoning and target benefit]
2. [Unique angle with reasoning and target benefit]
3. [Unique angle with reasoning and target benefit]
4. [Unique angle with reasoning and target benefit]
5. [Unique angle with reasoning and target benefit]

VERIFICATION REQUIREMENTS:
- Minimum 2 authoritative sources per major claim
- Prioritize: Industry publications > Research papers > News > Blogs
- 2024-2025 data strongly preferred
- All numbers must include context (timeframe, sample size, methodology)
- Every recommendation must be actionable for {target_audience}"""
        return prompt.strip()


class TargetedResearchStrategy(ResearchStrategy):
    """Targeted research strategy - focused on specific aspects."""
    
    def get_mode(self) -> ResearchMode:
        return ResearchMode.TARGETED
    
    def build_research_prompt(
        self,
        topic: str,
        industry: str,
        target_audience: str,
        config: ResearchConfig
    ) -> str:
        """Build targeted research prompt based on config preferences."""
        sections = []
        
        if config.include_trends:
            sections.append("""## CURRENT TRENDS
[3-5 trends with data and source URLs]""")
        
        if config.include_statistics:
            sections.append("""## KEY STATISTICS
[5-7 statistics with numbers and source URLs]""")
        
        if config.include_expert_quotes:
            sections.append("""## EXPERT OPINIONS
[3-4 expert quotes with attribution and source URLs]""")
        
        if config.include_competitors:
            sections.append("""## COMPETITOR ANALYSIS
Top Competitors: [3-5]
Content Gaps: [3-5]""")
        
        # Always include keywords and angles
        sections.append("""## KEYWORD ANALYSIS
Primary: [2-3 variations]
Secondary: [5-7 keywords]
Long-Tail: [3-5 phrases]""")
        
        sections.append("""## CONTENT ANGLES (3-5)
[Unique blog angles with reasoning]""")
        
        sections_str = "\n\n".join(sections)
        
        prompt = f"""You are a blog content strategist conducting targeted research for a {industry} blog targeting {target_audience}.

Research Topic: "{topic}"

Provide focused analysis in this EXACT format:

{sections_str}

REQUIREMENTS:
- Cite all claims with authoritative source URLs
- Include specific numbers, dates, examples
- Focus on actionable insights for {target_audience}
- Use 2024-2025 data when available"""
        return prompt.strip()


def get_strategy_for_mode(mode: ResearchMode) -> ResearchStrategy:
    """Factory function to get the appropriate strategy for a mode."""
    strategy_map = {
        ResearchMode.BASIC: BasicResearchStrategy,
        ResearchMode.COMPREHENSIVE: ComprehensiveResearchStrategy,
        ResearchMode.TARGETED: TargetedResearchStrategy,
    }
    
    strategy_class = strategy_map.get(mode, BasicResearchStrategy)
    return strategy_class()

