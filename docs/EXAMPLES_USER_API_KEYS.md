# User API Key Context - Usage Examples

This document shows how to use the `UserAPIKeyContext` in your backend services to ensure user-specific API keys are used.

## Quick Start

### **1. Basic Usage in FastAPI Endpoint**

```python
from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from services.user_api_key_context import user_api_keys
import google.generativeai as genai

router = APIRouter()

@router.post("/api/generate-content")
async def generate_content(
    prompt: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    
    # Get user-specific API keys
    with user_api_keys(user_id) as keys:
        gemini_key = keys.get('gemini')
        
        if not gemini_key:
            raise HTTPException(status_code=400, detail="Gemini API key not configured")
        
        # Configure Gemini with user's key
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate content using this user's quota
        response = model.generate_content(prompt)
        
        return {
            "content": response.text,
            "user_id": user_id  # For debugging
        }
```

---

## Examples by Use Case

### **Example 1: Blog Writer Service**

**File: `backend/services/blog_writer_service.py`**

```python
from services.user_api_key_context import user_api_keys, get_gemini_key
import google.generativeai as genai

class BlogWriterService:
    """
    Service for generating blog content using user-specific API keys.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def generate_blog_outline(self, topic: str) -> dict:
        """Generate blog outline using user's Gemini API key."""
        
        # Method 1: Using context manager (recommended)
        with user_api_keys(self.user_id) as keys:
            gemini_key = keys.get('gemini')
            
            if not gemini_key:
                raise ValueError(f"No Gemini API key found for user {self.user_id}")
            
            # Configure Gemini with user's key
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"Create a detailed blog outline for: {topic}"
            response = model.generate_content(prompt)
            
            return {
                "outline": response.text,
                "topic": topic,
                "user_id": self.user_id
            }
    
    async def generate_blog_section(self, section_heading: str, context: str) -> str:
        """Generate blog section using user's Gemini API key."""
        
        # Method 2: Using convenience function
        gemini_key = get_gemini_key(self.user_id)
        
        if not gemini_key:
            raise ValueError(f"No Gemini API key found for user {self.user_id}")
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"Write a blog section for '{section_heading}'\n\nContext: {context}"
        response = model.generate_content(prompt)
        
        return response.text
```

**Usage in FastAPI:**

```python
from fastapi import APIRouter, Depends
from middleware.auth_middleware import get_current_user
from services.blog_writer_service import BlogWriterService

router = APIRouter()

@router.post("/api/blog/outline")
async def create_blog_outline(
    topic: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    
    # Create service instance with user_id
    blog_service = BlogWriterService(user_id)
    
    # Service automatically uses this user's API keys
    outline = await blog_service.generate_blog_outline(topic)
    
    return outline
```

---

### **Example 2: Research Service with Multiple APIs**

**File: `backend/services/research_service.py`**

```python
from services.user_api_key_context import user_api_keys
from exa_py import Exa
import google.generativeai as genai

class ResearchService:
    """
    Service for conducting research using user-specific API keys.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def conduct_research(self, query: str) -> dict:
        """
        Conduct research using both Exa (search) and Gemini (analysis).
        Uses user-specific API keys for both services.
        """
        
        with user_api_keys(self.user_id) as keys:
            exa_key = keys.get('exa')
            gemini_key = keys.get('gemini')
            
            if not exa_key or not gemini_key:
                raise ValueError(f"Missing required API keys for user {self.user_id}")
            
            # 1. Search using user's Exa API key
            exa = Exa(api_key=exa_key)
            search_results = exa.search_and_contents(
                query,
                num_results=5,
                text=True
            )
            
            # 2. Analyze results using user's Gemini API key
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare context from search results
            context = "\n\n".join([
                f"Source: {r.url}\n{r.text[:500]}..."
                for r in search_results.results
            ])
            
            prompt = f"""
            Analyze the following research results for query: "{query}"
            
            {context}
            
            Provide a comprehensive summary and key insights.
            """
            
            analysis = model.generate_content(prompt)
            
            return {
                "query": query,
                "sources": [r.url for r in search_results.results],
                "analysis": analysis.text,
                "user_id": self.user_id  # For debugging
            }
```

---

### **Example 3: Persona Generation Service**

**File: `backend/services/persona/core_persona_service.py`**

```python
from services.user_api_key_context import user_api_keys, get_gemini_key
import google.generativeai as genai
from typing import Optional

class CorePersonaService:
    """
    Service for generating AI writing personas.
    """
    
    def generate_core_persona(
        self, 
        onboarding_data: dict,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Generate core persona using user's Gemini API key.
        
        Args:
            onboarding_data: User's onboarding information
            user_id: User ID (optional - uses .env in dev mode if None)
        """
        
        # Get user-specific Gemini key
        # In dev mode (user_id=None), this uses .env
        # In prod mode, this fetches from database
        gemini_key = get_gemini_key(user_id)
        
        if not gemini_key:
            if user_id:
                raise ValueError(f"No Gemini API key found for user {user_id}")
            else:
                raise ValueError("No Gemini API key found in .env file")
        
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Extract user's business info
        business_data = onboarding_data.get('businessData', {})
        website_analysis = onboarding_data.get('websiteAnalysis', {})
        
        prompt = f"""
        Generate an AI writing persona based on:
        
        Business: {business_data.get('name')}
        Industry: {business_data.get('industry')}
        Tone: {website_analysis.get('tone')}
        
        Create a detailed writing persona including voice, style, and personality.
        """
        
        response = model.generate_content(prompt)
        
        return {
            "persona": response.text,
            "user_id": user_id,
            "source": "dev_env" if user_id is None else "user_database"
        }
```

