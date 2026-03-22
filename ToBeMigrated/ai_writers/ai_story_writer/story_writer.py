import time
import os
import json
import streamlit as st

from .ai_story_generator import ai_story


def story_input_section():
    st.title("🧕 Alwrity - AI Story Writer")
    personas = [
        ("Award-Winning Science Fiction Author", "👽 Award-Winning Science Fiction Author"),
        ("Historical Fiction Author", "🏺 Historical Fiction Author"),
        ("Fantasy World Builder", "🧙 Fantasy World Builder"),
        ("Mystery Novelist", "🕵️ Mystery Novelist"),
        ("Romantic Poet", "💌 Romantic Poet"),
        ("Thriller Writer", "🔪 Thriller Writer"),
        ("Children's Book Author", "📚 Children's Book Author"),
        ("Satirical Humorist", "😂 Satirical Humorist"),
        ("Biographical Writer", "📜 Biographical Writer"),
        ("Dystopian Visionary", "🌆 Dystopian Visionary"),
        ("Magical Realism Author", "🪄 Magical Realism Author")
    ]

    selected_persona_name = st.selectbox(
        "Select Your Story Writing Persona Or Book Genre",
        options=[persona[0] for persona in personas]
    )

    persona_descriptions = {
    "Award-Winning Science Fiction Author": "You are an award-winning science fiction author with a penchant for expansive, intricately woven stories. Your ultimate goal is to write the next award-winning sci-fi novel.",
    "Historical Fiction Author": "You are a seasoned historical fiction author, meticulously researching past eras to weave captivating narratives. Your goal is to transport readers to different times and places through your vivid storytelling.",
    "Fantasy World Builder": "You are a world-building enthusiast, crafting intricate realms filled with magic, mythical creatures, and epic quests. Your ambition is to create the next immersive fantasy saga that captivates readers' imaginations.",
    "Mystery Novelist": "You are a master of suspense and intrigue, intricately plotting out mysteries with unexpected twists and turns. Your aim is to keep readers on the edge of their seats, eagerly turning pages to unravel the truth.",
    "Romantic Poet": "You are a romantic at heart, composing verses that capture the essence of love, longing, and human connections. Your dream is to write the next timeless love story that leaves readers swooning.",
    "Thriller Writer": "You are a thrill-seeker, crafting adrenaline-pumping tales of danger, suspense, and high-stakes action. Your mission is to keep readers hooked from start to finish with heart-pounding thrills and unexpected twists.",
    "Children's Book Author": "You are a storyteller for the young and young at heart, creating whimsical worlds and lovable characters that inspire imagination and wonder. Your goal is to spark joy and curiosity in young readers with enchanting tales.",
    "Satirical Humorist": "You are a keen observer of society, using humor and wit to satirize the absurdities of everyday life. Your aim is to entertain and provoke thought, delivering biting social commentary through clever and humorous storytelling.",
    "Biographical Writer": "You are a chronicler of lives, delving into the stories of real people and events to illuminate the human experience. Your passion is to bring history to life through richly detailed biographies that resonate with readers.",
    "Dystopian Visionary": "You are a visionary writer, exploring dark and dystopian futures that reflect contemporary fears and anxieties. Your vision is to challenge societal norms and provoke reflection on the path humanity is heading.",
    "Magical Realism Author": "You are a purveyor of magical realism, blending the ordinary with the extraordinary to create enchanting and thought-provoking tales. Your goal is to blur the lines between reality and fantasy, leaving readers enchanted and introspective."
        }

    # Story Setting
    st.subheader("🌍 Story Setting")
    story_setting = st.text_area(
        label="**Story Setting** (e.g., medieval kingdom in the past, futuristic city in the future, haunted house in the present):",
        placeholder="""Enter settings for your story, like Location (e.g., medieval kingdom, futuristic city, haunted house),
        Time period in which your story is set (e.g: Past, Present, Future)
        Example: 'A bustling futuristic city with towering skyscrapers and flying cars, set in the year 2150. 
        The city is known for its technological advancements but has a dark underbelly of crime and corruption.'""",
        help="Describe the main location and time period where the story will unfold in a detailed manner."
    )
    
    # Main Characters
    st.subheader("👥 Main Characters")
    character_input = st.text_area(
        label="**Character Information** (Names, Descriptions, Roles)",
        placeholder="""Example:
        Character Names: John, Xishan, Amol
        Character Descriptions: John is a tall, muscular man with a kind heart. Xishan is a clever and resourceful woman. Amol is a mischievous and energetic young boy.
        Character Roles: John - Hero, Xishan - Sidekick, Amol - Supporting Character""",
        help="Enter character information as specified in the placeholder."
    )
    
    # Plot Elements
    st.subheader("🗺️ Plot Elements")
    plot_elements = st.text_area(
        "**Plot Elements** - (Theme, Key Events & Main Conflict)",
        placeholder="""Example:
        Story Theme: Love conquers all, The hero's journey, Good vs. evil.
        Key Events: The hero meets the villain, The hero faces a challenge, The hero overcomes the conflict.
        Main Conflict: The hero must save the world from a powerful enemy, The hero must overcome a personal obstacle to achieve their goal.""",
        help="Enter plot elements as specified in the placeholder."
    )
    
    # Tone and Style
    st.subheader("🎨 Tone and Style")
    col1, col2, col3 = st.columns(3)
    with col1:
        writing_style = st.selectbox(
            "**Writing Style:**",
            ["🧐 Formal", "😎 Casual", "🎼 Poetic", "😂 Humorous"],
            help="Choose the writing style that fits your story."
        )
    with col2:
        story_tone = st.selectbox(
            "**Story Tone:**",
            ["🌑 Dark", "☀️ Uplifting", "⏳ Suspenseful", "🎈 Whimsical"],
            help="Select the overall tone or mood of the story."
        )
    with col3:
        narrative_pov = st.selectbox(
            "**Narrative Point of View:**",
            ["👤 First Person", "👥 Third Person Limited", "👁️ Third Person Omniscient"],
            help="Choose the point of view from which the story is told."
        )
    
    # Target Audience
    st.subheader("👨‍👩‍👧‍👦 Target Audience")
    col1, col2, col3 = st.columns(3)
    with col1:
        audience_age_group = st.selectbox(
            "**Audience Age Group:**",
            ["🧒 Children", "👨‍🎓 Young Adults", "🧑‍🦳 Adults"],
            help="Choose the intended audience age group."
        )
    with col2:
        content_rating = st.selectbox(
            "**Content Rating:**",
            ["🟢 G", "🟡 PG", "🔵 PG-13", "🔴 R"],
            help="Select a content rating for appropriateness."
        )
    with col3:
        ending_preference = st.selectbox(
            "Story Conclusion:",
            ["😊 Happy", "😢 Tragic", "❓ Cliffhanger", "🔀 Twist"],
            help="Choose the type of ending you prefer for the story."
        )

    if st.button('AI, Write a Story..'):
        if character_input.strip():
            with st.spinner("Generating Story...💥💥"):
                story_content = ai_story(persona_descriptions[selected_persona_name],
                        story_setting, character_input, plot_elements, writing_style,
                        story_tone, narrative_pov, audience_age_group, content_rating,
                        ending_preference)
                if story_content:
                    st.subheader('**🧕 Your Awesome Story:**')
                    st.markdown(story_content)
                else:
                    st.error("💥 **Failed to generate Story. Please try again!**")
        else:
            st.error("Describe the story you have in your mind.. !")
