# Research Component Integration Guide

## Overview

The modular Research component has been implemented as a standalone, testable wizard that can be integrated into the blog writer or used independently. This document outlines the architecture, usage, and integration steps.

## Architecture

### Backend Strategy Pattern

The research service now supports multiple research modes through a strategy pattern:

```python
# Research modes
- Basic: Quick keyword-focused analysis
- Comprehensive: Full analysis with all components
- Targeted: Customizable components based on config

# Strategy implementation
backend/services/blog_writer/research/research_strategies.py
- ResearchStrategy (base class)
- BasicResearchStrategy
- ComprehensiveResearchStrategy
- TargetedResearchStrategy
```

### Frontend Component Structure

```
frontend/src/components/Research/
├── index.tsx                    # Main exports
├── ResearchWizard.tsx          # Main wizard container
├── steps/
│   ├── StepKeyword.tsx         # Step 1: Keyword input
│   ├── StepOptions.tsx         # Step 2: Mode selection
│   ├── StepProgress.tsx        # Step 3: Progress display
│   └── StepResults.tsx         # Step 4: Results display
├── hooks/
│   ├── useResearchWizard.ts   # Wizard state management
│   └── useResearchExecution.ts # API calls and polling
├── types/
│   └── research.types.ts       # TypeScript interfaces
└── utils/
    └── researchUtils.ts        # Utility functions
```

## Test Page

A dedicated test page is available at `/research-test` for testing the research wizard independently.

**Features:**
- Quick preset keywords for testing
- Debug panel with JSON export
- Performance metrics display
- Cache state visualization

## Usage

### Standalone Usage

```typescript
import { ResearchWizard } from '../components/Research';

<ResearchWizard
  onComplete={(results) => {
    console.log('Research complete:', results);
  }}
  onCancel={() => {
    console.log('Cancelled');
  }}
  initialKeywords={['AI', 'marketing']}
  initialIndustry="Technology"
/>
```

### Integration with Blog Writer

The component is designed to be easily integrated into the BlogWriter research phase:

**Current Implementation:**
- Uses CopilotKit sidebar for research input
- Displays results in `ResearchResults` component
- Manual fallback via `ManualResearchForm`

**Proposed Integration:**
Replace the CopilotKit/manual form with the wizard:

```typescript
// In BlogWriter.tsx
{currentPhase === 'research' && (
  <ResearchWizard
    onComplete={(results) => setResearch(results)}
    onCancel={() => navigate('blog-writer')}
  />
)}
```

## Backend API Changes

### New Models

The `BlogResearchRequest` model now supports:

```python
class BlogResearchRequest(BaseModel):
    keywords: List[str]
    topic: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    tone: Optional[str] = None
    word_count_target: Optional[int] = 1500
    persona: Optional[PersonaInfo] = None
    research_mode: Optional[ResearchMode] = ResearchMode.BASIC  # NEW
    config: Optional[ResearchConfig] = None  # NEW
```

### Backward Compatibility

The API remains backward compatible:
- If `research_mode` is not provided, defaults to `BASIC`
- If `config` is not provided, defaults to standard configuration
- Existing requests continue to work unchanged

## Research Modes

### Basic Mode
- Quick keyword analysis
- Primary & secondary keywords
- Current trends overview
- Top 5 content angles
- Key statistics

### Comprehensive Mode
- All basic features plus:
- Expert quotes & opinions
- Competitor analysis
- Market forecasts
- Best practices & case studies
- Content gaps identification

### Targeted Mode
- Selectable components:
  - Statistics
  - Expert quotes
  - Competitors
  - Trends
  - Always includes: Keywords & content angles

## Configuration Options

### ResearchConfig Model

```python
class ResearchConfig(BaseModel):
    mode: ResearchMode = ResearchMode.BASIC
    date_range: Optional[DateRange] = None
    source_types: List[SourceType] = []
    max_sources: int = 10
    include_statistics: bool = True
    include_expert_quotes: bool = True
    include_competitors: bool = True
    include_trends: bool = True
```

