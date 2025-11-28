# Research Phase - AI Hyperpersonalization Guide

## Overview
This document outlines all research inputs, prompts, and configuration options that can be intelligently personalized using AI and user persona data. The goal is to make research effortless for beginners while maintaining full control for power users.

---

## 1. User Inputs (Current)

### 1.1 Primary Research Input
**Field**: `keywords` (textarea)  
**Current Format**: Array of strings  
**User Input Types**:
- Full sentences/paragraphs (e.g., "Research latest AI advancements in healthcare")
- Comma-separated keywords (e.g., "AI, healthcare, diagnostics")
- URLs (e.g., "https://techcrunch.com/2024/ai-trends")
- Mixed formats

**AI Personalization Opportunity**:
- Parse user intent and generate optimized search queries
- Expand keywords based on industry and audience
- Suggest related topics from persona interests
- Rewrite vague inputs into specific, actionable research queries

---

### 1.2 Industry Selection
**Field**: `industry` (dropdown)  
**Options**: General, Technology, Business, Marketing, Finance, Healthcare, Education, Real Estate, Entertainment, Food & Beverage, Travel, Fashion, Sports, Science, Law, Other

**Current Default**: "General"

**AI Personalization Opportunity**:
- Auto-detect from persona's `core_persona.industry` or `core_persona.profession`
- Suggest related industries based on research topic
- Use onboarding data: `business_info.industry`, `business_info.niche`

---

### 1.3 Target Audience
**Field**: `targetAudience` (text input)  
**Current Default**: "General"

**AI Personalization Opportunity**:
- Pull from persona's `core_persona.target_audience`
- Suggest audience based on research topic
- Use demographic data: `core_persona.demographics`, `core_persona.psychographics`

---

### 1.4 Research Mode
**Field**: `researchMode` (dropdown)  
**Options**: 
- `basic` - Quick insights (10 sources, fast)
- `comprehensive` - In-depth analysis (15-25 sources, thorough)
- `targeted` - Specific focus (12 sources, precise)

**Current Default**: "basic"

**AI Personalization Opportunity**:
- Infer from query complexity (word count, specificity)
- Match to user's persona complexity/expertise level
- Suggest based on content type (blog, whitepaper, social post)

---

### 1.5 Search Provider
**Field**: `config.provider` (dropdown)  
**Options**: 
- `google` - Google Search grounding (broad, general)
- `exa` - Exa Neural Search (semantic, deep)

**Current Default**: "google"

**AI Personalization Opportunity**:
- Academic topics → Exa (research papers)
- News/trends → Google (real-time)
- Technical deep-dive → Exa (neural semantic search)
- Match to persona's writing style (technical vs. casual)

---

## 2. Advanced Configuration (ResearchConfig)

### 2.1 Common Options (Both Providers)

#### `max_sources` (number)
- **Default**: 10 (basic), 15 (comprehensive), 12 (targeted)
- **Range**: 5-30
- **AI Suggestion**: More sources for complex topics, fewer for news updates

#### `include_statistics` (boolean)
- **Default**: true
- **AI Suggestion**: Enable for data-driven industries (Finance, Healthcare, Technology)

#### `include_expert_quotes` (boolean)
- **Default**: true
- **AI Suggestion**: Enable for thought leadership content

#### `include_competitors` (boolean)
- **Default**: true
- **AI Suggestion**: Enable for business/marketing topics

#### `include_trends` (boolean)
- **Default**: true
- **AI Suggestion**: Enable for forward-looking content

---

### 2.2 Exa-Specific Options

#### `exa_category` (string)
**Options**: 
- '' (All Categories)
- 'company' - Company Profiles
- 'research paper' - Research Papers
- 'news' - News Articles
- 'linkedin profile' - LinkedIn Profiles
- 'github' - GitHub Repos
- 'tweet' - Tweets
- 'movie', 'song', 'personal site', 'pdf', 'financial report'

**AI Personalization**:
```typescript
const aiSuggestExaCategory = (topic: string, industry: string) => {
  if (topic.includes('academic') || topic.includes('study')) return 'research paper';
  if (industry === 'Finance') return 'financial report';
  if (topic.includes('company') || topic.includes('startup')) return 'company';
  if (topic.includes('breaking') || topic.includes('latest')) return 'news';
  if (topic.includes('developer') || topic.includes('code')) return 'github';
  return '';
};
```

#### `exa_search_type` (string)
**Options**: 'auto', 'keyword', 'neural'  
**Default**: 'auto'

**AI Personalization**:
- `keyword` - For precise technical terms, product names
- `neural` - For conceptual, semantic queries
- `auto` - Let Exa decide (usually best)

#### `exa_include_domains` (string[])
**Example**: `['pubmed.gov', 'nejm.org', 'thelancet.com']`

