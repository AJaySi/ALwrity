import os
import datetime #I wish
import sys
from textwrap import dedent
from tqdm import tqdm, trange
import time

from pytubefix import YouTube
import tempfile
from html2image import Html2Image

from loguru import logger
logger.remove()
logger.add(sys.stdout,
        colorize=True,
        format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}"
    )

from ...ai_web_researcher.gpt_online_researcher import do_google_serp_search
from ..ai_blog_writer.blog_from_google_serp import blog_with_research
from ...blog_metadata.get_blog_metadata import blog_metadata
from ...blog_postprocessing.save_blog_to_file import save_blog_to_file
from ...gpt_providers.audio_to_text_generation.stt_audio_blog import speech_to_text
from ...gpt_providers.text_generation.main_text_generation import llm_text_gen


def youtube_to_blog(video_url):
    """Function to transcribe a given youtube url """
    try:
        # Starting the speech-to-text process
        logger.info("Starting with Speech to Text.")
        audio_text, audio_title = speech_to_text(video_url)
    except Exception as e:
        logger.error(f"Error in speech_to_text: {e}")
        sys.exit(1)  # Exit the program due to error in speech_to_text

    try:
        # Summarizing the content of the YouTube video
        audio_blog_content = summarize_youtube_video(audio_text)
        logger.info("Successfully converted given URL to blog article.")
        return audio_blog_content, audio_title
    except Exception as e:
        logger.error(f"Error in summarize_youtube_video: {e}")
        return False


def summarize_youtube_video(user_content):
    """Generates a summary of a YouTube video using OpenAI GPT-3 and displays a progress bar. 
    Args:
      video_link: The URL of the YouTube video to summarize.
    Returns:
      A string containing the summary of the video.
    """

    logger.info("Start summarize_youtube_video..")
    prompt = f"""
        You are an expert copywriter specializing in digital content writing. I will provide you with a transcript. 
        Your task is to transform a given transcript into a well-structured and informative blog article. 
        Please follow the below objectives:

        1. Master the Transcript: Understand main ideas, key points, and the core message.
        2. Sentence Structure: Rephrase while preserving logical flow and coherence. Dont quote anyone from video.
        3. Note: Check if the transcript is about programming, then include code examples and snippets in your article.
        4. Write Unique Content: Avoid direct copying; rewrite in your own words. 
        5. REMEMBER to avoid direct quoting and maintain uniqueness.
        6. Proofread: Check for grammar, spelling, and punctuation errors.
        7. Use Creative and Human-like Style: Incorporate contractions, idioms, transitional phrases, interjections, and colloquialisms.        8. Avoid repetitive phrases and unnatural sentence structures.
        9. Ensure Uniqueness: Guarantee the article is plagiarism-free.
        10. Punctuation: Use appropriate question marks at the end of questions.
        11. Pass AI Detection Tools: Create content that easily passes AI plagiarism detection tools.
        12. Rephrase words like 'video, youtube, channel' with 'article, blog' and such suitable words.

        Follow the above guidelines to create a well-optimized, unique, and informative article,
        that will rank well in search engine results and engage readers effectively.
        Follow above guidelines to craft a blog content from the following transcript:\n{user_content}
        """
    try:
        response = llm_text_gen(prompt)
        return response
    except Exception as err:
        logger.error(f"Failed to summarize_youtube_video: {err}")
        exit(1)


def generate_audio_blog(audio_input):
    """Takes a list of youtube videos and generates blog for each one of them.
    """
    # Use to store the blog in a string, to save in a *.md file.
    blog_markdown_str = ""
    try:
        logger.info(f"Starting to write blog on URL: {audio_input}")
        yt_blog, yt_title = youtube_to_blog(audio_input)
    except Exception as e:
        logger.error(f"Error in youtube_to_blog: {e}")
        sys.exit(1)

    try:
        logger.info("Starting with online research for URL title.")
        research_report = do_google_serp_search(yt_title)
        print(research_report)
    except Exception as e:
        logger.error(f"Error in do_online_research: {e}")
        sys.exit(1)

    try:
        # Note: Check if the order of input matters for your function
        logger.info("Preparing a blog content from audio script and online research content...")
        blog_markdown_str = blog_with_research(research_report, yt_blog)
    except Exception as e:
        logger.error(f"Error in blog_with_research: {e}")
        sys.exit(1)

    try:       
        import asyncio 
        # blog_metadata now returns 6 values: title, desc, tags, categories, hashtags, slug
        blog_title, blog_meta_desc, blog_tags, blog_categories, blog_hashtags, blog_slug = asyncio.run(blog_metadata(blog_markdown_str))
    except Exception as err:
        logger.error(f"Failed to generate blog metadata: {err}")
        # Set defaults in case of failure
        blog_title = "Blog Article"
        blog_meta_desc = "An informative blog post"
        blog_tags = "content, blog"
        blog_categories = "General, Information" 
        blog_hashtags = "#content #blog"
        blog_slug = "blog-article"

    try:
        # TBD: Save the blog content as a .md file. Markdown or HTML ?
        # Initialize generated_image_filepath to None since it's not generated in this function
        generated_image_filepath = None
        save_blog_to_file(blog_markdown_str, blog_title, blog_meta_desc, blog_tags, blog_categories, generated_image_filepath)
    except Exception as err:
        logger.error(f"Failed to save final blog in a file: {err}")

    blog_frontmatter = dedent(f"""\n\n\n\
                ---
                title: {blog_title}
                categories: [{blog_categories}]
                tags: [{blog_tags}]
                Meta description: {blog_meta_desc.replace(":", "-")}
                ---\n\n""")
    logger.info(f"{blog_frontmatter}{blog_markdown_str}")
    logger.info(f"\n\n ################ Finished writing Blog for : {audio_input} #################### \n")
