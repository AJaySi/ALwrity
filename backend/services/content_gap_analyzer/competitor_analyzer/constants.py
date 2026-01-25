"""
Constants for Competitor Analyzer Service

This module contains all constants, thresholds, and configuration values
used across the competitor analyzer services.
"""

# Analysis Limits and Thresholds
MAX_COMPETITORS_PER_ANALYSIS = 50
MAX_URLS_PER_BATCH = 10
MAX_CONTENT_PIECES_PER_COMPETITOR = 1000
MAX_KEYWORDS_PER_ANALYSIS = 100
MAX_RECOMMENDATIONS_PER_ANALYSIS = 20

# Scoring Thresholds
MIN_QUALITY_SCORE = 0.0
MAX_QUALITY_SCORE = 10.0
DEFAULT_QUALITY_SCORE = 5.0
HIGH_QUALITY_THRESHOLD = 8.0
MEDIUM_QUALITY_THRESHOLD = 6.0
LOW_QUALITY_THRESHOLD = 4.0

MIN_DOMAIN_AUTHORITY = 0
MAX_DOMAIN_AUTHORITY = 100
HIGH_DOMAIN_AUTHORITY_THRESHOLD = 70
MEDIUM_DOMAIN_AUTHORITY_THRESHOLD = 40
LOW_DOMAIN_AUTHORITY_THRESHOLD = 20

MIN_PAGE_SPEED_SCORE = 0
MAX_PAGE_SPEED_SCORE = 100
GOOD_PAGE_SPEED_THRESHOLD = 85
FAIR_PAGE_SPEED_THRESHOLD = 70
POOR_PAGE_SPEED_THRESHOLD = 50

# Engagement Metrics Thresholds
DEFAULT_AVG_TIME_ON_PAGE = 180  # seconds
HIGH_ENGAGEMENT_TIME_THRESHOLD = 300  # 5 minutes
LOW_ENGAGEMENT_TIME_THRESHOLD = 60  # 1 minute

DEFAULT_BOUNCE_RATE = 0.35  # 35%
HIGH_BOUNCE_RATE_THRESHOLD = 0.70  # 70%
LOW_BOUNCE_RATE_THRESHOLD = 0.30  # 30%

DEFAULT_SOCIAL_SHARES = 45
HIGH_SOCIAL_SHARES_THRESHOLD = 100
LOW_SOCIAL_SHARES_THRESHOLD = 10

# Content Analysis Constants
DEFAULT_CONTENT_COUNT = 150
HIGH_CONTENT_VOLUME_THRESHOLD = 500
MEDIUM_CONTENT_VOLUME_THRESHOLD = 200
LOW_CONTENT_VOLUME_THRESHOLD = 50

DEFAULT_AVG_WORD_COUNT = 1000
LONG_FORM_CONTENT_THRESHOLD = 2000
SHORT_FORM_CONTENT_THRESHOLD = 500

DEFAULT_KEYWORD_DENSITY = 0.025  # 2.5%
OPTIMAL_KEYWORD_DENSITY_MIN = 0.01  # 1%
OPTIMAL_KEYWORD_DENSITY_MAX = 0.05  # 5%

# Title and Meta Constants
OPTIMAL_TITLE_LENGTH = 55
MAX_TITLE_LENGTH = 60
MIN_TITLE_LENGTH = 30

OPTIMAL_META_DESCRIPTION_LENGTH = 155
MAX_META_DESCRIPTION_LENGTH = 160
MIN_META_DESCRIPTION_LENGTH = 120

# SEO Analysis Constants
DEFAULT_READABILITY_SCORE = 75
HIGH_READABILITY_THRESHOLD = 80
MEDIUM_READABILITY_THRESHOLD = 60
LOW_READABILITY_THRESHOLD = 40

DEFAULT_CONTENT_QUALITY_SCORE = 82
HIGH_CONTENT_QUALITY_THRESHOLD = 85
MEDIUM_CONTENT_QUALITY_THRESHOLD = 70
LOW_CONTENT_QUALITY_THRESHOLD = 50

# Market Analysis Constants
DEFAULT_MARKET_SHARE = 0.0  # 0%
HIGH_MARKET_SHARE_THRESHOLD = 30.0  # 30%
MEDIUM_MARKET_SHARE_THRESHOLD = 10.0  # 10%
LOW_MARKET_SHARE_THRESHOLD = 5.0  # 5%

