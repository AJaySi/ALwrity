"""
Smart Model Selection Module for ALwrity

This module implements intelligent model selection based on task requirements,
available resources, and user preferences. It helps optimize performance and
cost by matching the right model to each specific task.

Key Features:
- Task-based model selection (analysis, reasoning, creative, coding)
- Resource-aware selection (considering model size and system resources)
- Cost optimization (preferring local models when appropriate)
- Fallback strategies for model availability
- Performance monitoring and optimization

Task Categories:
1. Analysis Tasks: Data analysis, SEO analysis, content classification
   - Preferred: Small, fast models (llama3.2:3b, gemma2:2b)
   - Requirements: Speed, efficiency, basic reasoning

2. Reasoning Tasks: General content creation, blog writing, summarization
   - Preferred: Medium models (llama3.1:8b, qwen2.5:7b)
   - Requirements: Good reasoning, balanced performance

3. Complex Tasks: Research, advanced content creation, strategic planning
   - Preferred: Large models (llama3.1:70b, gpt-4, claude-3.5-sonnet)
   - Requirements: Advanced reasoning, comprehensive knowledge

4. Coding Tasks: Code generation, debugging, technical writing
   - Preferred: Code-specialized models (deepseek-coder, codellama)
   - Requirements: Code understanding, technical accuracy

5. Creative Tasks: Marketing copy, creative writing, brainstorming
   - Preferred: Creative models (gemma2:9b, gpt-4, claude-3.5-sonnet)
   - Requirements: Creativity, language fluency
"""

import os
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

class TaskType(Enum):
    """Define different types of tasks for model selection."""
    ANALYSIS = "analysis"
    REASONING = "reasoning"
    COMPLEX = "complex"
    CODING = "coding"
    CREATIVE = "creative"
    SEO_ANALYSIS = "seo_analysis"
    CONTENT_CLASSIFICATION = "content_classification"
    BLOG_WRITING = "blog_writing"
    RESEARCH = "research"
    SOCIAL_MEDIA = "social_media"

class ProviderType(Enum):
    """Define different provider types."""
    LOCAL = "local"       # Ollama
    CLOUD_FREE = "cloud_free"  # Free tier APIs
    CLOUD_PAID = "cloud_paid"  # Paid APIs

@dataclass
class ModelInfo:
    """Information about a specific model."""
    name: str
    provider: str
    provider_type: ProviderType
    suitable_tasks: List[TaskType]
    performance_score: int  # 1-10, higher is better
    speed_score: int       # 1-10, higher is faster
    cost_score: int        # 1-10, higher is more cost-effective
    resource_requirements: str  # "low", "medium", "high"

