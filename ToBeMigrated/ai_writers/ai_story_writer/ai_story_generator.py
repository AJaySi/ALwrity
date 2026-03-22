#####################################################
#
# google-gemini-cookbook - Story_Writing_with_Prompt_Chaining
#
#####################################################

import os
from pathlib import Path
import streamlit as st
from loguru import logger
import sys

from ...gpt_providers.text_generation.main_text_generation import llm_text_gen


def generate_with_retry(prompt, system_prompt=None):
    """
    Generates content using the llm_text_gen function with retry handling for errors.

    Parameters:
        prompt (str): The prompt to generate content from.
        system_prompt (str, optional): Custom system prompt to use instead of the default one.

    Returns:
        str: The generated content.
    """
    try:
        # Use llm_text_gen instead of directly calling the model
        return llm_text_gen(prompt, system_prompt)
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return ""


def ai_story(persona, story_setting, character_input, 
                       plot_elements, writing_style, story_tone, narrative_pov,
                       audience_age_group, content_rating, ending_preference):
    """
    Write a story using prompt chaining and iterative generation.

    Parameters:
        persona (str): The persona statement for the author.
        story_setting (str): The setting of the story.
        character_input (str): The characters in the story.
        plot_elements (str): The plot elements of the story.
        writing_style (str): The writing style of the story.
        story_tone (str): The tone of the story.
        narrative_pov (str): The narrative point of view.
        audience_age_group (str): The target audience age group.
        content_rating (str): The content rating of the story.
        ending_preference (str): The preferred ending of the story.
    """
    st.info(f"""
        You have chosen to create a story set in **{story_setting}**. 
        The main characters are: **{character_input}**.
        The plot will revolve around the theme of **{plot_elements}**.
        The story will be written in a **{writing_style}** style with a **{story_tone}** tone, from a **{narrative_pov}** perspective. 
        It is intended for a **{audience_age_group}** audience with a **{content_rating}** rating. 
        You prefer the story to have a **{ending_preference}** ending.
        """)
    try:
        persona = f"""{persona}
            Write a story with the following details:

		**The stroy Setting is:**
		{story_setting}
		
		**The Characters of the story are:**
		{character_input}
		
		**Plot Elements of the story:**
		{plot_elements}
		
		**Story Writing Style:**
		{writing_style}
		
		**The story Tone is:**
		{story_tone}
		
		**Write story from the Point of View of:**
		{narrative_pov}
		
		**Target Audience of the story:**
		{audience_age_group}, **Content Rating:** {content_rating}
		
		**Story Ending:**
		{ending_preference}
		
		Make sure the story is engaging and tailored to the specified audience and content rating. 
        Ensure the ending aligns with the preference indicated.

        """
        # Define persona and writing guidelines
        guidelines = f'''\
        Writing Guidelines:

        Delve deeper. Lose yourself in the world you're building. Unleash vivid
        descriptions to paint the scenes in your reader's mind.
        Develop your characters — let their motivations, fears, and complexities unfold naturally.
        Weave in the threads of your outline, but don't feel constrained by it.
        Allow your story to surprise you as you write. Use rich imagery, sensory details, and
        evocative language to bring the setting, characters, and events to life.
        Introduce elements subtly that can blossom into complex subplots, relationships,
        or worldbuilding details later in the story.
        Keep things intriguing but not fully resolved.
        Avoid boxing the story into a corner too early.
        Plant the seeds of subplots or potential character arc shifts that can be expanded later.

        Remember, your main goal is to write as much as you can. If you get through
        the story too fast, that is bad. Expand, never summarize.
        '''

        # Generate prompts
        premise_prompt = f'''\
        {persona}

        Write a single sentence premise for a {story_setting} story featuring {character_input}.
        '''

        outline_prompt = f'''\
        {persona}

        You have a gripping premise in mind:

        {{premise}}

        Write an outline for the plot of your story.
        '''

        starting_prompt = f'''\
        {persona}

        You have a gripping premise in mind:

        {{premise}}

        Your imagination has crafted a rich narrative outline:

        {{outline}}

        First, silently review the outline and the premise. Consider how to start the
        story.

        Start to write the very beginning of the story. You are not expected to finish
        the whole story now. Your writing should be detailed enough that you are only
        scratching the surface of the first bullet of your outline. Try to write AT
        MINIMUM 4000 WORDS.

        {guidelines}
        '''

        continuation_prompt = f'''\
        {persona}

        You have a gripping premise in mind:

        {{premise}}

        Your imagination has crafted a rich narrative outline:

        {{outline}}

        You've begun to immerse yourself in this world, and the words are flowing.
        Here's what you've written so far:

        {{story_text}}

        =====

        First, silently review the outline and story so far. Identify what the single
        next part of your outline you should write.

        Your task is to continue where you left off and write the next part of the story.
        You are not expected to finish the whole story now. Your writing should be
        detailed enough that you are only scratching the surface of the next part of
        your outline. Try to write AT MINIMUM 2000 WORDS. However, only once the story
        is COMPLETELY finished, write IAMDONE. Remember, do NOT write a whole chapter
        right now.

        {guidelines}
        '''

        # Generate prompts
        try:
            premise = generate_with_retry(premise_prompt)
            st.info(f"The premise of the story is: {premise}")
        except Exception as err:
            st.error(f"Premise Generation Error: {err}")
            return

        outline = generate_with_retry(outline_prompt.format(premise=premise))
        with st.expander("Click to Checkout the outline, writing still in progress.."):
            st.markdown(f"The Outline of the story is: {outline}\n\n")
        
        if not outline:
            st.error("Failed to generate outline. Exiting...")
            return

        # Generate starting draft
        try:
            starting_draft = generate_with_retry(
                    starting_prompt.format(premise=premise, outline=outline))
        except Exception as err:
            st.error(f"Failed to Generate Story draft: {err}")
            return

        try:
            draft = starting_draft
            continuation = generate_with_retry(
                    continuation_prompt.format(premise=premise, outline=outline, story_text=draft))
        except Exception as err:
            st.error(f"Failed to write the initial draft: {err}")

        # Add the continuation to the initial draft, keep building the story until we see 'IAMDONE'
        try:
            draft += '\n\n' + continuation
        except Exception as err:
            st.error(f"Failed as: {err} and {continuation}")
        
        with st.status("Story Writing in Progress..", expanded=True) as status:
            status.update(label=f"Writing in progress... Current draft length: {len(draft)} characters")
            while 'IAMDONE' not in continuation:
                try:
                    status.update(label=f"Writing in progress... Current draft length: {len(draft)} characters")
                    continuation = generate_with_retry(
                        continuation_prompt.format(premise=premise, outline=outline, story_text=draft))
                    draft += '\n\n' + continuation
                except Exception as err:
                    st.error(f"Failed to continually write the story: {err}")
                    return

        # Remove 'IAMDONE' and print the final story
        final = draft.replace('IAMDONE', '').strip()
        return(final)

    except Exception as e:
        st.error(f"Main Story writing: An error occurred: {e}")
        return ""
