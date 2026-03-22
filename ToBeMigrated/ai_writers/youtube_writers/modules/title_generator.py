"""
YouTube Title Generator Module

This module provides functionality for generating YouTube video titles.
"""

import streamlit as st
import time
import logging
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_title_generator')


def analyze_title(title):
    """Analyze a YouTube title for SEO and clickbait."""
    logger.info(f"Analyzing title: '{title}'")
    
    # Character count
    char_count = len(title)
    optimal_length = 50 <= char_count <= 60
    logger.info(f"Character count: {char_count}, Optimal length: {optimal_length}")
    
    # Clickbait detection. TBD: Use AI to detect clickbait.
    clickbait_phrases = [
        "shocking", "you won't believe", "gone wrong", "gone sexual", 
        "free v-bucks", "free robux", "100%", "gone viral", "viral",
        "you need to see this", "wait till the end", "at 3am", "3am",
        "don't watch this", "watch till the end", "gone too far",
        "insane", "unbelievable", "mind-blowing", "life-changing",
        "secret", "hidden", "revealed", "exposed", "leaked",
        "never before seen", "first time ever", "world's first",
        "no one knows", "experts hate this", "doctors hate this",
        "this will change your life", "this will blow your mind",
        "you've been doing it wrong", "the truth about", "the real reason",
        "what they don't want you to know", "what they're hiding",
        "what they don't tell you", "what you need to know",
        "what you should know", "what you must know", "what you must see",
        "what you must watch", "what you must do", "what you must have",
        "what you must buy", "what you must try", "what you must avoid",
        "what you must stop doing", "what you must start doing",
        "what you must change", "what you must learn", "what you must understand",
        "what you must realize", "what you must accept", "what you must believe",
        "what you must know about", "what you must see about", "what you must watch about",
        "what you must do about", "what you must have about", "what you must buy about",
        "what you must try about", "what you must avoid about", "what you must stop doing about",
        "what you must start doing about", "what you must change about", "what you must learn about",
        "what you must understand about", "what you must realize about", "what you must accept about",
        "what you must believe about", "what you must know about", "what you must see about",
        "what you must watch about", "what you must do about", "what you must have about",
        "what you must buy about", "what you must try about", "what you must avoid about",
        "what you must stop doing about", "what you must start doing about", "what you must change about",
        "what you must learn about", "what you must understand about", "what you must realize about",
        "what you must accept about", "what you must believe about"
    ]
    
    clickbait_score = 0
    detected_phrases = []
    for phrase in clickbait_phrases:
        if phrase.lower() in title.lower():
            clickbait_score += 1
            detected_phrases.append(phrase)
    
    is_clickbait = clickbait_score > 0
    logger.info(f"Clickbait detection: score={clickbait_score}, is_clickbait={is_clickbait}")
    if detected_phrases:
        logger.info(f"Detected clickbait phrases: {', '.join(detected_phrases)}")
    
    # SEO elements
    has_number = any(char.isdigit() for char in title)
    has_question = "?" in title
    has_colon = ":" in title
    has_brackets = "[" in title or "]" in title or "(" in title or ")" in title
    
    logger.info(f"SEO elements: has_number={has_number}, has_question={has_question}, has_colon={has_colon}, has_brackets={has_brackets}")
    
    # Calculate SEO score
    seo_score = 0
    if optimal_length:
        seo_score += 3
    if has_number:
        seo_score += 1
    if has_question:
        seo_score += 1
    if has_colon:
        seo_score += 1
    if has_brackets:
        seo_score += 1
    if not is_clickbait:
        seo_score += 2
    
    logger.info(f"Final SEO score: {seo_score}/10")
    
    return {
        "char_count": char_count,
        "optimal_length": optimal_length,
        "is_clickbait": is_clickbait,
        "clickbait_score": clickbait_score,
        "seo_score": seo_score,
        "has_number": has_number,
        "has_question": has_question,
        "has_colon": has_colon,
        "has_brackets": has_brackets
    }


