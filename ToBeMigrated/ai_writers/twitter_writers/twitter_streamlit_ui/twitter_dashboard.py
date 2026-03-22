"""
Enhanced Twitter Dashboard with real authentication and posting capabilities.
"""

import streamlit as st
import asyncio
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List, Optional

# Import our enhanced components
from .components.navigation import TwitterNavigation, create_main_navigation
from .components.cards import TwitterCard, create_analytics_card, create_tweet_card
from .components.forms import TweetForm, TwitterConfigForm
from ..tweet_generator.smart_tweet_generator import (
    smart_tweet_generator, 
    post_tweet_to_twitter,
    get_real_tweet_analytics,
    render_twitter_authentication
)
from ....integrations.twitter_auth_bridge import (
    TwitterAuthBridge,
    save_twitter_credentials,
    load_twitter_credentials,
    is_twitter_authenticated,
    setup_twitter_session,
    clear_twitter_session
)

# Initialize authentication bridge
auth_bridge = TwitterAuthBridge()

def initialize_dashboard():
    """Initialize the Twitter dashboard with proper styling and state management."""
    
    # Apply custom CSS
    st.markdown("""
    <style>
    .main-dashboard {
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .dashboard-header {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .dashboard-subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .status-connected {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-disconnected {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    @media (max-width: 768px) {
        .dashboard-grid {
            grid-template-columns: 1fr;
        }
    }
    
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'twitter_dashboard_initialized' not in st.session_state:
        st.session_state.twitter_dashboard_initialized = True
        st.session_state.current_page = 'dashboard'
        st.session_state.tweet_drafts = []
        st.session_state.posted_tweets = []
        st.session_state.analytics_data = {}

def render_dashboard_header():
    """Render the main dashboard header with connection status."""
    
    st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 class="dashboard-title">🐦 Twitter AI Dashboard</h1>', unsafe_allow_html=True)
        st.markdown('<p class="dashboard-subtitle">AI-Powered Tweet Generation & Analytics</p>', unsafe_allow_html=True)
        
        # Connection status
        is_connected = is_twitter_authenticated()
        
        if is_connected:
            user_info = st.session_state.get('twitter_user', {})
            username = user_info.get('screen_name', 'Unknown')
            st.markdown(f'''
            <div class="status-indicator status-connected">
                ✅ Connected as @{username}
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="status-indicator status-disconnected">
                ❌ Not Connected to Twitter
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_quick_actions():
    """Render quick action buttons."""
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Generate Tweet", key="quick_generate", help="Create AI-powered tweets"):
            st.session_state.current_page = 'generate'
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", key="quick_analytics", help="View tweet performance"):
            st.session_state.current_page = 'analytics'
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", key="quick_settings", help="Configure Twitter connection"):
            st.session_state.current_page = 'settings'
            st.rerun()
    
    with col4:
        if st.button("📋 Drafts", key="quick_drafts", help="Manage tweet drafts"):
            st.session_state.current_page = 'drafts'
            st.rerun()

def render_dashboard_overview():
    """Render the main dashboard overview with metrics."""
    
    if not is_twitter_authenticated():
        st.warning("⚠️ Please connect your Twitter account to view dashboard metrics.")
        if st.button("Connect Twitter Account", type="primary"):
            st.session_state.current_page = 'settings'
            st.rerun()
        return
    
    # Get user metrics
    user_info = st.session_state.get('twitter_user', {})
    
    # Display metrics
    st.markdown("### 📈 Account Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{user_info.get('followers_count', 0):,}</div>
            <div class="metric-label">Followers</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{user_info.get('friends_count', 0):,}</div>
            <div class="metric-label">Following</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        posted_count = len(st.session_state.get('posted_tweets', []))
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{posted_count}</div>
            <div class="metric-label">Posted Today</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        draft_count = len(st.session_state.get('tweet_drafts', []))
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{draft_count}</div>
            <div class="metric-label">Drafts</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("### 📝 Recent Activity")
    
    recent_tweets = st.session_state.get('posted_tweets', [])[-5:]  # Last 5 tweets
    
    if recent_tweets:
        for tweet in reversed(recent_tweets):
            with st.expander(f"Tweet: {tweet.get('text', '')[:50]}..."):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Text:** {tweet.get('text', '')}")
                    st.write(f"**Posted:** {tweet.get('created_at', '')}")
                    
                    if tweet.get('metrics'):
                        metrics = tweet['metrics']
                        st.write(f"**Engagement:** {metrics.get('favorite_count', 0)} likes, "
                               f"{metrics.get('retweet_count', 0)} retweets")
                
                with col2:
                    if st.button(f"View Analytics", key=f"analytics_{tweet.get('id')}"):
                        st.session_state.selected_tweet_id = tweet.get('id')
                        st.session_state.current_page = 'analytics'
                        st.rerun()
    else:
        st.info("No recent tweets found. Start by generating and posting some content!")

def render_settings_page():
    """Render the settings page for Twitter configuration."""
    
    st.markdown("### ⚙️ Twitter Configuration")
    
    # Twitter Authentication Section
    with st.expander("🔐 Twitter API Configuration", expanded=not is_twitter_authenticated()):
        render_twitter_authentication()
    
    # Account Information
    if is_twitter_authenticated():
        st.markdown("### 👤 Account Information")
        
        user_info = st.session_state.get('twitter_user', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Username:** @{user_info.get('screen_name', 'N/A')}")
            st.write(f"**Display Name:** {user_info.get('name', 'N/A')}")
            st.write(f"**Followers:** {user_info.get('followers_count', 0):,}")
        
        with col2:
            st.write(f"**Following:** {user_info.get('friends_count', 0):,}")
            st.write(f"**Tweets:** {user_info.get('statuses_count', 0):,}")
            st.write(f"**Account Created:** {user_info.get('created_at', 'N/A')}")
        
        # Disconnect option
        st.markdown("---")
        if st.button("🔓 Disconnect Twitter Account", type="secondary"):
            clear_twitter_session()
            st.success("Twitter account disconnected successfully!")
            st.rerun()

def render_analytics_page():
    """Render the analytics page with real Twitter metrics."""
    
    st.markdown("### 📊 Tweet Analytics")
    
    if not is_twitter_authenticated():
        st.warning("Please connect your Twitter account to view analytics.")
        return
    
    # Tweet selection
    posted_tweets = st.session_state.get('posted_tweets', [])
    
    if not posted_tweets:
        st.info("No tweets found. Generate and post some tweets to see analytics!")
        return
    
    # Select tweet for analysis
    tweet_options = {
        f"{tweet.get('text', '')[:50]}... ({tweet.get('created_at', '')})": tweet.get('id')
        for tweet in posted_tweets
    }
    
    selected_tweet_text = st.selectbox(
        "Select a tweet to analyze:",
        options=list(tweet_options.keys())
    )
    
    if selected_tweet_text:
        tweet_id = tweet_options[selected_tweet_text]
        
        # Get analytics
        with st.spinner("Loading analytics..."):
            analytics_result = asyncio.run(get_real_tweet_analytics(tweet_id))
        
        if analytics_result.get('success'):
            analytics_data = analytics_result['data']
            
            # Display metrics
            st.markdown("#### 📈 Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            metrics = analytics_data.get('metrics', {})
            
            with col1:
                st.metric("Likes", metrics.get('likes', 0))
            
            with col2:
                st.metric("Retweets", metrics.get('retweets', 0))
            
            with col3:
                st.metric("Replies", metrics.get('replies', 0))
            
            with col4:
                engagement = analytics_data.get('engagement', {})
                st.metric("Engagement Rate", f"{engagement.get('engagement_rate', 0):.2f}%")
            
            # Detailed analytics
            st.markdown("#### 🔍 Detailed Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Engagement Breakdown:**")
                total_engagement = metrics.get('total_engagement', 0)
                st.write(f"• Total Engagement: {total_engagement}")
                st.write(f"• Likes Rate: {engagement.get('likes_rate', 0):.2f}%")
                st.write(f"• Retweets Rate: {engagement.get('retweets_rate', 0):.2f}%")
            
            with col2:
                st.markdown("**Content Analysis:**")
                content_analysis = analytics_data.get('content_analysis', {})
                st.write(f"• Character Count: {content_analysis.get('character_count', 0)}")
                st.write(f"• Hashtags: {content_analysis.get('hashtag_count', 0)}")
                st.write(f"• Mentions: {content_analysis.get('mention_count', 0)}")
            
            # Timing analysis
            timing = analytics_data.get('timing', {})
            if timing:
                st.markdown("#### ⏰ Timing Analysis")
                st.write(f"• Posted: {timing.get('posted_at', 'N/A')}")
                st.write(f"• Age: {timing.get('age_hours', 0):.1f} hours")
                st.write(f"• Peak Period: {timing.get('peak_engagement_period', 'N/A')}")
                st.write(f"• Engagement Velocity: {timing.get('engagement_velocity', 0):.2f} per hour")
        
        else:
            st.error(f"Failed to load analytics: {analytics_result.get('error', 'Unknown error')}")

def render_drafts_page():
    """Render the drafts management page."""
    
    st.markdown("### 📋 Tweet Drafts")
    
    drafts = st.session_state.get('tweet_drafts', [])
    
    if not drafts:
        st.info("No drafts found. Create some tweets in the generator to save as drafts!")
        return
    
    for i, draft in enumerate(drafts):
        with st.expander(f"Draft {i+1}: {draft.get('text', '')[:50]}..."):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Text:** {draft.get('text', '')}")
                st.write(f"**Created:** {draft.get('created_at', '')}")
                if draft.get('hashtags'):
                    st.write(f"**Hashtags:** {', '.join(draft['hashtags'])}")
            
            with col2:
                if st.button(f"Post Now", key=f"post_draft_{i}"):
                    if is_twitter_authenticated():
                        with st.spinner("Posting tweet..."):
                            result = asyncio.run(post_tweet_to_twitter(draft))
                        
                        if result.get('success'):
                            st.success("Tweet posted successfully!")
                            # Move from drafts to posted
                            st.session_state.posted_tweets.append(result['data'])
                            st.session_state.tweet_drafts.pop(i)
                            st.rerun()
                        else:
                            st.error(f"Failed to post: {result.get('error')}")
                    else:
                        st.error("Please connect your Twitter account first!")
                
                if st.button(f"Delete", key=f"delete_draft_{i}"):
                    st.session_state.tweet_drafts.pop(i)
                    st.rerun()

def main_twitter_dashboard():
    """Main Twitter dashboard function."""
    
    # Initialize dashboard
    initialize_dashboard()
    
    # Create navigation
    nav = TwitterNavigation()
    current_page = nav.render_main_navigation()
    
    # Update session state if page changed
    if current_page != st.session_state.get('current_page'):
        st.session_state.current_page = current_page
    
    # Render dashboard header
    render_dashboard_header()
    
    # Route to appropriate page
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == 'dashboard':
        render_quick_actions()
        render_dashboard_overview()
    
    elif page == 'generate':
        st.markdown("### 🤖 AI Tweet Generator")
        smart_tweet_generator()
    
    elif page == 'analytics':
        render_analytics_page()
    
    elif page == 'settings':
        render_settings_page()
    
    elif page == 'drafts':
        render_drafts_page()
    
    else:
        # Default to dashboard
        render_quick_actions()
        render_dashboard_overview()

if __name__ == "__main__":
    main_twitter_dashboard() 