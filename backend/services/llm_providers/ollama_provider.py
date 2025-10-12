"""
Ollama Provider Module for ALwrity

This module provides functions for interacting with local Ollama API endpoints,
enabling the use of open-source models like Llama, Gemma, DeepSeek, etc.
running locally on the user's machine.

Key Features:
- Local AI model inference for privacy and cost savings
- Support for multiple open-source models (Llama, Gemma, DeepSeek, etc.)
- Automatic model availability detection
- Smart model selection based on task requirements
- Retry logic and comprehensive error handling
- Support for both text generation and structured JSON output

Model Categories:
1. Analysis Models (faster, smaller): llama3.2:3b, gemma2:2b, qwen2.5:3b
2. Reasoning Models (larger, more capable): llama3.1:8b, deepseek-coder:6.7b, qwen2.5:7b
3. Complex Task Models (largest): llama3.1:70b, qwen2.5:14b, deepseek-coder:33b

Best Practices:
- Use smaller models for data analysis and simple tasks
- Use larger models for complex reasoning and creative writing
- Implement graceful fallbacks when models are unavailable
- Monitor local system resources and adjust accordingly

Usage Examples:
    # Text generation with automatic model selection
    result = ollama_text_response(prompt, task_type="analysis")
    
    # Structured JSON response
    schema = {"type": "object", "properties": {...}}
    result = ollama_structured_json_response(prompt, schema, task_type="complex")

Dependencies:
- requests (for API communication)
- json (for response parsing)
- tenacity (for retry logic)
- loguru (for logging)
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

# Default Ollama configuration
DEFAULT_OLLAMA_ENDPOINT = "http://localhost:11434"
DEFAULT_MODELS = {
    "analysis": "llama3.2:3b",      # Fast model for data analysis
    "reasoning": "llama3.1:8b",     # Balanced model for general tasks
    "complex": "llama3.1:70b",      # Large model for complex tasks
    "coding": "deepseek-coder:6.7b", # Specialized for code generation
    "creative": "gemma2:9b"         # Good for creative writing
}

class OllamaProvider:
    """Ollama provider for local AI model inference.
    
    This class provides interface for interacting with Ollama API endpoints,
    enabling the use of open-source models running locally on the user's machine.
    
    Attributes:
        endpoint (str): The Ollama API endpoint URL.
        available_models (List[str]): List of available models on the Ollama instance.
        is_available (bool): Whether the Ollama service is available and running.
        
    Example:
        >>> provider = OllamaProvider()
        >>> if provider.is_available:
        ...     model = provider.get_best_model_for_task("analysis")
        ...     print(f"Selected model: {model}")
    """
    
    def __init__(self, endpoint: Optional[str] = None) -> None:
        """Initialize Ollama provider with endpoint.
        
        Args:
            endpoint: Optional custom endpoint URL. If None, uses environment variable
                     OLLAMA_ENDPOINT or falls back to default localhost:11434.
        
        Raises:
            ConnectionError: If unable to connect to Ollama service after initialization.
        """
        self.endpoint = endpoint or os.getenv("OLLAMA_ENDPOINT", DEFAULT_OLLAMA_ENDPOINT)
        self.available_models: List[str] = []
        self.is_available = self._check_availability()
        if self.is_available:
            self._load_available_models()
    
    def _check_availability(self) -> bool:
        """Check if Ollama is available and running.
        
        Returns:
            bool: True if Ollama service is responding, False otherwise.
            
        Note:
            This method makes a network request to the Ollama API /tags endpoint
            to verify service availability.
        """
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"[OllamaProvider] Ollama not available at {self.endpoint}: {str(e)}")
            return False
    
    def _load_available_models(self) -> None:
        """Load list of available models from Ollama.
        
        This method queries the Ollama API to get a list of installed models
        and updates the available_models attribute.
        
        Raises:
            requests.RequestException: If API request fails.
            ValueError: If API response format is unexpected.
        """
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
                logger.info(f"[OllamaProvider] Found {len(self.available_models)} available models")
            else:
                logger.warning(f"[OllamaProvider] Failed to load models: {response.status_code}")
        except Exception as e:
            logger.error(f"[OllamaProvider] Error loading models: {str(e)}")
    
    def get_best_model_for_task(self, task_type: str = "reasoning") -> str:
        """Select the best available model for a given task type.
        
        This method implements fallback logic to select the most appropriate
        model based on task requirements and model availability.
        
        Args:
            task_type: The type of task to optimize for. Must be one of:
                      "analysis", "reasoning", "complex", "coding", "creative".
                      
        Returns:
            str: The name of the selected model.
            
        Raises:
            RuntimeError: If no models are available on the Ollama instance.
            ValueError: If task_type is not recognized.
            
        Example:
            >>> provider = OllamaProvider()
            >>> model = provider.get_best_model_for_task("analysis")
            >>> print(f"Best model for analysis: {model}")
        """
        if task_type not in DEFAULT_MODELS:
            logger.warning(f"[OllamaProvider] Unknown task type '{task_type}', using 'reasoning'")
            task_type = "reasoning"
            
        preferred_model = DEFAULT_MODELS.get(task_type, DEFAULT_MODELS["reasoning"])
        
        # Check if preferred model is available
        if preferred_model in self.available_models:
            return preferred_model
        
        # Fallback to any available model in order of preference
        fallback_order = [
            DEFAULT_MODELS["reasoning"],
            DEFAULT_MODELS["analysis"], 
            DEFAULT_MODELS["complex"],
            DEFAULT_MODELS["coding"],
            DEFAULT_MODELS["creative"]
        ]
        
        for model in fallback_order:
            if model in self.available_models:
                logger.info(f"[OllamaProvider] Using fallback model {model} for task {task_type}")
                return model
        
        # If no default models available, use first available model
        if self.available_models:
            model = self.available_models[0]
            logger.info(f"[OllamaProvider] Using first available model {model} for task {task_type}")
            return model
        
        raise RuntimeError("No models available in Ollama")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _make_request(self, model: str, prompt: str, system_prompt: Optional[str] = None, 
                     temperature: float = 0.7, max_tokens: int = 4000,
                     format_json: bool = False) -> requests.Response:
        """Make a request to Ollama API with retry logic.
        
        This method sends a generation request to the Ollama API with automatic
        retry logic for handling transient failures.
        
        Args:
            model: The name of the model to use for generation.
            prompt: The input prompt for text generation.
            system_prompt: Optional system prompt for model instructions.
            temperature: Sampling temperature between 0.0 and 1.0. Higher values
                        make output more random, lower values more deterministic.
            max_tokens: Maximum number of tokens to generate.
            format_json: Whether to request JSON-formatted output.
            
        Returns:
            requests.Response: The HTTP response from the Ollama API.
            
        Raises:
            requests.RequestException: If all retry attempts fail.
            requests.Timeout: If the request times out.
            ValueError: If model parameter is invalid.
            
        Note:
            This method uses exponential backoff retry logic with up to 3 attempts.
            The timeout is set to 300 seconds (5 minutes) to accommodate large models.
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
            
        url = f"{self.endpoint}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if format_json:
            payload["format"] = "json"
        
        response = requests.post(url, json=payload, timeout=300)  # 5 minute timeout
        response.raise_for_status()
        return response

