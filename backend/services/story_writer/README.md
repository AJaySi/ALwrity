# Story Writer Service

Story generation service using prompt chaining approach, migrated from `ToBeMigrated/ai_writers/ai_story_writer/`.

## Structure

```
backend/
├── services/
│   └── story_writer/
│       ├── __init__.py
│       ├── story_service.py      # Core story generation logic
│       └── README.md
├── api/
│   └── story_writer/
│       ├── __init__.py
│       ├── router.py              # API endpoints
│       ├── task_manager.py        # Async task management
│       └── cache_manager.py       # Result caching
└── models/
    └── story_models.py             # Pydantic models
```

## Features

- **Prompt Chaining**: Generates stories through premise → outline → start → continuation
- **Multiple Personas**: Supports 11 predefined author personas/genres
- **Configurable Parameters**: 
  - Story setting, characters, plot elements
  - Writing style, tone, narrative POV
  - Audience age group, content rating, ending preference
- **Subscription Integration**: Automatic usage tracking via `main_text_generation`
- **Provider Support**: Works with both Gemini and HuggingFace
- **Async Task Management**: Long-running story generation with polling
- **Caching**: Result caching for identical requests

## API Endpoints

### Synchronous Endpoints

- `POST /api/story/generate-premise` - Generate story premise
- `POST /api/story/generate-outline` - Generate outline from premise
- `POST /api/story/generate-start` - Generate story beginning
- `POST /api/story/continue` - Continue story generation

### Asynchronous Endpoints

- `POST /api/story/generate-full` - Generate complete story (returns task_id)
- `GET /api/story/task/{task_id}/status` - Get task status
- `GET /api/story/task/{task_id}/result` - Get completed task result

### Cache Management

- `GET /api/story/cache/stats` - Get cache statistics
- `POST /api/story/cache/clear` - Clear cache

## Usage Example

```python
from services.story_writer.story_service import StoryWriterService

service = StoryWriterService()

# Generate full story
result = service.generate_full_story(
    persona="Award-Winning Science Fiction Author",
    story_setting="A bustling futuristic city in 2150",
    character_input="John, a tall muscular man with a kind heart",
    plot_elements="The hero's journey, Good vs. evil",
    writing_style="Formal",
    story_tone="Suspenseful",
    narrative_pov="Third Person Limited",
    audience_age_group="Adults",
    content_rating="PG-13",
    ending_preference="Happy",
    user_id="clerk_user_id",
    max_iterations=10
)

print(result["premise"])
print(result["outline"])
print(result["story"])
```

## Migration Notes

- Updated imports from legacy `...gpt_providers.text_generation.main_text_generation` to `services.llm_providers.main_text_generation`
- Added `user_id` parameter to all LLM calls for subscription support
- Removed Streamlit dependencies (UI moved to frontend)
- Added proper error handling with HTTPException support
- Added async task management for long-running operations
- Added caching support for identical requests

## Integration

The router is automatically registered via `alwrity_utils/router_manager.py` in the optional routers section.
