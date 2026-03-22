"""
YouTube Tags Generator Module

This module provides functionality for generating and optimizing YouTube video tags.
"""

import streamlit as st
import time
import logging
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from pytrends.request import TrendReq
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_tags_generator')

def get_pytrends_data(keyword):
    """Get trending data using PyTrends with simplified, reliable approach."""
    logger.info(f"Getting PyTrends data for: '{keyword}'")
    
    # Initialize empty results
    results = {
        'topics': [],
        'queries': [],
        'trending': []
    }
    
    try:
        # Initialize PyTrends with minimal configuration
        pytrends = TrendReq(hl='en-US', tz=360)
        time.sleep(1)  # Basic rate limiting
        
        # 1. Get suggestions (most reliable method)
        try:
            suggestions = pytrends.suggestions(keyword)
            if suggestions:
                results['trending'] = [sugg['title'] for sugg in suggestions if sugg['title']][:3]
        except Exception as e:
            logger.warning(f"Error getting suggestions: {str(e)}")
        
        # 2. Get trending searches as backup
        if not results['trending']:
            try:
                trending = pytrends.trending_searches(pn='united_states')
                if not trending.empty:
                    results['trending'] = trending.head(3).values.tolist()
            except Exception as e:
                logger.warning(f"Error getting trending searches: {str(e)}")
        
        # 3. Use keyword variations as fallback
        if not any(results.values()):
            results['trending'] = [keyword]
            results['queries'] = [keyword.lower(), keyword.title()]
            results['topics'] = [keyword.capitalize()]
        
        return results
        
    except Exception as e:
        logger.error(f"Error in PyTrends: {str(e)}")
        # Return basic keyword variations as fallback
        return {
            'topics': [keyword.capitalize()],
            'queries': [keyword.lower()],
            'trending': [keyword]
        }

def get_comprehensive_trends(title, description):
    """Get trending data from title and description keywords."""
    logger.info(f"Getting comprehensive trends for title: '{title}'")
    
    # Extract main keywords (only words longer than 3 chars)
    words = [w for w in title.split() if len(w) > 3]
    if description:
        desc_words = [w for w in description.split() if len(w) > 3]
        words.extend(desc_words)
    
    # Remove duplicates and limit to 2 keywords to prevent rate limiting
    keywords = list(dict.fromkeys(words))[:2]
    
    # Get trending data for main keywords
    all_trends = {
        'topics': [],
        'queries': [],
        'trending': []
    }
    
    for keyword in keywords:
        try:
            trends = get_pytrends_data(keyword)
            for key in all_trends:
                if trends[key]:
                    all_trends[key].extend(trends[key])
            time.sleep(1)  # Rate limiting between keywords
        except Exception as e:
            logger.warning(f"Error getting trends for keyword '{keyword}': {str(e)}")
            continue
    
    # Remove duplicates while preserving order
    for key in all_trends:
        seen = set()
        all_trends[key] = [x for x in all_trends[key] if x and not (x.lower() in seen or seen.add(x.lower()))][:5]
    
    return all_trends

def generate_tags_from_title_description(title, description, num_tags=10):
    """Generate relevant tags from video title, description, and trending data."""
    logger.info(f"Generating tags for title: '{title}'")
    
    # Get comprehensive trending data
    trends = get_comprehensive_trends(title, description)
    
    # Create a comprehensive context for GPT
    trend_context = f"""
    Related Topics: {', '.join(trends['topics'][:10])}
    Related Queries: {', '.join(trends['queries'][:10])}
    Trending Suggestions: {', '.join(trends['trending'][:10])}
    """
    
    system_prompt = """You are a YouTube SEO expert specializing in tag optimization.
    Generate relevant, searchable tags based on the video title, description, and trending data provided.
    Focus on a mix of specific and broad tags that will help with video discovery.
    Consider the trending topics and queries provided to maximize searchability.
    Return only the tags, separated by commas."""
    
    user_prompt = f"""Generate {num_tags} relevant YouTube tags for a video with:
    Title: {title}
    Description: {description}
    
    Consider this trending data:
    {trend_context}
    
    Include a mix of:
    - Exact match phrases from title and description
    - Related trending topics and queries
    - Broader category tags
    - Specific niche tags
    - Popular search variations
    
    Format: Return only the tags, separated by commas."""
    
    try:
        tags = llm_text_gen(user_prompt, system_prompt=system_prompt)
        generated_tags = [tag.strip() for tag in tags.split(',')]
        
        # Add some trending tags directly
        trending_tags = (
            trends['topics'][:3] +  # Top 3 related topics
            trends['queries'][:3] +  # Top 3 related queries
            trends['trending'][:3]   # Top 3 trending suggestions
        )
        
        # Combine and remove duplicates
        all_tags = generated_tags + trending_tags
        seen = set()
        final_tags = [tag for tag in all_tags if not (tag.lower() in seen or seen.add(tag.lower()))]
        
        return final_tags
    except Exception as e:
        logger.error(f"Error generating tags: {str(e)}")
        return []

