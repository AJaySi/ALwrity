# Intent Research API Reference

**Date**: 2025-01-29  
**Status**: Current API Documentation

---

## 📋 Overview

This document provides comprehensive API reference for intent-driven research endpoints. All endpoints require authentication via `get_current_user` dependency.

**Base Path**: `/api/research`

---

## 🔐 Authentication

All endpoints require authentication. The `user_id` is extracted from the JWT token via `get_current_user` dependency.

**Error Response** (401):
```json
{
  "detail": "Authentication required"
}
```

---

## 📡 Endpoints

### 1. POST `/api/research/intent/analyze`

Analyzes user input to understand research intent, generates targeted queries, and optimizes provider parameters.

#### Request

**Endpoint**: `POST /api/research/intent/analyze`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**:
```typescript
{
  user_input: string;              // Required: User's keywords, question, or goal
  keywords?: string[];              // Optional: Extracted keywords
  use_persona?: boolean;            // Optional: Use research persona (default: true)
  use_competitor_data?: boolean;    // Optional: Use competitor data (default: true)
}
```

**Example**:
```json
{
  "user_input": "AI marketing tools for small businesses",
  "keywords": ["AI", "marketing", "tools", "small", "businesses"],
  "use_persona": true,
  "use_competitor_data": true
}
```

#### Response

**Success** (200):
```typescript
{
  success: boolean;                 // Always true on success
  intent: {
    input_type: "keywords" | "question" | "goal" | "mixed";
    primary_question: string;
    secondary_questions: string[];
    purpose: "learn" | "create_content" | "make_decision" | "compare" | 
             "solve_problem" | "find_data" | "explore_trends" | 
             "validate" | "generate_ideas";
    content_output: "blog" | "podcast" | "video" | "social_post" | 
                   "newsletter" | "presentation" | "report" | 
                   "whitepaper" | "email" | "general";
    expected_deliverables: string[];  // e.g., ["key_statistics", "expert_quotes", "case_studies"]
    depth: "overview" | "detailed" | "expert";
    focus_areas: string[];
    perspective?: string;
    time_sensitivity: "real_time" | "recent" | "historical" | "evergreen";
    confidence: number;             // 0.0 - 1.0
    confidence_reason?: string;
    great_example?: string;
    needs_clarification: boolean;
    clarifying_questions: string[];
    analysis_summary: string;
  };
  analysis_summary: string;
  suggested_queries: Array<{
    query: string;
    purpose: string;               // Expected deliverable type
    provider: "exa" | "tavily";
    priority: number;              // 1-5 (5 = highest)
    expected_results: string;
    justification?: string;
  }>;
  suggested_keywords: string[];
  suggested_angles: string[];
  quick_options: Array<any>;        // Deprecated in unified approach
  confidence_reason?: string;
  great_example?: string;
  optimized_config: {
    provider: "exa" | "tavily" | "google";
    provider_justification: string;
    
    // Exa Settings
    exa_type: "auto" | "neural" | "fast" | "deep";
    exa_type_justification: string;
    exa_category?: "company" | "research paper" | "news" | "github" | 
                   "tweet" | "personal site" | "pdf" | "financial report" | "people";
    exa_category_justification?: string;
    exa_include_domains?: string[];
    exa_include_domains_justification?: string;
    exa_num_results: number;
    exa_num_results_justification: string;
    exa_date_filter?: string;      // ISO date string
    exa_date_justification?: string;
    exa_highlights: boolean;
    exa_highlights_justification: string;
    exa_context: boolean;
    exa_context_justification: string;
    
    // Tavily Settings
    tavily_topic: "general" | "news" | "finance";
    tavily_topic_justification: string;
    tavily_search_depth: "basic" | "advanced";
    tavily_search_depth_justification: string;
    tavily_include_answer: boolean | "basic" | "advanced";
    tavily_include_answer_justification: string;
    tavily_time_range?: "day" | "week" | "month" | "year";
    tavily_time_range_justification?: string;
    tavily_max_results: number;
    tavily_max_results_justification: string;
    tavily_raw_content: "false" | "true" | "markdown" | "text";
    tavily_raw_content_justification: string;
  };
  recommended_provider: "exa" | "tavily" | "google";
  error_message?: string;          // Only present on error
}
```

**Error** (500):
```json
{
  "success": false,
  "intent": {},
  "analysis_summary": "",
  "suggested_queries": [],
  "suggested_keywords": [],
  "suggested_angles": [],
  "quick_options": [],
  "confidence_reason": null,
  "great_example": null,
  "error_message": "Error message here"
}
```

#### Example Response

