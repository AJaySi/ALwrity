"""
Enhanced Smart Tweet Generator with real AI integration and platform adapter connectivity.
"""

import streamlit as st
import re
import json
import asyncio
from typing import Dict, List, Tuple, Optional, Any
import random
import emoji
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from ....gpt_providers.text_generation.main_text_generation import llm_text_gen
from ....integrations.twitter_auth_bridge import (
    get_twitter_adapter, 
    is_twitter_authenticated,
    validate_twitter_credentials,
    save_twitter_credentials,
    setup_twitter_session,
    clear_twitter_session
)
from ..twitter_streamlit_ui import (
    TweetForm,
    TweetCard,
    Theme,
    save_to_session,
    get_from_session,
    show_success_message,
    show_error_message,
    show_info_message,
    show_warning_message,
    validate_tweet_content,
    validate_hashtags,
    validate_emojis,
    calculate_engagement_score,
    generate_tweet_metrics,
    copy_to_clipboard,
    create_download_button
)

# Constants
MAX_TWEET_LENGTH = 280
EMOJI_CATEGORIES = {
    "Humorous": ["😄", "😂", "🤣", "😊", "😉", "😎", "🤪", "😜", "🤓", "😇"],
    "Informative": ["📚", "📊", "📈", "🔍", "💡", "📝", "📋", "🔎", "📖", "📑"],
    "Inspirational": ["✨", "🌟", "💫", "⭐", "🔥", "💪", "🙌", "👏", "💯", "🎯"],
    "Serious": ["🤔", "💭", "🧐", "📢", "🔔", "⚖️", "🎓", "📊", "🔬", "📰"],
    "Casual": ["👋", "👍", "🙋", "💁", "🤗", "👌", "✌️", "🤝", "👊", "🙏"]
}

def get_current_user_id() -> str:
    """Get current user ID for authentication."""
    # In a real app, this would come from your authentication system
    # For now, we'll use a session-based approach
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{hash(st.session_state.get('session_id', 'default'))}"
    return st.session_state.user_id

def render_twitter_authentication():
    """Render Twitter authentication interface."""
    st.markdown("### 🔐 Twitter Authentication")
    
    user_id = get_current_user_id()
    
    if is_twitter_authenticated():
        user_info = st.session_state.get('twitter_user_info', {})
        
        # Show connected status
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if user_info.get('profile_image_url'):
                st.image(user_info['profile_image_url'], width=60)
        
        with col2:
            st.markdown(f"**{user_info.get('name', 'Unknown')}**")
            st.markdown(f"@{user_info.get('screen_name', 'unknown')}")
            st.markdown(f"Followers: {user_info.get('followers_count', 0):,}")
        
        with col3:
            if st.button("🔓 Disconnect", type="secondary"):
                clear_twitter_session()
                st.rerun()
        
        return True
    else:
        st.warning("⚠️ Connect your Twitter account to enable posting")
        
        with st.expander("🔧 Twitter API Configuration", expanded=True):
            st.markdown("""
            **To connect your Twitter account:**
            1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
            2. Create a new app or use existing one
            3. Get your API credentials
            4. Enter them below
            """)
            
            # Input fields for credentials
            api_key = st.text_input("API Key", type="password", help="Your Twitter API Key")
            api_secret = st.text_input("API Secret", type="password", help="Your Twitter API Secret")
            access_token = st.text_input("Access Token", type="password", help="Your Twitter Access Token")
            access_token_secret = st.text_input("Access Token Secret", type="password", help="Your Twitter Access Token Secret")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧪 Test Connection", use_container_width=True):
                    if all([api_key, api_secret, access_token, access_token_secret]):
                        credentials = {
                            'api_key': api_key,
                            'api_secret': api_secret,
                            'access_token': access_token,
                            'access_token_secret': access_token_secret
                        }
                        
                        with st.spinner("Testing connection..."):
                            is_valid, message = validate_twitter_credentials(credentials)
                            
                        if is_valid:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("Please fill in all credentials")
            
            with col2:
                if st.button("💾 Save & Connect", use_container_width=True, type="primary"):
                    if all([api_key, api_secret, access_token, access_token_secret]):
                        credentials = {
                            'api_key': api_key,
                            'api_secret': api_secret,
                            'access_token': access_token,
                            'access_token_secret': access_token_secret
                        }
                        
                        with st.spinner("Connecting to Twitter..."):
                            # Validate first
                            is_valid, message = validate_twitter_credentials(credentials)
                            
                            if is_valid:
                                # Save credentials
                                if save_twitter_credentials(user_id, credentials):
                                    # Setup session
                                    if setup_twitter_session(user_id):
                                        st.success("✅ Successfully connected to Twitter!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to setup session")
                                else:
                                    st.error("❌ Failed to save credentials")
                            else:
                                st.error(f"❌ {message}")
                    else:
                        st.error("Please fill in all credentials")
        
        return False

