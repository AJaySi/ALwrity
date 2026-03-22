"""
YouTube Description Generator Module

This module provides functionality for generating YouTube video descriptions.
"""

import streamlit as st
import time
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen


def calculate_keyword_density(text, keywords):
    """Calculate the density of keywords in the text."""
    if not text or not keywords:
        return 0
    
    text = text.lower()
    keywords = [k.lower() for k in keywords]
    
    total_words = len(text.split())
    keyword_count = sum(text.count(k) for k in keywords)
    
    return (keyword_count / total_words) * 100 if total_words > 0 else 0


def calculate_seo_score(text, keywords):
    """Calculate the SEO score of the description."""
    score = 0
    
    # Text length (optimal: 250-300 words)
    word_count = len(text.split())
    if 250 <= word_count <= 300:
        score += 3
    elif 200 <= word_count <= 350:
        score += 2
    elif 150 <= word_count <= 400:
        score += 1
    
    # Keyword presence
    text_lower = text.lower()
    keywords_lower = [k.lower() for k in keywords]
    keyword_count = sum(text_lower.count(k) for k in keywords_lower)
    if keyword_count >= 3:
        score += 3
    elif keyword_count >= 2:
        score += 2
    elif keyword_count >= 1:
        score += 1
    
    # Call to action phrases
    cta_phrases = ["subscribe", "like", "comment", "share", "follow", "check out", "visit", "learn more"]
    cta_count = sum(text_lower.count(phrase) for phrase in cta_phrases)
    if cta_count >= 2:
        score += 2
    elif cta_count >= 1:
        score += 1
    
    # Hashtags
    hashtag_count = text.count("#")
    if 3 <= hashtag_count <= 5:
        score += 2
    elif 1 <= hashtag_count <= 8:
        score += 1
    
    # Links
    link_count = text.count("http")
    if 1 <= link_count <= 3:
        score += 2
    elif link_count > 3:
        score += 1
    
    return min(score, 10)  # Cap at 10