```json
{
  "success": true,
  "intent": {
    "input_type": "keywords",
    "primary_question": "What are the best AI marketing tools for small businesses?",
    "secondary_questions": [
      "What features do small businesses need in AI marketing tools?",
      "What is the ROI of AI marketing tools for small businesses?"
    ],
    "purpose": "make_decision",
    "content_output": "blog",
    "expected_deliverables": ["key_statistics", "case_studies", "comparisons", "best_practices"],
    "depth": "detailed",
    "focus_areas": ["small business", "AI automation", "marketing efficiency"],
    "time_sensitivity": "recent",
    "confidence": 0.85,
    "confidence_reason": "Clear intent to find tools for decision-making",
    "needs_clarification": false,
    "clarifying_questions": [],
    "analysis_summary": "User wants to research AI marketing tools specifically for small businesses, likely to make a purchasing decision. Needs comparisons, statistics, and case studies."
  },
  "analysis_summary": "User wants to research AI marketing tools specifically for small businesses...",
  "suggested_queries": [
    {
      "query": "best AI marketing tools small business 2024 comparison",
      "purpose": "comparisons",
      "provider": "exa",
      "priority": 5,
      "expected_results": "Tool comparison articles and reviews",
      "justification": "High priority for decision-making"
    },
    {
      "query": "AI marketing tools ROI statistics small business",
      "purpose": "key_statistics",
      "provider": "exa",
      "priority": 4,
      "expected_results": "Statistics on AI tool adoption and ROI",
      "justification": "Important for decision-making"
    }
  ],
  "suggested_keywords": ["AI marketing", "automation", "small business", "SMB tools"],
  "suggested_angles": [
    "Compare top AI marketing tools for small businesses",
    "ROI analysis of AI marketing automation",
    "Case studies: Small businesses using AI marketing tools"
  ],
  "optimized_config": {
    "provider": "exa",
    "provider_justification": "Exa's semantic search is best for finding tool comparisons and detailed analysis",
    "exa_type": "neural",
    "exa_type_justification": "Neural search provides better semantic understanding for tool comparisons",
    "exa_category": "company",
    "exa_category_justification": "Focus on company/product pages for tool information",
    "exa_num_results": 10,
    "exa_num_results_justification": "10 results provide comprehensive coverage without overwhelming",
    "exa_highlights": true,
    "exa_highlights_justification": "Highlights help extract key features and comparisons",
    "exa_context": true,
    "exa_context_justification": "Context string enables better AI analysis of results"
  },
  "recommended_provider": "exa"
}
```

#### Implementation Details

**Backend Flow**:
1. Validates authentication
2. Fetches research persona (if `use_persona: true`)
3. Fetches competitor data (if `use_competitor_data: true`)
4. Calls `UnifiedResearchAnalyzer.analyze()`
5. Returns structured response

**Performance**: Typically 2-5 seconds (single LLM call)

---

### 2. POST `/api/research/intent/research`

Executes research based on confirmed intent and returns structured deliverables.

#### Request

**Endpoint**: `POST /api/research/intent/research`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**:
```typescript
{
  user_input: string;                    // Required: Original user input
  confirmed_intent?: ResearchIntent;      // Optional: Confirmed intent from UI
  selected_queries?: ResearchQuery[];      // Optional: Selected queries to execute
  max_sources?: number;                   // Optional: Max sources (default: 10, min: 1, max: 25)
  include_domains?: string[];            // Optional: Domains to include
  exclude_domains?: string[];            // Optional: Domains to exclude
  skip_inference?: boolean;              // Optional: Skip intent inference if intent provided (default: false)
}
```

**Example**:
```json
{
  "user_input": "AI marketing tools for small businesses",
  "confirmed_intent": {
    "primary_question": "What are the best AI marketing tools for small businesses?",
    "purpose": "make_decision",
    "expected_deliverables": ["key_statistics", "case_studies", "comparisons"],
    "depth": "detailed"
  },
  "selected_queries": [
    {
      "query": "best AI marketing tools small business 2024 comparison",
      "purpose": "comparisons",
      "provider": "exa",
      "priority": 5
    }
  ],
  "max_sources": 10,
  "include_domains": [],
  "exclude_domains": []
}
```

#### Response