### Date Range Options
- `last_week`
- `last_month`
- `last_3_months`
- `last_6_months`
- `last_year`
- `all_time`

### Source Types
- `web` - Web articles
- `academic` - Academic papers
- `news` - News articles
- `industry` - Industry reports
- `expert` - Expert opinions

## Caching

The research component uses the existing cache infrastructure:
- Cache keys include research mode
- Cache is shared across basic/comprehensive/targeted modes
- Cache invalidation handled automatically

## Testing

### Test the Wizard

1. Navigate to `/research-test`
2. Use quick presets or enter custom keywords
3. Select research mode
4. Monitor progress
5. Review results
6. Export JSON for analysis

### Integration Testing

To test integration with BlogWriter:

1. Start backend: `python start_alwrity_backend.py`
2. Navigate to `/blog-writer` (current implementation)
3. Or navigate to `/research-test` (new wizard)
4. Compare results and UI

## Migration Path

### Phase 1: Parallel Testing (Current)
- `/research-test` - New wizard available
- `/blog-writer` - Current implementation unchanged
- Users can test both

### Phase 2: Integration
1. Add wizard as option in BlogWriter
2. A/B test user preference
3. Monitor performance metrics

### Phase 3: Replacement (Optional)
1. Replace CopilotKit/manual form with wizard
2. Remove old implementation
3. Update documentation

## API Endpoints

All existing endpoints remain unchanged:

```
POST /api/blog/research/start
- Supports new research_mode and config parameters
- Backward compatible with existing requests

GET /api/blog/research/status/{task_id}
- No changes required
```

## Benefits

1. **Modularity**: Component works standalone
2. **Testability**: Dedicated test page for experimentation
3. **Backward Compatibility**: Existing functionality unchanged
4. **Progressive Enhancement**: Can add features incrementally
5. **Reusability**: Can be used in other parts of the app

## Future Enhancements

Potential future improvements:

1. **Multi-stage Research**: Sequential research with refinement
2. **Source Quality Validation**: Advanced credibility scoring
3. **Interactive Query Builder**: Dynamic search refinement
4. **Advanced Prompting**: Few-shot examples, reasoning chains
5. **Custom Strategy Plugins**: User-defined research strategies

## Troubleshooting

### Research Results Not Showing

Check:
1. Backend logs for API errors
2. Network tab for failed requests
3. Browser console for JavaScript errors
4. Verify user authentication

### Cache Issues

Clear cache:
```typescript
import { researchCache } from '../services/researchCache';
researchCache.clearCache();
```

### Type Errors

Ensure all imports are correct:
```typescript
import { 
  ResearchWizard,
  useResearchWizard,
  WizardState 
} from '../components/Research';

import {
  BlogResearchRequest,
  BlogResearchResponse,
  ResearchMode,
  ResearchConfig
} from '../services/blogWriterApi';
```

## Examples

### Basic Integration

```typescript
import { ResearchWizard } from './components/Research';
import { BlogResearchResponse } from './services/blogWriterApi';

const MyComponent: React.FC = () => {
  const [results, setResults] = useState<BlogResearchResponse | null>(null);

  return (
    <ResearchWizard
      onComplete={(res) => setResults(res)}
      onCancel={() => console.log('Cancelled')}
    />
  );
};
```

### Advanced Integration with Custom Config

```typescript
const request: BlogResearchRequest = {
  keywords: ['AI', 'automation'],
  industry: 'Technology',
  research_mode: 'targeted',
  config: {
    mode: 'targeted',
    include_statistics: true,
    include_competitors: true,
    include_trends: false,
    max_sources: 20,
  }
};
```

## Support

For issues or questions:
1. Check this documentation
2. Review test page examples
3. Inspect backend logs
4. Check frontend console