---

### **Example 4: Background Task with User Keys**

**File: `backend/services/async_content_generator.py`**

```python
from fastapi import BackgroundTasks
from services.user_api_key_context import user_api_keys
import google.generativeai as genai

async def generate_content_background(
    user_id: str, 
    task_id: str, 
    prompt: str,
    callback_url: str = None
):
    """
    Background task that generates content using user's API keys.
    This runs asynchronously and doesn't block the API response.
    """
    
    try:
        # Get user-specific API keys
        with user_api_keys(user_id) as keys:
            gemini_key = keys.get('gemini')
            
            if not gemini_key:
                # Log error and notify user
                logger.error(f"No Gemini API key for user {user_id} in task {task_id}")
                return
            
            # Configure Gemini
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Generate content (this may take a while)
            response = model.generate_content(prompt)
            
            # Save to database or send callback
            if callback_url:
                # Notify user that content is ready
                await send_callback(callback_url, {
                    "task_id": task_id,
                    "content": response.text,
                    "status": "completed"
                })
            
            logger.info(f"Task {task_id} completed for user {user_id}")
            
    except Exception as e:
        logger.error(f"Task {task_id} failed for user {user_id}: {e}")


# Usage in FastAPI endpoint
@router.post("/api/generate-async")
async def generate_async(
    prompt: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id')
    task_id = str(uuid.uuid4())
    
    # Queue background task
    background_tasks.add_task(
        generate_content_background,
        user_id=user_id,
        task_id=task_id,
        prompt=prompt
    )
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Content generation started"
    }
```

---

### **Example 5: Migrating Existing Service**

**Before (WRONG - uses global .env):**

```python
import os
import google.generativeai as genai

class OldBlogService:
    def generate_content(self, prompt: str):
        # BAD: Uses same API key for all users!
        gemini_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=gemini_key)
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text
```

**After (CORRECT - uses user-specific keys):**

```python
from services.user_api_key_context import user_api_keys
import google.generativeai as genai

class NewBlogService:
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def generate_content(self, prompt: str):
        # GOOD: Uses user-specific API key!
        with user_api_keys(self.user_id) as keys:
            gemini_key = keys.get('gemini')
            
            if not gemini_key:
                raise ValueError(f"No Gemini API key for user {self.user_id}")
            
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            return response.text
```

---

## Best Practices

### ✅ **DO:**

1. **Always pass `user_id` to services:**
   ```python
   service = BlogWriterService(user_id=current_user.get('user_id'))
   ```

2. **Use context manager for multiple keys:**
   ```python
   with user_api_keys(user_id) as keys:
       gemini_key = keys.get('gemini')
       exa_key = keys.get('exa')
   ```

3. **Check for missing keys:**
   ```python
   if not gemini_key:
       raise HTTPException(status_code=400, detail="Please configure your Gemini API key")
   ```

4. **Log which user's keys are being used:**
   ```python
   logger.info(f"Generating content for user {user_id} with their API keys")
   ```

### ❌ **DON'T:**

1. **Don't use `os.getenv()` directly:**
   ```python
   # WRONG - same key for all users!
   gemini_key = os.getenv('GEMINI_API_KEY')
   ```

2. **Don't forget to pass `user_id`:**
   ```python
   # WRONG - will use .env even in production!
   with user_api_keys() as keys:  # Missing user_id!
   ```

3. **Don't hardcode API keys:**
   ```python
   # WRONG - security risk!
   genai.configure(api_key="AIzaSy...")
   ```

---

## Testing

### **Test in Development:**

```python
# Set DEBUG=true in backend/.env
# Then test:

def test_dev_mode():
    # user_id=None should use .env file
    with user_api_keys(user_id=None) as keys:
        assert keys.get('gemini') == os.getenv('GEMINI_API_KEY')
```

### **Test in Production:**

```python
# Set DEBUG=false and DEPLOY_ENV=render
# Then test:

def test_prod_mode():
    # Should fetch from database
    user_id = "user_12345"
    with user_api_keys(user_id) as keys:
        # Keys should come from database, not .env
        assert keys.get('gemini') != os.getenv('GEMINI_API_KEY')
```

---

## Summary

| Method | Use Case | Example |
|--------|----------|---------|
| `user_api_keys(user_id)` | Multiple keys needed | Research service (Exa + Gemini) |
| `get_gemini_key(user_id)` | Single key needed | Blog writer (only Gemini) |
| `get_exa_key(user_id)` | Single key needed | Search service (only Exa) |
| `get_user_api_keys(user_id)` | FastAPI dependency | Endpoint that needs all keys |

**Key Principle:**
> Always pass `user_id` to get user-specific API keys. In development (`user_id=None`), it uses `.env` for convenience.

This ensures:
- ✅ **Local dev**: Your keys from `.env`
- ✅ **Production**: Each user's keys from database
- ✅ **Zero cost**: Alpha testers use their own API keys
- ✅ **User isolation**: No conflicts between users