def analyze_tags(tags):
    """Analyze tags for optimization opportunities."""
    analysis = {
        'total_tags': len(tags),
        'total_characters': sum(len(tag) for tag in tags),
        'avg_tag_length': sum(len(tag) for tag in tags) / len(tags) if tags else 0,
        'duplicate_tags': len(tags) - len(set(tags)),
        'tags_too_long': [tag for tag in tags if len(tag) > 30],
        'single_word_tags': [tag for tag in tags if len(tag.split()) == 1],
        'optimization_score': 0
    }
    
    # Calculate optimization score (0-100)
    score = 100
    if analysis['total_tags'] < 5:
        score -= 30
    if analysis['total_characters'] > 500:
        score -= 20
    if analysis['duplicate_tags'] > 0:
        score -= 10 * analysis['duplicate_tags']
    if len(analysis['tags_too_long']) > 0:
        score -= 5 * len(analysis['tags_too_long'])
    if len(analysis['single_word_tags']) > len(tags) * 0.5:
        score -= 15
        
    analysis['optimization_score'] = max(0, score)
    return analysis

def display_tags(tags):
    """Display tags in a visually appealing format."""
    if not tags:
        return
    
    # Create a container for all tags
    st.markdown("""
        <style>
            .tag-container {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 16px;
                padding: 12px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            .tag {
                display: inline-flex;
                align-items: center;
                background-color: #f0f2f6;
                border-radius: 16px;
                padding: 6px 12px;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #e6e9ef;
                white-space: nowrap;
                transition: all 0.2s ease;
            }
            .tag:hover {
                background-color: #e6e9ef;
                border-color: #d1d5db;
                transform: translateY(-1px);
            }
        </style>
        <div class="tag-container">
    """, unsafe_allow_html=True)
    
    # Display tags
    for tag in tags:
        st.markdown(f'<div class="tag">{tag}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display tag count and character count
    tags_text = ", ".join(tags)
    char_count = len(tags_text)
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Total tags: {len(tags)}")
    with col2:
        st.caption(f"Characters: {char_count}/500")

def write_yt_tags():
    """Create a user interface for YouTube Tags Generator."""
    logger.info("Initializing YouTube Tags Generator UI")
    st.write("Generate optimized tags for your videos with trending tag suggestions to improve discoverability.")
    
    # Initialize session state
    if "generated_tags" not in st.session_state:
        st.session_state.generated_tags = None
    if "tag_analysis" not in st.session_state:
        st.session_state.tag_analysis = None
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Quick Generate", "Advanced Options", "Analysis"])
    
    with tab1:
        # Basic information inputs
        title = st.text_input("Video Title", 
                            placeholder="Enter your video title")
        description = st.text_area("Video Description", 
                                 placeholder="Enter your video description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_tags = st.number_input("Number of Tags", 
                                     min_value=5, 
                                     max_value=30, 
                                     value=15)
        
        with col2:
            include_trending = st.checkbox("Include Trending Suggestions", value=True)
        
        if st.button("Generate Tags"):
            if not title:
                st.error("Please enter a video title.")
                return
            
            with st.spinner("Generating tags..."):
                # Generate tags using the comprehensive method
                tags = generate_tags_from_title_description(title, description, num_tags)
                
                if tags:
                    # Analyze tags
                    st.session_state.tag_analysis = analyze_tags(tags)
                    st.session_state.generated_tags = tags
                    
                    # Display tags in the new format
                    st.subheader("Generated Tags")
                    display_tags(tags)
                    
                    # Add copy button for all tags
                    tags_text = ", ".join(tags)
                    st.text_area("Tags (copy to use)", value=tags_text, height=100)
                    
                    # Display character count
                    char_count = len(tags_text)
                    st.info(f"Total characters: {char_count}/500 ({500 - char_count} remaining)")
                    
                    # Quick analysis summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Number of Tags", len(tags))
                    with col2:
                        st.metric("Optimization Score", f"{st.session_state.tag_analysis['optimization_score']}%")
                    with col3:
                        st.metric("Avg Tag Length", f"{st.session_state.tag_analysis['avg_tag_length']:.1f}")
                    
                    # Display trending data summary if enabled
                    if include_trending:
                        st.subheader("Trending Data Used")
                        trends = get_comprehensive_trends(title, description)
                        
                        # Create columns for different trend types
                        tcol1, tcol2, tcol3 = st.columns(3)
                        
                        with tcol1:
                            st.markdown("##### Related Topics")
                            if trends['topics']:
                                for topic in trends['topics'][:5]:
                                    st.markdown(f"• {topic}")
                            else:
                                st.markdown("*No related topics found*")
                        
                        with tcol2:
                            st.markdown("##### Related Queries")
                            if trends['queries']:
                                for query in trends['queries'][:5]:
                                    st.markdown(f"• {query}")
                            else:
                                st.markdown("*No related queries found*")
                        
                        with tcol3:
                            st.markdown("##### Trending Suggestions")
                            if trends['trending']:
                                for trend in trends['trending'][:5]:
                                    st.markdown(f"• {trend}")
                            else:
                                st.markdown("*No trending suggestions found*")
                else:
                    st.error("Failed to generate tags. Please try again.")
    
    with tab2:
        st.info("Advanced tag generation options coming soon!")
        st.markdown("""
        Future features will include:
        - Competitor tag analysis
        - Tag performance tracking
        - Category-specific tag suggestions
        - Multi-language tag generation
        - Tag sets management
        """)
    
    with tab3:
        if st.session_state.tag_analysis:
            st.subheader("Tag Analysis")
            
            # Create metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Tags", st.session_state.tag_analysis['total_tags'])
                st.metric("Total Characters", st.session_state.tag_analysis['total_characters'])
                st.metric("Average Tag Length", f"{st.session_state.tag_analysis['avg_tag_length']:.1f}")
            
            with col2:
                st.metric("Duplicate Tags", st.session_state.tag_analysis['duplicate_tags'])
                st.metric("Single Word Tags", len(st.session_state.tag_analysis['single_word_tags']))
                st.metric("Tags Too Long", len(st.session_state.tag_analysis['tags_too_long']))
            
            # Optimization score with color
            score = st.session_state.tag_analysis['optimization_score']
            score_color = 'red' if score < 50 else 'orange' if score < 80 else 'green'
            st.markdown(f"""
                <div style='background-color: {score_color}; padding: 10px; border-radius: 5px; margin: 10px 0;'>
                    <h3 style='color: white; margin: 0;'>Optimization Score: {score}%</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Optimization suggestions
            st.subheader("Optimization Suggestions")
            suggestions = []
            
            if st.session_state.tag_analysis['total_tags'] < 5:
                suggestions.append("❌ Add more tags (aim for at least 15)")
            if st.session_state.tag_analysis['total_characters'] > 500:
                suggestions.append("❌ Total character count exceeds limit (max 500)")
            if st.session_state.tag_analysis['duplicate_tags'] > 0:
                suggestions.append("❌ Remove duplicate tags")
            if len(st.session_state.tag_analysis['tags_too_long']) > 0:
                suggestions.append("❌ Some tags are too long (max 30 characters)")
            if len(st.session_state.tag_analysis['single_word_tags']) > st.session_state.tag_analysis['total_tags'] * 0.5:
                suggestions.append("❌ Too many single-word tags (use more specific phrases)")
            
            if not suggestions:
                st.success("✅ Your tags are well-optimized!")
            else:
                for suggestion in suggestions:
                    st.warning(suggestion)
        else:
            st.info("Generate tags first to see analysis") 