DEFAULT_GROWTH_RATE = 0.0  # 0%
HIGH_GROWTH_RATE_THRESHOLD = 20.0  # 20%
MEDIUM_GROWTH_RATE_THRESHOLD = 10.0  # 10%
LOW_GROWTH_RATE_THRESHOLD = 5.0  # 5%

# Content Gap Analysis Constants
DEFAULT_IMPLEMENTATION_TIME_SHORT = "1-3 months"
DEFAULT_IMPLEMENTATION_TIME_MEDIUM = "3-6 months"
DEFAULT_IMPLEMENTATION_TIME_LONG = "6-12 months"

HIGH_PRIORITY_THRESHOLD = 8.0
MEDIUM_PRIORITY_THRESHOLD = 5.0
LOW_PRIORITY_THRESHOLD = 3.0

# Opportunity Scoring
MAX_OPPORTUNITY_SCORE = 10.0
HIGH_OPPORTUNITY_THRESHOLD = 8.0
MEDIUM_OPPORTUNITY_THRESHOLD = 6.0
LOW_OPPORTUNITY_THRESHOLD = 4.0

# AI Processing Constants
DEFAULT_AI_CONFIDENCE_SCORE = 0.8
MIN_AI_CONFIDENCE_SCORE = 0.5
MAX_AI_CONFIDENCE_SCORE = 1.0

AI_RETRY_ATTEMPTS = 3
AI_TIMEOUT_SECONDS = 30
AI_MAX_TOKENS = 4000

# Performance Constants
DEFAULT_PROCESSING_TIMEOUT = 300  # 5 minutes
BATCH_PROCESSING_SIZE = 5
CONCURRENT_ANALYSIS_LIMIT = 3

# Caching Constants
DEFAULT_CACHE_TTL = 3600  # 1 hour
SHORT_CACHE_TTL = 1800  # 30 minutes
LONG_CACHE_TTL = 7200  # 2 hours

# Monitoring and Health Check Constants
HEALTH_CHECK_TIMEOUT = 10
MAX_RESPONSE_TIME_THRESHOLD = 5000  # milliseconds
ERROR_RATE_THRESHOLD = 0.05  # 5%

# Content Format Suggestions
FORMAT_SUGGESTIONS = {
    'article': [
        'Create in-depth articles with comprehensive coverage',
        'Include expert quotes and statistics',
        'Add visual elements and infographics'
    ],
    'blog_post': [
        'Write engaging blog posts with personal insights',
        'Include call-to-actions',
        'Add social sharing buttons'
    ],
    'how_to': [
        'Create step-by-step guides',
        'Include screenshots or videos',
        'Add troubleshooting sections'
    ],
    'case_study': [
        'Present real-world examples',
        'Include metrics and results',
        'Add client testimonials'
    ],
    'video': [
        'Create engaging video content',
        'Include transcripts and captions',
        'Optimize for different platforms'
    ],
    'infographic': [
        'Design visually appealing graphics',
        'Include key statistics and data',
        'Make it shareable on social media'
    ],
    'whitepaper': [
        'Conduct comprehensive research',
        'Include data-driven insights',
        'Add executive summary'
    ],
    'ebook': [
        'Create comprehensive guides',
        'Include interactive elements',
        'Add downloadable resources'
    ],
    'webinar': [
        'Plan interactive sessions',
        'Include Q&A segments',
        'Provide recording access'
    ],
    'podcast': [
        'Create engaging audio content',
        'Include expert interviews',
        'Add show notes and transcripts'
    ]
}

DEFAULT_FORMAT_SUGGESTIONS = [
    'Research successful examples',
    'Analyze competitor implementation',
    'Create unique value proposition'
]

# Content Types
CONTENT_TYPES = [
    'blog', 'article', 'case_study', 'whitepaper', 'ebook',
    'video', 'podcast', 'webinar', 'infographic', 'checklist',
    'template', 'tool', 'calculator', 'quiz', 'survey',
    'research_report', 'press_release'
]

# Publishing Frequencies
PUBLISHING_FREQUENCIES = [
    'daily', 'weekly', 'bi_weekly', 'monthly',
    'quarterly', 'irregular'
]

DEFAULT_PUBLISHING_FREQUENCY = 'weekly'

# Gap Types
CONTENT_GAP_TYPES = [
    'topic_gap', 'format_gap', 'quality_gap', 'frequency_gap',
    'audience_gap', 'keyword_gap', 'intent_gap', 'timeliness_gap'
]

# SEO Gap Types
SEO_GAP_TYPES = [
    'keyword_gap', 'technical_seo_gap', 'content_seo_gap',
    'backlink_gap', 'local_seo_gap', 'mobile_seo_gap',
    'speed_gap', 'structured_data_gap'
]

