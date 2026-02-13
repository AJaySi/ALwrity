# Research Templates Library

Comprehensive collection of pre-built research templates for ALwrity Researcher, covering industry-specific research patterns, content creation workflows, and business intelligence scenarios.

## Overview

Research templates provide structured frameworks for common research scenarios, ensuring consistent quality and comprehensive coverage. Each template includes predefined research parameters, data sources, and output formats optimized for specific use cases.

## Template Categories

### Content Creation Templates

#### Blog Post Research Template

Comprehensive research framework for blog content creation.

**Template ID:** `blog_post_comprehensive`

**Use Case:** Research for in-depth blog posts (1500+ words)

**Research Parameters:**
```json
{
  "research_scope": {
    "depth": "comprehensive",
    "sources_minimum": 15,
    "fact_checking": true,
    "statistical_validation": true
  },
  "content_structure": {
    "sections": ["introduction", "background", "analysis", "case_studies", "conclusion"],
    "word_count_target": 2000,
    "citations_required": true
  },
  "audience_analysis": {
    "expertise_level": "intermediate",
    "pain_points": true,
    "knowledge_gaps": true
  }
}
```

**Data Sources Priority:**
1. **Primary Sources**: Academic papers, industry reports, expert interviews
2. **Secondary Sources**: News articles, blog posts, social media analysis
3. **Statistical Data**: Government databases, industry associations, surveys

**Output Format:**
```json
{
  "executive_summary": "Key findings and implications",
  "research_findings": [
    {"topic": "Market Size", "data": "...", "sources": ["..."]},
    {"topic": "Trends", "data": "...", "sources": ["..."]}
  ],
  "content_outline": {
    "introduction_hook": "...",
    "main_sections": ["...", "..."],
    "key_takeaways": ["...", "..."]
  },
  "sources_cited": ["...", "..."],
  "seo_optimization": {
    "primary_keywords": ["...", "..."],
    "secondary_keywords": ["...", "..."],
    "search_intent": "..."
  }
}
```

#### Social Media Content Research

Template for researching social media campaigns and content series.

**Template ID:** `social_media_campaign`

**Use Case:** Research for multi-post social media campaigns

**Research Parameters:**
```json
{
  "campaign_scope": {
    "platforms": ["instagram", "linkedin", "twitter"],
    "duration_weeks": 4,
    "posts_per_platform": 12
  },
  "content_strategy": {
    "pillars": ["education", "entertainment", "engagement"],
    "content_mix": {"educational": 40, "promotional": 30, "engagement": 30},
    "hashtag_research": true
  },
  "audience_insights": {
    "demographics": true,
    "behavior_patterns": true,
    "content_preferences": true
  }
}
```

### Business Intelligence Templates

#### Market Research Template

Comprehensive market analysis and competitive intelligence.

**Template ID:** `market_research_enterprise`

**Use Case:** Enterprise-level market research and competitive analysis

**Research Parameters:**
```json
{
  "market_analysis": {
    "tam_sam_som": true,
    "growth_forecasts": true,
    "segmentation_analysis": true,
    "regional_breakdown": true
  },
  "competitive_intelligence": {
    "competitor_mapping": true,
    "swot_analysis": true,
    "pricing_strategy": true,
    "market_positioning": true
  },
  "customer_insights": {
    "buyer_personas": true,
    "purchase_behavior": true,
    "pain_points_solutions": true,
    "loyalty_factors": true
  }
}
```

**Data Sources:**
- **Market Data**: Statista, Gartner, Forrester, IBISWorld
- **Financial Reports**: SEC filings, annual reports, investor presentations
- **Industry Analysis**: McKinsey, BCG, Deloitte reports
- **Customer Data**: Surveys, reviews, social media sentiment

#### Competitor Analysis Template

Detailed competitor research and strategic positioning.

**Template ID:** `competitor_intelligence_deep`

**Use Case:** Comprehensive competitor analysis for strategic planning

**Research Parameters:**
```json
{
  "competitor_profile": {
    "company_overview": true,
    "leadership_team": true,
    "funding_history": true,
    "product_portfolio": true
  },
  "market_positioning": {
    "target_segments": true,
    "pricing_strategy": true,
    "differentiation_factors": true,
    "brand_perception": true
  },
  "strategic_analysis": {
    "growth_strategy": true,
    "partnerships_alliances": true,
    "expansion_plans": true,
    "potential_threats": true
  }
}
```

### Industry-Specific Templates

#### Technology Sector Research

Specialized template for tech industry research and analysis.

**Template ID:** `technology_sector_analysis`

**Research Focus Areas:**
- **Emerging Technologies**: AI, blockchain, IoT, quantum computing
- **Market Trends**: Adoption rates, investment patterns, regulatory changes
- **Competitive Landscape**: Startup ecosystem, M&A activity, patent analysis
- **Talent Market**: Skills demand, salary trends, remote work impact

