"""OpenAI Provider Service for ALwrity Backend.

This service handles OpenAI API integrations,
migrated from the legacy lib/gpt_providers/text_generation/openai_text_gen.py
"""

import os
import time
import openai
import asyncio
from typing import Tuple
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

# Import APIKeyManager
from ..onboarding.api_key_manager import APIKeyManager

async def test_openai_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Test if the provided OpenAI API key is valid.
    
    Args:
        api_key (str): The OpenAI API key to test
        
    Returns:
        tuple[bool, str]: A tuple containing (is_valid, message)
    """
    try:
        # Create OpenAI client with the provided key
        client = openai.OpenAI(api_key=api_key)
        
        # Try to list models as a simple API test
        models = client.models.list()
        
        # If we get here, the key is valid
        return True, "OpenAI API key is valid"
        
    except openai.AuthenticationError:
        return False, "Invalid OpenAI API key"
    except openai.RateLimitError:
        return False, "Rate limit exceeded. Please try again later."
    except Exception as e:
        return False, f"Error testing OpenAI API key: {str(e)}"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def openai_chatgpt(prompt: str, model: str = "gpt-4o", temperature: float = 0.7, 
                   max_tokens: int = 4000, top_p: float = 0.9, n: int = 1, 
                   fp: int = 16, system_prompt: str = None) -> str:
    """
    Wrapper function for OpenAI's ChatGPT completion.

    Args:
        prompt (str): The input text to generate completion for.
        model (str, optional): Model to be used for the completion. Defaults to "gpt-4o".
        temperature (float, optional): Controls randomness. Lower values make responses more deterministic. Defaults to 0.7.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 4000.
        top_p (float, optional): Controls diversity. Defaults to 0.9.
        n (int, optional): Number of completions to generate. Defaults to 1.
        fp (int, optional): Frequency penalty. Defaults to 16.
        system_prompt (str, optional): System prompt for the conversation. Defaults to None.

    Returns:
        str: The generated text completion.

    Raises:
        SystemExit: If an API error, connection error, or rate limit error occurs.
    """
    # Wait for 5 seconds to comply with rate limits
    for _ in range(5):
        time.sleep(1)

    try:
        # Create variables to collect the stream of chunks
        collected_chunks = []
        collected_messages = []
        full_reply_content = None
        
        # Use APIKeyManager instead of direct environment variable access
        api_key_manager = APIKeyManager()
        api_key = api_key_manager.get_api_key("openai")
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please configure it in the onboarding process.")
        
        client = openai.OpenAI(api_key=api_key)
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            n=n,
            top_p=top_p,
            stream=True,
            frequency_penalty=fp,
            temperature=temperature
        )
        
        # Iterate through the stream of events
        for chunk in response:
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
            print(chunk.choices[0].delta.content, end="", flush=True)
        
        # Clean None in collected_messages
        collected_messages = [m for m in collected_messages if m is not None]
        full_reply_content = ''.join([m for m in collected_messages])
        
        logger.info(f"[openai_chatgpt] Generated response with {len(full_reply_content)} characters")
        return full_reply_content

    except openai.APIError as e:
        logger.error(f"OpenAI API Error: {e}")
        raise SystemExit from e
    except openai.RateLimitError as e:
        logger.error(f"OpenAI Rate Limit Error: {e}")
        raise SystemExit from e
    except openai.APIConnectionError as e:
        logger.error(f"OpenAI API Connection Error: {e}")
        raise SystemExit from e
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI API call: {e}")
        raise SystemExit from e 