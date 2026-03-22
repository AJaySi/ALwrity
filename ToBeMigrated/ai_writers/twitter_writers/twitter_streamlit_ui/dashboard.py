"""
Main dashboard for Twitter UI.
Combines all UI components into a cohesive interface.
"""

import streamlit as st
from typing import Dict, Any, Optional
from .components.cards import FeatureCard, TweetCard
from .components.forms import TweetForm, SettingsForm
from .components.navigation import Sidebar, Header, Tabs, Breadcrumbs
from .styles.theme import Theme
import os

class TwitterDashboard:
    """Main dashboard class for Twitter UI."""
    
    def __init__(self):
        """Initialize the Twitter dashboard."""
        self.setup_theme()
        self.setup_navigation()
        self.setup_state()
    
    def get_logo_path(self) -> str:
        """Get the best available logo path with fallbacks."""
        # List of potential logo paths in order of preference
        logo_paths = [
            "lib/workspace/alwrity_logo.png",
            "lib/workspace/AskAlwrity-min.ico",
            "lib/workspace/alwrity_ai_writer.png"
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                return path
        
        # If no logo files are found, return None
        return None
    
    def setup_theme(self) -> None:
        """Setup theme and styling."""
        Theme.apply()
    
    def setup_navigation(self) -> None:
        """Setup navigation components."""
        # Sidebar
        self.sidebar = Sidebar(
            title="Twitter Tools",
            logo=self.get_logo_path()
        )
        
        # Add menu items
        self.sidebar.add_menu_item("Dashboard", "📊", "dashboard")
        self.sidebar.add_menu_item("Tweet Generator", "✍️", "tweet_generator")
        self.sidebar.add_menu_item("Analytics", "📈", "analytics")
        self.sidebar.add_menu_item("Settings", "⚙️", "settings")
        
        # Header
        self.header = Header(
            title="Twitter Dashboard",
            subtitle="Create and manage your Twitter content"
        )
        
        # Add header actions
        self.header.add_action(
            "New Tweet",
            "✏️",
            self.create_new_tweet,
            "Create a new tweet"
        )
        self.header.add_action(
            "Refresh",
            "🔄",
            self.refresh_dashboard,
            "Refresh dashboard data"
        )
        
        # Tabs
        self.tabs = Tabs()
        
        # Add tabs
        self.tabs.add_tab("Overview", "📊", self.render_overview)
        self.tabs.add_tab("Recent Tweets", "🐦", self.render_recent_tweets)
        self.tabs.add_tab("Analytics", "📈", self.render_analytics)
        
        # Breadcrumbs
        self.breadcrumbs = Breadcrumbs()
    
    def setup_state(self) -> None:
        """Initialize session state variables."""
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "dashboard"
        if "current_tab" not in st.session_state:
            st.session_state["current_tab"] = "Overview"
        if "tweets" not in st.session_state:
            st.session_state["tweets"] = []
    
    def create_new_tweet(self) -> None:
        """Handle new tweet creation."""
        st.session_state["current_page"] = "tweet_generator"
    
    def refresh_dashboard(self) -> None:
        """Refresh dashboard data."""
        st.rerun()
    
    def render_overview(self) -> None:
        """Render the overview tab content."""
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            FeatureCard(
                title="Tweet Generator",
                description="Create engaging tweets with AI assistance",
                icon="✍️",
                features=[
                    {
                        "name": "AI-Powered",
                        "description": "Generate tweets using advanced AI"
                    },
                    {
                        "name": "Customizable",
                        "description": "Adjust tone, length, and style"
                    }
                ],
                on_click=self.create_new_tweet
            ).render()
        
        with col2:
            FeatureCard(
                title="Analytics",
                description="Track your tweet performance",
                icon="📈",
                features=[
                    {
                        "name": "Engagement",
                        "description": "Monitor likes, retweets, and replies"
                    },
                    {
                        "name": "Growth",
                        "description": "Track follower growth over time"
                    }
                ]
            ).render()
        
        with col3:
            FeatureCard(
                title="Settings",
                description="Customize your experience",
                icon="⚙️",
                features=[
                    {
                        "name": "Preferences",
                        "description": "Set your default options"
                    },
                    {
                        "name": "API",
                        "description": "Configure Twitter API settings"
                    }
                ]
            ).render()
    
    def render_recent_tweets(self) -> None:
        """Render the recent tweets tab content."""
        # Tweet form
        tweet_form = TweetForm(
            on_submit=self.handle_tweet_submit
        )
        tweet_form.render()
        
        # Recent tweets
        st.markdown("### Recent Tweets")
        
        for tweet in st.session_state["tweets"]:
            TweetCard(
                content=tweet["content"],
                engagement_score=tweet["engagement_score"],
                hashtags=tweet["hashtags"],
                emojis=tweet["emojis"],
                metrics=tweet["metrics"],
                on_copy=lambda: self.copy_tweet(tweet),
                on_save=lambda: self.save_tweet(tweet)
            ).render()
    
    def render_analytics(self) -> None:
        """Render the analytics tab content."""
        # Analytics content
        st.markdown("### Tweet Analytics")
        
        # Placeholder for analytics charts
        st.info("Analytics features coming soon!")
    
    def handle_tweet_submit(self) -> None:
        """Handle tweet form submission."""
        # Get form data
        content = st.session_state["tweet_content"]
        tone = st.session_state["tone"]
        length = st.session_state["length"]
        hashtags = st.session_state["hashtags"]
        emojis = st.session_state["emojis"]
        engagement_boost = st.session_state["engagement_boost"]
        
        # Create tweet object
        tweet = {
            "content": content,
            "tone": tone,
            "length": length,
            "hashtags": hashtags,
            "emojis": emojis,
            "engagement_score": engagement_boost,
            "metrics": {
                "Engagement": engagement_boost,
                "Reach": engagement_boost * 0.8,
                "Growth": engagement_boost * 0.6
            }
        }
        
        # Add to tweets list
        st.session_state["tweets"].append(tweet)
        
        # Show success message
        st.success("Tweet created successfully!")
    
    def copy_tweet(self, tweet: Dict[str, Any]) -> None:
        """Copy tweet to clipboard."""
        st.write("Tweet copied to clipboard!")
    
    def save_tweet(self, tweet: Dict[str, Any]) -> None:
        """Save tweet for later."""
        st.write("Tweet saved!")
    
    def render(self) -> None:
        """Render the complete dashboard."""
        # Render navigation
        self.sidebar.render()
        self.header.render()
        self.breadcrumbs.render()
        
        # Render content based on current page
        if st.session_state["current_page"] == "dashboard":
            self.tabs.render()
        elif st.session_state["current_page"] == "tweet_generator":
            self.render_recent_tweets()
        elif st.session_state["current_page"] == "analytics":
            self.render_analytics()
        elif st.session_state["current_page"] == "settings":
            settings_form = SettingsForm(
                on_submit=self.handle_settings_submit
            )
            settings_form.render()
    
    def handle_settings_submit(self) -> None:
        """Handle settings form submission."""
        # Get form data
        api_key = st.session_state["api_key"]
        theme = st.session_state["theme"]
        notifications = st.session_state["notifications"]
        auto_save = st.session_state["auto_save"]
        language = st.session_state["language"]
        
        # Save settings
        st.session_state["settings"] = {
            "api_key": api_key,
            "theme": theme,
            "notifications": notifications,
            "auto_save": auto_save,
            "language": language
        }
        
        # Show success message
        st.success("Settings saved successfully!")

def main():
    """Main entry point for the dashboard."""
    dashboard = TwitterDashboard()
    dashboard.render()

if __name__ == "__main__":
    main() 