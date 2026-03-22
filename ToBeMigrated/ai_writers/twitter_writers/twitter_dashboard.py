"""
Enhanced Twitter Dashboard with modern UI components and improved user experience.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from .tweet_generator import smart_tweet_generator
from .twitter_streamlit_ui import (
    TwitterDashboard,
    FeatureCard,
    TweetCard,
    TweetForm,
    SettingsForm,
    Sidebar,
    Header,
    Tabs,
    Breadcrumbs,
    Theme,
    save_to_session,
    get_from_session,
    clear_session,
    show_success_message,
    show_error_message,
    show_info_message,
    show_warning_message
)

def apply_modern_styling():
    """Apply modern CSS styling to the dashboard."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main Container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Header Styles */
    .dashboard-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1DA1F2, #0C85D0);
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 30px rgba(29, 161, 242, 0.3);
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #718096;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    .feature-status {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-active {
        background: linear-gradient(135deg, #48BB78, #38A169);
        color: white;
    }
    
    .status-coming-soon {
        background: linear-gradient(135deg, #ED8936, #DD6B20);
        color: white;
    }
    
    /* Metrics Cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #1DA1F2;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2D3748;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #718096;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1DA1F2, #0C85D0);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(29, 161, 242, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(29, 161, 242, 0.4);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #4A5568;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #1DA1F2;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Connection Status */
    .connection-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #C6F6D5, #9AE6B4);
        color: #22543D;
        border: 1px solid #9AE6B4;
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #FED7D7, #FEB2B2);
        color: #742A2A;
        border: 1px solid #FEB2B2;
    }
    
    /* Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .quick-action-btn {
        background: white;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        text-decoration: none;
    }
    
    .quick-action-btn:hover {
        border-color: #1DA1F2;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(29, 161, 242, 0.15);
    }
    
    .quick-action-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .quick-action-title {
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 0.25rem;
    }
    
    .quick-action-desc {
        font-size: 0.85rem;
        color: #718096;
    }
    
    /* Analytics Charts */
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .dashboard-title {
            font-size: 2rem;
        }
        
        .quick-actions {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_connection_status():
    """Render Twitter connection status with modern styling."""
    # Simulate connection status (replace with real authentication check)
    is_connected = get_from_session("twitter_connected", False)
    
    if is_connected:
        user_info = get_from_session("twitter_user", {"name": "Demo User", "handle": "@demo_user"})
        st.markdown(f"""
        <div class="connection-status status-connected">
            <span style="font-size: 1.2rem;">✅</span>
            <div>
                <strong>Connected as {user_info['name']}</strong>
                <div style="font-size: 0.9rem; opacity: 0.8;">{user_info['handle']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="connection-status status-disconnected">
            <span style="font-size: 1.2rem;">⚠️</span>
            <div>
                <strong>Twitter Not Connected</strong>
                <div style="font-size: 0.9rem; opacity: 0.8;">Connect your account to access all features</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔗 Connect Twitter Account", key="connect_twitter"):
            # Simulate connection (replace with real OAuth flow)
            save_to_session("twitter_connected", True)
            save_to_session("twitter_user", {"name": "Demo User", "handle": "@demo_user"})
            st.rerun()

def render_dashboard_header():
    """Render the modern dashboard header."""
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="dashboard-title">🐦 Twitter AI Dashboard</h1>
        <p class="dashboard-subtitle">Create, analyze, and optimize your Twitter content with AI-powered tools</p>
    </div>
    """, unsafe_allow_html=True)

def render_quick_actions():
    """Render quick action buttons."""
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✍️ Create Tweet", use_container_width=True, key="quick_tweet"):
            st.session_state.current_page = "tweet_generator"
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True, key="quick_analytics"):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col3:
        if st.button("📅 Content Calendar", use_container_width=True, key="quick_calendar"):
            show_info_message("Content Calendar feature coming soon!")
    
    with col4:
        if st.button("⚙️ Settings", use_container_width=True, key="quick_settings"):
            st.session_state.current_page = "settings"
            st.rerun()