def generate_youtube_title(target_audience, main_points, tone_style, use_case, num_titles=5, progress_bar=None):
    """ Generate youtube title generator """
    logger.info(f"Starting title generation with parameters: target_audience='{target_audience}', main_points='{main_points}', tone_style='{tone_style}', use_case='{use_case}', num_titles={num_titles}")

    # Create a custom system prompt that doesn't include blog-specific instructions
    system_prompt = """You are a YouTube title expert specializing in creating engaging, clickable video titles.
    Your task is to generate YouTube video titles based on the provided information.
    Focus ONLY on creating titles that are optimized for YouTube.
    Return ONLY the titles, one per line, without any numbering or additional text."""

    prompt = f"""
    **Instructions:**

    Please generate {num_titles} YouTube title options for a video about **{main_points}** based on the following information:


    **Target Audience:** {target_audience}

    **Tone and Style:** {tone_style}

    **Use Case:** {use_case}

    **Specific Instructions:**

    * Make the titles catchy and attention-grabbing.
    * Use relevant keywords to improve SEO.
    * Tailor the language and tone to the target audience.
    * Ensure the title reflects the content and use case of the video.
    * Return ONLY the titles, one per line, without any numbering or additional text.
    """
    
    logger.info("Generated prompt for title generation")
    logger.debug(f"Prompt: {prompt}")
    logger.debug(f"System prompt: {system_prompt}")

    try:
        # Update progress bar if provided
        if progress_bar:
            progress_bar.progress(30)
            progress_bar.text("Analyzing your content and target audience...")
            logger.info("Progress bar updated: 30% - Analyzing content and target audience")
            
        # Simulate some processing time to show progress
        time.sleep(1)
        
        if progress_bar:
            progress_bar.progress(60)
            progress_bar.text("Generating creative title options...")
            logger.info("Progress bar updated: 60% - Generating creative title options")
            
        # Get the response from the language model with custom system prompt
        logger.info("Calling LLM for title generation with custom system prompt")
        start_time = time.time()
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        end_time = time.time()
        logger.info(f"LLM response received in {end_time - start_time:.2f} seconds")
        logger.debug(f"Raw LLM response: {response}")
        
        if progress_bar:
            progress_bar.progress(90)
            progress_bar.text("Processing and formatting titles...")
            logger.info("Progress bar updated: 90% - Processing and formatting titles")
            
        # Split the response into individual titles
        titles = [title.strip() for title in response.split('\n') if title.strip()]
        logger.info(f"Generated {len(titles)} titles")
        for i, title in enumerate(titles, 1):
            logger.info(f"Title {i}: '{title}'")
        
        if progress_bar:
            progress_bar.progress(100)
            progress_bar.text("Titles generated successfully!")
            logger.info("Progress bar updated: 100% - Titles generated successfully")
            
        return titles
    except Exception as err:
        logger.error(f"Error generating titles: {err}", exc_info=True)
        if progress_bar:
            progress_bar.progress(100)
            progress_bar.text("Error generating titles. Please try again.")
            logger.info("Progress bar updated: 100% - Error generating titles")
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None


