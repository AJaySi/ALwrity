"""
Theme configuration for Twitter UI components.
Provides consistent styling across all Twitter-related features.
"""

import streamlit as st
from typing import Dict, Any

class Theme:
    """Theme configuration for Twitter UI components."""
    
    # Color palette
    COLORS = {
        "primary": "#1DA1F2",  # Twitter blue
        "secondary": "#14171A",  # Dark blue
        "background": "#15202B",  # Dark background
        "text": "#FFFFFF",  # White text
        "text_secondary": "#8899A6",  # Gray text
        "success": "#17BF63",  # Green
        "warning": "#FFAD1F",  # Yellow
        "error": "#E0245E",  # Red
        "border": "rgba(255, 255, 255, 0.1)",  # Subtle border
    }
    
    # Typography
    TYPOGRAPHY = {
        "font_family": "'Helvetica Neue', sans-serif",
        "font_sizes": {
            "h1": "2.5rem",
            "h2": "2rem",
            "h3": "1.5rem",
            "body": "1rem",
            "small": "0.875rem",
        },
        "font_weights": {
            "regular": 400,
            "medium": 500,
            "bold": 700,
        },
    }
    
    # Spacing
    SPACING = {
        "xs": "0.25rem",
        "sm": "0.5rem",
        "md": "1rem",
        "lg": "1.5rem",
        "xl": "2rem",
    }
    
    # Border radius
    BORDER_RADIUS = {
        "sm": "4px",
        "md": "8px",
        "lg": "12px",
        "xl": "16px",
        "full": "9999px",
    }
    
    # Shadows
    SHADOWS = {
        "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
        "md": "0 4px 6px rgba(0, 0, 0, 0.1)",
        "lg": "0 10px 15px rgba(0, 0, 0, 0.1)",
        "xl": "0 20px 25px rgba(0, 0, 0, 0.15)",
    }
    
    # Transitions
    TRANSITIONS = {
        "fast": "0.15s ease",
        "normal": "0.3s ease",
        "slow": "0.5s ease",
    }
    
    @classmethod
    def get_css(cls) -> str:
        """Get the complete CSS for the theme."""
        return f"""
            /* Base styles */
            .stApp {{
                background-color: {cls.COLORS['background']};
                color: {cls.COLORS['text']};
                font-family: {cls.TYPOGRAPHY['font_family']};
            }}
            
            /* Typography */
            h1, h2, h3, h4, h5, h6 {{
                color: {cls.COLORS['text']};
                font-family: {cls.TYPOGRAPHY['font_family']};
                font-weight: {cls.TYPOGRAPHY['font_weights']['bold']};
            }}
            
            /* Buttons */
            .stButton > button {{
                background: linear-gradient(45deg, {cls.COLORS['primary']}, #0C85D0);
                color: {cls.COLORS['text']};
                border: none;
                padding: {cls.SPACING['md']} {cls.SPACING['lg']};
                border-radius: {cls.BORDER_RADIUS['full']};
                font-weight: {cls.TYPOGRAPHY['font_weights']['medium']};
                transition: all {cls.TRANSITIONS['normal']};
                box-shadow: {cls.SHADOWS['md']};
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: {cls.SHADOWS['lg']};
            }}
            
            /* Cards */
            .card {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['lg']};
                padding: {cls.SPACING['lg']};
                margin-bottom: {cls.SPACING['md']};
                backdrop-filter: blur(10px);
                transition: transform {cls.TRANSITIONS['normal']};
            }}
            
            .card:hover {{
                transform: translateY(-4px);
            }}
            
            /* Forms */
            .stTextInput > div > div > input {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['md']};
                color: {cls.COLORS['text']};
                padding: {cls.SPACING['md']};
            }}
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                gap: {cls.SPACING['sm']};
                background-color: rgba(0, 0, 0, 0.2);
                padding: {cls.SPACING['md']};
                border-radius: {cls.BORDER_RADIUS['lg']};
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent;
                color: {cls.COLORS['text']};
                border: 1px solid {cls.COLORS['border']};
                border-radius: {cls.BORDER_RADIUS['md']};
                padding: {cls.SPACING['sm']} {cls.SPACING['md']};
            }}
            
            /* Status badges */
            .status-badge {{
                display: inline-block;
                padding: {cls.SPACING['xs']} {cls.SPACING['md']};
                border-radius: {cls.BORDER_RADIUS['full']};
                font-size: {cls.TYPOGRAPHY['font_sizes']['small']};
                font-weight: {cls.TYPOGRAPHY['font_weights']['medium']};
            }}
            
            .status-active {{
                background: linear-gradient(45deg, {cls.COLORS['success']}, #69F0AE);
                color: {cls.COLORS['secondary']};
            }}
            
            .status-coming-soon {{
                background: linear-gradient(45deg, {cls.COLORS['warning']}, #FFA000);
                color: {cls.COLORS['secondary']};
            }}
        """
    
    @classmethod
    def apply(cls) -> None:
        """Apply the theme to the Streamlit app."""
        st.markdown(f"<style>{cls.get_css()}</style>", unsafe_allow_html=True) 