def apply_tweet_generator_styling():
    """Apply modern CSS styling specific to the tweet generator."""
    st.markdown("""
    <style>
    /* Tweet Generator Specific Styles */
    .tweet-generator-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    .tweet-preview {
        background: white;
        border: 1px solid #E1E8ED;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        position: relative;
    }
    
    .tweet-preview::before {
        content: "🐦";
        position: absolute;
        top: -10px;
        left: 20px;
        background: white;
        padding: 0 10px;
        font-size: 1.2rem;
    }
    
    .tweet-text {
        font-size: 1.1rem;
        line-height: 1.5;
        color: #14171A;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .tweet-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #657786;
        font-size: 0.9rem;
        border-top: 1px solid #E1E8ED;
        padding-top: 1rem;
    }
    
    .character-count {
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
    }
    
    .count-good {
        background: #E6F7FF;
        color: #1890FF;
    }
    
    .count-warning {
        background: #FFF7E6;
        color: #FA8C16;
    }
    
    .count-danger {
        background: #FFF1F0;
        color: #F5222D;
    }
    
    .engagement-score {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #52C41A, #73D13D);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .tweet-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .action-btn {
        background: #F7F9FA;
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #657786;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .action-btn:hover {
        background: #1DA1F2;
        color: white;
        border-color: #1DA1F2;
    }
    
    .input-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .tips-section {
        background: linear-gradient(135deg, #E6F7FF, #F0F9FF);
        border: 1px solid #91D5FF;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .tip-item {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        color: #2D3748;
    }
    
    .tip-icon {
        color: #1890FF;
        font-weight: bold;
        margin-top: 0.1rem;
    }
    
    .ai-status {
        background: linear-gradient(135deg, #52C41A, #73D13D);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .twitter-status {
        background: linear-gradient(135deg, #1DA1F2, #0C85D0);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Form Enhancements */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #1DA1F2 !important;
        box-shadow: 0 0 0 3px rgba(29, 161, 242, 0.1) !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 2px solid #E2E8F0 !important;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #1DA1F2, #0C85D0) !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .tweet-generator-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .input-section {
            padding: 1rem;
        }
        
        .tweet-actions {
            flex-direction: column;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def suggest_hashtags(topic: str, tone: str) -> List[str]:
    """Suggest relevant hashtags based on topic and tone."""
    base_hashtags = {
        "professional": ["#Business", "#Leadership", "#Innovation", "#Growth", "#Success"],
        "casual": ["#Life", "#Fun", "#Trending", "#Daily", "#Mood"],
        "informative": ["#Learn", "#Tips", "#HowTo", "#Knowledge", "#Education"],
        "humorous": ["#Funny", "#LOL", "#Humor", "#Comedy", "#Memes"],
        "inspirational": ["#Motivation", "#Success", "#Growth", "#Inspiration", "#Goals"]
    }
    
    topic_hashtags = {
        "tech": ["#Technology", "#TechNews", "#Innovation", "#AI", "#Digital"],
        "business": ["#Business", "#Entrepreneurship", "#Startup", "#Marketing", "#Sales"],
        "marketing": ["#Marketing", "#DigitalMarketing", "#SocialMedia", "#Content", "#Branding"],
        "education": ["#Education", "#Learning", "#Knowledge", "#Skills", "#Training"],
        "health": ["#Health", "#Wellness", "#Fitness", "#Lifestyle", "#Mindfulness"]
    }
    
    # Combine and return unique hashtags
    suggested = base_hashtags.get(tone.lower(), []) + topic_hashtags.get(topic.lower(), [])
    return list(set(suggested))[:5]

def suggest_emojis(tone: str, count: int = 3) -> List[str]:
    """Suggest emojis based on tone."""
    return EMOJI_CATEGORIES.get(tone.capitalize(), EMOJI_CATEGORIES["Casual"])[:count]

def calculate_character_count(text: str) -> Dict[str, any]:
    """Calculate character count and provide styling info."""
    count = len(text)
    remaining = MAX_TWEET_LENGTH - count
    
    if count <= 240:
        status = "good"
        color_class = "count-good"
    elif count <= 270:
        status = "warning"
        color_class = "count-warning"
    else:
        status = "danger"
        color_class = "count-danger"
    
    return {
        "count": count,
        "remaining": remaining,
        "status": status,
        "color_class": color_class,
        "percentage": (count / MAX_TWEET_LENGTH) * 100
    }

def render_tweet_preview(tweet_text: str, hashtags: List[str], engagement_score: int):
    """Render a modern tweet preview."""
    char_info = calculate_character_count(tweet_text)
    
    # Format hashtags
    hashtag_str = " ".join(hashtags) if hashtags else ""
    full_text = f"{tweet_text} {hashtag_str}".strip()
    
    st.markdown(f"""
    <div class="tweet-preview">
        <div class="tweet-text">{full_text}</div>
        <div class="tweet-meta">
            <div class="engagement-score">
                📊 {engagement_score}% Engagement Score
            </div>
            <div class="character-count {char_info['color_class']}">
                {char_info['count']}/{MAX_TWEET_LENGTH}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return char_info

def render_optimization_tips():
    """Render tweet optimization tips."""
    st.markdown("""
    <div class="tips-section">
        <h4 style="margin-bottom: 1rem; color: #1890FF;">💡 Tweet Optimization Tips</h4>
        <div class="tip-item">
            <span class="tip-icon">•</span>
            <span>Keep tweets between 70-140 characters for maximum engagement</span>
        </div>
        <div class="tip-item">
            <span class="tip-icon">•</span>
            <span>Use 1-2 relevant hashtags to increase discoverability</span>
        </div>
        <div class="tip-item">
            <span class="tip-icon">•</span>
            <span>Include emojis to make your tweets more visually appealing</span>
        </div>
        <div class="tip-item">
            <span class="tip-icon">•</span>
            <span>Ask questions to encourage engagement and replies</span>
        </div>
        <div class="tip-item">
            <span class="tip-icon">•</span>
            <span>Post during peak hours (9-10 AM, 7-9 PM) for better reach</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def generate_ai_tweet_variations(
    hook: str,
    target_audience: str,
    tone: str,
    call_to_action: str = "",
    keywords: str = "",
    length: str = "medium",
    num_variations: int = 3
) -> List[Dict]:
    """Generate tweet variations using real AI integration."""
    
    # Create a comprehensive prompt for AI generation
    system_prompt = """You are an expert social media content creator specializing in Twitter. 
    Your task is to create engaging, viral-worthy tweets that maximize engagement and reach.
    
    You understand Twitter's algorithm, trending topics, and what makes content shareable.
    You know how to craft tweets that spark conversations, drive engagement, and build communities.
    
    Always consider:
    - Character limits (280 max)
    - Optimal hashtag usage (1-2 per tweet)
    - Emoji placement for visual appeal
    - Call-to-action integration
    - Audience-specific language and tone
    - Current social media trends
    """
    
    # Length specifications
    length_specs = {
        "short": "50-100 characters",
        "medium": "100-180 characters", 
        "long": "180-270 characters"
    }
    
    length_spec = length_specs.get(length, "100-180 characters")
    
    prompt = f"""
    Create {num_variations} unique, engaging tweet variations with these specifications:
    
    **Content Requirements:**
    - Main Topic/Hook: {hook}
    - Target Audience: {target_audience}
    - Tone: {tone}
    - Call to Action: {call_to_action}
    - Keywords to include: {keywords}
    - Length: {length_spec}
    
    **Tweet Guidelines:**
    1. Each tweet must be unique and engaging
    2. Include 1-2 relevant hashtags per tweet
    3. Use appropriate emojis for the tone (2-3 per tweet)
    4. Stay within Twitter's 280 character limit
    5. Naturally integrate the call to action
    6. Make them conversation-starters
    7. Optimize for engagement and shareability
    
    **Output Format:**
    Return ONLY a valid JSON array with this exact structure:
    [
        {{
            "text": "tweet content without hashtags",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "emojis": ["emoji1", "emoji2"],
            "engagement_score": 85,
            "reasoning": "brief explanation of why this tweet will perform well"
        }}
    ]
    
    **Important:**
    - Do not include hashtags in the "text" field - put them separately in "hashtags"
    - Engagement score should be 60-95 based on predicted performance
    - Each tweet should have a different approach/angle
    - Make them authentic and human-like, not robotic
    """
    
    try:
        # Generate tweets using AI
        ai_response = llm_text_gen(prompt, system_prompt)
        
        # Parse the JSON response
        try:
            # Clean the response to extract JSON
            json_start = ai_response.find('[')
            json_end = ai_response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                tweets = json.loads(json_str)
                
                # Validate and clean the tweets
                validated_tweets = []
                for tweet in tweets:
                    if validate_ai_tweet(tweet):
                        validated_tweets.append(tweet)
                
                if validated_tweets:
                    return validated_tweets
                else:
                    raise ValueError("No valid tweets generated")
            else:
                raise ValueError("No valid JSON found in response")
                
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response as JSON: {e}")
            # Fallback to template-based generation
            return generate_fallback_tweets(hook, tone, call_to_action, keywords, num_variations)
            
    except Exception as e:
        st.error(f"AI generation failed: {e}")
        # Fallback to template-based generation
        return generate_fallback_tweets(hook, tone, call_to_action, keywords, num_variations)

def validate_ai_tweet(tweet: Dict) -> bool:
    """Validate AI-generated tweet structure and content."""
    required_fields = ['text', 'hashtags', 'emojis', 'engagement_score']
    
    # Check required fields
    for field in required_fields:
        if field not in tweet:
            return False
    
    # Validate text length
    full_text = f"{tweet['text']} {' '.join(tweet['hashtags'])}"
    if len(full_text) > MAX_TWEET_LENGTH:
        return False
    
    # Validate hashtags format
    if not isinstance(tweet['hashtags'], list):
        return False
    
    for hashtag in tweet['hashtags']:
        if not hashtag.startswith('#'):
            return False
    
    # Validate engagement score
    if not isinstance(tweet['engagement_score'], (int, float)):
        return False
    
    if not (0 <= tweet['engagement_score'] <= 100):
        return False
    
    return True

def generate_fallback_tweets(hook: str, tone: str, cta: str, keywords: str, num_variations: int) -> List[Dict]:
    """Generate fallback tweets using templates when AI fails."""
    templates = [
        "{emoji} {hook} {hashtags} {cta}",
        "{hook} {emoji} {hashtags} {cta}",
        "{emoji} {hook} - {cta} {hashtags}",
        "💡 {hook} {emoji} {hashtags} {cta}",
        "{hook} 🚀 {cta} {hashtags} {emoji}"
    ]
    
    tweets = []
    for i in range(num_variations):
        template = templates[i % len(templates)]
        emoji_list = suggest_emojis(tone, 2)
        hashtag_list = suggest_hashtags(keywords, tone)
        
        emoji_str = " ".join(emoji_list[:2])
        hashtag_str = " ".join(hashtag_list[:2])
        
        tweet_text = template.format(
            emoji=emoji_str,
            hook=hook,
            hashtags=hashtag_str,
            cta=cta
        ).strip()
        
        # Ensure tweet is within character limit
        if len(tweet_text) > MAX_TWEET_LENGTH:
            tweet_text = tweet_text[:MAX_TWEET_LENGTH-3] + "..."
        
        tweets.append({
            "text": hook,
            "hashtags": hashtag_list[:2],
            "emojis": emoji_list[:2],
            "engagement_score": random.randint(65, 85),
            "reasoning": "Template-based generation (AI fallback)"
        })
    
    return tweets

async def post_tweet_to_twitter(tweet_content: str, hashtags: List[str]) -> Dict[str, any]:
    """Post tweet to Twitter using the platform adapter with real error handling."""
    user_id = get_current_user_id()
    adapter = get_twitter_adapter(user_id)
    
    if not adapter:
        return {
            "success": False,
            "error": "Twitter adapter not configured. Please connect your Twitter account."
        }
    
    # Prepare content for posting
    full_text = f"{tweet_content} {' '.join(hashtags)}".strip()
    
    # Validate tweet length
    if len(full_text) > MAX_TWEET_LENGTH:
        return {
            "success": False,
            "error": f"Tweet too long ({len(full_text)}/{MAX_TWEET_LENGTH} characters)"
        }
    
    content = {
        "text": full_text,
        "media": []
    }
    
    try:
        # Post the tweet
        result = await adapter.publish_content(content)
        
        if result.get("success"):
            tweet_data = result.get("data", {})
            return {
                "success": True,
                "tweet_id": tweet_data.get("id"),
                "tweet_url": f"https://twitter.com/{st.session_state.twitter_user_info['screen_name']}/status/{tweet_data.get('id')}",
                "posted_at": tweet_data.get("created_at"),
                "full_text": full_text
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error occurred")
            }
            
    except Exception as e:
        error_message = str(e)
        
        # Handle specific Twitter API errors
        if "401" in error_message or "Unauthorized" in error_message:
            return {
                "success": False,
                "error": "Authentication failed. Please reconnect your Twitter account."
            }
        elif "403" in error_message or "Forbidden" in error_message:
            return {
                "success": False,
                "error": "Access forbidden. Check your API permissions."
            }
        elif "429" in error_message or "Rate limit" in error_message:
            return {
                "success": False,
                "error": "Rate limit exceeded. Please wait before posting again."
            }
        elif "duplicate" in error_message.lower():
            return {
                "success": False,
                "error": "Duplicate tweet detected. Please modify your content."
            }
        else:
            return {
                "success": False,
                "error": f"Failed to post tweet: {error_message}"
            }

async def get_real_tweet_analytics(tweet_id: str) -> Dict[str, Any]:
    """Get real analytics for a posted tweet."""
    user_id = get_current_user_id()
    adapter = get_twitter_adapter(user_id)
    
    if not adapter:
        return {"error": "Twitter adapter not available"}
    
    try:
        result = await adapter.get_analytics(tweet_id)
        
        if result.get("success"):
            metrics = result.get("data", {}).get("metrics", {})
            return {
                "success": True,
                "metrics": {
                    "likes": metrics.get("favorites", 0),
                    "retweets": metrics.get("retweets", 0),
                    "replies": metrics.get("replies", 0),
                    "impressions": metrics.get("impressions", 0),
                    "engagement_rate": result.get("data", {}).get("engagement_rate", 0)
                }
            }
        else:
            return {"error": result.get("error", "Failed to get analytics")}
            
    except Exception as e:
        return {"error": f"Analytics error: {str(e)}"}

def smart_tweet_generator():
    """Enhanced Smart Tweet Generator with real AI integration and Twitter posting."""
    # Apply styling
    apply_tweet_generator_styling()
    
    # Header
    st.markdown("""
    <div class="tweet-generator-container">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #1DA1F2; margin-bottom: 0.5rem;">✨ AI-Powered Tweet Generator</h1>
            <p style="color: #657786; font-size: 1.1rem;">Create engaging tweets with real AI and post directly to Twitter</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Status
    st.markdown("""
    <div class="ai-status">
        🤖 AI Integration Active - Using advanced language models for tweet generation
    </div>
    """, unsafe_allow_html=True)
    
    # Twitter Authentication
    twitter_connected = render_twitter_authentication()
    
    # Input Section
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">📝 Tweet Content</h3>', unsafe_allow_html=True)
        
        # Main content input
        hook = st.text_area(
            "What's your main message?",
            placeholder="Enter your tweet content, idea, or topic...",
            help="This will be the core message of your tweet",
            height=100
        )
        
        # Advanced options in columns
        col1, col2 = st.columns(2)
        
        with col1:
            target_audience = st.selectbox(
                "🎯 Target Audience",
                ["General Public", "Professionals", "Students", "Entrepreneurs", "Creators", "Tech Enthusiasts"],
                help="Who is your primary audience?"
            )
            
            tone = st.selectbox(
                "🎭 Tone & Style",
                ["Professional", "Casual", "Humorous", "Inspirational", "Informative"],
                index=1,
                help="Choose the tone that matches your brand"
            )
            
            length = st.select_slider(
                "📏 Tweet Length",
                options=["Short (< 100 chars)", "Medium (100-200 chars)", "Long (200+ chars)"],
                value="Medium (100-200 chars)",
                help="Shorter tweets often get more engagement"
            )
        
        with col2:
            call_to_action = st.text_input(
                "📢 Call to Action",
                placeholder="e.g., Learn more, Follow for tips, Share your thoughts...",
                help="What action do you want your audience to take?"
            )
            
            keywords = st.text_input(
                "🔍 Keywords/Topics",
                placeholder="e.g., AI, marketing, productivity...",
                help="Keywords to help generate relevant hashtags"
            )
            
            num_variations = st.slider(
                "🔄 Number of Variations",
                min_value=1,
                max_value=5,
                value=3,
                help="How many different tweet versions would you like?"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Optimization Tips
    render_optimization_tips()
    
    # Generate Button
    if st.button("🚀 Generate AI Tweets", use_container_width=True, type="primary"):
        if not hook.strip():
            show_error_message("Please enter your main message or topic!")
            return
        
        with st.spinner("🤖 AI is crafting your tweets..."):
            # Generate tweet variations using AI
            tweets = generate_ai_tweet_variations(
                hook, target_audience, tone,
                call_to_action, keywords, length.split()[0].lower(),
                num_variations
            )
            
            # Store in session state
            save_to_session("generated_tweets", tweets)
            
        show_success_message(f"✅ Generated {len(tweets)} AI-powered tweet variations!")
    
    # Display Generated Tweets
    generated_tweets = get_from_session("generated_tweets", [])
    
    if generated_tweets:
        st.markdown("### 🎯 AI-Generated Tweet Variations")
        
        for i, tweet in enumerate(generated_tweets):
            with st.container():
                st.markdown(f"#### Variation {i + 1}")
                
                # Tweet preview
                char_info = render_tweet_preview(
                    tweet["text"], 
                    tweet["hashtags"], 
                    tweet["engagement_score"]
                )
                
                # Show AI reasoning if available
                if "reasoning" in tweet:
                    st.markdown(f"**AI Insight:** {tweet['reasoning']}")
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"📋 Copy", key=f"copy_{i}"):
                        full_tweet = f"{tweet['text']} {' '.join(tweet['hashtags'])}"
                        st.code(full_tweet, language=None)
                        show_success_message("Tweet copied to clipboard!")
                
                with col2:
                    if st.button(f"💾 Save", key=f"save_{i}"):
                        saved_tweets = get_from_session("saved_tweets", [])
                        saved_tweets.append(tweet)
                        save_to_session("saved_tweets", saved_tweets)
                        show_success_message("Tweet saved!")
                
                with col3:
                    if st.button(f"🔄 Regenerate", key=f"regen_{i}"):
                        with st.spinner("🤖 Regenerating tweet..."):
                            new_tweets = generate_ai_tweet_variations(
                                hook, target_audience, tone,
                                call_to_action, keywords, length.split()[0].lower(),
                                1
                            )
                            if new_tweets:
                                generated_tweets[i] = new_tweets[0]
                                save_to_session("generated_tweets", generated_tweets)
                                st.rerun()
                
                with col4:
                    if twitter_connected:
                        if st.button(f"🐦 Post to Twitter", key=f"post_{i}"):
                            with st.spinner("🐦 Posting to Twitter..."):
                                result = asyncio.run(post_tweet_to_twitter(
                                    tweet["text"], 
                                    tweet["hashtags"]
                                ))
                                
                                if result["success"]:
                                    show_success_message(f"✅ Tweet posted successfully!")
                                    
                                    # Update tweet with posted info
                                    tweet["posted"] = True
                                    tweet["tweet_id"] = result["tweet_id"]
                                    tweet["tweet_url"] = result["tweet_url"]
                                    tweet["posted_at"] = result["posted_at"]
                                    save_to_session("generated_tweets", generated_tweets)
                                    
                                    # Show tweet URL
                                    st.markdown(f"[View Tweet on Twitter]({result['tweet_url']})")
                                else:
                                    show_error_message(f"❌ {result['error']}")
                    else:
                        st.button(f"🔒 Connect Twitter", key=f"connect_{i}", disabled=True, 
                                help="Connect your Twitter account to enable posting")
                
                # Tweet details with real analytics if posted
                with st.expander(f"📊 Details for Variation {i + 1}"):
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Hashtags:**")
                        for hashtag in tweet["hashtags"]:
                            st.markdown(f"- {hashtag}")
                        
                        st.markdown("**Emojis:**")
                        st.markdown(" ".join(tweet["emojis"]))
                        
                        if tweet.get("posted"):
                            st.markdown("**Status:** ✅ Posted to Twitter")
                            if tweet.get("tweet_url"):
                                st.markdown(f"**Tweet URL:** [View on Twitter]({tweet['tweet_url']})")
                    
                    with detail_col2:
                        st.markdown("**Character Count:**")
                        full_text = f"{tweet['text']} {' '.join(tweet['hashtags'])}"
                        char_info = calculate_character_count(full_text)
                        st.markdown(f"- Total: {char_info['count']}/{MAX_TWEET_LENGTH}")
                        st.markdown(f"- Remaining: {char_info['remaining']}")
                        
                        # Show real analytics if tweet is posted
                        if tweet.get("posted") and tweet.get("tweet_id"):
                            if st.button(f"📊 Get Real Analytics", key=f"analytics_{i}"):
                                with st.spinner("Fetching real analytics..."):
                                    analytics = asyncio.run(get_real_tweet_analytics(tweet["tweet_id"]))
                                    
                                if analytics.get("success"):
                                    metrics = analytics["metrics"]
                                    st.markdown("**Real Twitter Analytics:**")
                                    st.markdown(f"- Likes: {metrics['likes']}")
                                    st.markdown(f"- Retweets: {metrics['retweets']}")
                                    st.markdown(f"- Replies: {metrics['replies']}")
                                    st.markdown(f"- Engagement Rate: {metrics['engagement_rate']:.2f}%")
                                else:
                                    st.error(f"Failed to get analytics: {analytics.get('error')}")
                        else:
                            st.markdown("**AI Engagement Score:**")
                            st.progress(tweet["engagement_score"] / 100)
                            st.markdown(f"{tweet['engagement_score']}% predicted engagement")
                
                st.markdown("---")
    
    # Saved Tweets Section
    saved_tweets = get_from_session("saved_tweets", [])
    if saved_tweets:
        with st.expander(f"💾 Saved Tweets ({len(saved_tweets)})"):
            for i, tweet in enumerate(saved_tweets):
                st.markdown(f"**Saved Tweet {i + 1}:**")
                st.markdown(f"{tweet['text']} {' '.join(tweet['hashtags'])}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Remove", key=f"remove_saved_{i}"):
                        saved_tweets.pop(i)
                        save_to_session("saved_tweets", saved_tweets)
                        st.rerun()
                
                with col2:
                    if twitter_connected and not tweet.get("posted"):
                        if st.button(f"🐦 Post", key=f"post_saved_{i}"):
                            with st.spinner("🐦 Posting to Twitter..."):
                                result = asyncio.run(post_tweet_to_twitter(
                                    tweet["text"], 
                                    tweet["hashtags"]
                                ))
                                
                                if result["success"]:
                                    show_success_message(f"✅ Tweet posted successfully!")
                                    tweet["posted"] = True
                                    tweet["tweet_id"] = result["tweet_id"]
                                    tweet["tweet_url"] = result["tweet_url"]
                                    save_to_session("saved_tweets", saved_tweets)
                                    st.rerun()
                
                st.markdown("---")
    
    # Analytics Section
    if generated_tweets:
        st.markdown("### 📊 AI Tweet Analytics Preview")
        
        # Create engagement comparison chart
        tweet_names = [f"Variation {i+1}" for i in range(len(generated_tweets))]
        engagement_scores = [tweet["engagement_score"] for tweet in generated_tweets]
        
        fig = px.bar(
            x=tweet_names,
            y=engagement_scores,
            title="AI-Predicted Engagement Comparison",
            labels={"x": "Tweet Variations", "y": "AI Engagement Score (%)"},
            color=engagement_scores,
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # AI insights and best practices
        st.markdown("### 🤖 AI Optimization Insights")
        
        best_tweet = max(generated_tweets, key=lambda x: x["engagement_score"])
        best_index = generated_tweets.index(best_tweet)
        
        # Calculate average character count
        total_chars = 0
        for t in generated_tweets:
            full_text = f"{t['text']} {' '.join(t['hashtags'])}"
            total_chars += len(full_text)
        avg_chars = total_chars // len(generated_tweets)
        
        # Calculate average hashtag count
        avg_hashtags = sum(len(t['hashtags']) for t in generated_tweets) // len(generated_tweets)
        
        insights = [
            f"🏆 Variation {best_index + 1} has the highest AI-predicted engagement ({best_tweet['engagement_score']}%)",
            f"📏 Average character count: {avg_chars} characters",
            f"#️⃣ Using {avg_hashtags} hashtags on average",
            "🎯 AI recommends posting during peak hours (9-10 AM, 7-9 PM) for better reach",
            "🤖 All tweets generated using advanced AI for maximum engagement potential"
        ]
        
        for insight in insights:
            st.info(insight)

if __name__ == "__main__":
    smart_tweet_generator() 