#### Healthcare Industry Research

Comprehensive healthcare sector analysis template.

**Template ID:** `healthcare_market_research`

**Research Parameters:**
```json
{
  "regulatory_landscape": {
    "fda_approvals": true,
    "compliance_requirements": true,
    "reimbursement_policies": true,
    "international_standards": true
  },
  "clinical_research": {
    "trial_data": true,
    "treatment_efficacy": true,
    "patient_outcomes": true,
    "adverse_events": true
  },
  "market_dynamics": {
    "payer_landscape": true,
    "provider_consolidation": true,
    "telemedicine_trends": true,
    "digital_health_innovation": true
  }
}
```

#### SaaS Product Research Template

Template for Software-as-a-Service product research and market analysis.

**Template ID:** `saas_product_research`

**Research Framework:**
- **Product-Market Fit**: Target user analysis, use case validation
- **Pricing Strategy**: Competitive pricing, monetization models
- **Feature Analysis**: Must-have vs. nice-to-have features
- **Adoption Barriers**: Technical, organizational, financial factors

### Academic & Research Templates

#### Literature Review Template

Systematic literature review research framework.

**Template ID:** `literature_review_systematic`

**Research Methodology:**
```json
{
  "search_strategy": {
    "databases": ["PubMed", "IEEE Xplore", "Google Scholar", "JSTOR"],
    "inclusion_criteria": {
      "date_range": "2018-present",
      "study_types": ["randomized_trials", "meta_analysis", "systematic_reviews"],
      "language": "english"
    },
    "exclusion_criteria": {
      "study_quality": "low_quality_studies",
      "relevance": "off_topic_papers"
    }
  },
  "data_extraction": {
    "fields": ["study_design", "sample_size", "intervention", "outcomes", "limitations"],
    "quality_assessment": "cochrane_risk_of_bias",
    "synthesis_method": "narrative_synthesis"
  }
}
```

#### Meta-Analysis Research Template

Statistical meta-analysis research framework.

**Template ID:** `meta_analysis_statistical`

**Research Parameters:**
- **Effect Size Calculation**: Standardized mean differences, odds ratios
- **Heterogeneity Assessment**: I² statistic, Q-test, subgroup analysis
- **Publication Bias**: Funnel plots, Egger's test, trim-and-fill
- **Sensitivity Analysis**: One-study removal, influence diagnostics

### Custom Template Builder

#### Template Creation Framework

Build custom research templates using the ALwrity Researcher API.

```javascript
// Create custom research template
const customTemplate = {
  id: "custom_business_intelligence",
  name: "Custom Business Intelligence Research",
  description: "Tailored research template for specific business needs",

  research_parameters: {
    scope: {
      depth: "custom",
      sources: ["industry_reports", "financial_data", "social_media"],
      time_horizon: "12_months"
    },
    focus_areas: [
      "market_trends",
      "competitor_actions",
      "customer_sentiment",
      "regulatory_changes"
    ]
  },

  output_format: {
    structure: ["executive_summary", "detailed_findings", "recommendations"],
    visualizations: ["charts", "graphs", "heatmaps"],
    export_formats: ["pdf", "pptx", "xlsx"]
  }
};

await researcher.templates.create(customTemplate);
```

## Template Usage Examples

### Using Pre-built Templates

```javascript
// Research a new market opportunity
const marketResearch = await researcher.templates.use('market_research_enterprise', {
  topic: "AI-powered customer service solutions",
  industry: "technology",
  geography: "north_america",
  timeframe: "2024"
});

// Generate comprehensive research report
const report = await marketResearch.generateReport({
  format: "detailed",
  include_sources: true,
  executive_summary: true
});
```

### Template Customization

```javascript
// Customize existing template
const customizedTemplate = await researcher.templates.customize('blog_post_comprehensive', {
  modifications: {
    add_sections: ["expert_interviews", "reader_poll"],
    modify_sources: {
      add: ["industry_podcasts", "video_content"],
      remove: ["academic_papers"]
    },
    output_format: {
      include_visualizations: true,
      citation_style: "APA"
    }
  }
});
```

### Template Performance Analytics

```javascript
// Analyze template effectiveness
const analytics = await researcher.templates.analytics('blog_post_comprehensive', {
  timeframe: "last_30_days",
  metrics: ["completion_rate", "quality_score", "user_satisfaction"]
});

console.log(`Template success rate: ${analytics.completion_rate}%`);
console.log(`Average quality score: ${analytics.quality_score}/10`);
```

## Template Management

### Template Library Access