**Success** (200):
```typescript
{
  success: boolean;
  
  // Direct Answers
  primary_answer: string;
  secondary_answers: Dict<string, string>;
  
  // Deliverables
  statistics: Array<{
    value: string;
    description: string;
    citation: {
      title: string;
      url: string;
      domain: string;
    };
    relevance_score: number;
  }>;
  expert_quotes: Array<{
    quote: string;
    author: string;
    author_title?: string;
    source: {
      title: string;
      url: string;
      domain: string;
    };
    relevance_score: number;
  }>;
  case_studies: Array<{
    title: string;
    summary: string;
    key_findings: string[];
    source: {
      title: string;
      url: string;
      domain: string;
    };
    relevance_score: number;
  }>;
  trends: Array<{
    trend: string;
    description: string;
    evidence: string[];
    time_frame: string;
    source: {
      title: string;
      url: string;
      domain: string;
    };
  }>;
  comparisons: Array<{
    title: string;
    items: Array<{
      name: string;
      attributes: Dict<string, string>;
    }>;
    source: {
      title: string;
      url: string;
      domain: string;
    };
  }>;
  best_practices: string[];
  step_by_step: string[];
  pros_cons?: {
    pros: string[];
    cons: string[];
    source?: {
      title: string;
      url: string;
      domain: string;
    };
  };
  definitions: Dict<string, string>;
  examples: string[];
  predictions: string[];
  
  // Content-Ready Outputs
  executive_summary: string;
  key_takeaways: string[];
  suggested_outline: string[];
  
  // Sources and Metadata
  sources: Array<{
    title: string;
    url: string;
    domain: string;
    snippet: string;
    credibility_score: number;
    relevance_score: number;
    published_date?: string;
  }>;
  confidence: number;                    // 0.0 - 1.0
  gaps_identified: string[];
  follow_up_queries: string[];
  
  // The inferred/confirmed intent
  intent?: ResearchIntent;
  
  error_message?: string;                // Only present on error
}
```

**Error** (500):
```json
{
  "success": false,
  "primary_answer": "",
  "secondary_answers": {},
  "statistics": [],
  "expert_quotes": [],
  "case_studies": [],
  "trends": [],
  "comparisons": [],
  "best_practices": [],
  "step_by_step": [],
  "pros_cons": null,
  "definitions": {},
  "examples": [],
  "predictions": [],
  "executive_summary": "",
  "key_takeaways": [],
  "suggested_outline": [],
  "sources": [],
  "confidence": 0.0,
  "gaps_identified": [],
  "follow_up_queries": [],
  "error_message": "Error message here"
}
```

#### Example Response

