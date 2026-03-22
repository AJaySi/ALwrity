"""
Enhanced UI Cards with modern styling and improved functionality.
"""

import streamlit as st
from typing import Dict, List, Optional, Callable
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def apply_cards_styling():
    """Apply modern CSS styling for cards."""
    st.markdown("""
    <style>
    /* Modern Card Styles */
    .modern-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #1DA1F2, #0C85D0);
    }
    
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #E1E8ED;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(29, 161, 242, 0.15);
        border-color: #1DA1F2;
    }
    
    .feature-card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .feature-icon {
        font-size: 2rem;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #E6F7FF, #F0F9FF);
        border-radius: 12px;
        border: 2px solid #91D5FF;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2D3748;
        margin: 0;
    }
    
    .feature-description {
        color: #657786;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }
    
    .feature-stats {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #E1E8ED;
    }
    
    .stat-item {
        text-align: center;
        flex: 1;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1DA1F2;
        display: block;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #657786;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .tweet-card {
        background: white;
        border: 1px solid #E1E8ED;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        position: relative;
    }
    
    .tweet-card::before {
        content: "🐦";
        position: absolute;
        top: -10px;
        left: 20px;
        background: white;
        padding: 0 10px;
        font-size: 1.2rem;
    }
    
    .tweet-content {
        font-size: 1.1rem;
        line-height: 1.5;
        color: #14171A;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    .tweet-metadata {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #657786;
        font-size: 0.9rem;
        border-top: 1px solid #E1E8ED;
        padding-top: 1rem;
    }
    
    .engagement-badge {
        background: linear-gradient(135deg, #52C41A, #73D13D);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .character-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .char-good { background: #E6F7FF; color: #1890FF; }
    .char-warning { background: #FFF7E6; color: #FA8C16; }
    .char-danger { background: #FFF1F0; color: #F5222D; }
    
    .card-actions {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        flex-wrap: wrap;
    }
    
    .action-button {
        background: #F7F9FA;
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #657786;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .action-button:hover {
        background: #1DA1F2;
        color: white;
        border-color: #1DA1F2;
        transform: translateY(-1px);
    }
    
    .action-button.primary {
        background: #1DA1F2;
        color: white;
        border-color: #1DA1F2;
    }
    
    .action-button.primary:hover {
        background: #0C85D0;
        border-color: #0C85D0;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #E1E8ED;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1DA1F2;
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #657786;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .modern-card, .feature-card, .tweet-card {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .feature-card-header {
            flex-direction: column;
            text-align: center;
        }
        
        .feature-stats {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .card-actions {
            justify-content: center;
        }
        
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    </style>
    """, unsafe_allow_html=True)

