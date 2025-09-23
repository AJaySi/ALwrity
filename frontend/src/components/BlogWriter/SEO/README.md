# SEO Components

This folder contains extracted SEO analysis components that were refactored from the main `SEOAnalysisModal` component to improve maintainability and code organization.

## Components

### KeywordAnalysis
- **File**: `KeywordAnalysis.tsx`
- **Purpose**: Displays comprehensive keyword analysis including:
  - Keyword types overview (primary, long-tail, semantic)
  - Keyword density analysis with optimal range indicators
  - Missing keywords detection
  - Over-optimized keywords detection
  - Keyword distribution analysis

### ReadabilityAnalysis
- **File**: `ReadabilityAnalysis.tsx`
- **Purpose**: Displays comprehensive readability analysis including:
  - 6 different readability metrics with tooltips
  - Content statistics (word count, sections, paragraphs, etc.)
  - Sentence and paragraph analysis
  - Target audience determination
  - Content quality metrics

### StructureAnalysis
- **File**: `StructureAnalysis.tsx`
- **Purpose**: Displays comprehensive content structure analysis including:
  - Structure overview (sections, paragraphs, sentences, structure score)
  - Content elements detection (introduction, conclusion, call-to-action)
  - Heading structure analysis (H1, H2, H3 counts and actual headings)
  - Heading hierarchy score

### Recommendations
- **File**: `Recommendations.tsx`
- **Purpose**: Displays actionable SEO recommendations including:
  - Priority-based recommendation cards (High, Medium, Low)
  - Category tags for each recommendation
  - Impact descriptions
  - Visual priority indicators with icons

### SEOProcessor
- **File**: `SEOProcessor.tsx`
- **Purpose**: Provides CopilotKit actions for SEO functionality including:
  - `generateSEOMetadata` - Generate SEO metadata for blog content
  - `optimizeSection` - Optimize individual sections for SEO
  - Interactive UI components for user feedback

## Refactoring Benefits

1. **Improved Maintainability**: Each component is focused on a single responsibility
2. **Better Code Organization**: Related functionality is grouped together
3. **Easier Testing**: Individual components can be tested in isolation
4. **Reusability**: Components can be reused in other parts of the application
5. **Reduced File Size**: Main modal component reduced by ~600+ lines
6. **Modular Architecture**: Clean separation of concerns

## Usage

```tsx
import { 
  KeywordAnalysis, 
  ReadabilityAnalysis, 
  StructureAnalysis, 
  Recommendations,
  SEOProcessor 
} from './SEO';

// In your component
<KeywordAnalysis detailedAnalysis={analysisResult.detailed_analysis} />
<ReadabilityAnalysis 
  detailedAnalysis={analysisResult.detailed_analysis} 
  visualizationData={analysisResult.visualization_data}
/>
<StructureAnalysis detailedAnalysis={analysisResult.detailed_analysis} />
<Recommendations recommendations={analysisResult.actionable_recommendations} />
<SEOProcessor 
  buildFullMarkdown={buildFullMarkdown}
  seoMetadata={seoMetadata}
  onSEOAnalysis={onSEOAnalysis}
  onSEOMetadata={onSEOMetadata}
/>
```

## Props

### KeywordAnalysis Props
- `detailedAnalysis?: { keyword_analysis?: {...} }` - Detailed analysis data from backend

### ReadabilityAnalysis Props
- `detailedAnalysis?: { readability_analysis?: {...}, content_quality?: {...}, content_structure?: {...} }` - Detailed analysis data
- `visualizationData?: { content_stats?: {...} }` - Visualization data for fallback values

### StructureAnalysis Props
- `detailedAnalysis?: { content_structure?: {...}, heading_structure?: {...} }` - Detailed analysis data

### Recommendations Props
- `recommendations: Recommendation[]` - Array of actionable recommendations with priority and impact

### SEOProcessor Props
- `buildFullMarkdown: () => string` - Function to build full markdown content
- `seoMetadata: BlogSEOMetadataResponse | null` - Current SEO metadata
- `onSEOAnalysis: (analysis: any) => void` - Callback for SEO analysis results
- `onSEOMetadata: (metadata: BlogSEOMetadataResponse) => void` - Callback for SEO metadata results
