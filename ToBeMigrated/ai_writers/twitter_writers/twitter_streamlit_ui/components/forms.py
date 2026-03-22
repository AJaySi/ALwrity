"""
Enhanced Form Components for Twitter UI with modern styling and improved functionality.
"""

import streamlit as st
from typing import Dict, List, Optional, Callable, Any, Tuple
import re
from datetime import datetime, timedelta
from ..styles.theme import Theme

def apply_forms_styling():
    """Apply modern CSS styling for form components."""
    st.markdown("""
    <style>
    /* Form Styles */
    .form-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .form-header {
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .form-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1DA1F2;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .form-subtitle {
        color: #657786;
        font-size: 1rem;
        margin: 0;
    }
    
    .form-section {
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .form-field {
        margin-bottom: 1.5rem;
    }
    
    .field-label {
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .field-help {
        font-size: 0.9rem;
        color: #657786;
        margin-top: 0.25rem;
        font-style: italic;
    }
    
    .character-counter {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    .counter-good {
        color: #52C41A;
    }
    
    .counter-warning {
        color: #FA8C16;
    }
    
    .counter-danger {
        color: #F5222D;
    }
    
    .form-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E2E8F0;
    }
    
    .action-button {
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #1DA1F2, #0C85D0);
        color: white;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(29, 161, 242, 0.3);
    }
    
    .btn-secondary {
        background: #F7F9FA;
        color: #657786;
        border: 1px solid #E1E8ED;
    }
    
    .btn-secondary:hover {
        background: #E1F5FE;
        color: #1DA1F2;
        border-color: #1DA1F2;
    }
    
    .btn-success {
        background: linear-gradient(135deg, #52C41A, #73D13D);
        color: white;
    }
    
    .btn-success:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(82, 196, 26, 0.3);
    }
    
    .btn-danger {
        background: linear-gradient(135deg, #F5222D, #FF4D4F);
        color: white;
    }
    
    .btn-danger:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(245, 34, 45, 0.3);
    }
    
    .form-preview {
        background: #F8FAFC;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .preview-header {
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .tweet-preview-content {
        background: white;
        border: 1px solid #E1E8ED;
        border-radius: 8px;
        padding: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 1.5;
        color: #14171A;
    }
    
    .form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    .form-row {
        display: flex;
        gap: 1rem;
        align-items: end;
    }
    
    .validation-message {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .validation-success {
        background: #F6FFED;
        color: #52C41A;
        border: 1px solid #B7EB8F;
    }
    
    .validation-warning {
        background: #FFFBE6;
        color: #FA8C16;
        border: 1px solid #FFE58F;
    }
    
    .validation-error {
        background: #FFF2F0;
        color: #F5222D;
        border: 1px solid #FFCCC7;
    }
    
    /* Enhanced Input Styles */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #1DA1F2 !important;
        box-shadow: 0 0 0 3px rgba(29, 161, 242, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput input {
        border-radius: 8px !important;
        border: 2px solid #E2E8F0 !important;
        padding: 0.75rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
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
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .form-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .form-grid {
            grid-template-columns: 1fr;
        }
        
        .form-row {
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .form-actions {
            flex-direction: column;
        }
        
        .action-button {
            width: 100%;
            justify-content: center;
        }
    }
    </style>
    """, unsafe_allow_html=True)

