# Story Generation Code Adaptation Guide

This guide shows how to adapt the existing story generation code to use the production-ready `main_text_generation` and subscription system.

## 1. Import Path Updates

### Before (Legacy)
```python
from ...gpt_providers.text_generation.main_text_generation import llm_text_gen
```

### After (Production)
```python
from services.llm_providers.main_text_generation import llm_text_gen
```

## 2. Adding User ID and Subscription Support

### Before
```python
def generate_with_retry(prompt, system_prompt=None):
    try:
        return llm_text_gen(prompt, system_prompt)
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return ""
```

### After
```python
def generate_with_retry(prompt, system_prompt=None, user_id: str = None):
    """
    Generate content with retry handling and subscription support.
    
    Args:
        prompt: The prompt to generate content from
        system_prompt: Custom system prompt (optional)
        user_id: Clerk user ID (required for subscription checking)
    
    Returns:
        Generated content string
    
    Raises:
        RuntimeError: If user_id is missing or subscription limits exceeded
        HTTPException: If subscription limit exceeded (429 status)
    """
    if not user_id:
        raise RuntimeError("user_id is required for subscription checking")
    
    try:
        return llm_text_gen(
            prompt=prompt,
            system_prompt=system_prompt,
            user_id=user_id
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions (e.g., 429 subscription limit)
        raise
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise RuntimeError(f"Failed to generate content: {str(e)}") from e
```

## 3. Structured JSON Response for Outline

### Before
```python
outline = generate_with_retry(outline_prompt.format(premise=premise))
# Returns plain text, needs parsing
```

### After
```python
# Define JSON schema for structured outline
outline_schema = {
    "type": "object",
    "properties": {
        "outline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "scene_number": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "key_events": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["scene_number", "title", "description"]
            }
        }
    },
    "required": ["outline"]
}

# Generate structured outline
outline_response = llm_text_gen(
    prompt=outline_prompt.format(premise=premise),
    system_prompt=system_prompt,
    json_struct=outline_schema,
    user_id=user_id
)

# Parse JSON response
import json
outline_data = json.loads(outline_response)
outline = outline_data.get("outline", [])
```

## 4. Complete Service Example

