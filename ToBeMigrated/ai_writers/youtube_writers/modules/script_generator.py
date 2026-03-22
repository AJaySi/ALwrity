"""
YouTube Script Generator Module

This module provides functionality for generating YouTube video scripts.
"""

import streamlit as st
import time
import json
import os
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen


def generate_youtube_script(target_audience, main_points, tone_style, use_case, script_structure, 
                          include_hook=False, include_cta=False, include_engagement=False, 
                          include_timestamps=False, include_visual_cues=False, engagement_hooks=None,
                          community_interactions=None, language="English"):
    """Generate a YouTube script based on the provided parameters."""
    
    # Create a custom system prompt for YouTube script generation
    system_prompt = f"""You are a YouTube script expert specializing in creating engaging, well-structured video scripts in {language}.
    Your task is to generate YouTube video scripts based on the provided information.
    Focus ONLY on creating scripts that are optimized for YouTube, with proper structure, engagement hooks, and calls to action.
    Return ONLY the script text, without any additional commentary or explanations.
    Format the script with clear sections, speaker notes, and visual cues where appropriate.
    Write the entire script in {language}."""
    
    # Build structure-specific instructions
    structure_instructions = {
        "Problem-Solution": "Structure the script to first present a problem, then provide a solution.",
        "Before-After-Bridge": "Structure the script to show the before state, the transformation process, and the after state.",
        "Hook-Problem-Solution-Call to Action": "Start with a hook, present the problem, provide the solution, and end with a call to action.",
        "Compare and Contrast": "Structure the script to compare and contrast different options or approaches.",
        "Step-by-Step Tutorial": "Break down the content into clear, sequential steps.",
        "Case Study": "Present a real-world example or case study to illustrate the main points.",
        "Interview Format": "Structure the script as an interview with questions and answers.",
        "Review Format": "Structure the script as a review with pros, cons, and a final verdict.",
        "Vlog Format": "Structure the script as a personal video blog with a conversational tone.",
        "Educational Format": "Structure the script to teach a concept with examples and explanations.",
        "Entertainment Format": "Structure the script to entertain while delivering the main message."
    }
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Please generate a YouTube script in {language} for a video about **{main_points}** based on the following information:

    **Target Audience:** {target_audience}
    **Tone and Style:** {tone_style}
    **Use Case:** {use_case}
    **Script Structure:** {script_structure}
    **Language:** {language}

    **Structure Instructions:**
    {structure_instructions.get(script_structure, "Follow a logical flow to present the content.")}

    **Additional Elements:**
    {"- Include a hook at the beginning to grab attention." if include_hook else ""}
    {"- End with a strong call to action." if include_cta else ""}
    {"- Include prompts for viewer engagement (e.g., questions, polls)." if include_engagement else ""}
    {"- Include suggested timestamps for key sections." if include_timestamps else ""}
    {"- Include visual cues and transitions." if include_visual_cues else ""}
    """

    # Add engagement hooks if provided
    if engagement_hooks:
        prompt += "\n**Engagement Hooks:**\n"
        for hook in engagement_hooks:
            prompt += f"- {hook}\n"
    
    # Add community interaction points if provided
    if community_interactions:
        prompt += "\n**Community Interaction Points:**\n"
        for interaction in community_interactions:
            prompt += f"- {interaction}\n"

    prompt += """
    **Specific Instructions:**
    * Keep the language clear and engaging.
    * Use a conversational tone that matches the target audience.
    * Include relevant examples and explanations.
    * Ensure the script flows naturally and maintains viewer interest.
    """
    
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response
    except Exception as err:
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None


def generate_youtube_script_with_changes(target_audience, main_points, tone_style, use_case, script_structure, 
                                       include_hook=False, include_cta=False, include_engagement=False, 
                                       include_timestamps=False, include_visual_cues=False, engagement_hooks=None,
                                       community_interactions=None, changes="", language="English"):
    """Generate a YouTube script based on the provided parameters and requested changes."""
    
    # Create a custom system prompt for YouTube script generation
    system_prompt = f"""You are a YouTube script expert specializing in creating engaging, well-structured video scripts in {language}.
    Your task is to generate YouTube video scripts based on the provided information.
    Focus ONLY on creating scripts that are optimized for YouTube, with proper structure, engagement hooks, and calls to action.
    Return ONLY the script text, without any additional commentary or explanations.
    Format the script with clear sections, speaker notes, and visual cues where appropriate.
    Write the entire script in {language}."""
    
    # Build structure-specific instructions
    structure_instructions = {
        "Problem-Solution": "Structure the script to first present a problem, then provide a solution.",
        "Before-After-Bridge": "Structure the script to show the before state, the transformation process, and the after state.",
        "Hook-Problem-Solution-Call to Action": "Start with a hook, present the problem, provide the solution, and end with a call to action.",
        "Compare and Contrast": "Structure the script to compare and contrast different options or approaches.",
        "Step-by-Step Tutorial": "Break down the content into clear, sequential steps.",
        "Case Study": "Present a real-world example or case study to illustrate the main points.",
        "Interview Format": "Structure the script as an interview with questions and answers.",
        "Review Format": "Structure the script as a review with pros, cons, and a final verdict.",
        "Vlog Format": "Structure the script as a personal video blog with a conversational tone.",
        "Educational Format": "Structure the script to teach a concept with examples and explanations.",
        "Entertainment Format": "Structure the script to entertain while delivering the main message."
    }
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Please generate a YouTube script in {language} for a video about **{main_points}** based on the following information:

    **Target Audience:** {target_audience}
    **Tone and Style:** {tone_style}
    **Use Case:** {use_case}
    **Script Structure:** {script_structure}
    **Language:** {language}

    **Structure Instructions:**
    {structure_instructions.get(script_structure, "Follow a logical flow to present the content.")}

    **Additional Elements:**
    {"- Include a hook at the beginning to grab attention." if include_hook else ""}
    {"- End with a strong call to action." if include_cta else ""}
    {"- Include prompts for viewer engagement (e.g., questions, polls)." if include_engagement else ""}
    {"- Include suggested timestamps for key sections." if include_timestamps else ""}
    {"- Include visual cues and transitions." if include_visual_cues else ""}
    """

    # Add engagement hooks if provided
    if engagement_hooks:
        prompt += "\n**Engagement Hooks:**\n"
        for hook in engagement_hooks:
            prompt += f"- {hook}\n"
    
    # Add community interaction points if provided
    if community_interactions:
        prompt += "\n**Community Interaction Points:**\n"
        for interaction in community_interactions:
            prompt += f"- {interaction}\n"
    
    # Add requested changes
    prompt += f"""
    **Requested Changes:**
    {changes}

    **Specific Instructions:**
    * Keep the language clear and engaging.
    * Use a conversational tone that matches the target audience.
    * Include relevant examples and explanations.
    * Ensure the script flows naturally and maintains viewer interest.
    * Incorporate the requested changes into the script.
    """
    
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response
    except Exception as err:
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None


