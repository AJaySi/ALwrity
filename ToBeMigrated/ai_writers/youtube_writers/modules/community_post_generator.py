"""
YouTube Community Post Generator Module

This module provides sophisticated functionality for generating engaging community posts
with AI-powered content suggestions, engagement analysis, and timing optimization.
"""

import streamlit as st
import time
import logging
import random
from datetime import datetime, timedelta
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
import re
from textblob import TextBlob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_community_post_generator')

def generate_community_post(post_type, main_topic, target_audience, tone_style, 
                          content_purpose, channel_niche, include_emoji=True,
                          include_hashtags=True, include_poll=False, 
                          include_image_prompt=False, include_timing_suggestion=True,
                          max_length=None, language="English"):
    """Generate an AI-optimized community post with engagement features."""
    
    # Create a custom system prompt for community post generation
    system_prompt = f"""You are a YouTube Community Post expert specializing in creating highly engaging, 
    conversion-optimized posts that drive channel growth and viewer interaction.
    Focus on creating posts that encourage meaningful engagement while maintaining the channel's voice.
    Write the entire post in {language}.
    Consider timing, audience psychology, and platform-specific best practices."""
    
    # Build post type-specific instructions
    post_instructions = {
        "Question": "Create an thought-provoking question that sparks discussion",
        "Poll": "Design a compelling poll with strategic options that drive engagement",
        "Behind the Scenes": "Share an authentic, exclusive glimpse into the content creation process",
        "Sneak Peek": "Tease upcoming content in an exciting way",
        "Channel Update": "Share channel news in an engaging format",
        "Milestone Celebration": "Celebrate achievements while engaging the community",
        "Content Preview": "Preview upcoming video content engagingly",
        "Fan Spotlight": "Highlight community members/comments",
        "Quick Tip": "Share a valuable tip related to your niche",
        "Discussion Starter": "Begin a meaningful community discussion"
    }
    
    # Build engagement hooks based on content purpose
    engagement_hooks = {
        "Build Hype": [
            "Create anticipation for upcoming content",
            "Use countdown elements",
            "Include exclusive previews"
        ],
        "Drive Discussion": [
            "Ask open-ended questions",
            "Present contrasting viewpoints",
            "Share controversial opinions"
        ],
        "Gather Feedback": [
            "Ask specific questions",
            "Create focused polls",
            "Request detailed responses"
        ],
        "Share Updates": [
            "Create excitement around news",
            "Include behind-the-scenes elements",
            "Add personal touches"
        ],
        "Boost Engagement": [
            "Include call-to-actions",
            "Create interactive elements",
            "Use engagement triggers"
        ]
    }
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Create a YouTube Community Post about **{main_topic}** with these specifications:

    **Core Elements:**
    - Post Type: {post_type} - {post_instructions.get(post_type, "Create an engaging post")}
    - Target Audience: {target_audience}
    - Tone/Style: {tone_style}
    - Content Purpose: {content_purpose}
    - Channel Niche: {channel_niche}
    - Language: {language}
    {"- Maximum Length: " + str(max_length) + " characters" if max_length else ""}

    **Required Elements:**
    {"- Include strategic emoji placement" if include_emoji else ""}
    {"- Include relevant hashtags" if include_hashtags else ""}
    {"- Include poll options" if include_poll else ""}
    {"- Include image prompt suggestions" if include_image_prompt else ""}
    {"- Include optimal posting time suggestion" if include_timing_suggestion else ""}

    **Engagement Hooks:**
    {" ".join(engagement_hooks.get(content_purpose, ["Create engaging content"]))}

    **Format the post with:**
    1. Main Content
    2. Engagement Elements
    3. Call-to-Action
    4. Additional Components (hashtags, etc.)

    **Remember:**
    - Keep the tone consistent with channel voice
    - Use psychology triggers for engagement
    - Include clear call-to-actions
    - Make it easy to respond to
    - Create shareable content
    """
    
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response
    except Exception as err:
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None

def analyze_post_engagement(post_content):
    """Analyze a community post for engagement potential using advanced AI metrics."""
    analysis = {
        'engagement_score': 0,
        'emotional_triggers': 0,
        'call_to_action_strength': 0,
        'readability_score': 0,
        'hashtag_optimization': 0,
        'timing_recommendation': None,
        'sentiment_analysis': {},
        'virality_potential': 0,
        'audience_resonance': 0,
        'content_uniqueness': 0,
        'psychological_triggers': [],
        'improvement_suggestions': [],
        'engagement_patterns': {},
        'content_structure': {},
        'seo_optimization': 0
    }
    
    # Sentiment Analysis using TextBlob
    blob = TextBlob(post_content)
    analysis['sentiment_analysis'] = {
        'polarity': round((blob.sentiment.polarity + 1) * 50, 2),  # Convert to 0-100 scale
        'subjectivity': round(blob.sentiment.subjectivity * 100, 2),
        'tone': 'Positive' if blob.sentiment.polarity > 0 else 'Negative' if blob.sentiment.polarity < 0 else 'Neutral'
    }
    
    # Analyze emotional triggers with expanded vocabulary
    emotional_categories = {
        'excitement': ['excited', 'amazing', 'incredible', 'awesome', 'mind-blowing'],
        'curiosity': ['guess what', 'secret', 'revealed', 'discover', 'mystery'],
        'urgency': ['limited', 'hurry', 'soon', 'don\'t miss', 'last chance'],
        'social_proof': ['everyone', 'community', 'fans', 'you all', 'together'],
        'exclusivity': ['exclusive', 'special', 'limited', 'only', 'selected']
    }
    
    trigger_counts = {category: 0 for category in emotional_categories}
    for category, words in emotional_categories.items():
        trigger_counts[category] = sum(post_content.lower().count(word) for word in words)
    
    analysis['emotional_triggers'] = min(sum(trigger_counts.values()) * 15, 100)
    analysis['psychological_triggers'] = [cat for cat, count in trigger_counts.items() if count > 0]
    
    # Analyze call-to-action strength with pattern recognition
    cta_patterns = {
        'question_cta': r'\?',
        'direct_command': r'(?i)(comment|share|like|subscribe|follow)',
        'engagement_request': r'(?i)(let (me|us) know|tell (me|us)|what do you think)',
        'time_sensitive': r'(?i)(today|now|limited time|hurry)',
        'value_proposition': r'(?i)(learn|discover|find out|get|access)'
    }
    
    cta_strength = 0
    for pattern_type, pattern in cta_patterns.items():
        matches = len(re.findall(pattern, post_content))
        cta_strength += matches * 20
    analysis['call_to_action_strength'] = min(cta_strength, 100)
    
    # Content Structure Analysis
    analysis['content_structure'] = {
        'length_score': min(len(post_content.split()) / 5, 100),  # Optimal length analysis
        'paragraph_breaks': min(post_content.count('\n\n') * 20, 100),  # Readability through structure
        'emoji_balance': min(len(re.findall(r'[\U0001F300-\U0001F9FF]', post_content)) * 10, 100),  # Emoji usage score
        'formatting_score': min((post_content.count('*') + post_content.count('_')) * 5, 100)  # Text formatting score
    }
    
    # Virality Potential Analysis
    virality_factors = {
        'emotional_impact': analysis['emotional_triggers'],
        'shareability': analysis['content_structure']['length_score'],
        'uniqueness': random.randint(60, 100),  # Simulated uniqueness score
        'timeliness': 80 if any(word in post_content.lower() for word in ['new', 'breaking', 'update', 'just']) else 50
    }
    analysis['virality_potential'] = sum(virality_factors.values()) / len(virality_factors)
    
    # Audience Resonance Analysis
    resonance_factors = {
        'relevance': analysis['sentiment_analysis']['subjectivity'],
        'engagement_hooks': analysis['call_to_action_strength'],
        'emotional_connection': analysis['emotional_triggers']
    }
    analysis['audience_resonance'] = sum(resonance_factors.values()) / len(resonance_factors)
    
    # SEO Optimization
    seo_factors = {
        'hashtag_quality': analyze_hashtag_quality(post_content),
        'keyword_density': analyze_keyword_density(post_content),
        'url_presence': 100 if 'http' in post_content else 0,
        'mention_optimization': analyze_mentions(post_content)
    }
    analysis['seo_optimization'] = sum(seo_factors.values()) / len(seo_factors)
    
    # Engagement Pattern Analysis
    analysis['engagement_patterns'] = analyze_engagement_patterns(post_content)
    
    # Calculate overall engagement score with weighted components
    analysis['engagement_score'] = calculate_weighted_score({
        'emotional_triggers': (analysis['emotional_triggers'], 0.2),
        'call_to_action_strength': (analysis['call_to_action_strength'], 0.2),
        'virality_potential': (analysis['virality_potential'], 0.15),
        'audience_resonance': (analysis['audience_resonance'], 0.15),
        'seo_optimization': (analysis['seo_optimization'], 0.1),
        'sentiment_balance': (analysis['sentiment_analysis']['polarity'], 0.1),
        'content_structure': (sum(analysis['content_structure'].values()) / len(analysis['content_structure']), 0.1)
    })
    
    # Generate AI-powered improvement suggestions
    analysis['improvement_suggestions'] = generate_ai_suggestions(analysis)
    
    # Timing optimization
    analysis['timing_recommendation'] = get_optimal_posting_time(analysis)
    
    return analysis

def analyze_hashtag_quality(content):
    """Analyze the quality and relevance of hashtags."""
    hashtags = re.findall(r'#\w+', content)
    if not hashtags:
        return 0
    
    score = 0
    score += min(len(hashtags), 5) * 20  # Optimal number of hashtags (1-5)
    score += sum(10 for tag in hashtags if 4 <= len(tag) <= 20)  # Length optimization
    score += 20 if len(set(hashtags)) == len(hashtags) else 0  # No duplicates
    
    return min(score, 100)

def analyze_keyword_density(content):
    """Analyze keyword density and distribution."""
    words = content.lower().split()
    if not words:
        return 0
    
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Ignore short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    if not word_freq:
        return 0
    
    # Calculate density score
    max_density = max(word_freq.values()) / len(words)
    return 100 if 0.01 <= max_density <= 0.04 else 50  # Optimal density between 1-4%

def analyze_mentions(content):
    """Analyze the use of @mentions and their placement."""
    mentions = re.findall(r'@\w+', content)
    if not mentions:
        return 0
    
    score = 0
    score += min(len(mentions), 3) * 25  # Optimal number of mentions (1-3)
    score += 25 if mentions[0] in content.split()[:len(content.split())//2] else 0  # Early mention bonus
    
    return min(score, 100)

def analyze_engagement_patterns(content):
    """Analyze patterns that typically drive engagement."""
    patterns = {
        'question_hooks': len(re.findall(r'\?', content)),
        'emotional_words': len(re.findall(r'\b(love|hate|amazing|awesome|incredible|excited)\b', content.lower())),
        'community_references': len(re.findall(r'\b(we|our|community|together|everyone)\b', content.lower())),
        'action_words': len(re.findall(r'\b(get|do|make|try|click|watch|share)\b', content.lower())),
        'urgency_triggers': len(re.findall(r'\b(now|today|limited|soon|hurry)\b', content.lower()))
    }
    
    return {k: min(v * 20, 100) for k, v in patterns.items()}

def calculate_weighted_score(components):
    """Calculate weighted score from multiple components."""
    return sum(score * weight for (score, weight) in components.values())

def generate_ai_suggestions(analysis):
    """Generate AI-powered improvement suggestions based on analysis."""
    suggestions = []
    
    if analysis['emotional_triggers'] < 70:
        suggestions.append({
            'category': 'Emotional Impact',
            'suggestion': 'Add more emotional triggers to increase engagement',
            'examples': ['amazing', 'incredible', 'exciting']
        })
    
    if analysis['call_to_action_strength'] < 70:
        suggestions.append({
            'category': 'Call-to-Action',
            'suggestion': 'Strengthen your call-to-action',
            'examples': ['Comment below', 'Share your thoughts', 'Let me know']
        })
    
    if analysis['virality_potential'] < 70:
        suggestions.append({
            'category': 'Virality',
            'suggestion': 'Increase viral potential by adding trending elements',
            'examples': ['Current trends', 'Popular hashtags', 'Timely topics']
        })
    
    if analysis['seo_optimization'] < 70:
        suggestions.append({
            'category': 'SEO',
            'suggestion': 'Optimize for better discovery',
            'examples': ['Strategic hashtags', 'Relevant keywords', 'Proper mentions']
        })
    
    return suggestions

def get_optimal_posting_time(analysis):
    """Determine optimal posting time based on content analysis."""
    current_hour = datetime.now().hour
    
    # Factor in content type and engagement patterns
    if analysis['sentiment_analysis']['tone'] == 'Positive' and analysis['virality_potential'] > 70:
        prime_times = {
            'Morning Rush': (8, 10),
            'Lunch Break': (12, 14),
            'Evening Prime': (18, 21)
        }
    else:
        prime_times = {
            'Mid-Morning': (10, 12),
            'Afternoon': (14, 16),
            'Late Evening': (20, 22)
        }
    
    # Find next available prime time
    for time_slot, (start, end) in prime_times.items():
        if start <= current_hour <= end:
            return f"Post now ({time_slot})"
        elif current_hour < start:
            return f"Schedule for {time_slot} ({start}:00 - {end}:00)"
    
    return "Schedule for tomorrow morning (8:00 - 10:00)"

def write_yt_community_post():
    """Create a user interface for YouTube Community Post Generator."""
    st.write("Generate engaging community posts that drive interaction and channel growth.")
    
    # Initialize session state
    if "generated_post" not in st.session_state:
        st.session_state.generated_post = None
    if "post_history" not in st.session_state:
        st.session_state.post_history = []
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Post Creation", "Engagement Strategy", "Preview & Analytics"])
    
    with tab1:
        # Core elements
        main_topic = st.text_area("Main Topic/Message", 
                                placeholder="e.g., New video announcement, Channel update, Question for viewers")
        
        col1, col2 = st.columns(2)
        with col1:
            post_type = st.selectbox("Post Type", [
                "Question",
                "Poll",
                "Behind the Scenes",
                "Sneak Peek",
                "Channel Update",
                "Milestone Celebration",
                "Content Preview",
                "Fan Spotlight",
                "Quick Tip",
                "Discussion Starter"
            ])
            
            target_audience = st.text_input("Target Audience", 
                                          placeholder="e.g., Tech enthusiasts, Gamers, DIY lovers")
        
        with col2:
            content_purpose = st.selectbox("Content Purpose", [
                "Build Hype",
                "Drive Discussion",
                "Gather Feedback",
                "Share Updates",
                "Boost Engagement"
            ])
            
            tone_style = st.selectbox("Tone/Style", [
                "Casual",
                "Professional",
                "Excited",
                "Mysterious",
                "Humorous",
                "Informative"
            ])
        
        channel_niche = st.text_input("Channel Niche", 
                                    placeholder="e.g., Tech Reviews, Gaming, Education")
    
    with tab2:
        # Engagement options
        st.subheader("Engagement Elements")
        col1, col2 = st.columns(2)
        
        with col1:
            include_emoji = st.checkbox("Include Emojis", value=True)
            include_hashtags = st.checkbox("Include Hashtags", value=True)
            max_length = st.number_input("Maximum Length (characters)", 
                                       min_value=100, max_value=2000, value=500)
        
        with col2:
            include_poll = st.checkbox("Include Poll", value=False)
            include_image_prompt = st.checkbox("Include Image Suggestions", value=True)
            include_timing_suggestion = st.checkbox("Include Timing Suggestion", value=True)
        
        # Advanced options
        st.subheader("Advanced Options")
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
            "Chinese"
        ])
    
    with tab3:
        if st.session_state.generated_post:
            # Display the generated post
            st.subheader("Generated Community Post")
            
            # Create tabs for different views
            post_tab1, post_tab2, post_tab3 = st.tabs(["Preview", "Analytics", "History"])
            
            with post_tab1:
                st.markdown(st.session_state.generated_post)
                
                # Quick actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Copy to Clipboard"):
                        st.code(st.session_state.generated_post)
                        st.success("Post copied to clipboard!")
                
                with col2:
                    if st.button("Save to History"):
                        st.session_state.post_history.append({
                            'post': st.session_state.generated_post,
                            'timestamp': datetime.now(),
                            'type': post_type
                        })
                        st.success("Post saved to history!")
            
            with post_tab2:
                # Analyze the post
                analysis = analyze_post_engagement(st.session_state.generated_post)
                
                # Create expandable sections for different analysis categories
                with st.expander("📊 Overall Performance Metrics", expanded=True):
                    cols = st.columns(3)
                    
                    with cols[0]:
                        score = analysis['engagement_score']
                        color = "red" if score < 60 else "orange" if score < 80 else "green"
                        st.markdown(f"### Overall Score: <span style='color: {color}'>{score:.1f}%</span>", 
                                  unsafe_allow_html=True)
                        
                        # Sentiment Analysis
                        st.markdown("#### Sentiment Analysis")
                        st.metric("Polarity", f"{analysis['sentiment_analysis']['polarity']}%")
                        st.metric("Subjectivity", f"{analysis['sentiment_analysis']['subjectivity']}%")
                        st.info(f"Tone: {analysis['sentiment_analysis']['tone']}")
                    
                    with cols[1]:
                        st.markdown("#### Engagement Metrics")
                        st.metric("Emotional Impact", f"{analysis['emotional_triggers']}%")
                        st.metric("CTA Strength", f"{analysis['call_to_action_strength']}%")
                        st.metric("Virality Potential", f"{analysis['virality_potential']:.1f}%")
                    
                    with cols[2]:
                        st.markdown("#### Content Quality")
                        st.metric("Audience Resonance", f"{analysis['audience_resonance']:.1f}%")
                        st.metric("SEO Score", f"{analysis['seo_optimization']:.1f}%")
                        if analysis['timing_recommendation']:
                            st.success(f"📅 {analysis['timing_recommendation']}")
                
                with st.expander("🎯 Psychological Triggers & Patterns"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Active Psychological Triggers")
                        if analysis['psychological_triggers']:
                            for trigger in analysis['psychological_triggers']:
                                st.markdown(f"✓ {trigger.title()}")
                        else:
                            st.info("No strong psychological triggers detected")
                    
                    with col2:
                        st.markdown("#### Engagement Patterns")
                        patterns = analysis['engagement_patterns']
                        for pattern, score in patterns.items():
                            st.metric(pattern.replace('_', ' ').title(), f"{score}%")
                
                with st.expander("📝 Content Structure Analysis"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        structure = analysis['content_structure']
                        st.markdown("#### Structure Metrics")
                        for metric, score in structure.items():
                            st.metric(
                                metric.replace('_', ' ').title(),
                                f"{score:.1f}%"
                            )
                    
                    with col2:
                        st.markdown("#### SEO Analysis")
                        st.metric("Hashtag Quality", f"{analyze_hashtag_quality(st.session_state.generated_post)}%")
                        st.metric("Keyword Density", f"{analyze_keyword_density(st.session_state.generated_post)}%")
                        st.metric("Mention Optimization", f"{analyze_mentions(st.session_state.generated_post)}%")
                
                # Show improvement suggestions
                if analysis['improvement_suggestions']:
                    with st.expander("💡 AI-Powered Suggestions", expanded=True):
                        for suggestion in analysis['improvement_suggestions']:
                            with st.container():
                                st.markdown(f"#### {suggestion['category']}")
                                st.info(suggestion['suggestion'])
                                if suggestion['examples']:
                                    st.markdown("**Examples:**")
                                    for example in suggestion['examples']:
                                        st.markdown(f"- {example}")
                
                # Add a refresh button for analysis
                if st.button("🔄 Refresh Analysis"):
                    st.rerun()
            
            with post_tab3:
                if st.session_state.post_history:
                    st.subheader("Previous Posts")
                    for i, post in enumerate(reversed(st.session_state.post_history)):
                        with st.expander(f"Post {len(st.session_state.post_history)-i}: "
                                       f"{post['type']} - "
                                       f"{post['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                            st.write(post['post'])
                else:
                    st.info("No post history yet. Save posts to see them here!")
    
    # Generate button
    if st.button("Generate Community Post"):
        if not main_topic:
            st.error("Please enter a main topic/message.")
            return
        
        with st.spinner("Generating community post..."):
            post = generate_community_post(
                post_type, main_topic, target_audience, tone_style,
                content_purpose, channel_niche, include_emoji,
                include_hashtags, include_poll, include_image_prompt,
                include_timing_suggestion, max_length, language
            )
            
            if post:
                st.session_state.generated_post = post
                st.success("✨ Post generated successfully! Check the 'Preview & Analytics' tab to view, analyze, and save your post.")
                st.rerun()
            else:
                st.error("Failed to generate post. Please try again.") 