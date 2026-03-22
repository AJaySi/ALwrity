import sys
import os
import json

from ..gpt_providers.text_generation.openai_text_gen import openai_text_generation
from ..gpt_providers.text_generation.gemini_pro_text import gemini_text_generation

from loguru import logger
logger.remove()
logger.add(sys.stdout,
        colorize=True,
        format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}"
    )


# FIXME: Provide num_blogs, num_faqs as inputs.
def get_blog_sections_from_websearch(search_keyword, search_results):
    """Combine the given online research and gpt blog content"""
    gpt_providers = os.environ["GPT_PROVIDER"]
    prompt = f"""
        As a SEO expert and content writer, I will provide you with a search keyword and its google search result.
        Your task is to write a blog title and 5 blog sub titles, from the given google search result.
        The subtitles should be less than 40 characters and click worthy.
        Do not explain, describe your response. Respond in json format, always name the key as 'blogSections'.

        Web Research Keyword: "{search_keyword}"
        Google search Result: "{search_results}"
        """

    if 'gemini' in gpt_providers:
        try:
            response = gemini_text_response(prompt)
            if '```' in response and '\n' in response:
                response = response.strip().split('\n')
                # Remove the first and last lines
                response = '\n'.join(response[1:-1])
                response = json.loads(response)
            return response
        except Exception as err:
            logger.error(f"Failed to get response from gemini: {err}")
            logger.error(f"Gemini Error: {response.prompt_feedback}")
            raise err
    elif 'openai' in gpt_providers:
        try:
            logger.info("Calling OpenAI LLM.")
            response = openai_chatgpt(prompt)
            return response
        except Exception as err:
            logger.error(f"Failed to get response from Openai: {err}")
            raise err
