"""
Streamlit UI for FAQ Generator

This module provides a user-friendly interface for generating FAQs from various content sources.
"""

import streamlit as st
from pathlib import Path
from typing import Optional
import json
import requests
from bs4 import BeautifulSoup
import logging
import pyperclip

from .faqs_generator_blog import FAQGenerator, FAQConfig, TargetAudience, FAQStyle, SearchDepth

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard and show success message."""
    try:
        pyperclip.copy(text)
        st.success("Copied to clipboard!")
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {str(e)}")

def fetch_url_content(url):
    """Fetch and extract content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        st.error(f"Error fetching URL content: {str(e)}")
        return None

def main():
    st.title("FAQ Generator")
    st.markdown("Generate comprehensive FAQs from your content with research integration.")
    
    # Initialize session state variables if they don't exist
    if 'search_queries' not in st.session_state:
        st.session_state.search_queries = []
    if 'selected_queries' not in st.session_state:
        st.session_state.selected_queries = []
    if 'research_completed' not in st.session_state:
        st.session_state.research_completed = False
    if 'research_results' not in st.session_state:
        st.session_state.research_results = {}
    if 'faq_config' not in st.session_state:
        st.session_state.faq_config = None
    if 'generator' not in st.session_state:
        st.session_state.generator = FAQGenerator()
    if 'generated_faqs' not in st.session_state:
        st.session_state.generated_faqs = None
    if 'output_format' not in st.session_state:
        st.session_state.output_format = "Preview"
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Basic settings
        num_faqs = st.slider("Number of FAQs", 1, 20, 5)
        target_audience = st.selectbox(
            "Target Audience",
            [audience.value for audience in TargetAudience]
        )
        faq_style = st.selectbox(
            "FAQ Style",
            [style.value for style in FAQStyle]
        )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            include_emojis = st.checkbox("Include Emojis", value=True)
            include_code_examples = st.checkbox("Include Code Examples", value=True)
            include_references = st.checkbox("Include References", value=True)
            
            search_depth = st.selectbox(
                "Search Depth",
                [depth.value for depth in SearchDepth]
            )
            time_range = st.selectbox(
                "Time Range",
                ["last_month", "last_6_months", "last_year", "all_time"]
            )
            language = st.text_input("Language", value="English")
    
    # Main content area
    content_type = st.radio(
        "Content Source",
        ["Direct Input", "File Upload", "URL"]
    )
    
    content = ""
    if content_type == "Direct Input":
        content = st.text_area("Enter your content", height=300)
    
    elif content_type == "URL":
        url = st.text_input("Enter URL")
        if url:
            content = fetch_url_content(url)
            if content:
                st.text_area("Extracted Content", content, height=300)
    
    # Step 1: Generate search queries
    if content and not st.session_state.search_queries:
        if st.button("Generate Search Queries"):
            with st.spinner("Generating search queries..."):
                search_queries = st.session_state.generator.generate_search_queries(content)
                if search_queries:
                    st.session_state.search_queries = search_queries
                    st.session_state.selected_queries = []  # Reset selected queries
                    st.session_state.research_completed = False  # Reset research status
                    st.session_state.research_results = {}  # Reset research results
                    st.session_state.faq_config = None  # Reset config
                    st.session_state.generated_faqs = None  # Reset generated FAQs
                    st.success("Search queries generated successfully!")
    
    # Step 2: Display and select search queries
    if st.session_state.search_queries:
        st.subheader("Select Search Queries")
        st.info("Select the queries you want to use for web research. You can select multiple queries.")
        
        # Create checkboxes for each search query
        selected_queries = []
        for query in st.session_state.search_queries:
            if st.checkbox(query, key=f"query_{query}", value=query in st.session_state.selected_queries):
                selected_queries.append(query)
        
        # Update selected queries in session state
        st.session_state.selected_queries = selected_queries
        
        # Step 3: Do web research
        if st.session_state.selected_queries and not st.session_state.research_completed:
            if st.button("Do Web Research"):
                try:
                    # Create config with selected queries
                    config = FAQConfig(
                        num_faqs=num_faqs,
                        target_audience=TargetAudience(target_audience),
                        faq_style=FAQStyle(faq_style),
                        include_emojis=include_emojis,
                        include_code_examples=include_code_examples,
                        include_references=include_references,
                        search_depth=SearchDepth(search_depth),
                        time_range=time_range,
                        language=language,
                        selected_search_queries=selected_queries
                    )
                    
                    # Store config in session state
                    st.session_state.faq_config = config
                    
                    # Update generator with config
                    st.session_state.generator.config = config
                    
                    # Do research
                    with st.spinner("Conducting web research..."):
                        research_results = st.session_state.generator._conduct_research(content)
                        st.session_state.research_completed = True
                        st.session_state.research_results = research_results
                        st.success("Web research completed successfully!")
                        
                        # Display research results
                        st.subheader("Research Results")
                        for query, results in research_results.items():
                            with st.expander(f"Results for: {query}"):
                                if isinstance(results, dict):
                                    st.json(results)
                                else:
                                    st.text(results)
                
                except Exception as e:
                    st.error(f"Error during web research: {str(e)}")
                    st.error("Please try again with different search queries or adjust the search depth.")
        
        # Step 4: Generate FAQs
        if st.session_state.research_completed and st.session_state.research_results and st.session_state.faq_config:
            if st.button("Generate FAQs"):
                try:
                    # Update generator with stored config
                    st.session_state.generator.config = st.session_state.faq_config
                    
                    # Generate FAQs
                    with st.spinner("Generating FAQs..."):
                        logger.info("Starting FAQ generation...")
                        faqs = st.session_state.generator.generate_faqs(content)
                        logger.info(f"Generated {len(faqs) if faqs else 0} FAQs")
                        
                        if not faqs:
                            st.error("No FAQs were generated. Please try again.")
                            return
                            
                        st.session_state.generated_faqs = faqs
                        st.success("FAQs generated successfully!")
                
                except Exception as e:
                    logger.error(f"Error generating FAQs: {str(e)}")
                    st.error(f"Error generating FAQs: {str(e)}")
                    st.error("Please try again or adjust your settings.")
        
        # Display generated FAQs if they exist
        if st.session_state.generated_faqs:
            st.subheader("Generated FAQs")
            
            # Output format selection
            output_format = st.radio(
                "Output Format",
                ["Preview", "Markdown", "HTML", "JSON"],
                key="output_format"
            )
            
            # Create columns for copy and download buttons
            col1, col2 = st.columns(2)
            
            if output_format == "Preview":
                # Create a formatted text for copying
                preview_text = ""
                for i, faq in enumerate(st.session_state.generated_faqs, 1):
                    preview_text += f"{i}. {faq.question}\n"
                    preview_text += f"{faq.answer}\n\n"
                    if faq.code_example:
                        preview_text += f"Code Example:\n{faq.code_example}\n\n"
                    if faq.references:
                        preview_text += "References:\n"
                        for ref in faq.references:
                            preview_text += f"- {ref['source']}\n"
                    preview_text += "\n"
                
                with col1:
                    if st.button("Copy to Clipboard", key="copy_preview"):
                        copy_to_clipboard(preview_text)
                
                # Display the FAQs
                for i, faq in enumerate(st.session_state.generated_faqs, 1):
                    with st.expander(f"{i}. {faq.question}"):
                        st.markdown(faq.answer)
                        if faq.code_example:
                            st.code(faq.code_example)
                        if faq.references:
                            st.markdown("**References:**")
                            for ref in faq.references:
                                st.markdown(f"- {ref['source']}")
            
            elif output_format == "Markdown":
                markdown_output = st.session_state.generator.to_markdown()
                st.code(markdown_output, language="markdown")
                
                with col1:
                    if st.button("Copy to Clipboard", key="copy_markdown"):
                        copy_to_clipboard(markdown_output)
                with col2:
                    st.download_button(
                        "Download Markdown",
                        markdown_output,
                        file_name="faqs.md",
                        mime="text/markdown"
                    )
            
            elif output_format == "HTML":
                html_output = st.session_state.generator.to_html()
                st.code(html_output, language="html")
                
                with col1:
                    if st.button("Copy to Clipboard", key="copy_html"):
                        copy_to_clipboard(html_output)
                with col2:
                    st.download_button(
                        "Download HTML",
                        html_output,
                        file_name="faqs.html",
                        mime="text/html"
                    )
            
            elif output_format == "JSON":
                json_output = json.dumps([faq.__dict__ for faq in st.session_state.generated_faqs], indent=2)
                st.code(json_output, language="json")
                
                with col1:
                    if st.button("Copy to Clipboard", key="copy_json"):
                        copy_to_clipboard(json_output)
                with col2:
                    st.download_button(
                        "Download JSON",
                        json_output,
                        file_name="faqs.json",
                        mime="application/json"
                    )

if __name__ == "__main__":
    main() 