# Competitor Types
COMPETITOR_TYPES = [
    'direct', 'indirect', 'substitute', 'potential'
]

# Market Positions
MARKET_POSITIONS = [
    'leader', 'challenger', 'follower', 'niche', 'emerging'
]

# Priority Levels
PRIORITY_LEVELS = ['low', 'medium', 'high', 'urgent']

# Impact Levels
IMPACT_LEVELS = ['low', 'medium', 'high', 'very_high']

# Opportunity Levels
OPPORTUNITY_LEVELS = ['low', 'medium', 'high', 'critical']

# Analysis Status
ANALYSIS_STATUS = ['pending', 'in_progress', 'completed', 'failed', 'cancelled']

# Default Values for Simulated Data
DEFAULT_COMPETITOR_ANALYSIS = {
    'content_count': DEFAULT_CONTENT_COUNT,
    'avg_quality_score': DEFAULT_QUALITY_SCORE,
    'top_keywords': ['AI', 'ML', 'Data Science'],
    'content_types': ['blog', 'case_study', 'whitepaper'],
    'publishing_frequency': DEFAULT_PUBLISHING_FREQUENCY,
    'engagement_metrics': {
        'avg_time_on_page': DEFAULT_AVG_TIME_ON_PAGE,
        'bounce_rate': DEFAULT_BOUNCE_RATE,
        'social_shares': DEFAULT_SOCIAL_SHARES
    },
    'seo_metrics': {
        'domain_authority': HIGH_DOMAIN_AUTHORITY_THRESHOLD,
        'page_speed': GOOD_PAGE_SPEED_THRESHOLD,
        'mobile_friendly': True
    }
}

# Default Market Position Fallback
DEFAULT_MARKET_POSITION = {
    'market_leader': 'competitor1.com',
    'content_leader': 'competitor2.com',
    'quality_leader': 'competitor3.com',
    'market_gaps': [
        'Video content',
        'Interactive content',
        'Expert insights'
    ],
    'opportunities': [
        'Educational content',
        'Interactive tools',
        'Thought leadership'
    ],
    'competitive_advantages': [
        'Established authority',
        'Comprehensive coverage',
        'Regular updates'
    ],
    'strategic_recommendations': [
        {
            'type': 'content_strategy',
            'recommendation': 'Focus on video content',
            'priority': 'high',
            'estimated_impact': 'High engagement'
        }
    ]
}

# Default Content Gaps
DEFAULT_CONTENT_GAPS = [
    {
        'gap_type': 'video_content',
        'description': 'Limited video tutorials and demonstrations',
        'opportunity_level': 'high',
        'estimated_impact': 'High engagement potential',
        'content_suggestions': ['Video tutorials', 'Product demos', 'Expert interviews'],
        'priority': 'high',
        'implementation_time': DEFAULT_IMPLEMENTATION_TIME_MEDIUM
    },
    {
        'gap_type': 'interactive_content',
        'description': 'Limited interactive tools and calculators',
        'opportunity_level': 'medium',
        'estimated_impact': 'Lead generation and engagement',
        'content_suggestions': ['Interactive calculators', 'Assessment tools', 'Quizzes'],
        'priority': 'medium',
        'implementation_time': DEFAULT_IMPLEMENTATION_TIME_SHORT
    },
    {
        'gap_type': 'expert_insights',
        'description': 'Limited expert interviews and insights',
        'opportunity_level': 'high',
        'estimated_impact': 'Authority building',
        'content_suggestions': ['Expert interviews', 'Industry insights', 'Thought leadership'],
        'priority': 'high',
        'implementation_time': DEFAULT_IMPLEMENTATION_TIME_SHORT
    }
]

# Default Competitive Insights
DEFAULT_COMPETITIVE_INSIGHTS = [
    {
        'insight_type': 'content_gap',
        'insight': 'Competitors lack comprehensive video content',
        'opportunity': 'Create video tutorials and demos',
        'priority': 'high',
        'estimated_impact': 'High engagement',
        'implementation_suggestion': 'Start with product demonstration videos'
    },
    {
        'insight_type': 'quality_opportunity',
        'insight': 'Content quality varies significantly across competitors',
        'opportunity': 'Establish quality leadership',
        'priority': 'medium',
        'estimated_impact': 'Medium authority building',
        'implementation_suggestion': 'Implement content quality standards'
    }
]

