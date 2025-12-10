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
        """Build basic research prompt focused on podcast-ready, actionable insights."""
        prompt = f"""You are a podcast researcher creating TALKING POINTS and FACT CARDS for a {industry} audience of {target_audience}.

Research Topic: "{topic}"

Provide analysis in this EXACT format:

## PODCAST HOOKS (3)
- [Hook line with tension + data point + source URL]

## OBJECTIONS & COUNTERS (3)
- Objection: [common listener objection]
  Counter: [concise rebuttal with stat + source URL]

## KEY STATS & PROOF (6)
- [Specific metric with %/number, date, and source URL]

## MINI CASE SNAPS (3)
- [Brand/company], [what they did], [outcome metric], [source URL]

## KEYWORDS TO MENTION (Primary + 5 Secondary)
- Primary: "{topic}"
- Secondary: [5 related keywords]

## 5 CONTENT ANGLES
1. [Angle with audience benefit + why-now]
2. [Angle ...]
3. [Angle ...]
4. [Angle ...]
5. [Angle ...]

## FACT CARD LIST (8)
- For each: Quote/claim, source URL, published date, metric/context.

REQUIREMENTS:
- Every claim MUST include a source URL (authoritative, recent: 2024-2025 preferred).
- Use concrete numbers, dates, outcomes; avoid generic advice.
- Keep bullets tight and scannable for spoken narration."""
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
        """Build comprehensive research prompt with podcast-focused, high-value insights."""
        date_filter = f"\nDate Focus: {config.date_range.value.replace('_', ' ')}" if config.date_range else ""
        source_filter = f"\nPriority Sources: {', '.join([s.value for s in config.source_types])}" if config.source_types else ""
        
        prompt = f"""You are a senior podcast researcher creating deeply sourced talking points for a {industry} audience of {target_audience}.

Research Topic: "{topic}"{date_filter}{source_filter}

Provide COMPLETE analysis in this EXACT format:

## WHAT'S CHANGED (2024-2025)
[5-7 concise trend bullets with numbers + source URLs]

## PROOF & NUMBERS
[10 stats with metric, date, sample size/method, and source URL]

## EXPERT SIGNALS
[5 expert quotes with name, title/company, source URL]

## RECENT MOVES
[5-7 news items or launches with dates and source URLs]

## MARKET SNAPSHOTS
[3-5 insights with TAM/SAM/SOM or adoption metrics, source URLs]

## CASE SNAPS
[3-5 cases: who, what they did, outcome metric, source URL]

## KEYWORD PLAN
Primary (3), Secondary (8-10), Long-tail (5-7) with intent hints.

## COMPETITOR GAPS
- Top 5 competitors (URL) + 1-line strength
- 5 content gaps we can own
- 3 unique angles to differentiate

## PODCAST-READY ANGLES (5)
- Each: Hook, promised takeaway, data or example, source URL.

## FACT CARD LIST (10)
- Each: Quote/claim, source URL, published date, metric/context, suggested angle tag.

VERIFICATION REQUIREMENTS:
- Minimum 2 authoritative sources per major claim.
- Prefer industry reports > research papers > news > blogs.
- 2024-2025 data strongly preferred.
- All numbers must include timeframe and methodology.
- Every bullet must be concise for spoken narration and actionable for {target_audience}."""
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