**AI Personalization by Industry**:
```typescript
const domainSuggestions = {
  Healthcare: ['pubmed.gov', 'nejm.org', 'thelancet.com', 'nih.gov'],
  Technology: ['techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com'],
  Finance: ['wsj.com', 'bloomberg.com', 'ft.com', 'reuters.com'],
  Science: ['nature.com', 'sciencemag.org', 'cell.com', 'pnas.org'],
  Business: ['hbr.org', 'forbes.com', 'businessinsider.com', 'mckinsey.com']
};
```

#### `exa_exclude_domains` (string[])
**Example**: `['spam.com', 'ads.com']`

**AI Personalization**:
- Auto-exclude low-quality domains
- Exclude competitor domains if requested
- Exclude domains based on persona's dislikes

---

## 3. Persona Data Integration

### 3.1 Available Persona Fields (from Onboarding)

#### Core Persona
```typescript
interface CorePersona {
  // Demographics
  age_range?: string;
  gender?: string;
  location?: string;
  education_level?: string;
  income_level?: string;
  occupation?: string;
  industry?: string;
  company_size?: string;
  
  // Psychographics
  interests?: string[];
  values?: string[];
  pain_points?: string[];
  goals?: string[];
  challenges?: string[];
  
  // Behavioral
  content_preferences?: string[];
  learning_style?: string;
  decision_making_style?: string;
  preferred_platforms?: string[];
  
  // Content Context
  target_audience?: string;
  writing_tone?: string;
  expertise_level?: string;
}
```

#### Business Info (from onboarding)
```typescript
interface BusinessInfo {
  industry: string;
  niche: string;
  target_audience: string;
  content_goals: string[];
  primary_platform: string;
}
```

---

## 4. AI-Powered Suggestions (Implementation Roadmap)

### Phase 1: Rule-Based Intelligence (Current)
✅ Intelligent input parsing (sentences, keywords, URLs)  
✅ Preset templates with full configuration  
✅ Visual feedback on input type  

### Phase 2: Persona-Aware Defaults (Next)
🔄 Auto-fill industry from persona  
🔄 Auto-fill target audience from persona  
🔄 Suggest research mode based on topic complexity  
🔄 Suggest provider based on topic type  
🔄 Suggest Exa category based on industry  
🔄 Suggest domains based on industry  

### Phase 3: AI Query Enhancement (Future)
🔮 Generate optimal search queries from vague inputs  
🔮 Expand keywords semantically  
🔮 Suggest related research angles  
🔮 Predict best configuration for user's goal  

---

## 5. Backend Research Prompt Templates

### 5.1 Basic Research Prompt
```python
def build_basic_research_prompt(topic: str, industry: str, target_audience: str) -> str:
    return f"""You are a professional blog content strategist researching for a {industry} blog targeting {target_audience}.

Research Topic: "{topic}"

Provide analysis in this EXACT format:

## CURRENT TRENDS (2024-2025)
- [Trend 1 with specific data and source URL]
- [Trend 2 with specific data and source URL]
- [Trend 3 with specific data and source URL]

## KEY STATISTICS
- [Statistic 1: specific number/percentage with source URL]
- [Statistic 2: specific number/percentage with source URL]
... (5 total)

## PRIMARY KEYWORDS
1. "{topic}" (main keyword)
2. [Variation 1]
3. [Variation 2]

## SECONDARY KEYWORDS
[5 related keywords for blog content]

## CONTENT ANGLES (Top 5)
1. [Angle 1: specific unique approach]
...

REQUIREMENTS:
- Cite EVERY claim with authoritative source URLs
- Use 2024-2025 data when available
- Include specific numbers, dates, examples
- Focus on actionable blog insights for {target_audience}"""
```

### 5.2 Comprehensive Research Prompt
```python
def build_comprehensive_research_prompt(topic: str, industry: str, target_audience: str, config: ResearchConfig) -> str:
    sections = []
    
    sections.append(f"""You are an expert research analyst for {industry} content targeting {target_audience}.

Research Topic: "{topic}"

Conduct comprehensive research and provide:""")
    
    if config.include_trends:
        sections.append("""
## TREND ANALYSIS
- Emerging trends (2024-2025) with adoption rates
- Historical context and evolution
- Future projections from industry experts""")
    
    if config.include_statistics:
        sections.append("""
## DATA & STATISTICS
- Market size, growth rates, key metrics
- Demographic data and user behavior
- Comparative statistics across segments
(Minimum 10 statistics with sources)""")
    
    if config.include_expert_quotes:
        sections.append("""
## EXPERT INSIGHTS
- Quotes from industry leaders with credentials
- Research findings from institutions
- Case studies and success stories""")
    
    if config.include_competitors:
        sections.append("""
## COMPETITIVE LANDSCAPE
- Key players and market share
- Differentiating factors
- Best practices and innovations""")
    
    return "\n".join(sections)
```