# Performance Metrics Defaults
DEFAULT_PERFORMANCE_METRICS = {
    'average_engagement_rate': 0.045,  # 4.5%
    'content_frequency': '2.3 posts/week',
    'top_performing_content_types': ['How-to guides', 'Case studies', 'Industry insights'],
    'content_quality_score': DEFAULT_CONTENT_QUALITY_SCORE
}

# SEO Analysis Defaults
DEFAULT_SEO_ANALYSIS = {
    'onpage_seo': {
        'meta_tags': {
            'title': {'status': 'good', 'length': OPTIMAL_TITLE_LENGTH, 'keyword_density': 0.02},
            'description': {'status': 'good', 'length': OPTIMAL_META_DESCRIPTION_LENGTH, 'keyword_density': 0.015},
            'keywords': {'status': 'missing', 'recommendation': 'Add meta keywords'}
        },
        'content': {
            'readability_score': DEFAULT_READABILITY_SCORE,
            'content_quality_score': DEFAULT_CONTENT_QUALITY_SCORE,
            'keyword_density': DEFAULT_KEYWORD_DENSITY,
            'heading_structure': 'good'
        }
    },
    'technical_seo': {
        'page_speed': GOOD_PAGE_SPEED_THRESHOLD,
        'mobile_friendly': True,
        'ssl_certificate': True,
        'structured_data': 'implemented'
    }
}

# Title Analysis Defaults
DEFAULT_TITLE_PATTERNS = {
    'question_format': 0.3,
    'how_to_format': 0.25,
    'list_format': 0.2,
    'comparison_format': 0.15,
    'other_format': 0.1
}

TITLE_SUGGESTIONS = [
    'Use question-based titles for engagement',
    'Include numbers for better CTR',
    'Add emotional triggers',
    'Keep titles under 60 characters',
    'Include target keywords naturally'
]

# Content Structure Analysis Defaults
DEFAULT_STRUCTURE_ANALYSIS = {
    'title_patterns': {
        'avg_length': OPTIMAL_TITLE_LENGTH,
        'keyword_density': 0.15,
        'brand_mention': True
    },
    'meta_description_patterns': {
        'avg_length': OPTIMAL_META_DESCRIPTION_LENGTH,
        'call_to_action': True,
        'keyword_inclusion': 0.8
    },
    'content_hierarchy': {
        'h1_usage': 95,  # percentage
        'h2_usage': 85,
        'h3_usage': 70,
        'proper_hierarchy': True
    }
}

# Analysis Summary Defaults
DEFAULT_ANALYSIS_SUMMARY = {
    'competitors_analyzed': 5,
    'content_gaps_identified': 8,
    'competitive_insights': 6,
    'market_position': 'Competitive',
    'estimated_impact': 'High'
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_url': 'Invalid competitor URL provided',
    'analysis_failed': 'Competitor analysis failed',
    'ai_service_error': 'AI service temporarily unavailable',
    'timeout_error': 'Analysis timeout exceeded',
    'rate_limit_error': 'Rate limit exceeded, please try again later',
    'invalid_industry': 'Invalid industry category provided',
    'empty_competitor_list': 'No competitor URLs provided',
    'network_error': 'Network connectivity issue',
    'parsing_error': 'Error parsing competitor data',
    'validation_error': 'Data validation failed'
}

# Success Messages
SUCCESS_MESSAGES = {
    'analysis_completed': 'Competitor analysis completed successfully',
    'market_position_analyzed': 'Market position analysis completed',
    'content_gaps_identified': 'Content gaps identified successfully',
    'insights_generated': 'Competitive insights generated successfully',
    'seo_analysis_completed': 'SEO analysis completed successfully',
    'structure_analyzed': 'Content structure analysis completed',
    'performance_analyzed': 'Content performance analysis completed'
}

# Log Messages
LOG_MESSAGES = {
    'analysis_started': 'Starting competitor analysis for {count} competitors in {industry} industry',
    'analysis_completed': 'Competitor analysis completed for {count} competitors',
    'single_competitor_analysis': 'Analyzing competitor: {url}',
    'market_position_analysis': 'Evaluating market position using AI',
    'content_gap_identification': 'Identifying content gaps using AI',
    'competitive_insights_generation': 'Generating competitive insights using AI',
    'health_check_performed': 'Performing health check for CompetitorAnalyzer',
    'seo_analysis_running': 'Running comprehensive SEO analysis on {url}',
    'title_patterns_analysis': 'Analyzing title patterns using AI',
    'competitor_comparison': 'Comparing results across all competitors'
}