def write_yt_title():
    """Create a user interface for YouTube Title Generator."""
    logger.info("Initializing YouTube Title Generator UI")
    st.write("Generate engaging YouTube video titles that drive clicks and views.")
    
    # Initialize session state for generated titles if it doesn't exist
    if "generated_titles" not in st.session_state:
        st.session_state.generated_titles = None
    
    # Main points input (full width)
    main_points = st.text_area("Main Points/Keywords (comma-separated)", 
                              placeholder="e.g., cooking tips, healthy recipes, quick meals")
    
    # Create columns for the other inputs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tone_style = st.selectbox("Tone/Style", 
                                ["Professional", "Casual", "Humorous", "Educational", "Entertaining", "Inspirational"])
    
    with col2:
        target_audience = st.text_input("Target Audience", 
                                      placeholder="e.g., beginners, professionals, parents")
    
    with col3:
        use_case = st.selectbox("Use Case", 
                              ["How-to/Tutorial", "Vlog", "Review", "Educational", "Entertainment", "News"])
    
    with col4:
        num_titles = st.number_input("Number of Titles", 
                                   min_value=1, 
                                   max_value=20, 
                                   value=5, 
                                   step=1)
    
    if st.button("Generate Titles"):
        logger.info("Generate Titles button clicked")
        logger.info(f"User inputs: main_points='{main_points}', tone_style='{tone_style}', target_audience='{target_audience}', use_case='{use_case}', num_titles={num_titles}")
        
        if not main_points:
            logger.warning("No main points provided")
            st.error("Please enter main points/keywords.")
            return
        
        # Create a progress bar
        progress_bar = st.progress(0)
        progress_bar.text("Initializing title generation...")
        logger.info("Created progress bar for title generation")
        
        # Generate titles with progress updates
        logger.info("Calling generate_youtube_title function")
        titles = generate_youtube_title(main_points, tone_style, target_audience, use_case, num_titles, progress_bar)
        
        # Clear the progress bar after a short delay
        time.sleep(1)
        progress_bar.empty()
        logger.info("Cleared progress bar")
        
        if titles:
            logger.info(f"Successfully generated {len(titles)} titles")
            
            # Store titles in session state for persistence
            st.session_state.generated_titles = titles
            
            # Display titles section
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='color: #FF0000; text-align: center;'>Generated YouTube Titles</h2>
                <p style='text-align: center;'>Click on a title to see detailed analysis and copy options</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display titles with analysis
            for i, title in enumerate(titles, 1):
                logger.info(f"Analyzing title {i}: '{title}'")
                
                # Create a more visually appealing expander
                with st.expander(f"Title {i}: {title}", expanded=False):
                    # Add a divider for better visual separation
                    st.markdown("---")
                    
                    # Title display with better formatting
                    st.markdown(f"""
                    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #FF0000;'>
                        <h3 style='margin: 0;'>{title}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Analysis section
                    st.markdown("### Analysis")
                    analysis = analyze_title(title)
                    
                    # Create columns for analysis metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Character count
                        st.markdown("#### Character Count")
                        st.write(f"**{analysis['char_count']}** characters")
                        if analysis['optimal_length']:
                            st.success("✅ Optimal length (50-60 characters)")
                        else:
                            st.warning("⚠️ Not optimal length (should be 50-60 characters)")
                        
                        # Clickbait detection
                        st.markdown("#### Clickbait Detection")
                        if analysis['is_clickbait']:
                            st.error(f"⚠️ Possible clickbait detected (score: {analysis['clickbait_score']})")
                        else:
                            st.success("✅ No clickbait detected")
                    
                    with col2:
                        # SEO score
                        st.markdown("#### SEO Score")
                        score_color = "#28a745" if analysis['seo_score'] >= 7 else "#ffc107" if analysis['seo_score'] >= 5 else "#dc3545"
                        st.markdown(f"<h2 style='color: {score_color};'>{analysis['seo_score']}/10</h2>", unsafe_allow_html=True)
                        if analysis['seo_score'] >= 7:
                            st.success("✅ Good SEO score")
                        elif analysis['seo_score'] >= 5:
                            st.warning("⚠️ Moderate SEO score")
                        else:
                            st.error("❌ Low SEO score")
                        
                        # SEO elements
                        st.markdown("#### SEO Elements")
                        elements = []
                        if analysis['has_number']:
                            elements.append("✅ Contains numbers")
                        if analysis['has_question']:
                            elements.append("✅ Contains question mark")
                        if analysis['has_colon']:
                            elements.append("✅ Contains colon")
                        if analysis['has_brackets']:
                            elements.append("✅ Contains brackets/parentheses")
                        
                        for element in elements:
                            st.write(element)
                    
                    # Copy functionality using session state
                    st.markdown("### Copy Title")
                    st.code(title, language="text")
                    
                    # Use a different approach for copy functionality
                    copy_key = f"copy_{i}"
                    if st.button(f"Copy Title {i}", key=copy_key):
                        # Use JavaScript to copy to clipboard
                        escaped_title = title.replace('"', '\\"')
                        st.markdown(
                            f"""
                            <script>
                                navigator.clipboard.writeText("{escaped_title}");
                            </script>
                            """,
                            unsafe_allow_html=True
                        )
                        st.success(f"✅ Title {i} copied to clipboard!")
        else:
            logger.error("Failed to generate titles")
            st.error("Failed to generate titles. Please try again.")
    
    # Display previously generated titles if they exist in session state
    elif st.session_state.generated_titles:
        titles = st.session_state.generated_titles
        
        # Display titles section
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: #FF0000; text-align: center;'>Generated YouTube Titles</h2>
            <p style='text-align: center;'>Click on a title to see detailed analysis and copy options</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display titles with analysis
        for i, title in enumerate(titles, 1):
            logger.info(f"Analyzing title {i}: '{title}'")
            
            # Create a more visually appealing expander
            with st.expander(f"Title {i}: {title}", expanded=False):
                # Add a divider for better visual separation
                st.markdown("---")
                
                # Title display with better formatting
                st.markdown(f"""
                <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #FF0000;'>
                    <h3 style='margin: 0;'>{title}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Analysis section
                st.markdown("### Analysis")
                analysis = analyze_title(title)
                
                # Create columns for analysis metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    # Character count
                    st.markdown("#### Character Count")
                    st.write(f"**{analysis['char_count']}** characters")
                    if analysis['optimal_length']:
                        st.success("✅ Optimal length (50-60 characters)")
                    else:
                        st.warning("⚠️ Not optimal length (should be 50-60 characters)")
                    
                    # Clickbait detection
                    st.markdown("#### Clickbait Detection")
                    if analysis['is_clickbait']:
                        st.error(f"⚠️ Possible clickbait detected (score: {analysis['clickbait_score']})")
                    else:
                        st.success("✅ No clickbait detected")
                
                with col2:
                    # SEO score
                    st.markdown("#### SEO Score")
                    score_color = "#28a745" if analysis['seo_score'] >= 7 else "#ffc107" if analysis['seo_score'] >= 5 else "#dc3545"
                    st.markdown(f"<h2 style='color: {score_color};'>{analysis['seo_score']}/10</h2>", unsafe_allow_html=True)
                    if analysis['seo_score'] >= 7:
                        st.success("✅ Good SEO score")
                    elif analysis['seo_score'] >= 5:
                        st.warning("⚠️ Moderate SEO score")
                    else:
                        st.error("❌ Low SEO score")
                    
                    # SEO elements
                    st.markdown("#### SEO Elements")
                    elements = []
                    if analysis['has_number']:
                        elements.append("✅ Contains numbers")
                    if analysis['has_question']:
                        elements.append("✅ Contains question mark")
                    if analysis['has_colon']:
                        elements.append("✅ Contains colon")
                    if analysis['has_brackets']:
                        elements.append("✅ Contains brackets/parentheses")
                    
                    for element in elements:
                        st.write(element)
                
                # Copy functionality using session state
                st.markdown("### Copy Title")
                st.code(title, language="text")
                
                # Use a different approach for copy functionality
                copy_key = f"copy_{i}"
                if st.button(f"Copy Title {i}", key=copy_key):
                    # Use JavaScript to copy to clipboard
                    escaped_title = title.replace('"', '\\"')
                    st.markdown(
                        f"""
                        <script>
                            navigator.clipboard.writeText("{escaped_title}");
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                    st.success(f"✅ Title {i} copied to clipboard!") 