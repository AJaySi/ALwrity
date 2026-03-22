import sys
import os

from textwrap import dedent
import json
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
from ..blog_metadata.get_blog_metadata import blog_metadata, run_async
from ..blog_postprocessing.save_blog_to_file import save_blog_to_file
from ..gpt_providers.text_to_image_generation.main_generate_image_from_prompt import generate_image
from ..gpt_providers.text_generation.main_text_generation import llm_text_gen


def blog_from_url(weburl):
    """
    This function will take a blog Topic to first generate sections for it
    and then generate content for each section.
    """
    # Use to store the blog in a string, to save in a *.md file.
    blog_markdown_str = None
    tavily_search_result = None
    # Initializing the variables
    blog_title = None
    blog_meta_desc = None
    blog_tags = None
    blog_categories = None

    logger.info(f"Researching and Writing Blog on: {weburl}")
    with st.status("Started Writing..", expanded=True) as status:
        st.empty()
        status.update(label=f"Researching and Writing Blog on: {weburl}")
        try:
            scraped_text = scrape_url(weburl)
            #logger.info(scraped_text)
        except Exception as err:
            st.error(f"Failed to scrape web page from url-{weburl} - Error: {err}")
            logger.error(f"Failed in web research: {err}")
            st.stop()
        status.update(label=f"Successfully Scraped/Fetched url: {weburl}", expanded=False, state="complete")

    with st.status(f"Started Writing blog from {weburl}..", expanded=True) as status:
        # Do Tavily AI research to augument the above blog.
        try:
            blog_markdown_str = write_blog_from_weburl(scraped_text)
            status.update(label="Finished Writing Blog From: {weburl}")
        except Exception as err:
            logger.error(f"Failed to write blog from: {weburl}")
            st.error(f"Failed to write blog from: {weburl}")
            st.stop()

        try:
            status.update(label="🙎 Generating - Title, Meta Description, Tags, Categories for the content.")
            blog_title, blog_meta_desc, blog_tags, blog_categories = run_async(blog_metadata(blog_markdown_str))
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
        
        logger.info(f"\n\n --------- Finished writing Blog for : {weburl} -------------- \n")
        if generated_image_filepath:
            st.image(generated_image_filepath)
        
        st.markdown(f"{blog_markdown_str}")
        status.update(label=f"Finished, Review & Use your Original Content Below: {saved_blog_to_file}", state="complete")
        

def write_blog_from_weburl(scraped_website):
    """Combine the given online research and GPT blog content"""
    try:
        config_path = Path(os.environ["ALWRITY_CONFIG"])
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
    except Exception as err:
        logger.error(f"Error: Failed to read values from config: {err}")
        exit(1)

    blog_characteristics = config['Blog Content Characteristics']
    
    prompt = f"""
        As expert Creative Content writer, I will provide you with scraped website content.
        I want you to write a detailed {blog_characteristics['Blog Type']} blog post including 5 FAQs.
        
        Below are the guidelines to follow:
        1). You must respond in {blog_characteristics['Blog Language']} language.
        2). Tone and Brand Alignment: Adjust your tone, voice, personality for {blog_characteristics['Blog Tone']} audience.
        3). Make sure your response content length is of {blog_characteristics['Blog Length']} words.
        4). Include FAQs from 'People also Ask' section of provided context 'google search result'.

        I want the post to offer unique insights, relatable examples, and a fresh perspective on the topic.
        \n\n
        Website Content:
        '''{scraped_website}'''
        """ 
    logger.info("Generating blog and FAQs from Google web search results.")
    
    try:
        response = llm_text_gen(prompt)
        return response
    except Exception as err:
        logger.error(f"Exit: Failed to get response from LLM: {err}")
        exit(1)