def generate_youtube_description(target_audience, main_points, tone_style, use_case, primary_keywords, 
                               secondary_keywords, language, seo_goals, include_timestamps=False, 
                               include_hashtags=False, include_social_handles=False):
    """Generate a YouTube description based on the provided parameters."""
    
    # Create a custom system prompt for YouTube description generation
    system_prompt = """You are a YouTube description expert specializing in creating engaging, SEO-optimized video descriptions.
    Your task is to generate YouTube video descriptions based on the provided information.
    Focus ONLY on creating descriptions that are optimized for YouTube, with proper formatting, keywords, and calls to action.
    Return ONLY the description text, without any additional commentary or explanations."""
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Please generate a YouTube description for a video about **{main_points}** based on the following information:

    **Target Audience:** {target_audience}
    **Tone and Style:** {tone_style}
    **Use Case:** {use_case}
    **Language:** {language}
    **Primary Keywords:** {primary_keywords}
    **Secondary Keywords:** {secondary_keywords}
    **SEO Goals:** {seo_goals}

    **Additional Elements:**
    {"- Include timestamps for key sections." if include_timestamps else ""}
    {"- Include relevant hashtags." if include_hashtags else ""}
    {"- Include social media handles." if include_social_handles else ""}

    **Specific Instructions:**
    * Keep the description informative and engaging.
    * Use a conversational tone that matches the target audience.
    * Include relevant keywords naturally.
    * Add a call to action.
    * Keep the length between 250-300 words for optimal SEO.
    """
    
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response
    except Exception as err:
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None


def write_yt_description():
    """Create a user interface for YouTube Description Generator."""
    st.write("Generate SEO-optimized YouTube video descriptions that drive engagement.")
    
    # Initialize session state for generated description if it doesn't exist
    if "generated_description" not in st.session_state:
        st.session_state.generated_description = None
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Basic Info", "SEO Optimization", "Advanced Options"])
    
    with tab1:
        # Basic information inputs
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
            language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Italian", "Portuguese"])
    
    with tab2:
        # SEO optimization inputs
        primary_keywords = st.text_input("Primary Keywords (comma-separated)", 
                                       placeholder="e.g., cooking, recipes, healthy food")
        secondary_keywords = st.text_input("Secondary Keywords (comma-separated)", 
                                         placeholder="e.g., quick meals, budget cooking")
        seo_goals = st.multiselect("SEO Goals", 
                                 ["Increase Views", "Drive Engagement", "Build Subscribers", "Promote Products/Services"])
    
    with tab3:
        # Advanced options
        st.subheader("Additional Elements")
        include_timestamps = st.checkbox("Include Timestamps", value=True)
        include_hashtags = st.checkbox("Include Hashtags", value=True)
        include_social_handles = st.checkbox("Include Social Media Handles", value=True)
    
    if st.button("Generate Description"):
        if not main_points:
            st.error("Please enter main points/keywords.")
            return
        
        with st.spinner("Generating description..."):
            description = generate_youtube_description(
                target_audience, main_points, tone_style, use_case, primary_keywords, 
                secondary_keywords, language, seo_goals, include_timestamps, 
                include_hashtags, include_social_handles
            )
            
            if description:
                # Store the description in session state
                st.session_state.generated_description = description
                
                # Store other parameters in session state for regeneration
                st.session_state.description_params = {
                    "target_audience": target_audience,
                    "main_points": main_points,
                    "tone_style": tone_style,
                    "use_case": use_case,
                    "primary_keywords": primary_keywords,
                    "secondary_keywords": secondary_keywords,
                    "language": language,
                    "seo_goals": seo_goals,
                    "include_timestamps": include_timestamps,
                    "include_hashtags": include_hashtags,
                    "include_social_handles": include_social_handles
                }
                
                st.subheader("Generated Description")
                
                # Display description with analysis
                st.text_area("Description", description, height=200)
                
                # Calculate and display metrics
                all_keywords = primary_keywords.split(",") + secondary_keywords.split(",")
                keyword_density = calculate_keyword_density(description, all_keywords)
                seo_score = calculate_seo_score(description, all_keywords)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Keyword Density", f"{keyword_density:.1f}%")
                with col2:
                    st.metric("SEO Score", f"{seo_score}/10")
                
                # Create columns for the buttons
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    # Download button
                    st.download_button(
                        label="Download Description",
                        data=description,
                        file_name="youtube_description.txt",
                        mime="text/plain"
                    )
                
                with btn_col2:
                    # Regenerate button
                    if st.button("Regenerate"):
                        st.session_state.show_regenerate_popover = True
                
                # Regenerate popover
                if st.session_state.get("show_regenerate_popover", False):
                    with st.form("regenerate_form"):
                        st.subheader("Regenerate Description")
                        st.write("Specify changes you'd like to make to the description:")
                        changes = st.text_area("Changes to make", 
                                             placeholder="e.g., Make it more casual, add more call-to-actions, focus on product benefits")
                        
                        submitted = st.form_submit_button("Regenerate with Changes")
                        
                        if submitted and changes:
                            with st.spinner("Regenerating description..."):
                                # Get the stored parameters
                                params = st.session_state.description_params
                                
                                # Add the changes to the prompt
                                params["changes"] = changes
                                
                                # Generate a new description with the changes
                                new_description = generate_youtube_description_with_changes(
                                    params["target_audience"], 
                                    params["main_points"], 
                                    params["tone_style"], 
                                    params["use_case"], 
                                    params["primary_keywords"], 
                                    params["secondary_keywords"], 
                                    params["language"], 
                                    params["seo_goals"], 
                                    params["include_timestamps"], 
                                    params["include_hashtags"], 
                                    params["include_social_handles"],
                                    changes
                                )
                                
                                if new_description:
                                    # Update the stored description
                                    st.session_state.generated_description = new_description
                                    st.session_state.show_regenerate_popover = False
                                    st.rerun()
                                else:
                                    st.error("Failed to regenerate description. Please try again.")
            else:
                st.error("Failed to generate description. Please try again.")
    
    # Display previously generated description if it exists in session state
    elif st.session_state.generated_description:
        description = st.session_state.generated_description
        params = st.session_state.description_params
        
        st.subheader("Generated Description")
        
        # Display description with analysis
        st.text_area("Description", description, height=200)
        
        # Calculate and display metrics
        all_keywords = params["primary_keywords"].split(",") + params["secondary_keywords"].split(",")
        keyword_density = calculate_keyword_density(description, all_keywords)
        seo_score = calculate_seo_score(description, all_keywords)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Keyword Density", f"{keyword_density:.1f}%")
        with col2:
            st.metric("SEO Score", f"{seo_score}/10")
        
        # Create columns for the buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Download button
            st.download_button(
                label="Download Description",
                data=description,
                file_name="youtube_description.txt",
                mime="text/plain"
            )
        
        with btn_col2:
            # Regenerate button
            if st.button("Regenerate"):
                st.session_state.show_regenerate_popover = True
        
        # Regenerate popover
        if st.session_state.get("show_regenerate_popover", False):
            with st.form("regenerate_form"):
                st.subheader("Regenerate Description")
                st.write("Specify changes you'd like to make to the description:")
                changes = st.text_area("Changes to make", 
                                     placeholder="e.g., Make it more casual, add more call-to-actions, focus on product benefits")
                
                submitted = st.form_submit_button("Regenerate with Changes")
                
                if submitted and changes:
                    with st.spinner("Regenerating description..."):
                        # Add the changes to the prompt
                        params["changes"] = changes
                        
                        # Generate a new description with the changes
                        new_description = generate_youtube_description_with_changes(
                            params["target_audience"], 
                            params["main_points"], 
                            params["tone_style"], 
                            params["use_case"], 
                            params["primary_keywords"], 
                            params["secondary_keywords"], 
                            params["language"], 
                            params["seo_goals"], 
                            params["include_timestamps"], 
                            params["include_hashtags"], 
                            params["include_social_handles"],
                            changes
                        )
                        
                        if new_description:
                            # Update the stored description
                            st.session_state.generated_description = new_description
                            st.session_state.show_regenerate_popover = False
                            st.rerun()
                        else:
                            st.error("Failed to regenerate description. Please try again.")


def generate_youtube_description_with_changes(target_audience, main_points, tone_style, use_case, primary_keywords, 
                                            secondary_keywords, language, seo_goals, include_timestamps=False, 
                                            include_hashtags=False, include_social_handles=False, changes=""):
    """Generate a YouTube description based on the provided parameters and requested changes."""
    
    # Create a custom system prompt for YouTube description generation
    system_prompt = """You are a YouTube description expert specializing in creating engaging, SEO-optimized video descriptions.
    Your task is to generate YouTube video descriptions based on the provided information.
    Focus ONLY on creating descriptions that are optimized for YouTube, with proper formatting, keywords, and calls to action.
    Return ONLY the description text, without any additional commentary or explanations."""
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Please generate a YouTube description for a video about **{main_points}** based on the following information:

    **Target Audience:** {target_audience}
    **Tone and Style:** {tone_style}
    **Use Case:** {use_case}
    **Language:** {language}
    **Primary Keywords:** {primary_keywords}
    **Secondary Keywords:** {secondary_keywords}
    **SEO Goals:** {seo_goals}

    **Additional Elements:**
    {"- Include timestamps for key sections." if include_timestamps else ""}
    {"- Include relevant hashtags." if include_hashtags else ""}
    {"- Include social media handles." if include_social_handles else ""}

    **Requested Changes:**
    {changes}

    **Specific Instructions:**
    * Keep the description informative and engaging.
    * Use a conversational tone that matches the target audience.
    * Include relevant keywords naturally.
    * Add a call to action.
    * Keep the length between 250-300 words for optimal SEO.
    * Incorporate the requested changes into the description.
    """
    
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response
    except Exception as err:
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None 