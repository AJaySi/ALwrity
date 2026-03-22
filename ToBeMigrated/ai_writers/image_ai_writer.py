import sys
import os

from textwrap import dedent
import json
import asyncio
from pathlib import Path
from datetime import datetime
import streamlit as st

from dotenv import load_dotenv
load_dotenv(Path('../../.env'))
from loguru import logger
logger.remove()
logger.add(sys.stdout,
        colorize=True,
        format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}"
    )

from ..ai_web_researcher.firecrawl_web_crawler import scrape_url
from ..blog_metadata.get_blog_metadata import blog_metadata
from ..blog_postprocessing.save_blog_to_file import save_blog_to_file
from ..gpt_providers.text_to_image_generation.main_generate_image_from_prompt import generate_image
from ..gpt_providers.text_generation.main_text_generation import llm_text_gen
from ..gpt_providers.image_to_text_gen.gemini_image_describe import describe_image, analyze_image_with_prompt


def blog_from_image(prompt, uploaded_img):
    """
    This function will take a blog Topic to first generate sections for it
    and then generate content for each section.
    """
    # Use to store the blog in a string, to save in a *.md file.
    blog_markdown_str = None
    logger.info(f"Researching and Writing Blog on {uploaded_img} and {prompt}")
    # FIXME: Implement support for Openai.
    if not os.getenv("GEMINI_API_KEY"):
        st.error("Only Gemini supported, Open Issue ticket on github for Openai, others.")
        st.stop()

    with st.status("Started Writing from Image..", expanded=True) as status:
        st.empty()
        status.update(label=f"Researching and Writing Blog on given Image")
        try:
            blog_markdown_str = write_blog_from_image(prompt, uploaded_img)
        except Exception as err:
            st.error(f"Failed to write blog from Image - Error: {err}")
            logger.error(f"Failed to write blog from image: {err}")
            st.stop()
        status.update(label="Successfully wrote blog from image.", expanded=False, state="complete")

        try:
            status.update(label="🙎 Generating - Title, Meta Description, Tags, Categories for the content.")
            blog_title, blog_meta_desc, blog_tags, blog_categories = asyncio.run(blog_metadata(blog_markdown_str))
        except Exception as err:
            st.error(f"Failed to get blog metadata: {err}")

        try:
            status.update(label="🙎 Generating Image for the new blog.")
            generated_image_filepath = generate_image(f"{blog_title} + ' ' + {blog_meta_desc}")
        except Exception as err:
            st.warning(f"Failed in Image generation: {err}")

        saved_blog_to_file = save_blog_to_file(blog_markdown_str, blog_title, blog_meta_desc, 
                            blog_tags, blog_categories, generated_image_filepath)
        status.update(label=f"Saved the content in this file: {saved_blog_to_file}")
        logger.info(f"\n\n --------- Finished writing Blog -------------- \n")
        st.image(generated_image_filepath, caption=blog_title)
        st.markdown(f"{blog_markdown_str}")
        status.update(label=f"Finished, Review & Use your Original Content Below: {saved_blog_to_file}", state="complete")

        # Clean up the temporary file after processing (optional)
        os.remove(uploaded_img)


def write_blog_from_image(prompt, uploaded_img):
    """Combine the given online research and GPT blog content"""
    try:
        config_path = Path(os.environ["ALWRITY_CONFIG"])
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
    except Exception as err:
        logger.error(f"Error: Failed to read values from config: {err}")
        exit(1)

    blog_characteristics = config['Blog Content Characteristics']
    
    if not prompt:
        prompt = f"""
            As expert Creative Content writer, analyse the given image carefully.
            I want you to write a detailed {blog_characteristics['Blog Type']} blog post including 5 FAQs.
        
            Below are the guidelines to follow:
            1). You must respond in {blog_characteristics['Blog Language']} language.
            2). Tone and Brand Alignment: Adjust your tone, voice, personality for {blog_characteristics['Blog Tone']} audience.
            3). Make sure your response content length is of {blog_characteristics['Blog Length']} words.
        """
    logger.info("Generating blog and FAQs from image analysis.")
    
    try:
        # Use the gemini_image_describe function to analyze the image with the custom prompt
        response = analyze_image_with_prompt(uploaded_img, prompt)
        if not response:
            logger.error("Failed to get response from image analysis")
            return "Failed to generate content from image."
        return response
    except Exception as err:
        logger.error(f"Exit: Failed to get response from image analysis: {err}")
        exit(1)