class SmartModelSelector:
    """Smart model selection system for ALwrity."""
    
    def __init__(self):
        """Initialize the model selector with available models."""
        self.models = self._initialize_models()
        self.user_preferences = self._load_user_preferences()
        
    def _initialize_models(self) -> Dict[str, ModelInfo]:
        """Initialize available models with their characteristics."""
        models = {
            # Ollama Local Models
            "llama3.2:3b": ModelInfo(
                name="llama3.2:3b",
                provider="ollama",
                provider_type=ProviderType.LOCAL,
                suitable_tasks=[TaskType.ANALYSIS, TaskType.SEO_ANALYSIS, TaskType.CONTENT_CLASSIFICATION],
                performance_score=6,
                speed_score=9,
                cost_score=10,
                resource_requirements="low"
            ),
            "llama3.1:8b": ModelInfo(
                name="llama3.1:8b",
                provider="ollama",
                provider_type=ProviderType.LOCAL,
                suitable_tasks=[TaskType.REASONING, TaskType.BLOG_WRITING, TaskType.SOCIAL_MEDIA],
                performance_score=7,
                speed_score=7,
                cost_score=10,
                resource_requirements="medium"
            ),
            "llama3.1:70b": ModelInfo(
                name="llama3.1:70b",
                provider="ollama",
                provider_type=ProviderType.LOCAL,
                suitable_tasks=[TaskType.COMPLEX, TaskType.RESEARCH, TaskType.CREATIVE],
                performance_score=9,
                speed_score=3,
                cost_score=10,
                resource_requirements="high"
            ),
            "deepseek-coder:6.7b": ModelInfo(
                name="deepseek-coder:6.7b",
                provider="ollama",
                provider_type=ProviderType.LOCAL,
                suitable_tasks=[TaskType.CODING],
                performance_score=8,
                speed_score=6,
                cost_score=10,
                resource_requirements="medium"
            ),
            "gemma2:9b": ModelInfo(
                name="gemma2:9b",
                provider="ollama",
                provider_type=ProviderType.LOCAL,
                suitable_tasks=[TaskType.CREATIVE, TaskType.SOCIAL_MEDIA],
                performance_score=7,
                speed_score=6,
                cost_score=10,
                resource_requirements="medium"
            ),
            
            # Cloud Models
            "gemini-2.0-flash-001": ModelInfo(
                name="gemini-2.0-flash-001",
                provider="google",
                provider_type=ProviderType.CLOUD_FREE,
                suitable_tasks=[TaskType.REASONING, TaskType.ANALYSIS, TaskType.BLOG_WRITING],
                performance_score=8,
                speed_score=8,
                cost_score=8,
                resource_requirements="low"
            ),
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider="openai",
                provider_type=ProviderType.CLOUD_PAID,
                suitable_tasks=[TaskType.COMPLEX, TaskType.REASONING, TaskType.CREATIVE, TaskType.RESEARCH],
                performance_score=9,
                speed_score=7,
                cost_score=4,
                resource_requirements="low"
            ),
            "claude-3-5-sonnet-20241022": ModelInfo(
                name="claude-3-5-sonnet-20241022",
                provider="anthropic",
                provider_type=ProviderType.CLOUD_PAID,
                suitable_tasks=[TaskType.COMPLEX, TaskType.CREATIVE, TaskType.RESEARCH, TaskType.CODING],
                performance_score=9,
                speed_score=6,
                cost_score=4,
                resource_requirements="low"
            ),
            "deepseek-chat": ModelInfo(
                name="deepseek-chat",
                provider="deepseek",
                provider_type=ProviderType.CLOUD_FREE,
                suitable_tasks=[TaskType.REASONING, TaskType.CODING, TaskType.ANALYSIS],
                performance_score=7,
                speed_score=7,
                cost_score=9,
                resource_requirements="low"
            )
        }
        return models
    
    def _load_user_preferences(self) -> Dict[str, any]:
        """Load user preferences for model selection."""
        return {
            "prefer_local": os.getenv("PREFER_LOCAL_AI", "true").lower() == "true",
            "max_cost_tier": os.getenv("MAX_COST_TIER", "free"),  # free, paid
            "performance_priority": os.getenv("PERFORMANCE_PRIORITY", "balanced"),  # speed, quality, balanced
            "resource_limit": os.getenv("RESOURCE_LIMIT", "medium")  # low, medium, high
        }
    
    def select_model_for_task(self, task_type: TaskType, available_providers: List[str], 
                             context_length: int = 4000, priority: str = "balanced") -> Tuple[str, str]:
        """Select the best model for a given task.
        
        This method implements intelligent model selection by considering task
        requirements, available providers, resource constraints, and user preferences.
        
        Args:
            task_type: The type of task to perform. Must be a valid TaskType enum value.
            available_providers: List of provider names that are currently available
                               (e.g., ["ollama", "google", "openai"]).
            context_length: Required context length in tokens. Used for filtering
                          models that can handle the required context size.
            priority: Selection priority. One of:
                     - "speed": Prioritize fastest response time
                     - "quality": Prioritize best output quality  
                     - "cost": Prioritize lowest cost/resource usage
                     - "balanced": Balance all factors (default)
        
        Returns:
            Tuple[str, str]: A tuple of (provider_name, model_name) representing
                           the selected provider and model.
                           
        Raises:
            ValueError: If task_type is invalid or priority is not recognized.
            RuntimeError: If no suitable models are found for the task.
            
        Example:
            >>> selector = SmartModelSelector()
            >>> providers = ["ollama", "google"]
            >>> provider, model = selector.select_model_for_task(
            ...     TaskType.ANALYSIS, providers, priority="speed"
            ... )
            >>> print(f"Selected: {provider}:{model}")
            
        Note:
            The selection process involves multiple stages:
            1. Filter models by task suitability and provider availability
            2. Apply user preferences and resource constraints
            3. Score models based on priority and select the highest-scoring option
            4. Fall back to default selection if no suitable models found
        """
        if not isinstance(task_type, TaskType):
            raise ValueError(f"task_type must be a TaskType enum, got {type(task_type)}")
            
        if priority not in ["speed", "quality", "cost", "balanced"]:
            raise ValueError(f"priority must be one of ['speed', 'quality', 'cost', 'balanced'], got '{priority}'")
            
        if not available_providers:
            raise ValueError("available_providers cannot be empty")
        
        try:
            logger.info(f"[SmartModelSelector] Selecting model for task: {task_type.value}")
            
            # Filter models by task suitability and availability
            suitable_models = []
            for model_name, model_info in self.models.items():
                if (task_type in model_info.suitable_tasks and 
                    model_info.provider in available_providers):
                    suitable_models.append((model_name, model_info))
            
            if not suitable_models:
                logger.warning(f"[SmartModelSelector] No suitable models found for task {task_type.value}")
                return self._fallback_selection(available_providers)
            
            # Apply user preferences
            suitable_models = self._apply_preferences(suitable_models)
            
            # Apply resource constraints
            suitable_models = self._apply_resource_constraints(suitable_models)
            
            # Score and rank models based on priority
            scored_models = self._score_models(suitable_models, priority)
            
            if scored_models:
                best_model = scored_models[0]
                model_name, model_info = best_model[1], best_model[2]
                logger.info(f"[SmartModelSelector] Selected {model_info.provider}:{model_name} (score: {best_model[0]})")
                return model_info.provider, model_name
            else:
                logger.warning(f"[SmartModelSelector] No models passed scoring, using fallback")
                return self._fallback_selection(available_providers)
                
        except Exception as e:
            logger.error(f"[SmartModelSelector] Error in model selection: {str(e)}")
            return self._fallback_selection(available_providers)
    
    def _apply_preferences(self, models: List[Tuple[str, ModelInfo]]) -> List[Tuple[str, ModelInfo]]:
        """Apply user preferences to filter models."""
        filtered = []
        
        for model_name, model_info in models:
            # Check local preference
            if (self.user_preferences["prefer_local"] and 
                model_info.provider_type == ProviderType.LOCAL):
                filtered.append((model_name, model_info))
            elif not self.user_preferences["prefer_local"]:
                # Check cost tier preference
                if (self.user_preferences["max_cost_tier"] == "free" and 
                    model_info.provider_type != ProviderType.CLOUD_PAID):
                    filtered.append((model_name, model_info))
                elif self.user_preferences["max_cost_tier"] == "paid":
                    filtered.append((model_name, model_info))
        
        return filtered if filtered else models  # Fallback to all if none match preferences
    
    def _apply_resource_constraints(self, models: List[Tuple[str, ModelInfo]]) -> List[Tuple[str, ModelInfo]]:
        """Apply resource constraints to filter models."""
        resource_limit = self.user_preferences["resource_limit"]
        
        if resource_limit == "low":
            allowed_requirements = ["low"]
        elif resource_limit == "medium":
            allowed_requirements = ["low", "medium"]
        else:  # high
            allowed_requirements = ["low", "medium", "high"]
        
        filtered = [(name, info) for name, info in models 
                   if info.resource_requirements in allowed_requirements]
        
        return filtered if filtered else models  # Fallback if none match
    
    def _score_models(self, models: List[Tuple[str, ModelInfo]], priority: str) -> List[Tuple[float, str, ModelInfo]]:
        """Score and rank models based on priority."""
        scored = []
        
        for model_name, model_info in models:
            if priority == "speed":
                score = model_info.speed_score * 0.6 + model_info.performance_score * 0.3 + model_info.cost_score * 0.1
            elif priority == "quality":
                score = model_info.performance_score * 0.7 + model_info.speed_score * 0.1 + model_info.cost_score * 0.2
            elif priority == "cost":
                score = model_info.cost_score * 0.6 + model_info.performance_score * 0.3 + model_info.speed_score * 0.1
            else:  # balanced
                score = (model_info.performance_score + model_info.speed_score + model_info.cost_score) / 3
            
            scored.append((score, model_name, model_info))
        
        # Sort by score (descending)
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored
    
    def _fallback_selection(self, available_providers: List[str]) -> Tuple[str, str]:
        """Fallback selection when no specific models are suitable."""
        # Prefer providers in this order: ollama, google, openai, anthropic, deepseek
        fallback_order = ["ollama", "google", "openai", "anthropic", "deepseek"]
        
        for provider in fallback_order:
            if provider in available_providers:
                if provider == "ollama":
                    return "ollama", "llama3.1:8b"
                elif provider == "google":
                    return "google", "gemini-2.0-flash-001"
                elif provider == "openai":
                    return "openai", "gpt-4o"
                elif provider == "anthropic":
                    return "anthropic", "claude-3-5-sonnet-20241022"
                elif provider == "deepseek":
                    return "deepseek", "deepseek-chat"
        
        # Ultimate fallback
        if available_providers:
            provider = available_providers[0]
            return provider, "default"
        
        raise RuntimeError("No providers available")
    
    def get_task_type_from_prompt(self, prompt: str, context: str = "") -> TaskType:
        """Analyze prompt to determine the most appropriate task type."""
        prompt_lower = prompt.lower()
        context_lower = context.lower()
        combined = f"{prompt_lower} {context_lower}"
        
        # SEO Analysis patterns
        if any(keyword in combined for keyword in ["seo", "keywords", "ranking", "search engine", "serp", "backlink"]):
            return TaskType.SEO_ANALYSIS
        
        # Coding patterns
        if any(keyword in combined for keyword in ["code", "programming", "function", "debug", "api", "javascript", "python"]):
            return TaskType.CODING
        
        # Analysis patterns
        if any(keyword in combined for keyword in ["analyze", "analysis", "data", "metrics", "statistics", "classify"]):
            return TaskType.ANALYSIS
        
        # Creative patterns
        if any(keyword in combined for keyword in ["creative", "marketing", "brand", "slogan", "tagline", "story"]):
            return TaskType.CREATIVE
        
        # Social Media patterns
        if any(keyword in combined for keyword in ["social media", "instagram", "twitter", "facebook", "linkedin", "post"]):
            return TaskType.SOCIAL_MEDIA
        
        # Research patterns
        if any(keyword in combined for keyword in ["research", "investigate", "comprehensive", "detailed study", "in-depth"]):
            return TaskType.RESEARCH
        
        # Blog writing patterns
        if any(keyword in combined for keyword in ["blog", "article", "content", "write", "post"]):
            return TaskType.BLOG_WRITING
        
        # Complex patterns
        if any(keyword in combined for keyword in ["strategy", "plan", "complex", "advanced", "comprehensive"]):
            return TaskType.COMPLEX
        
        # Default to reasoning for general tasks
        return TaskType.REASONING

# Global instance
_model_selector = None

def get_model_selector() -> SmartModelSelector:
    """Get the global model selector instance."""
    global _model_selector
    if _model_selector is None:
        _model_selector = SmartModelSelector()
    return _model_selector