```javascript
// List available templates
const templates = await researcher.templates.list({
  category: "content_creation",
  industry: "technology",
  sort_by: "popularity"
});

// Get template details
const templateDetails = await researcher.templates.get('blog_post_comprehensive');

// Search templates
const searchResults = await researcher.templates.search({
  query: "market research",
  tags: ["enterprise", "comprehensive"],
  min_rating: 4.5
});
```

### Template Ratings & Reviews

```javascript
// Rate a template
await researcher.templates.rate('blog_post_comprehensive', {
  rating: 5,
  review: "Excellent for in-depth blog research. Comprehensive coverage.",
  use_case: "Technology blog posts"
});

// Get template reviews
const reviews = await researcher.templates.reviews('blog_post_comprehensive', {
  limit: 10,
  sort_by: "helpful"
});
```

## Advanced Template Features

### Conditional Logic Templates

Templates that adapt based on research findings.

```json
{
  "template_id": "adaptive_market_research",
  "conditional_logic": {
    "if_market_growing": {
      "condition": "market_growth_rate > 15%",
      "additional_research": ["competitor_entry_barriers", "investment_opportunities"],
      "output_sections": ["growth_drivers", "investment_thesis"]
    },
    "if_market_declining": {
      "condition": "market_growth_rate < 0%",
      "additional_research": ["exit_strategies", "pivot_opportunities"],
      "output_sections": ["decline_causes", "survival_strategies"]
    }
  }
}
```

### Multi-Language Research Templates

Templates supporting research across multiple languages.

```json
{
  "template_id": "multilingual_market_research",
  "language_support": {
    "primary_languages": ["en", "es", "fr", "de"],
    "translation_services": true,
    "cultural_adaptation": true,
    "regional_sources": true
  },
  "output_options": {
    "unified_report": true,
    "language_specific_sections": true,
    "cultural_insights": true
  }
}
```

### Collaborative Research Templates

Templates designed for team research workflows.

```json
{
  "template_id": "collaborative_research_project",
  "collaboration_features": {
    "role_assignment": {
      "research_lead": "topic_selection,data_collection",
      "analyst": "data_analysis,insights_generation",
      "reviewer": "quality_assurance,fact_checking"
    },
    "workflow_stages": [
      "planning", "research", "analysis", "review", "finalization"
    ],
    "approval_gates": {
      "peer_review_required": true,
      "manager_approval": true
    }
  }
}
```

## Template Performance Optimization

### Quality Metrics

Templates are continuously optimized based on performance data:

- **Completion Rate**: Percentage of research projects completed successfully
- **Quality Score**: Average quality rating from users
- **Time Efficiency**: Average time to complete research using template
- **User Satisfaction**: Net Promoter Score and detailed feedback

### A/B Testing Framework

Templates undergo continuous optimization through A/B testing:

```javascript
// A/B test template variations
const testResults = await researcher.templates.abTest({
  template_id: "blog_post_comprehensive",
  variations: {
    "v1": { sources_minimum: 15, depth: "comprehensive" },
    "v2": { sources_minimum: 20, depth: "comprehensive" }
  },
  test_duration: 30,
  success_metric: "quality_score",
  sample_size: 100
});
```

## Integration & Automation

### API Integration

Templates can be integrated into existing workflows:

```javascript
// Integrate with content management system
const cmsIntegration = {
  trigger: "new_content_request",
  template_selection: "automatic",
  parameters: {
    content_type: "blog_post",
    topic: "from_cms",
    audience: "from_cms_user_data"
  },
  output_destination: "cms_draft_folder"
};

await researcher.templates.integrate(cmsIntegration);
```

### Webhook Integration

Receive notifications when template-based research is complete:

```javascript
// Setup webhook for research completion
await researcher.webhooks.create({
  event: "template_research_completed",
  template_id: "market_research_enterprise",
  url: "https://your-app.com/webhooks/research-complete",
  secret: "your-webhook-secret"
});
```

## Best Practices

### Template Selection

1. **Match Complexity**: Choose template complexity appropriate for research scope
2. **Industry Alignment**: Use industry-specific templates for better results
3. **Customization**: Modify templates to fit specific research needs
4. **Quality Verification**: Review template outputs for accuracy and completeness

### Template Optimization

1. **Regular Updates**: Keep templates current with latest research methodologies
2. **User Feedback**: Incorporate user feedback to improve template effectiveness
3. **Performance Monitoring**: Track template performance and optimize accordingly
4. **Version Control**: Maintain version history for template improvements

### Team Collaboration

1. **Shared Templates**: Create organization-wide templates for consistency
2. **Access Control**: Manage template access based on user roles
3. **Usage Analytics**: Track template usage patterns and effectiveness
4. **Knowledge Sharing**: Share successful template customizations across teams

---

[:octicons-arrow-right-24: Back to Overview](overview.md)