class FeatureCard:
    """Modern feature card component."""
    
    def __init__(
        self,
        title: str,
        description: str,
        icon: str = "🔧",
        stats: Optional[Dict[str, any]] = None,
        actions: Optional[List[Dict]] = None,
        on_click: Optional[Callable] = None
    ):
        self.title = title
        self.description = description
        self.icon = icon
        self.stats = stats or {}
        self.actions = actions or []
        self.on_click = on_click
    
    def render(self):
        """Render the feature card."""
        apply_cards_styling()
        
        # Create stats HTML
        stats_html = ""
        if self.stats:
            stats_items = []
            for label, value in self.stats.items():
                stats_items.append(f"""
                    <div class="stat-item">
                        <span class="stat-value">{value}</span>
                        <span class="stat-label">{label}</span>
                    </div>
                """)
            stats_html = f"""
                <div class="feature-stats">
                    {''.join(stats_items)}
                </div>
            """
        
        # Create actions HTML
        actions_html = ""
        if self.actions:
            action_buttons = []
            for action in self.actions:
                button_class = "action-button"
                if action.get("primary", False):
                    button_class += " primary"
                
                action_buttons.append(f"""
                    <button class="{button_class}" onclick="{action.get('onclick', '')}">
                        {action.get('icon', '')} {action.get('label', 'Action')}
                    </button>
                """)
            actions_html = f"""
                <div class="card-actions">
                    {''.join(action_buttons)}
                </div>
            """
        
        # Render the card
        card_html = f"""
        <div class="feature-card" onclick="{self.on_click or ''}">
            <div class="feature-card-header">
                <div class="feature-icon">{self.icon}</div>
                <div>
                    <h3 class="feature-title">{self.title}</h3>
                </div>
            </div>
            <p class="feature-description">{self.description}</p>
            {stats_html}
            {actions_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

class TweetCard:
    """Modern tweet card component."""
    
    def __init__(
        self,
        content: str,
        engagement_score: int = 0,
        hashtags: List[str] = None,
        emojis: List[str] = None,
        metrics: Optional[Dict] = None,
        timestamp: Optional[str] = None,
        on_copy: Optional[Callable] = None,
        on_save: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_post: Optional[Callable] = None
    ):
        self.content = content
        self.engagement_score = engagement_score
        self.hashtags = hashtags or []
        self.emojis = emojis or []
        self.metrics = metrics or {}
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.on_copy = on_copy
        self.on_save = on_save
        self.on_edit = on_edit
        self.on_post = on_post
    
    def _get_character_info(self):
        """Get character count information."""
        full_text = f"{self.content} {' '.join(self.hashtags)}"
        count = len(full_text)
        remaining = 280 - count
        
        if count <= 240:
            status_class = "char-good"
        elif count <= 270:
            status_class = "char-warning"
        else:
            status_class = "char-danger"
        
        return {
            "count": count,
            "remaining": remaining,
            "status_class": status_class
        }
    
    def render(self):
        """Render the tweet card."""
        apply_cards_styling()
        
        char_info = self._get_character_info()
        full_content = f"{self.content} {' '.join(self.hashtags)}"
        
        # Create metrics HTML
        metrics_html = ""
        if self.metrics:
            metric_items = []
            for label, value in self.metrics.items():
                metric_items.append(f"""
                    <div class="metric-card">
                        <span class="metric-value">{value}</span>
                        <span class="metric-label">{label}</span>
                    </div>
                """)
            metrics_html = f"""
                <div class="metrics-grid">
                    {''.join(metric_items)}
                </div>
            """
        
        # Create actions
        actions = []
        if self.on_copy:
            actions.append('<button class="action-button" onclick="copyTweet()">📋 Copy</button>')
        if self.on_save:
            actions.append('<button class="action-button" onclick="saveTweet()">💾 Save</button>')
        if self.on_edit:
            actions.append('<button class="action-button" onclick="editTweet()">✏️ Edit</button>')
        if self.on_post:
            actions.append('<button class="action-button primary" onclick="postTweet()">🐦 Post</button>')
        
        actions_html = f'<div class="card-actions">{"".join(actions)}</div>' if actions else ""
        
        # Render the card
        card_html = f"""
        <div class="tweet-card">
            <div class="tweet-content">{full_content}</div>
            {metrics_html}
            <div class="tweet-metadata">
                <div class="engagement-badge">
                    📊 {self.engagement_score}% Engagement
                </div>
                <div class="character-badge {char_info['status_class']}">
                    {char_info['count']}/280
                </div>
            </div>
            {actions_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

class MetricsCard:
    """Modern metrics display card."""
    
    def __init__(
        self,
        title: str,
        metrics: Dict[str, any],
        chart_data: Optional[Dict] = None,
        trend: Optional[str] = None
    ):
        self.title = title
        self.metrics = metrics
        self.chart_data = chart_data
        self.trend = trend
    
    def render(self):
        """Render the metrics card."""
        apply_cards_styling()
        
        # Create metrics grid
        metric_items = []
        for label, value in self.metrics.items():
            metric_items.append(f"""
                <div class="metric-card">
                    <span class="metric-value">{value}</span>
                    <span class="metric-label">{label}</span>
                </div>
            """)
        
        metrics_grid = f"""
            <div class="metrics-grid">
                {''.join(metric_items)}
            </div>
        """
        
        # Add trend indicator
        trend_html = ""
        if self.trend:
            trend_color = "#52C41A" if "up" in self.trend.lower() else "#F5222D"
            trend_icon = "📈" if "up" in self.trend.lower() else "📉"
            trend_html = f"""
                <div style="text-align: center; margin-top: 1rem; color: {trend_color};">
                    {trend_icon} {self.trend}
                </div>
            """
        
        # Render the card
        card_html = f"""
        <div class="modern-card">
            <h3 style="margin-bottom: 1rem; color: #2D3748;">{self.title}</h3>
            {metrics_grid}
            {trend_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Add chart if provided
        if self.chart_data:
            self._render_chart()
    
    def _render_chart(self):
        """Render chart for metrics."""
        if self.chart_data.get("type") == "line":
            fig = px.line(
                x=self.chart_data.get("x", []),
                y=self.chart_data.get("y", []),
                title=self.chart_data.get("title", ""),
                labels=self.chart_data.get("labels", {})
            )
        elif self.chart_data.get("type") == "bar":
            fig = px.bar(
                x=self.chart_data.get("x", []),
                y=self.chart_data.get("y", []),
                title=self.chart_data.get("title", ""),
                labels=self.chart_data.get("labels", {})
            )
        else:
            return
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

class StatusCard:
    """Status indicator card."""
    
    def __init__(
        self,
        title: str,
        status: str,
        message: str,
        icon: str = "ℹ️",
        actions: Optional[List[Dict]] = None
    ):
        self.title = title
        self.status = status  # success, warning, error, info
        self.message = message
        self.icon = icon
        self.actions = actions or []
    
    def render(self):
        """Render the status card."""
        apply_cards_styling()
        
        # Status colors
        status_colors = {
            "success": "#52C41A",
            "warning": "#FA8C16",
            "error": "#F5222D",
            "info": "#1890FF"
        }
        
        color = status_colors.get(self.status, "#1890FF")
        
        # Create actions
        actions_html = ""
        if self.actions:
            action_buttons = []
            for action in self.actions:
                action_buttons.append(f"""
                    <button class="action-button" onclick="{action.get('onclick', '')}">
                        {action.get('icon', '')} {action.get('label', 'Action')}
                    </button>
                """)
            actions_html = f"""
                <div class="card-actions">
                    {''.join(action_buttons)}
                </div>
            """
        
        # Render the card
        card_html = f"""
        <div class="modern-card" style="border-left: 4px solid {color};">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="font-size: 2rem;">{self.icon}</span>
                <div>
                    <h3 style="margin: 0; color: #2D3748;">{self.title}</h3>
                    <span style="color: {color}; font-weight: 600; text-transform: uppercase; font-size: 0.8rem;">
                        {self.status}
                    </span>
                </div>
            </div>
            <p style="color: #657786; margin-bottom: 1rem;">{self.message}</p>
            {actions_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

# Utility functions for creating common cards
def create_feature_card(title: str, description: str, icon: str = "🔧", **kwargs):
    """Create and render a feature card."""
    card = FeatureCard(title, description, icon, **kwargs)
    card.render()

def create_tweet_card(content: str, **kwargs):
    """Create and render a tweet card."""
    card = TweetCard(content, **kwargs)
    card.render()

def create_metrics_card(title: str, metrics: Dict, **kwargs):
    """Create and render a metrics card."""
    card = MetricsCard(title, metrics, **kwargs)
    card.render()

def create_status_card(title: str, status: str, message: str, **kwargs):
    """Create and render a status card."""
    card = StatusCard(title, status, message, **kwargs)
    card.render() 