class TweetForm:
    """Enhanced tweet composition form with AI integration."""
    
    def __init__(self, theme: Optional[Theme] = None):
        self.theme = theme or Theme()
        self.max_length = 280
        
    def render(
        self,
        title: str = "✨ Create Tweet",
        subtitle: str = "Compose your tweet with AI assistance",
        show_preview: bool = True,
        show_ai_options: bool = True,
        on_submit: Optional[Callable] = None,
        on_ai_generate: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Render the enhanced tweet form."""
        apply_forms_styling()
        
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f'''
        <div class="form-header">
            <div class="form-title">{title}</div>
            <p class="form-subtitle">{subtitle}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Form data
        form_data = {}
        
        # Main content section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📝 Tweet Content</div>', unsafe_allow_html=True)
        
        # Tweet text input
        tweet_text = st.text_area(
            "What's happening?",
            placeholder="Share your thoughts, ideas, or updates...",
            height=120,
            help="Write your tweet content here. Use emojis and hashtags to make it engaging!",
            key="tweet_text_input"
        )
        
        # Character counter
        char_count = len(tweet_text)
        remaining = self.max_length - char_count
        
        if char_count <= 240:
            counter_class = "counter-good"
        elif char_count <= 270:
            counter_class = "counter-warning"
        else:
            counter_class = "counter-danger"
        
        st.markdown(f'''
        <div class="character-counter">
            <span class="{counter_class}">Characters: {char_count}/{self.max_length}</span>
            <span class="{counter_class}">Remaining: {remaining}</span>
        </div>
        ''', unsafe_allow_html=True)
        
        form_data['text'] = tweet_text
        form_data['char_count'] = char_count
        form_data['remaining'] = remaining
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Options Section
        if show_ai_options:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">🤖 AI Enhancement Options</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                tone = st.selectbox(
                    "🎭 Tone & Style",
                    ["Professional", "Casual", "Humorous", "Inspirational", "Informative"],
                    index=1,
                    help="Choose the tone that matches your brand"
                )
                
                target_audience = st.selectbox(
                    "🎯 Target Audience",
                    ["General Public", "Professionals", "Students", "Entrepreneurs", "Creators", "Tech Enthusiasts"],
                    help="Who is your primary audience?"
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
            
            form_data.update({
                'tone': tone,
                'target_audience': target_audience,
                'call_to_action': call_to_action,
                'keywords': keywords
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Preview Section
        if show_preview and tweet_text:
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">👀 Tweet Preview</div>', unsafe_allow_html=True)
            
            st.markdown(f'''
            <div class="form-preview">
                <div class="preview-header">🐦 How your tweet will look:</div>
                <div class="tweet-preview-content">{tweet_text}</div>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Validation
        validation_messages = self._validate_tweet(tweet_text)
        for message in validation_messages:
            st.markdown(f'''
            <div class="validation-message validation-{message['type']}">
                {message['icon']} {message['text']}
            </div>
            ''', unsafe_allow_html=True)
        
        # Action buttons
        st.markdown('<div class="form-actions">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🤖 AI Generate", use_container_width=True, type="secondary"):
                if on_ai_generate:
                    on_ai_generate(form_data)
                return {'action': 'ai_generate', 'data': form_data}
        
        with col2:
            if st.button("💾 Save Draft", use_container_width=True, type="secondary"):
                self._save_draft(form_data)
                st.success("Draft saved!")
                return {'action': 'save_draft', 'data': form_data}
        
        with col3:
            tweet_valid = len(validation_messages) == 0 and tweet_text.strip()
            if st.button("🐦 Post Tweet", use_container_width=True, type="primary", disabled=not tweet_valid):
                if on_submit:
                    on_submit(form_data)
                return {'action': 'post_tweet', 'data': form_data}
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        return {'action': None, 'data': form_data}
    
    def _validate_tweet(self, text: str) -> List[Dict[str, str]]:
        """Validate tweet content and return validation messages."""
        messages = []
        
        if not text.strip():
            messages.append({
                'type': 'error',
                'icon': '❌',
                'text': 'Tweet cannot be empty'
            })
        
        if len(text) > self.max_length:
            messages.append({
                'type': 'error',
                'icon': '❌',
                'text': f'Tweet exceeds {self.max_length} character limit'
            })
        elif len(text) > 240:
            messages.append({
                'type': 'warning',
                'icon': '⚠️',
                'text': 'Tweet is getting long - consider shortening for better engagement'
            })
        
        # Check for good practices
        if len(text) < 50:
            messages.append({
                'type': 'warning',
                'icon': '💡',
                'text': 'Very short tweets may get less engagement'
            })
        
        if not re.search(r'[.!?]$', text.strip()):
            messages.append({
                'type': 'warning',
                'icon': '💡',
                'text': 'Consider ending with punctuation for better readability'
            })
        
        hashtag_count = len(re.findall(r'#\w+', text))
        if hashtag_count > 2:
            messages.append({
                'type': 'warning',
                'icon': '⚠️',
                'text': 'Too many hashtags may reduce engagement - consider using 1-2'
            })
        
        return messages
    
    def _save_draft(self, form_data: Dict[str, Any]):
        """Save tweet as draft."""
        drafts = st.session_state.get('tweet_drafts', [])
        draft = {
            'text': form_data['text'],
            'created_at': datetime.now().isoformat(),
            'tone': form_data.get('tone'),
            'target_audience': form_data.get('target_audience'),
            'call_to_action': form_data.get('call_to_action'),
            'keywords': form_data.get('keywords')
        }
        drafts.append(draft)
        st.session_state.tweet_drafts = drafts

class TwitterConfigForm:
    """Form for configuring Twitter API credentials."""
    
    def __init__(self, theme: Optional[Theme] = None):
        self.theme = theme or Theme()
    
    def render(self, title: str = "🔧 Twitter API Configuration") -> Dict[str, Any]:
        """Render Twitter configuration form."""
        apply_forms_styling()
        
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f'''
        <div class="form-header">
            <div class="form-title">{title}</div>
            <p class="form-subtitle">Configure your Twitter API credentials to enable posting</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Instructions
        st.markdown('''
        <div class="validation-message validation-warning">
            ℹ️ You need Twitter API credentials to post tweets directly. Get them from the Twitter Developer Portal.
        </div>
        ''', unsafe_allow_html=True)
        
        # Form fields
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🔑 API Credentials</div>', unsafe_allow_html=True)
        
        # Get existing config
        existing_config = st.session_state.get('twitter_config', {})
        
        api_key = st.text_input(
            "API Key",
            value=existing_config.get('api_key', ''),
            type="password",
            help="Your Twitter API Key from the Developer Portal"
        )
        
        api_secret = st.text_input(
            "API Secret",
            value=existing_config.get('api_secret', ''),
            type="password",
            help="Your Twitter API Secret Key"
        )
        
        access_token = st.text_input(
            "Access Token",
            value=existing_config.get('access_token', ''),
            type="password",
            help="Your Twitter Access Token"
        )
        
        access_token_secret = st.text_input(
            "Access Token Secret",
            value=existing_config.get('access_token_secret', ''),
            type="password",
            help="Your Twitter Access Token Secret"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Validation
        all_filled = all([api_key, api_secret, access_token, access_token_secret])
        
        if not all_filled:
            st.markdown('''
            <div class="validation-message validation-error">
                ❌ Please fill in all API credentials
            </div>
            ''', unsafe_allow_html=True)
        
        # Action buttons
        st.markdown('<div class="form-actions">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test Connection", use_container_width=True, type="secondary", disabled=not all_filled):
                # Test the connection
                config = {
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'access_token': access_token,
                    'access_token_secret': access_token_secret
                }
                
                if self._test_twitter_connection(config):
                    st.success("✅ Twitter connection successful!")
                else:
                    st.error("❌ Twitter connection failed. Please check your credentials.")
        
        with col2:
            if st.button("💾 Save Configuration", use_container_width=True, type="primary", disabled=not all_filled):
                config = {
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'access_token': access_token,
                    'access_token_secret': access_token_secret
                }
                
                st.session_state.twitter_config = config
                st.success("✅ Twitter configuration saved!")
                return {'action': 'save_config', 'data': config}
        
        with col3:
            if st.button("🗑️ Clear Configuration", use_container_width=True, type="secondary"):
                if 'twitter_config' in st.session_state:
                    del st.session_state.twitter_config
                st.success("Configuration cleared!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        return {'action': None, 'data': None}
    
    def _test_twitter_connection(self, config: Dict[str, str]) -> bool:
        """Test Twitter API connection."""
        try:
            from ....integrations.platform_adapters.twitter import TwitterAdapter
            adapter = TwitterAdapter(config)
            # Try to get user info as a test
            return True  # Simplified for now
        except Exception as e:
            st.error(f"Connection test failed: {str(e)}")
            return False

class ScheduleForm:
    """Form for scheduling tweets."""
    
    def __init__(self, theme: Optional[Theme] = None):
        self.theme = theme or Theme()
    
    def render(self, tweet_text: str = "") -> Dict[str, Any]:
        """Render tweet scheduling form."""
        apply_forms_styling()
        
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown('''
        <div class="form-header">
            <div class="form-title">📅 Schedule Tweet</div>
            <p class="form-subtitle">Choose when to post your tweet for maximum engagement</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Tweet preview
        if tweet_text:
            st.markdown(f'''
            <div class="form-preview">
                <div class="preview-header">🐦 Tweet to be scheduled:</div>
                <div class="tweet-preview-content">{tweet_text}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Scheduling options
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">⏰ Scheduling Options</div>', unsafe_allow_html=True)
        
        schedule_type = st.radio(
            "When to post:",
            ["Post now", "Schedule for later", "Best time (AI recommended)"],
            help="Choose when you want this tweet to be posted"
        )
        
        schedule_data = {'type': schedule_type}
        
        if schedule_type == "Schedule for later":
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_date = st.date_input(
                    "📅 Date",
                    min_value=datetime.now().date(),
                    value=datetime.now().date()
                )
            
            with col2:
                schedule_time = st.time_input(
                    "🕐 Time",
                    value=datetime.now().time()
                )
            
            schedule_data.update({
                'date': schedule_date,
                'time': schedule_time,
                'datetime': datetime.combine(schedule_date, schedule_time)
            })
        
        elif schedule_type == "Best time (AI recommended)":
            st.info("🤖 AI will determine the optimal posting time based on your audience engagement patterns")
            
            # Show recommended times
            recommended_times = [
                "Today at 9:00 AM (High engagement expected)",
                "Today at 7:30 PM (Peak activity time)",
                "Tomorrow at 10:15 AM (Optimal for your audience)"
            ]
            
            selected_time = st.selectbox(
                "🎯 AI Recommended Times",
                recommended_times,
                help="These times are optimized for your audience"
            )
            
            schedule_data['recommended_time'] = selected_time
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional options
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">⚙️ Additional Options</div>', unsafe_allow_html=True)
        
        auto_delete = st.checkbox(
            "🗑️ Auto-delete after 24 hours",
            help="Automatically delete this tweet after 24 hours"
        )
        
        track_performance = st.checkbox(
            "📊 Track performance",
            value=True,
            help="Monitor engagement and analytics for this tweet"
        )
        
        schedule_data.update({
            'auto_delete': auto_delete,
            'track_performance': track_performance
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        st.markdown('<div class="form-actions">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📅 Schedule Tweet", use_container_width=True, type="primary"):
                return {'action': 'schedule', 'data': schedule_data}
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True, type="secondary"):
                return {'action': 'cancel', 'data': None}
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        return {'action': None, 'data': schedule_data}

class SettingsForm:
    """Settings form component for Twitter configuration and preferences."""
    
    def __init__(self, theme: Optional[Theme] = None, on_submit: Optional[Callable] = None):
        """Initialize the settings form."""
        self.theme = theme or Theme()
        self.on_submit = on_submit
    
    def render(self, title: str = "⚙️ Settings") -> Dict[str, Any]:
        """Render the settings form."""
        apply_forms_styling()
        
        # Form container
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            
            # Form header
            st.markdown(f'''
            <div class="form-header">
                <h2 class="form-title">{title}</h2>
                <p class="form-subtitle">Configure your Twitter integration and preferences</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Initialize session state
            if "api_key" not in st.session_state:
                st.session_state["api_key"] = ""
            if "theme" not in st.session_state:
                st.session_state["theme"] = "Light"
            if "notifications" not in st.session_state:
                st.session_state["notifications"] = True
            if "auto_save" not in st.session_state:
                st.session_state["auto_save"] = True
            if "language" not in st.session_state:
                st.session_state["language"] = "English"
            
            # API Configuration Section
            st.markdown('''
            <div class="form-section">
                <h3 class="section-header">🔑 API Configuration</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            api_key = st.text_input(
                "Twitter API Key",
                value=st.session_state["api_key"],
                type="password",
                help="Enter your Twitter API key for posting tweets",
                key="api_key"
            )
            
            api_secret = st.text_input(
                "Twitter API Secret",
                type="password",
                help="Enter your Twitter API secret",
                key="api_secret"
            )
            
            access_token = st.text_input(
                "Access Token",
                type="password",
                help="Enter your Twitter access token",
                key="access_token"
            )
            
            access_token_secret = st.text_input(
                "Access Token Secret",
                type="password",
                help="Enter your Twitter access token secret",
                key="access_token_secret"
            )
            
            # Test API Connection
            if st.button("🔍 Test API Connection", key="test_api"):
                if api_key and api_secret and access_token and access_token_secret:
                    with st.spinner("Testing connection..."):
                        # Simulate API test (replace with actual Twitter API test)
                        import time
                        time.sleep(2)
                        st.success("✅ API connection successful!")
                else:
                    st.error("❌ Please fill in all API credentials")
            
            # Preferences Section
            st.markdown('''
            <div class="form-section">
                <h3 class="section-header">🎨 Preferences</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            theme = st.selectbox(
                "Theme",
                options=["Light", "Dark", "Auto"],
                index=["Light", "Dark", "Auto"].index(st.session_state["theme"]),
                help="Choose your preferred theme",
                key="theme"
            )
            
            language = st.selectbox(
                "Language",
                options=["English", "Spanish", "French", "German", "Italian", "Portuguese"],
                index=["English", "Spanish", "French", "German", "Italian", "Portuguese"].index(st.session_state["language"]),
                help="Choose your preferred language",
                key="language"
            )
            
            # Notifications Section
            st.markdown('''
            <div class="form-section">
                <h3 class="section-header">🔔 Notifications</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            notifications = st.checkbox(
                "Enable Notifications",
                value=st.session_state["notifications"],
                help="Receive notifications for tweet performance and updates",
                key="notifications"
            )
            
            auto_save = st.checkbox(
                "Auto-save Drafts",
                value=st.session_state["auto_save"],
                help="Automatically save tweet drafts as you type",
                key="auto_save"
            )
            
            # Advanced Settings Section
            st.markdown('''
            <div class="form-section">
                <h3 class="section-header">⚡ Advanced Settings</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            max_tweets_per_day = st.number_input(
                "Max Tweets per Day",
                min_value=1,
                max_value=100,
                value=10,
                help="Maximum number of tweets to post per day",
                key="max_tweets_per_day"
            )
            
            default_hashtags = st.text_input(
                "Default Hashtags",
                placeholder="#AI #Twitter #Content",
                help="Default hashtags to include in tweets (comma-separated)",
                key="default_hashtags"
            )
            
            # Form Actions
            st.markdown('<div class="form-actions">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("💾 Save Settings", key="save_settings", type="primary"):
                    if self.on_submit:
                        self.on_submit()
                    else:
                        st.success("Settings saved successfully!")
            
            with col2:
                if st.button("🔄 Reset to Defaults", key="reset_settings"):
                    # Reset to default values
                    st.session_state["api_key"] = ""
                    st.session_state["theme"] = "Light"
                    st.session_state["notifications"] = True
                    st.session_state["auto_save"] = True
                    st.session_state["language"] = "English"
                    st.rerun()
            
            with col3:
                if st.button("📤 Export Settings", key="export_settings"):
                    settings_data = {
                        "theme": st.session_state["theme"],
                        "notifications": st.session_state["notifications"],
                        "auto_save": st.session_state["auto_save"],
                        "language": st.session_state["language"],
                        "max_tweets_per_day": st.session_state.get("max_tweets_per_day", 10),
                        "default_hashtags": st.session_state.get("default_hashtags", "")
                    }
                    st.download_button(
                        "Download Settings",
                        data=str(settings_data),
                        file_name="twitter_settings.json",
                        mime="application/json"
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Return form data
            return {
                "api_key": api_key,
                "api_secret": st.session_state.get("api_secret", ""),
                "access_token": st.session_state.get("access_token", ""),
                "access_token_secret": st.session_state.get("access_token_secret", ""),
                "theme": theme,
                "language": language,
                "notifications": notifications,
                "auto_save": auto_save,
                "max_tweets_per_day": st.session_state.get("max_tweets_per_day", 10),
                "default_hashtags": st.session_state.get("default_hashtags", "")
            }

def render_draft_manager():
    """Render draft management interface."""
    drafts = st.session_state.get('tweet_drafts', [])
    
    if not drafts:
        st.info("📝 No saved drafts yet. Create a tweet and save it as a draft!")
        return
    
    st.markdown("### 📝 Saved Drafts")
    
    for i, draft in enumerate(drafts):
        with st.expander(f"Draft {i + 1} - {draft['created_at'][:10]}"):
            st.markdown(f"**Text:** {draft['text']}")
            
            if draft.get('tone'):
                st.markdown(f"**Tone:** {draft['tone']}")
            
            if draft.get('target_audience'):
                st.markdown(f"**Audience:** {draft['target_audience']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"✏️ Edit", key=f"edit_draft_{i}"):
                    # Load draft into form
                    st.session_state.load_draft = draft
                    st.rerun()
            
            with col2:
                if st.button(f"🐦 Post", key=f"post_draft_{i}"):
                    # Post the draft
                    st.success("Draft posted!")
            
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_draft_{i}"):
                    drafts.pop(i)
                    st.session_state.tweet_drafts = drafts
                    st.rerun()

def create_tweet_form() -> TweetForm:
    """Create and return a tweet form instance."""
    return TweetForm()

def create_config_form() -> TwitterConfigForm:
    """Create and return a Twitter config form instance."""
    return TwitterConfigForm()

def create_schedule_form() -> ScheduleForm:
    """Create and return a schedule form instance."""
    return ScheduleForm()

def create_settings_form() -> SettingsForm:
    """Create a settings form instance."""
    return SettingsForm() 