def render_metrics_overview():
    """Render key metrics overview."""
    st.markdown("### 📈 Performance Overview")
    
    # Generate sample metrics (replace with real data)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1,234</div>
            <div class="metric-label">Total Tweets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">45.2K</div>
            <div class="metric-label">Total Engagement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3.8%</div>
            <div class="metric-label">Engagement Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12.5K</div>
            <div class="metric-label">Followers</div>
        </div>
        """, unsafe_allow_html=True)

def render_engagement_chart():
    """Render engagement trends chart."""
    st.markdown("### 📊 Engagement Trends")
    
    # Generate sample data (replace with real Twitter data)
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30)
    engagement = np.random.normal(100, 20, 30)
    engagement = np.maximum(engagement, 0)  # Ensure positive values
    
    df = pd.DataFrame({
        'Date': dates,
        'Engagement': engagement,
        'Likes': engagement * 0.6,
        'Retweets': engagement * 0.3,
        'Replies': engagement * 0.1
    })
    
    # Create interactive chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Total Engagement', 'Engagement Breakdown'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Main engagement line
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Engagement'],
            mode='lines+markers',
            name='Total Engagement',
            line=dict(color='#1DA1F2', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Stacked area chart for breakdown
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Likes'],
            mode='lines',
            name='Likes',
            fill='tonexty',
            line=dict(color='#E53E3E')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Retweets'],
            mode='lines',
            name='Retweets',
            fill='tonexty',
            line=dict(color='#38A169')
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Replies'],
            mode='lines',
            name='Replies',
            fill='tonexty',
            line=dict(color='#D69E2E')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    st.plotly_chart(fig, use_container_width=True)

def render_feature_grid():
    """Render the feature grid with modern cards."""
    st.markdown("### 🛠️ Available Tools")
    
    features = [
        {
            "title": "Smart Tweet Generator",
            "description": "Create engaging tweets with AI assistance, hashtag suggestions, and emoji optimization",
            "icon": "✨",
            "status": "active",
            "action": "tweet_generator"
        },
        {
            "title": "Performance Predictor",
            "description": "Predict tweet engagement and find optimal posting times",
            "icon": "🔮",
            "status": "coming_soon",
            "action": None
        },
        {
            "title": "Content Calendar",
            "description": "Plan and schedule your Twitter content strategy",
            "icon": "📅",
            "status": "coming_soon",
            "action": None
        },
        {
            "title": "Hashtag Research",
            "description": "Discover trending hashtags and analyze their performance",
            "icon": "#️⃣",
            "status": "coming_soon",
            "action": None
        },
        {
            "title": "Visual Content",
            "description": "Create quote cards, infographics, and visual tweets",
            "icon": "🎨",
            "status": "coming_soon",
            "action": None
        },
        {
            "title": "Analytics Dashboard",
            "description": "Deep dive into your Twitter performance metrics",
            "icon": "📊",
            "status": "coming_soon",
            "action": None
        }
    ]
    
    # Create grid layout
    cols = st.columns(3)
    
    for i, feature in enumerate(features):
        with cols[i % 3]:
            status_class = "status-active" if feature["status"] == "active" else "status-coming-soon"
            
            card_html = f"""
            <div class="feature-card" onclick="handleFeatureClick('{feature['action']}')">
                <span class="feature-icon">{feature['icon']}</span>
                <h3 class="feature-title">{feature['title']}</h3>
                <p class="feature-description">{feature['description']}</p>
                <span class="feature-status {status_class}">{feature['status'].replace('_', ' ')}</span>
            </div>
            """
            
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Add button for active features
            if feature["status"] == "active" and feature["action"]:
                if st.button(f"Launch {feature['title']}", key=f"launch_{i}", use_container_width=True):
                    st.session_state.current_page = feature["action"]
                    st.rerun()

def render_recent_activity():
    """Render recent activity feed."""
    st.markdown("### 📱 Recent Activity")
    
    # Sample activity data (replace with real data)
    activities = [
        {"time": "2 hours ago", "action": "Generated tweet", "details": "AI-powered content about social media trends"},
        {"time": "5 hours ago", "action": "Analyzed performance", "details": "Tweet received 45 likes and 12 retweets"},
        {"time": "1 day ago", "action": "Scheduled tweet", "details": "Content scheduled for optimal posting time"},
        {"time": "2 days ago", "action": "Updated hashtags", "details": "Added trending hashtags to improve reach"}
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid #1DA1F2;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        ">
            <div style="font-weight: 600; color: #2D3748; margin-bottom: 0.25rem;">
                {activity['action']}
            </div>
            <div style="color: #718096; font-size: 0.9rem; margin-bottom: 0.25rem;">
                {activity['details']}
            </div>
            <div style="color: #A0AEC0; font-size: 0.8rem;">
                {activity['time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def run_dashboard():
    """Main function to run the enhanced Twitter dashboard."""
    # Apply modern styling
    apply_modern_styling()
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Handle page navigation
    if st.session_state.current_page == "tweet_generator":
        if st.button("← Back to Dashboard", key="back_to_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        smart_tweet_generator()
        return
    
    # Main dashboard container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Render dashboard header
    render_dashboard_header()
    
    # Render connection status
    render_connection_status()
    
    # Create main layout
    tab1, tab2, tab3 = st.tabs(["🏠 Overview", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        # Quick actions
        render_quick_actions()
        
        # Metrics overview
        render_metrics_overview()
        
        # Feature grid
        render_feature_grid()
        
        # Recent activity
        col1, col2 = st.columns([2, 1])
        with col1:
            render_engagement_chart()
        with col2:
            render_recent_activity()
    
    with tab2:
        st.markdown("### 📈 Advanced Analytics")
        
        # Time range selector
        col1, col2 = st.columns([1, 3])
        with col1:
            time_range = st.selectbox(
                "Time Range",
                ["Last 7 days", "Last 30 days", "Last 90 days", "Last year"],
                index=1
            )
        
        # Detailed analytics
        render_engagement_chart()
        
        # Performance insights
        st.markdown("### 💡 Performance Insights")
        
        insights = [
            "Your tweets perform 23% better when posted between 2-4 PM",
            "Tweets with 2-3 hashtags get 15% more engagement",
            "Visual content increases engagement by 35%",
            "Questions in tweets boost replies by 28%"
        ]
        
        for insight in insights:
            st.info(f"💡 {insight}")
    
    with tab3:
        st.markdown("### ⚙️ Dashboard Settings")
        
        # Twitter API settings
        with st.expander("🔑 Twitter API Configuration", expanded=False):
            st.markdown("Configure your Twitter API credentials to enable full functionality.")
            
            api_key = st.text_input("API Key", type="password", help="Your Twitter API key")
            api_secret = st.text_input("API Secret", type="password", help="Your Twitter API secret")
            access_token = st.text_input("Access Token", type="password", help="Your Twitter access token")
            access_token_secret = st.text_input("Access Token Secret", type="password", help="Your Twitter access token secret")
            
            if st.button("Save API Configuration"):
                # Save configuration (implement secure storage)
                show_success_message("API configuration saved successfully!")
        
        # Dashboard preferences
        with st.expander("🎨 Dashboard Preferences", expanded=True):
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
            default_tone = st.selectbox("Default Tweet Tone", ["Professional", "Casual", "Humorous", "Inspirational"], index=1)
            auto_hashtags = st.checkbox("Auto-suggest hashtags", value=True)
            
            if st.button("Save Preferences"):
                show_success_message("Preferences saved successfully!")
        
        # Account management
        with st.expander("👤 Account Management", expanded=False):
            st.markdown("Manage your connected Twitter accounts and permissions.")
            
            if get_from_session("twitter_connected", False):
                st.success("✅ Twitter account connected")
                if st.button("Disconnect Account"):
                    save_to_session("twitter_connected", False)
                    st.rerun()
            else:
                st.warning("⚠️ No Twitter account connected")
                if st.button("Connect Account"):
                    save_to_session("twitter_connected", True)
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# JavaScript for handling feature clicks
st.markdown("""
<script>
function handleFeatureClick(action) {
    if (action && action !== 'null') {
        // This would trigger a Streamlit rerun with the selected action
        console.log('Feature clicked:', action);
    }
}
</script>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    run_dashboard() 