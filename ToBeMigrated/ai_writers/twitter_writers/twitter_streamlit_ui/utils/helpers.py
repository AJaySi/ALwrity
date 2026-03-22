"""
Utility functions for Twitter UI.
Provides helper functions for common operations.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

def save_to_session(key: str, value: Any) -> None:
    """Save a value to the session state."""
    st.session_state[key] = value

def get_from_session(key: str, default: Any = None) -> Any:
    """Get a value from the session state."""
    return st.session_state.get(key, default)

def clear_session() -> None:
    """Clear all session state variables."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def save_to_file(data: Dict[str, Any], filename: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

def load_from_file(filename: str) -> Optional[Dict[str, Any]]:
    """Load data from a JSON file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
    return None

def format_datetime(dt: datetime) -> str:
    """Format a datetime object for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse a datetime string."""
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

def validate_tweet_content(content: str) -> bool:
    """Validate tweet content."""
    if not content:
        st.error("Tweet content cannot be empty")
        return False
    if len(content) > 280:
        st.error("Tweet content cannot exceed 280 characters")
        return False
    return True

def validate_hashtags(hashtags: List[str]) -> bool:
    """Validate hashtags."""
    for tag in hashtags:
        if not tag.startswith('#'):
            st.error(f"Hashtag {tag} must start with #")
            return False
        if len(tag) > 30:
            st.error(f"Hashtag {tag} cannot exceed 30 characters")
            return False
    return True

def validate_emojis(emojis: List[str]) -> bool:
    """Validate emojis."""
    for emoji in emojis:
        if len(emoji) != 1:
            st.error(f"Invalid emoji: {emoji}")
            return False
    return True

def calculate_engagement_score(
    content: str,
    hashtags: List[str],
    emojis: List[str],
    tone: str
) -> float:
    """Calculate engagement score for a tweet."""
    score = 0.0
    
    # Content length score (optimal length is 100-150 characters)
    content_length = len(content)
    if 100 <= content_length <= 150:
        score += 30
    elif 50 <= content_length <= 200:
        score += 20
    else:
        score += 10
    
    # Hashtag score (optimal number is 2-3 hashtags)
    hashtag_count = len(hashtags)
    if 2 <= hashtag_count <= 3:
        score += 20
    elif 1 <= hashtag_count <= 4:
        score += 15
    else:
        score += 5
    
    # Emoji score (optimal number is 1-2 emojis)
    emoji_count = len(emojis)
    if 1 <= emoji_count <= 2:
        score += 20
    elif 0 <= emoji_count <= 3:
        score += 15
    else:
        score += 5
    
    # Tone score
    tone_scores = {
        "professional": 15,
        "casual": 20,
        "humorous": 25,
        "informative": 15,
        "inspirational": 20
    }
    score += tone_scores.get(tone, 10)
    
    return min(score, 100)

def generate_tweet_metrics(engagement_score: float) -> Dict[str, float]:
    """Generate metrics for a tweet based on engagement score."""
    return {
        "Engagement": engagement_score,
        "Reach": engagement_score * 0.8,
        "Growth": engagement_score * 0.6
    }

def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard."""
    try:
        st.write(f'<script>navigator.clipboard.writeText("{text}")</script>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error copying to clipboard: {str(e)}")

def show_success_message(message: str) -> None:
    """Show a success message."""
    st.success(message)

def show_error_message(message: str) -> None:
    """Show an error message."""
    st.error(message)

def show_info_message(message: str) -> None:
    """Show an info message."""
    st.info(message)

def show_warning_message(message: str) -> None:
    """Show a warning message."""
    st.warning(message)

def create_download_button(
    data: Dict[str, Any],
    filename: str,
    button_text: str = "Download"
) -> None:
    """Create a download button for data."""
    try:
        json_str = json.dumps(data, indent=4)
        st.download_button(
            label=button_text,
            data=json_str,
            file_name=filename,
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error creating download button: {str(e)}")

def create_upload_button(
    on_upload: callable,
    button_text: str = "Upload",
    file_types: List[str] = ["json"]
) -> None:
    """Create an upload button for data."""
    try:
        uploaded_file = st.file_uploader(
            button_text,
            type=file_types
        )
        if uploaded_file is not None:
            data = json.load(uploaded_file)
            on_upload(data)
    except Exception as e:
        st.error(f"Error handling upload: {str(e)}") 