```json
{
  "success": true,
  "primary_answer": "The best AI marketing tools for small businesses include Mailchimp, HubSpot, and Hootsuite, offering automation, analytics, and social media management at affordable prices.",
  "secondary_answers": {
    "pricing": "Most tools range from $0-50/month for small businesses",
    "features": "Key features include email automation, social scheduling, and analytics"
  },
  "statistics": [
    {
      "value": "78%",
      "description": "of small businesses use AI marketing tools",
      "citation": {
        "title": "Small Business Marketing Trends 2024",
        "url": "https://example.com/trends",
        "domain": "example.com"
      },
      "relevance_score": 0.95
    }
  ],
  "expert_quotes": [
    {
      "quote": "AI marketing tools have become essential for small businesses to compete effectively.",
      "author": "Jane Smith",
      "author_title": "Marketing Expert",
      "source": {
        "title": "Marketing Technology Guide",
        "url": "https://example.com/guide",
        "domain": "example.com"
      },
      "relevance_score": 0.90
    }
  ],
  "case_studies": [
    {
      "title": "Small Business Increases ROI by 40% with AI Tools",
      "summary": "A local bakery used AI marketing automation to increase customer engagement and revenue.",
      "key_findings": [
        "40% increase in ROI",
        "3x email open rates",
        "50% reduction in manual work"
      ],
      "source": {
        "title": "Case Study: AI Marketing Success",
        "url": "https://example.com/case-study",
        "domain": "example.com"
      },
      "relevance_score": 0.88
    }
  ],
  "trends": [
    {
      "trend": "AI Marketing Automation Adoption",
      "description": "Small businesses are rapidly adopting AI marketing tools",
      "evidence": [
        "78% adoption rate in 2024",
        "Growing market of affordable tools"
      ],
      "time_frame": "2024",
      "source": {
        "title": "Marketing Trends Report",
        "url": "https://example.com/trends",
        "domain": "example.com"
      }
    }
  ],
  "comparisons": [
    {
      "title": "AI Marketing Tools Comparison",
      "items": [
        {
          "name": "Mailchimp",
          "attributes": {
            "price": "$0-50/month",
            "features": "Email, Automation, Analytics"
          }
        },
        {
          "name": "HubSpot",
          "attributes": {
            "price": "$0-90/month",
            "features": "CRM, Email, Social, Analytics"
          }
        }
      ],
      "source": {
        "title": "Tool Comparison Guide",
        "url": "https://example.com/comparison",
        "domain": "example.com"
      }
    }
  ],
  "best_practices": [
    "Start with free trials to test tools",
    "Focus on tools that integrate with your existing stack",
    "Prioritize automation features for time savings"
  ],
  "step_by_step": [
    "1. Identify your marketing needs",
    "2. Research available AI tools",
    "3. Compare features and pricing",
    "4. Start with free trials",
    "5. Implement gradually"
  ],
  "pros_cons": {
    "pros": [
      "Time savings through automation",
      "Better targeting and personalization",
      "Improved ROI tracking"
    ],
    "cons": [
      "Learning curve for new tools",
      "Potential costs for advanced features",
      "Dependency on technology"
    ]
  },
  "definitions": {
    "AI Marketing": "Use of artificial intelligence to automate and optimize marketing tasks",
    "Marketing Automation": "Technology that automates repetitive marketing tasks"
  },
  "examples": [
    "Mailchimp's AI-powered email subject line suggestions",
    "HubSpot's predictive lead scoring",
    "Hootsuite's optimal posting time recommendations"
  ],
  "predictions": [
    "AI marketing tools will become standard for all businesses by 2026",
    "Integration between tools will improve significantly",
    "Costs will continue to decrease as competition increases"
  ],
  "executive_summary": "AI marketing tools offer significant benefits for small businesses, including automation, better targeting, and improved ROI. Key tools include Mailchimp, HubSpot, and Hootsuite, with most offering affordable pricing for small businesses.",
  "key_takeaways": [
    "78% of small businesses use AI marketing tools",
    "Tools range from $0-50/month for small businesses",
    "Key benefits include automation and improved ROI",
    "Free trials are available for most tools"
  ],
  "suggested_outline": [
    "Introduction to AI Marketing Tools",
    "Benefits for Small Businesses",
    "Top Tools Comparison",
    "Case Studies and Success Stories",
    "Implementation Guide",
    "Conclusion and Recommendations"
  ],
  "sources": [
    {
      "title": "Small Business Marketing Trends 2024",
      "url": "https://example.com/trends",
      "domain": "example.com",
      "snippet": "78% of small businesses now use AI marketing tools...",
      "credibility_score": 0.92,
      "relevance_score": 0.95,
      "published_date": "2024-01-15"
    }
  ],
  "confidence": 0.88,
  "gaps_identified": [
    "Limited data on long-term ROI",
    "Need more case studies from specific industries"
  ],
  "follow_up_queries": [
    "What are the specific ROI metrics for AI marketing tools?",
    "How do AI marketing tools compare to traditional methods?"
  ],
  "intent": {
    "primary_question": "What are the best AI marketing tools for small businesses?",
    "purpose": "make_decision",
    "expected_deliverables": ["key_statistics", "case_studies", "comparisons"],
    "depth": "detailed"
  }
}
```

#### Implementation Details

**Backend Flow**:
1. Validates authentication
2. Determines intent (from `confirmed_intent` or infers from `user_input`)
3. Generates queries (from `selected_queries` or generates from intent)
4. Executes research via `ResearchEngine` (Exa → Tavily → Google)
5. Analyzes results via `IntentAwareAnalyzer`
6. Returns structured deliverables

**Performance**: Typically 10-30 seconds (depends on provider and query count)

---

## 🔄 Error Handling

### Common Error Responses

**401 Unauthorized**:
```json
{
  "detail": "Authentication required"
}
```

**500 Internal Server Error**:
```json
{
  "success": false,
  "error_message": "Detailed error message",
  // ... other fields with empty/default values
}
```

### Error Scenarios

1. **Invalid user_input**: Empty or too short
2. **Provider unavailable**: Exa/Tavily API keys not configured
3. **LLM failure**: AI service unavailable or rate limited
4. **Database error**: Persona/competitor data fetch failed
5. **Subscription limits**: User exceeded subscription quota

---

## 📊 Rate Limits

- **Intent Analysis**: Subject to subscription tier limits
- **Research Execution**: Subject to subscription tier limits
- **Provider APIs**: Exa/Tavily/Google have their own rate limits

---

## 🔗 Related Endpoints

- `GET /api/research/config` - Get research configuration and persona defaults
- `GET /api/research/providers/status` - Get provider availability
- `POST /api/research/execute` - Traditional synchronous research (fallback)
- `POST /api/research/start` - Traditional asynchronous research (fallback)

---

## 📚 Related Documentation

- **Intent-Driven Research Guide**: `INTENT_DRIVEN_RESEARCH_GUIDE.md`
- **Architecture Rules**: `.cursor/rules/researcher-architecture.mdc`
- **Architecture Overview**: `CURRENT_ARCHITECTURE_OVERVIEW.md`

---

**Status**: Current API Reference - Use this for integrating with intent-driven research endpoints.
