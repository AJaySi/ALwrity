# Image Generation for Blog Writer - Technical Documentation

## Overview

This document describes the improvements made to image generation for the ALwrity Blog Writer feature, making generated images more relevant to blog content through intelligent visual data extraction and model selection.

## Architecture

### New Module Structure

```
backend/services/image_generation/
├── __init__.py                      # Package exports
└── visual_data_extractor.py         # Core extraction logic

backend/api/images.py                 # Updated to use new module
```

### Key Components

1. **Visual Data Extractor** (`visual_data_extractor.py`)
   - Extracts statistics, data points, visual concepts, and domain-specific imagery
   - Pre-compiled regex patterns for performance
   - Domain detection across 16 industry verticals
   - Dataclass-based return type for type safety

2. **Model-Specific Guidance** (`images.py`)
   - Extended guidance for 5 models (Ideogram V3, FLUX Kontext Pro, Qwen Image, FLUX 2 Flex, GLM-Image)
   - Image type recommendations (infographic, chart, conceptual, etc.)
   - Content-based model selection

## Features

### 1. Statistics Extraction

**Patterns Supported:**
- Percentages: `42%`, `1,000,000%`
- Currency: `$500`, `$1.5M`
- Multipliers: `5x`, `10x growth`
- Large numbers: `million`, `billion`, `thousand`
- Ranges: `20-30%`
- Change indicators: `up by 30%`, `down by 15%`
- CAGR: `CAGR of 44.9%`

**Example:**
```python
section = {"key_points": ["Market grew 40% in 2023", "Investment reached $5 billion"]}
result = extract_visual_data(section, None)
# result.statistics = ["Market grew 40% in 2023", "Investment reached $5 billion"]
```

### 2. Domain Detection

**Supported Domains (16):**
- Tech (AI, cloud, software, digital transformation)
- Healthcare (medical, hospital, patient care)
- Finance (investment, banking, stock market)
- Marketing (digital marketing, social media, ROI)
- Education (learning, academic, curriculum)
- E-commerce (shopping, conversion, inventory)
- Real Estate (property, mortgage, housing)
- Food (restaurant, cooking, recipe)
- Travel (destination, adventure, vacation)
- Fitness (workout, nutrition, wellness)
- Fashion (clothing, style, designer)
- Entertainment (streaming, gaming, content)
- Business (enterprise, strategy, leadership)
- Science (research, experiment, laboratory)
- Sports (competition, training, championship)
- Legal (compliance, contracts, courtroom)
- Environmental (sustainability, renewable, eco-friendly)

**Example:**
```python
section = {"heading": "AI in Healthcare Market"}
result = extract_visual_data(section, None)
# result.detected_domains = ["healthcare", "tech"]
# result.domain_concepts = ["stethoscope", "medical chart", "hospital equipment"]
```

### 3. Visual Data Patterns

**Detected Patterns:**
- Rankings: `ranked #1`, `top performer`, `leading brand`
- Comparisons: `vs`, `versus`, `compared to`
- Trends: `increase`, `decrease`, `growth`, `surge`
- Multipliers: `5 times`, `3-fold`

### 4. Model Selection Recommendations

Based on extracted content type:

**For Data-Heavy Content (statistics/data points):**
- FLUX Kontext Pro: Best for data visualizations with text labels
- GLM-Image: Excellent for infographics and educational diagrams
- Ideogram V3 Turbo: Good for simple charts with text overlays

**For Domain-Specific Content:**
- Qwen Image: Best for abstract conceptual imagery
- FLUX Kontext Pro: Good for conceptual imagery with text support
- FLUX 2 Flex: Excellent for poster-style conceptual designs

## API Integration

### Endpoint: `POST /api/images/suggest-prompts`

**Request Body:**
```json
{
  "provider": "wavespeed",
  "model": "flux-kontext-pro",
  "image_type": "infographic",
  "title": "AI in Healthcare Market",
  "section": {
    "heading": "Market Growth",
    "subheadings": ["Statistics", "Key Players"],
    "key_points": ["Market grew 40% in 2023", "Investment reached $5B"]
  },
  "research": {
    "domain": "healthcare",
    "key_facts": ["CAGR of 44.9% projected"]
  },
  "persona": {
    "audience": "healthcare professionals",
    "tone": "professional"
  }
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "prompt": "Professional infographic showing AI healthcare market growth...",
      "negative_prompt": "blurry, distorted, text artifacts...",
      "width": 1024,
      "height": 1024,
      "overlay_text": "40% Growth"
    }
  ]
}
```

## Usage Example

```python
from services.image_generation import extract_visual_data, build_visual_summary, get_model_recommendation

# Extract visual data from blog section and research
section = {
    "heading": "Digital Marketing Trends 2024",
    "key_points": [
        "Social media engagement up 60% YoY",
        "Video content drives 3x more engagement",
        "ROI increased by 45% with personalized campaigns"
    ],
    "keywords": ["marketing", "social media", "ROI"]
}

research = {
    "domain": "marketing",
    "sources": [
        {
            "title": "Marketing Trends Report 2024",
            "excerpt": "Digital ad spend reached $50 billion, up 25% from last year."
        }
    ]
}

# Extract visual data
result = extract_visual_data(section, research)

# Access extracted data
print(f"Statistics: {result.statistics}")
print(f"Domain: {result.detected_domains}")
print(f"Concepts: {result.domain_concepts}")

# Get model recommendation
rec = get_model_recommendation(result)
print(f"Recommendation: {rec}")

# Build summary for prompt
summary = build_visual_summary(result)
```

## Testing

**Unit Tests:** `backend/tests/services/test_visual_data_extractor.py`

Run tests:
```bash
cd backend
pytest tests/services/test_visual_data_extractor.py -v
```

**Test Coverage:**
- Statistics extraction (8 tests)
- Visual mention detection (5 tests)
- Trend keyword detection (4 tests)
- Domain detection (6 tests)
- Deduplication (5 tests)
- Main extraction function (8 tests)
- Model recommendations (3 tests)
- Visual summary building (3 tests)
- Integration tests (3 tests)

## Performance Considerations

1. **Pre-compiled Regex Patterns**: All regex patterns are compiled once at module load time, not on each function call.

2. **Deduplication**: Results are deduplicated using normalized keys to prevent duplicate entries.

3. **Lazy Evaluation**: Only processes required fields from input data.

## Future Enhancements

1. **Additional Domains**: Support for more industry verticals
2. **Custom Visual Metaphors**: Allow users to define domain-specific visual concepts
3. **A/B Testing**: Compare image relevance across different prompt strategies
4. **Feedback Loop**: Use image selection data to improve future prompt generation