def export_script(script, format_type, filename=None):
    """Export the script in various formats."""
    if not filename:
        filename = "youtube_script"
    
    if format_type == "Text":
        return script, f"{filename}.txt", "text/plain"
    elif format_type == "Markdown":
        return script, f"{filename}.md", "text/markdown"
    elif format_type == "HTML":
        html_content = f"<html><body><pre>{script}</pre></body></html>"
        return html_content, f"{filename}.html", "text/html"
    elif format_type == "JSON":
        json_content = json.dumps({"script": script}, indent=2)
        return json_content, f"{filename}.json", "application/json"
    elif format_type == "Subtitles (SRT)":
        # Convert script to basic SRT format
        lines = script.split('\n')
        srt_content = ""
        for i, line in enumerate(lines):
            if line.strip():
                start_time = f"00:00:{i*5:02d},000"
                end_time = f"00:00:{(i+1)*5:02d},000"
                srt_content += f"{i+1}\n{start_time} --> {end_time}\n{line}\n\n"
        return srt_content, f"{filename}.srt", "text/plain"
    else:
        return script, f"{filename}.txt", "text/plain"


def write_yt_script():
    """Create a user interface for YouTube Script Generator."""
    st.write("Generate professional YouTube video scripts with optimized structures for engagement.")
    
    # Initialize session state for generated script if it doesn't exist
    if "generated_script" not in st.session_state:
        st.session_state.generated_script = None
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Basic Info", "Advanced Options", "Engagement & Export"])
    
    with tab1:
        # Basic information inputs
        main_points = st.text_area("Main Points/Keywords (comma-separated)", 
                                 placeholder="e.g., cooking tips, healthy recipes, quick meals")
        target_audience = st.text_input("Target Audience", 
                                      placeholder="e.g., beginners, professionals, parents")
        
        # Create columns for tone, use case, structure, and language
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tone_style = st.selectbox("Tone/Style", 
                                    ["Professional", "Casual", "Humorous", "Educational", "Entertaining", "Inspirational"])
        
        with col2:
            use_case = st.selectbox("Use Case", 
                                  ["How-to/Tutorial", "Vlog", "Review", "Educational", "Entertainment", "News"])
        
        with col3:
            script_structure = st.selectbox("Script Structure", [
                "Problem-Solution",
                "Before-After-Bridge",
                "Hook-Problem-Solution-Call to Action",
                "Compare and Contrast",
                "Step-by-Step Tutorial",
                "Case Study",
                "Interview Format",
                "Review Format",
                "Vlog Format",
                "Educational Format",
                "Entertainment Format"
            ])
        
        with col4:
            language = st.selectbox("Language", [
                "English",
                "Spanish",
                "French",
                "German",
                "Italian",
                "Portuguese",
                "Russian",
                "Japanese",
                "Korean",
                "Chinese",
                "Hindi",
                "Arabic"
            ])
    
    with tab2:
        # Advanced options
        st.subheader("Additional Elements")
        include_hook = st.checkbox("Include Hook", value=True)
        include_cta = st.checkbox("Include Call to Action", value=True)
        include_engagement = st.checkbox("Include Viewer Engagement Prompts", value=True)
        include_timestamps = st.checkbox("Include Suggested Timestamps", value=True)
        include_visual_cues = st.checkbox("Include Visual Cues/Transitions", value=True)
    
    with tab3:
        # Engagement hooks
        st.subheader("Engagement Hooks")
        st.write("Select engagement hooks to include in your script:")
        
        engagement_hooks = []
        if st.checkbox("Question Hook", value=False):
            engagement_hooks.append("Start with a thought-provoking question to engage viewers immediately")
        if st.checkbox("Story Hook", value=False):
            engagement_hooks.append("Begin with a brief, relevant story or anecdote")
        if st.checkbox("Statistic Hook", value=False):
            engagement_hooks.append("Open with an interesting statistic or fact")
        if st.checkbox("Controversy Hook", value=False):
            engagement_hooks.append("Present a controversial statement or opinion to spark interest")
        if st.checkbox("Promise Hook", value=False):
            engagement_hooks.append("Make a promise about what viewers will learn or gain")
        if st.checkbox("Scenario Hook", value=False):
            engagement_hooks.append("Describe a scenario or situation viewers can relate to")
        if st.checkbox("Mystery Hook", value=False):
            engagement_hooks.append("Create a sense of mystery or intrigue")
        if st.checkbox("Quote Hook", value=False):
            engagement_hooks.append("Start with a relevant quote from an expert or notable figure")
        
        # Community interaction points
        st.subheader("Community Interaction Points")
        st.write("Select community interaction points to include in your script:")
        
        community_interactions = []
        if st.checkbox("Comment Prompt", value=False):
            community_interactions.append("Ask viewers to share their experiences or opinions in the comments")
        if st.checkbox("Poll Suggestion", value=False):
            community_interactions.append("Suggest creating a poll for viewers to vote on")
        if st.checkbox("Question for Comments", value=False):
            community_interactions.append("Pose a specific question for viewers to answer in the comments")
        if st.checkbox("Challenge", value=False):
            community_interactions.append("Challenge viewers to try something and report back")
        if st.checkbox("Tag Friends", value=False):
            community_interactions.append("Encourage viewers to tag friends who might benefit from the content")
        if st.checkbox("Share Request", value=False):
            community_interactions.append("Ask viewers to share the video with others who might find it helpful")
        if st.checkbox("Community Post", value=False):
            community_interactions.append("Mention creating a community post to continue the discussion")
        if st.checkbox("Live Stream Teaser", value=False):
            community_interactions.append("Tease an upcoming live stream on the same topic")
        
        # Export options
        st.subheader("Export Options")
        export_format = st.selectbox("Export Format", [
            "Text",
            "Markdown",
            "HTML",
            "JSON",
            "Subtitles (SRT)"
        ])
        
        custom_filename = st.text_input("Custom Filename (optional)", 
                                      placeholder="Leave blank for default filename")
    
    if st.button("Generate Script"):
        if not main_points:
            st.error("Please enter main points/keywords.")
            return
        
        with st.spinner("Generating script..."):
            script = generate_youtube_script(
                target_audience, main_points, tone_style, use_case, script_structure,
                include_hook, include_cta, include_engagement, include_timestamps, include_visual_cues,
                engagement_hooks if engagement_hooks else None,
                community_interactions if community_interactions else None,
                language
            )
            
            if script:
                # Store the script in session state
                st.session_state.generated_script = script
                
                # Store other parameters in session state for regeneration
                st.session_state.script_params = {
                    "target_audience": target_audience,
                    "main_points": main_points,
                    "tone_style": tone_style,
                    "use_case": use_case,
                    "script_structure": script_structure,
                    "include_hook": include_hook,
                    "include_cta": include_cta,
                    "include_engagement": include_engagement,
                    "include_timestamps": include_timestamps,
                    "include_visual_cues": include_visual_cues,
                    "engagement_hooks": engagement_hooks if engagement_hooks else None,
                    "community_interactions": community_interactions if community_interactions else None,
                    "language": language
                }
                
                st.subheader("Generated Script")
                
                # Display script with tabs for different views
                script_tab1, script_tab2 = st.tabs(["Formatted View", "Plain Text"])
                
                with script_tab1:
                    st.markdown(script)
                
                with script_tab2:
                    st.code(script)
                
                # Export options
                st.subheader("Export Script")
                
                # Get export data
                export_data, export_filename, mime_type = export_script(
                    script, 
                    export_format, 
                    custom_filename if custom_filename else None
                )
                
                # Create columns for the buttons
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    # Download button
                    st.download_button(
                        label=f"Download as {export_format}",
                        data=export_data,
                        file_name=export_filename,
                        mime=mime_type
                    )
                
                with btn_col2:
                    # Regenerate button
                    if st.button("Regenerate"):
                        st.session_state.show_regenerate_popover = True
                
                # Regenerate popover
                if st.session_state.get("show_regenerate_popover", False):
                    with st.form("regenerate_form"):
                        st.subheader("Regenerate Script")
                        st.write("Specify changes you'd like to make to the script:")
                        changes = st.text_area("Changes to make", 
                                             placeholder="e.g., Make it more casual, add more call-to-actions, focus on product benefits")
                        
                        submitted = st.form_submit_button("Regenerate with Changes")
                        
                        if submitted and changes:
                            with st.spinner("Regenerating script..."):
                                # Get the stored parameters
                                params = st.session_state.script_params
                                
                                # Generate a new script with the changes
                                new_script = generate_youtube_script_with_changes(
                                    params["target_audience"], 
                                    params["main_points"], 
                                    params["tone_style"], 
                                    params["use_case"], 
                                    params["script_structure"],
                                    params["include_hook"], 
                                    params["include_cta"], 
                                    params["include_engagement"], 
                                    params["include_timestamps"], 
                                    params["include_visual_cues"],
                                    params["engagement_hooks"],
                                    params["community_interactions"],
                                    changes,
                                    params["language"]
                                )
                                
                                if new_script:
                                    # Update the stored script
                                    st.session_state.generated_script = new_script
                                    st.session_state.show_regenerate_popover = False
                                    st.rerun()
                                else:
                                    st.error("Failed to regenerate script. Please try again.")
                
                # Additional export options
                if st.checkbox("Show additional export options"):
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Copy to Clipboard"):
                            st.code(script)
                            st.success("Script copied to clipboard!")
                    
                    with col2:
                        if st.button("Save to Local File"):
                            # This is a placeholder - actual file saving would require additional backend functionality
                            st.info("This feature would save the file locally on your device.")
            else:
                st.error("Failed to generate script. Please try again.")
    
    # Display previously generated script if it exists in session state
    elif st.session_state.generated_script:
        script = st.session_state.generated_script
        params = st.session_state.script_params
        
        st.subheader("Generated Script")
        
        # Display script with tabs for different views
        script_tab1, script_tab2 = st.tabs(["Formatted View", "Plain Text"])
        
        with script_tab1:
            st.markdown(script)
        
        with script_tab2:
            st.code(script)
        
        # Export options
        st.subheader("Export Script")
        
        # Get export data
        export_data, export_filename, mime_type = export_script(
            script, 
            export_format, 
            custom_filename if custom_filename else None
        )
        
        # Create columns for the buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Download button
            st.download_button(
                label=f"Download as {export_format}",
                data=export_data,
                file_name=export_filename,
                mime=mime_type
            )
        
        with btn_col2:
            # Regenerate button
            if st.button("Regenerate"):
                st.session_state.show_regenerate_popover = True
        
        # Regenerate popover
        if st.session_state.get("show_regenerate_popover", False):
            with st.form("regenerate_form"):
                st.subheader("Regenerate Script")
                st.write("Specify changes you'd like to make to the script:")
                changes = st.text_area("Changes to make", 
                                     placeholder="e.g., Make it more casual, add more call-to-actions, focus on product benefits")
                
                submitted = st.form_submit_button("Regenerate with Changes")
                
                if submitted and changes:
                    with st.spinner("Regenerating script..."):
                        # Generate a new script with the changes
                        new_script = generate_youtube_script_with_changes(
                            params["target_audience"], 
                            params["main_points"], 
                            params["tone_style"], 
                            params["use_case"], 
                            params["script_structure"],
                            params["include_hook"], 
                            params["include_cta"], 
                            params["include_engagement"], 
                            params["include_timestamps"], 
                            params["include_visual_cues"],
                            params["engagement_hooks"],
                            params["community_interactions"],
                            changes,
                            params["language"]
                        )
                        
                        if new_script:
                            # Update the stored script
                            st.session_state.generated_script = new_script
                            st.session_state.show_regenerate_popover = False
                            st.rerun()
                        else:
                            st.error("Failed to regenerate script. Please try again.")
        
        # Additional export options
        if st.checkbox("Show additional export options"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy to Clipboard"):
                    st.code(script)
                    st.success("Script copied to clipboard!")
            
            with col2:
                if st.button("Save to Local File"):
                    # This is a placeholder - actual file saving would require additional backend functionality
                    st.info("This feature would save the file locally on your device.") 