def ollama_text_response(prompt: str, model: Optional[str] = None, temperature: float = 0.7,
                        max_tokens: int = 4000, system_prompt: Optional[str] = None,
                        task_type: str = "reasoning") -> str:
    """Generate text response using Ollama.
    
    This function provides a high-level interface for generating text using
    local Ollama models with automatic model selection and error handling.
    
    Args:
        prompt: The input prompt for text generation. Must be non-empty.
        model: Specific model to use. If None, auto-selects based on task_type.
        temperature: Sampling temperature between 0.0 and 1.0. Higher values
                    make output more random, lower values more deterministic.
        max_tokens: Maximum number of tokens to generate. Must be positive.
        system_prompt: Optional system prompt for model instructions.
        task_type: Type of task for model selection. One of: "analysis", 
                  "reasoning", "complex", "coding", "creative".
    
    Returns:
        str: Generated text response from the model.
        
    Raises:
        RuntimeError: If Ollama is not available or no models are installed.
        ValueError: If prompt is empty or parameters are invalid.
        requests.RequestException: If API request fails after retries.
        
    Example:
        >>> response = ollama_text_response(
        ...     prompt="Explain quantum computing",
        ...     task_type="analysis"
        ... )
        >>> print(f"Generated: {response[:100]}...")
        
    Note:
        This function automatically handles model selection, retries, and
        graceful error handling. For structured output, use 
        ollama_structured_json_response() instead.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
        
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
        
    if not (0.0 <= temperature <= 1.0):
        raise ValueError("temperature must be between 0.0 and 1.0")
    
    try:
        logger.info(f"[ollama_text_response] Starting text generation with task_type: {task_type}")
        
        # Initialize provider
        provider = OllamaProvider()
        if not provider.is_available:
            raise RuntimeError("Ollama is not available. Please ensure Ollama is installed and running.")
        
        # Select model
        if model is None:
            model = provider.get_best_model_for_task(task_type)
        elif model not in provider.available_models:
            logger.warning(f"[ollama_text_response] Requested model {model} not available, auto-selecting")
            model = provider.get_best_model_for_task(task_type)
        
        logger.info(f"[ollama_text_response] Using model: {model}")
        
        # Make request
        response = provider._make_request(
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Parse response
        result = response.json()
        generated_text = ""
        
        # Handle different response formats
        if "response" in result and result["response"].strip():
            generated_text = result["response"].strip()
        elif "thinking" in result and result["thinking"].strip():
            # Some models (like qwen3) put the actual response in "thinking" field
            generated_text = result["thinking"].strip()
        
        if generated_text:
            logger.info(f"[ollama_text_response] Successfully generated {len(generated_text)} characters")
            return generated_text
        else:
            logger.error(f"[ollama_text_response] No valid response found in: {result}")
            raise RuntimeError("No valid response from Ollama model")
            
    except Exception as e:
        logger.error(f"[ollama_text_response] Error: {str(e)}")
        raise

def ollama_structured_json_response(prompt: str, schema: Dict[str, Any], model: Optional[str] = None,
                                   temperature: float = 0.3, max_tokens: int = 8192,
                                   system_prompt: Optional[str] = None, task_type: str = "reasoning") -> str:
    """Generate structured JSON response using Ollama.
    
    This function generates JSON-formatted responses that conform to a specified
    schema, useful for structured data extraction and API responses.
    
    Args:
        prompt: The input prompt for JSON generation. Must be non-empty.
        schema: JSON schema dictionary defining the expected output structure.
                Must be a valid JSON schema with type and properties.
        model: Specific model to use. If None, auto-selects based on task_type.
        temperature: Sampling temperature between 0.0 and 1.0. Lower values
                    (0.1-0.3) recommended for more consistent JSON structure.
        max_tokens: Maximum number of tokens to generate. Must be positive.
        system_prompt: Optional system prompt for additional instructions.
        task_type: Type of task for model selection. One of: "analysis",
                  "reasoning", "complex", "coding", "creative".
    
    Returns:
        str: JSON string response conforming to the provided schema.
        
    Raises:
        RuntimeError: If Ollama is not available or no models are installed.
        ValueError: If prompt is empty, schema is invalid, or parameters are invalid.
        requests.RequestException: If API request fails after retries.
        json.JSONDecodeError: If the model response is not valid JSON.
        
    Example:
        >>> schema = {
        ...     "type": "object",
        ...     "properties": {
        ...         "title": {"type": "string"},
        ...         "summary": {"type": "string"},
        ...         "tags": {"type": "array", "items": {"type": "string"}}
        ...     }
        ... }
        >>> response = ollama_structured_json_response(
        ...     prompt="Analyze this blog post about AI",
        ...     schema=schema,
        ...     task_type="analysis"
        ... )
        >>> data = json.loads(response)
        
    Note:
        Lower temperature values (0.1-0.3) are recommended for structured output
        to ensure consistent JSON formatting. The function automatically enhances
        the prompt and system prompt to encourage JSON-only responses.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
        
    if not schema or not isinstance(schema, dict):
        raise ValueError("Schema must be a non-empty dictionary")
        
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")
        
    if not (0.0 <= temperature <= 1.0):
        raise ValueError("temperature must be between 0.0 and 1.0")
    
    try:
        logger.info(f"[ollama_structured_json_response] Starting JSON generation with task_type: {task_type}")
        
        # Initialize provider
        provider = OllamaProvider()
        if not provider.is_available:
            raise RuntimeError("Ollama is not available. Please ensure Ollama is installed and running.")
        
        # Select model
        if model is None:
            model = provider.get_best_model_for_task(task_type)
        elif model not in provider.available_models:
            logger.warning(f"[ollama_structured_json_response] Requested model {model} not available, auto-selecting")
            model = provider.get_best_model_for_task(task_type)
        
        logger.info(f"[ollama_structured_json_response] Using model: {model}")
        
        # Enhance prompt for JSON output
        json_prompt = f"""
{prompt}

Please respond with valid JSON only, following this exact schema:
{json.dumps(schema, indent=2)}

Important: Return only the JSON object, no additional text or formatting.
"""
        
        # Enhance system prompt for JSON
        json_system_prompt = system_prompt or ""
        json_system_prompt += "\n\nYou must respond with valid JSON only. Do not include any text outside the JSON object."
        
        # Make request with JSON formatting
        response = provider._make_request(
            model=model,
            prompt=json_prompt,
            system_prompt=json_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            format_json=True
        )
        
        # Parse response
        result = response.json()
        json_response = ""
        
        # Handle different response formats
        if "response" in result and result["response"].strip():
            json_response = result["response"].strip()
        elif "thinking" in result and result["thinking"].strip():
            # Some models (like qwen3) put the actual response in "thinking" field
            json_response = result["thinking"].strip()
        
        if json_response:
            # Validate JSON
            try:
                json.loads(json_response)
                logger.info(f"[ollama_structured_json_response] Successfully generated valid JSON")
                return json_response
            except json.JSONDecodeError as e:
                logger.warning(f"[ollama_structured_json_response] Invalid JSON, attempting to fix: {e}")
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', json_response, re.DOTALL)
                if json_match:
                    cleaned_json = json_match.group()
                    try:
                        json.loads(cleaned_json)
                        return cleaned_json
                    except json.JSONDecodeError:
                        pass
                
                # If all else fails, return raw response
                logger.error(f"[ollama_structured_json_response] Could not parse valid JSON from response")
                return json_response
        else:
            logger.error(f"[ollama_structured_json_response] No valid response found in: {result}")
            raise RuntimeError("No valid response from Ollama model")
            
    except Exception as e:
        logger.error(f"[ollama_structured_json_response] Error: {str(e)}")
        raise