### 5.3 Targeted Research Prompt
```python
def build_targeted_research_prompt(topic: str, industry: str, target_audience: str, config: ResearchConfig) -> str:
    return f"""You are a specialized researcher for {industry} focusing on {target_audience}.

Research Topic: "{topic}"

Provide TARGETED, ACTIONABLE insights:

## CORE FINDINGS
- 3-5 most critical insights
- Each with specific data points and authoritative sources
- Direct relevance to {target_audience}'s needs

## IMPLEMENTATION GUIDANCE
- Practical steps and recommendations
- Tools, resources, platforms
- Expected outcomes and metrics

## EVIDENCE BASE
- Recent studies (2024-2025)
- Industry reports and whitepapers
- Expert consensus

CONSTRAINTS:
- Maximum {config.max_sources} sources
- Focus on depth over breadth
- Prioritize actionable over theoretical"""
```

---

## 6. AI Personalization API Design (Proposed)

### Endpoint: `/api/research/ai-suggestions`

#### Request
```typescript
interface AISuggestionRequest {
  user_input: string;  // Raw user input
  user_id?: string;    // For persona access
  context?: {
    previous_research?: string[];
    content_type?: 'blog' | 'whitepaper' | 'social' | 'email';
  };
}
```

#### Response
```typescript
interface AISuggestionResponse {
  enhanced_query: string;           // Optimized research query
  suggested_config: ResearchConfig; // Recommended configuration
  keywords: string[];               // Extracted/expanded keywords
  industry: string;                 // Detected industry
  target_audience: string;          // Suggested audience
  reasoning: string;                // Why these suggestions
  alternative_angles: string[];     // Other research directions
}
```

### Implementation Steps
1. **Fetch persona data** from onboarding
2. **Parse user input** (detect intent, entities, complexity)
3. **Apply persona context** (industry, audience, preferences)
4. **Generate suggestions** using LLM with persona-aware prompt
5. **Return structured config** ready to apply

---

## 7. Example AI Enhancement Flow

### User Input (Vague)
```
"write something about AI"
```

### AI Analysis
- **Intent Detection**: User wants to create content about AI
- **Persona Context**: 
  - Industry: Healthcare (from onboarding)
  - Audience: Medical professionals
  - Expertise: Intermediate
- **Complexity**: Low (very vague)

### AI Enhanced Output
```typescript
{
  enhanced_query: "Research: AI-powered diagnostic tools and clinical decision support systems in healthcare",
  suggested_config: {
    mode: 'comprehensive',
    provider: 'exa',
    max_sources: 20,
    include_statistics: true,
    include_expert_quotes: true,
    exa_category: 'research paper',
    exa_search_type: 'neural',
    exa_include_domains: ['pubmed.gov', 'nejm.org', 'nih.gov']
  },
  keywords: [
    "AI diagnostic tools",
    "clinical decision support",
    "medical AI applications",
    "healthcare automation",
    "patient outcomes AI"
  ],
  industry: "Healthcare",
  target_audience: "Medical professionals and healthcare administrators",
  reasoning: "Based on your healthcare focus and medical professional audience from your profile, I've tailored this research to explore AI diagnostic tools with clinical evidence and expert insights.",
  alternative_angles: [
    "AI ethics in medical decision-making",
    "Cost-benefit analysis of AI diagnostic systems",
    "Training medical staff on AI tools"
  ]
}
```

---

## 8. Testing Scenarios

### Scenario 1: Beginner User
- **Profile**: New blogger, general audience
- **Input**: "best marketing tools"
- **AI Should**: Suggest basic mode, Google search, expand to "top marketing automation tools for small businesses"

### Scenario 2: Technical Expert
- **Profile**: Data scientist, technical audience
- **Input**: "transformer architectures"
- **AI Should**: Suggest comprehensive mode, Exa neural, include research papers, arxiv.org domains

### Scenario 3: Business Professional
- **Profile**: CMO, C-suite audience
- **Input**: "ROI of content marketing"
- **AI Should**: Suggest targeted mode, include statistics & competitors, focus on HBR, McKinsey sources

---

## 9. Implementation Priority

### High Priority (Week 1)
1. ✅ Fix preset click behavior
2. ✅ Show Exa options for all modes
3. 🔄 Create persona fetch API endpoint
4. 🔄 Add persona-aware default suggestions

### Medium Priority (Week 2)
5. AI query enhancement endpoint
6. Smart preset generation from persona
7. Industry-specific domain suggestions

### Low Priority (Week 3+)
8. Learning from user research history
9. Collaborative filtering (similar users' successful configs)
10. A/B testing AI suggestions

---

## 10. Success Metrics

- **User Engagement**: % of users who modify AI suggestions
- **Research Quality**: User ratings of research results
- **Time Saved**: Reduction in research configuration time
- **Adoption Rate**: % of users using presets vs. manual config
- **Accuracy**: % of AI suggestions that match user intent

---

## Conclusion

By leveraging persona data and AI, we can transform research from a complex configuration task into a simple, one-click experience for beginners while maintaining full customization for power users. The key is intelligent defaults that "just work" based on who the user is and what they're trying to achieve.