### Story Service Structure
```python
# backend/services/story_writer/story_service.py

from typing import Dict, Any, Optional, List
from loguru import logger
from services.llm_providers.main_text_generation import llm_text_gen
import json

class StoryWriterService:
    """Service for generating stories using prompt chaining."""
    
    def __init__(self):
        self.guidelines = """\
Writing Guidelines:

Delve deeper. Lose yourself in the world you're building. Unleash vivid
descriptions to paint the scenes in your reader's mind.
Develop your characters — let their motivations, fears, and complexities unfold naturally.
Weave in the threads of your outline, but don't feel constrained by it.
Allow your story to surprise you as you write. Use rich imagery, sensory details, and
evocative language to bring the setting, characters, and events to life.
Introduce elements subtly that can blossom into complex subplots, relationships,
or worldbuilding details later in the story.
Keep things intriguing but not fully resolved.
Avoid boxing the story into a corner too early.
Plant the seeds of subplots or potential character arc shifts that can be expanded later.

Remember, your main goal is to write as much as you can. If you get through
the story too fast, that is bad. Expand, never summarize.
"""
    
    def generate_premise(
        self,
        persona: str,
        story_setting: str,
        character_input: str,
        plot_elements: str,
        user_id: str
    ) -> str:
        """Generate story premise."""
        prompt = f"""\
{persona}

Write a single sentence premise for a {story_setting} story featuring {character_input}.
The plot will revolve around: {plot_elements}
"""
        
        try:
            premise = llm_text_gen(
                prompt=prompt,
                user_id=user_id
            )
            return premise.strip()
        except Exception as e:
            logger.error(f"Error generating premise: {e}")
            raise RuntimeError(f"Failed to generate premise: {str(e)}") from e
    
    def generate_outline(
        self,
        premise: str,
        persona: str,
        story_setting: str,
        character_input: str,
        plot_elements: str,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Generate structured story outline."""
        prompt = f"""\
{persona}

You have a gripping premise in mind:

{premise}

Write an outline for the plot of your story set in {story_setting} featuring {character_input}.
The plot elements are: {plot_elements}
"""
        
        # Define JSON schema for structured response
        json_schema = {
            "type": "object",
            "properties": {
                "outline": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_number": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "key_events": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["scene_number", "title", "description"]
                    }
                }
            },
            "required": ["outline"]
        }
        
        try:
            response = llm_text_gen(
                prompt=prompt,
                json_struct=json_schema,
                user_id=user_id
            )
            
            # Parse JSON response
            outline_data = json.loads(response)
            return outline_data.get("outline", [])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse outline JSON: {e}")
            # Fallback to text parsing if JSON fails
            return self._parse_text_outline(response)
        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            raise RuntimeError(f"Failed to generate outline: {str(e)}") from e
    
    def generate_story_start(
        self,
        premise: str,
        outline: str,
        persona: str,
        story_setting: str,
        character_input: str,
        plot_elements: str,
        writing_style: str,
        story_tone: str,
        narrative_pov: str,
        audience_age_group: str,
        content_rating: str,
        ending_preference: str,
        user_id: str
    ) -> str:
        """Generate the starting section of the story."""
        # Format outline as text if it's a list
        if isinstance(outline, list):
            outline_text = "\n".join([
                f"{item.get('scene_number', i+1)}. {item.get('title', '')}: {item.get('description', '')}"
                for i, item in enumerate(outline)
            ])
        else:
            outline_text = str(outline)
        
        prompt = f"""\
{persona}

Write a story with the following details:

**The Story Setting is:**
{story_setting}

**The Characters of the story are:**
{character_input}

**Plot Elements of the story:**
{plot_elements}

**Story Writing Style:**
{writing_style}

**The story Tone is:**
{story_tone}

**Write story from the Point of View of:**
{narrative_pov}

**Target Audience of the story:**
{audience_age_group}, **Content Rating:** {content_rating}

**Story Ending:**
{ending_preference}

You have a gripping premise in mind:

{premise}

Your imagination has crafted a rich narrative outline:

{outline_text}

First, silently review the outline and the premise. Consider how to start the story.

Start to write the very beginning of the story. You are not expected to finish
the whole story now. Your writing should be detailed enough that you are only
scratching the surface of the first bullet of your outline. Try to write AT
MINIMUM 4000 WORDS.

{self.guidelines}
"""
        
        try:
            starting_draft = llm_text_gen(
                prompt=prompt,
                user_id=user_id
            )
            return starting_draft.strip()
        except Exception as e:
            logger.error(f"Error generating story start: {e}")
            raise RuntimeError(f"Failed to generate story start: {str(e)}") from e
    
    def continue_story(
        self,
        premise: str,
        outline: str,
        story_text: str,
        persona: str,
        story_setting: str,
        character_input: str,
        plot_elements: str,
        writing_style: str,
        story_tone: str,
        narrative_pov: str,
        audience_age_group: str,
        content_rating: str,
        ending_preference: str,
        user_id: str
    ) -> str:
        """Continue writing the story."""
        # Format outline as text if it's a list
        if isinstance(outline, list):
            outline_text = "\n".join([
                f"{item.get('scene_number', i+1)}. {item.get('title', '')}: {item.get('description', '')}"
                for i, item in enumerate(outline)
            ])
        else:
            outline_text = str(outline)
        
        prompt = f"""\
{persona}

Write a story with the following details:

**The Story Setting is:**
{story_setting}

**The Characters of the story are:**
{character_input}

**Plot Elements of the story:**
{plot_elements}

**Story Writing Style:**
{writing_style}

**The story Tone is:**
{story_tone}

**Write story from the Point of View of:**
{narrative_pov}

**Target Audience of the story:**
{audience_age_group}, **Content Rating:** {content_rating}

**Story Ending:**
{ending_preference}

You have a gripping premise in mind:

{premise}

Your imagination has crafted a rich narrative outline:

{outline_text}

You've begun to immerse yourself in this world, and the words are flowing.
Here's what you've written so far:

{story_text}

=====

First, silently review the outline and story so far. Identify what the single
next part of your outline you should write.

Your task is to continue where you left off and write the next part of the story.
You are not expected to finish the whole story now. Your writing should be
detailed enough that you are only scratching the surface of the next part of
your outline. Try to write AT MINIMUM 2000 WORDS. However, only once the story
is COMPLETELY finished, write IAMDONE. Remember, do NOT write a whole chapter
right now.

{self.guidelines}
"""
        
        try:
            continuation = llm_text_gen(
                prompt=prompt,
                user_id=user_id
            )
            return continuation.strip()
        except Exception as e:
            logger.error(f"Error continuing story: {e}")
            raise RuntimeError(f"Failed to continue story: {str(e)}") from e
    
    def _parse_text_outline(self, text: str) -> List[Dict[str, Any]]:
        """Fallback method to parse text outline if JSON parsing fails."""
        # Simple text parsing logic
        lines = text.strip().split('\n')
        outline = []
        for i, line in enumerate(lines):
            if line.strip():
                outline.append({
                    "scene_number": i + 1,
                    "title": f"Scene {i + 1}",
                    "description": line.strip(),
                    "key_events": []
                })
        return outline
```

## 5. API Endpoint Example

```python
# backend/api/story_writer/router.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from middleware.auth_middleware import get_current_user
from services.story_writer.story_service import StoryWriterService
from models.story_models import StoryGenerationRequest

router = APIRouter(prefix="/api/story", tags=["Story Writer"])
service = StoryWriterService()

@router.post("/generate-premise")
async def generate_premise(
    request: StoryGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate story premise."""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        premise = service.generate_premise(
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            user_id=user_id
        )
        
        return {"premise": premise, "success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate premise: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 6. Key Differences Summary

| Aspect | Legacy Code | Production Code |
|--------|------------|-----------------|
| Import Path | `...gpt_providers.text_generation.main_text_generation` | `services.llm_providers.main_text_generation` |
| User ID | Not required | Required parameter |
| Subscription | No checks | Automatic via `main_text_generation` |
| Error Handling | Basic try/except | HTTPException handling for 429 errors |
| Structured Responses | Text parsing | JSON schema support |
| Async Support | Synchronous | Can use async/await |
| Logging | Basic | Comprehensive with loguru |

## 7. Testing Checklist

When adapting code, verify:
- [ ] All imports updated to production paths
- [ ] `user_id` parameter added to all LLM calls
- [ ] Subscription errors (429) are handled properly
- [ ] Error messages are user-friendly
- [ ] Logging is comprehensive
- [ ] Structured JSON responses work correctly
- [ ] Fallback logic for text parsing exists
- [ ] Long-running operations use task management

## 8. Common Pitfalls

1. **Missing user_id**: Always pass `user_id` parameter
2. **Ignoring HTTPException**: Re-raise HTTPExceptions (especially 429)
3. **No fallback parsing**: If JSON parsing fails, have text parsing fallback
4. **Synchronous blocking**: Use async endpoints for long-running operations
5. **No error context**: Include original exception in error messages