def check_ollama_availability() -> bool:
    """Check if Ollama is available and running.
    
    This function attempts to connect to the Ollama service and verify
    that it's responding to API requests.
    
    Returns:
        bool: True if Ollama service is available and responding, False otherwise.
        
    Example:
        >>> if check_ollama_availability():
        ...     print("Ollama is ready to use")
        ... else:
        ...     print("Please start Ollama service")
        
    Note:
        This function creates a temporary OllamaProvider instance to check
        availability. It does not raise exceptions on connection failures.
    """
    provider = OllamaProvider()
    return provider.is_available

def get_available_models() -> List[str]:
    """Get list of available Ollama models.
    
    This function returns a list of all models currently installed and
    available in the local Ollama instance.
    
    Returns:
        List[str]: List of available model names. Empty list if Ollama
                  is not available or no models are installed.
                  
    Example:
        >>> models = get_available_models()
        >>> if models:
        ...     print(f"Available models: {', '.join(models)}")
        ... else:
        ...     print("No models available. Please install some models.")
        
    Note:
        This function returns an empty list rather than raising an exception
        if Ollama is not available, making it safe to use for availability checks.
    """
    provider = OllamaProvider()
    return provider.available_models if provider.is_available else []

def suggest_models_for_download() -> Dict[str, str]:
    """Suggest models to download for different task types.
    
    This function returns a dictionary mapping task types to recommended
    Ollama pull commands for optimal performance in each use case.
    
    Returns:
        Dict[str, str]: Mapping of task types to ollama pull commands.
                       Keys are task types, values are shell commands.
                       
    Example:
        >>> suggestions = suggest_models_for_download()
        >>> for task, command in suggestions.items():
        ...     print(f"{task}: {command}")
        analysis: ollama pull llama3.2:3b
        reasoning: ollama pull llama3.1:8b
        ...
        
    Note:
        These are recommendations based on model performance characteristics.
        Users may choose different models based on their specific requirements
        and available system resources.
    """
    return {
        "analysis": "ollama pull llama3.2:3b",
        "reasoning": "ollama pull llama3.1:8b", 
        "complex": "ollama pull llama3.1:70b",
        "coding": "ollama pull deepseek-coder:6.7b",
        "creative": "ollama pull gemma2:9b"
    }
