"""
Enhanced Navigation Component for Twitter UI with modern styling and improved functionality.
"""

import streamlit as st
from typing import Dict, List, Optional, Callable, Any
from ..styles.theme import Theme
import os

def apply_navigation_styling():
    """Apply modern CSS styling for navigation components."""
    st.markdown("""
    <style>
    /* Navigation Styles */
    .nav-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .nav-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1DA1F2;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .status-connected {
        background: linear-gradient(135deg, #52C41A, #73D13D);
        color: white;
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #FA8C16, #FFA940);
        color: white;
    }
    
    .nav-menu {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .nav-item {
        background: #F7F9FA;
        border: 2px solid transparent;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        color: #657786;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .nav-item:hover {
        background: #E1F5FE;
        border-color: #1DA1F2;
        color: #1DA1F2;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(29, 161, 242, 0.2);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #1DA1F2, #0C85D0);
        color: white;
        border-color: #1DA1F2;
        box-shadow: 0 4px 15px rgba(29, 161, 242, 0.3);
    }
    
    .nav-item.active:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(29, 161, 242, 0.4);
    }
    
    .nav-breadcrumb {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #657786;
    }
    
    .breadcrumb-item {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .breadcrumb-separator {
        color: #CBD5E0;
        margin: 0 0.5rem;
    }
    
    .nav-actions {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .action-button {
        background: linear-gradient(135deg, #52C41A, #73D13D);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(82, 196, 26, 0.3);
    }
    
    .action-button.secondary {
        background: #F7F9FA;
        color: #657786;
        border: 1px solid #E1E8ED;
    }
    
    .action-button.secondary:hover {
        background: #E1F5FE;
        color: #1DA1F2;
        border-color: #1DA1F2;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .nav-header {
            flex-direction: column;
            gap: 1rem;
            align-items: flex-start;
        }
        
        .nav-menu {
            flex-direction: column;
            width: 100%;
        }
        
        .nav-item {
            width: 100%;
            justify-content: center;
        }
        
        .nav-actions {
            width: 100%;
            justify-content: center;
        }
    }
    </style>
    """, unsafe_allow_html=True)

class TwitterNavigation:
    """Enhanced navigation component for Twitter dashboard."""
    
    def __init__(self, theme: Optional[Theme] = None):
        self.theme = theme or Theme()
        self.current_page = st.session_state.get('current_page', 'dashboard')
        
    def render_header(self, title: str = "Twitter AI Assistant", show_status: bool = True):
        """Render the navigation header with title and status."""
        apply_navigation_styling()
        
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        st.markdown('<div class="nav-header">', unsafe_allow_html=True)
        
        # Title
        st.markdown(f'<div class="nav-title">🐦 {title}</div>', unsafe_allow_html=True)
        
        # Status indicator
        if show_status:
            twitter_connected = self._check_twitter_connection()
            status_class = "status-connected" if twitter_connected else "status-disconnected"
            status_text = "Connected" if twitter_connected else "Not Connected"
            status_icon = "✅" if twitter_connected else "⚠️"
            
            st.markdown(f'''
            <div class="nav-status {status_class}">
                {status_icon} Twitter {status_text}
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_menu(self, menu_items: List[Dict], current_page: Optional[str] = None):
        """Render navigation menu with items."""
        if current_page:
            self.current_page = current_page
            st.session_state.current_page = current_page
        
        st.markdown('<div class="nav-menu">', unsafe_allow_html=True)
        
        cols = st.columns(len(menu_items))
        
        for i, item in enumerate(menu_items):
            with cols[i]:
                active_class = "active" if item.get('key') == self.current_page else ""
                
                if st.button(
                    f"{item.get('icon', '')} {item.get('label', '')}",
                    key=f"nav_{item.get('key', i)}",
                    use_container_width=True,
                    type="primary" if active_class else "secondary"
                ):
                    st.session_state.current_page = item.get('key')
                    if item.get('callback'):
                        item['callback']()
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        return st.session_state.get('current_page', menu_items[0].get('key'))
    
    def render_breadcrumb(self, items: List[Dict]):
        """Render breadcrumb navigation."""
        st.markdown('<div class="nav-breadcrumb">', unsafe_allow_html=True)
        
        for i, item in enumerate(items):
            if i > 0:
                st.markdown('<span class="breadcrumb-separator">›</span>', unsafe_allow_html=True)
            
            icon = item.get('icon', '')
            label = item.get('label', '')
            
            if item.get('active', False):
                st.markdown(f'<span class="breadcrumb-item"><strong>{icon} {label}</strong></span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="breadcrumb-item">{icon} {label}</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_actions(self, actions: List[Dict]):
        """Render action buttons in navigation."""
        st.markdown('<div class="nav-actions">', unsafe_allow_html=True)
        
        cols = st.columns(len(actions))
        
        for i, action in enumerate(actions):
            with cols[i]:
                button_type = action.get('type', 'primary')
                
                if st.button(
                    f"{action.get('icon', '')} {action.get('label', '')}",
                    key=f"action_{action.get('key', i)}",
                    type=button_type,
                    use_container_width=True,
                    help=action.get('help', '')
                ):
                    if action.get('callback'):
                        action['callback']()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_sidebar_menu(self, menu_items: List[Dict]):
        """Render sidebar navigation menu."""
        with st.sidebar:
            st.markdown("### 🐦 Twitter Tools")
            
            for item in menu_items:
                icon = item.get('icon', '')
                label = item.get('label', '')
                key = item.get('key', '')
                
                if st.button(f"{icon} {label}", key=f"sidebar_{key}", use_container_width=True):
                    st.session_state.current_page = key
                    if item.get('callback'):
                        item['callback']()
                    st.rerun()
            
            # Twitter connection status in sidebar
            st.markdown("---")
            twitter_connected = self._check_twitter_connection()
            
            if twitter_connected:
                st.success("🐦 Twitter Connected")
            else:
                st.warning("⚠️ Twitter Not Connected")
                if st.button("🔧 Configure Twitter", use_container_width=True):
                    st.session_state.show_twitter_config = True
                    st.rerun()
    
    def _check_twitter_connection(self) -> bool:
        """Check if Twitter is connected."""
        twitter_config = st.session_state.get('twitter_config', {})
        return bool(twitter_config and all([
            twitter_config.get('api_key'),
            twitter_config.get('api_secret'),
            twitter_config.get('access_token'),
            twitter_config.get('access_token_secret')
        ]))

class Sidebar:
    """Sidebar navigation component."""
    
    def __init__(self, title: str = "Navigation", logo: Optional[str] = None):
        """Initialize the sidebar."""
        self.title = title
        self.logo = logo
        self.menu_items = []
    
    def add_menu_item(self, label: str, icon: str, key: str, callback: Optional[Callable] = None):
        """Add a menu item to the sidebar."""
        self.menu_items.append({
            'label': label,
            'icon': icon,
            'key': key,
            'callback': callback
        })
    
    def render(self) -> str:
        """Render the sidebar and return the selected page."""
        with st.sidebar:
            # Logo and title
            if self.logo and os.path.exists(self.logo):
                st.image(self.logo, width=100)
            st.title(self.title)
            st.markdown("---")
            
            # Menu items
            selected_page = None
            for item in self.menu_items:
                if st.button(
                    f"{item['icon']} {item['label']}",
                    key=f"sidebar_{item['key']}",
                    use_container_width=True
                ):
                    selected_page = item['key']
                    if item.get('callback'):
                        item['callback']()
            
            return selected_page or st.session_state.get('current_page', 'dashboard')


class Header:
    """Header component with title and actions."""
    
    def __init__(self, title: str = "Dashboard", subtitle: str = ""):
        """Initialize the header."""
        self.title = title
        self.subtitle = subtitle
        self.actions = []
    
    def add_action(self, label: str, icon: str, callback: Callable, help_text: str = ""):
        """Add an action button to the header."""
        self.actions.append({
            'label': label,
            'icon': icon,
            'callback': callback,
            'help': help_text
        })
    
    def render(self):
        """Render the header."""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.title(f"{self.title}")
            if self.subtitle:
                st.markdown(f"*{self.subtitle}*")
        
        with col2:
            if self.actions:
                for i, action in enumerate(self.actions):
                    if st.button(
                        f"{action['icon']} {action['label']}",
                        key=f"header_action_{i}",
                        help=action.get('help', ''),
                        use_container_width=True
                    ):
                        action['callback']()


class Tabs:
    """Tab navigation component."""
    
    def __init__(self):
        """Initialize the tabs."""
        self.tabs = []
    
    def add_tab(self, label: str, icon: str, content_func: Callable):
        """Add a tab."""
        self.tabs.append({
            'label': label,
            'icon': icon,
            'content_func': content_func
        })
    
    def render(self):
        """Render the tabs."""
        if not self.tabs:
            return
        
        tab_labels = [f"{tab['icon']} {tab['label']}" for tab in self.tabs]
        selected_tabs = st.tabs(tab_labels)
        
        for i, tab in enumerate(self.tabs):
            with selected_tabs[i]:
                tab['content_func']()


class Breadcrumbs:
    """Breadcrumb navigation component."""
    
    def __init__(self):
        """Initialize breadcrumbs."""
        self.items = []
    
    def add_item(self, label: str, key: str = None, callback: Callable = None):
        """Add a breadcrumb item."""
        self.items.append({
            'label': label,
            'key': key,
            'callback': callback
        })
    
    def render(self):
        """Render the breadcrumbs."""
        if not self.items:
            return
        
        breadcrumb_html = '<div class="nav-breadcrumb">'
        
        for i, item in enumerate(self.items):
            if i > 0:
                breadcrumb_html += '<span class="breadcrumb-separator">›</span>'
            
            if item.get('callback'):
                breadcrumb_html += f'<span class="breadcrumb-item clickable" onclick="handleBreadcrumbClick(\'{item["key"]}\')">{item["label"]}</span>'
            else:
                breadcrumb_html += f'<span class="breadcrumb-item">{item["label"]}</span>'
        
        breadcrumb_html += '</div>'
        st.markdown(breadcrumb_html, unsafe_allow_html=True)


def create_main_navigation() -> TwitterNavigation:
    """Create and return the main navigation instance."""
    return TwitterNavigation()

def render_page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a consistent page header."""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #E6F7FF, #F0F9FF); border-radius: 16px;">
        <h1 style="color: #1DA1F2; margin-bottom: 0.5rem;">{icon} {title}</h1>
        {f'<p style="color: #657786; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_quick_actions(actions: List[Dict]):
    """Render quick action buttons."""
    st.markdown("### ⚡ Quick Actions")
    
    cols = st.columns(len(actions))
    
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(
                f"{action.get('icon', '')} {action.get('label', '')}",
                key=f"quick_action_{i}",
                use_container_width=True,
                help=action.get('help', '')
            ):
                if action.get('callback'):
                    action['callback']()

# Default menu items for Twitter dashboard
DEFAULT_MENU_ITEMS = [
    {
        'key': 'dashboard',
        'label': 'Dashboard',
        'icon': '🏠',
        'help': 'Main dashboard overview'
    },
    {
        'key': 'generator',
        'label': 'Tweet Generator',
        'icon': '✨',
        'help': 'AI-powered tweet generation'
    },
    {
        'key': 'analytics',
        'label': 'Analytics',
        'icon': '📊',
        'help': 'Tweet performance analytics'
    },
    {
        'key': 'scheduler',
        'label': 'Scheduler',
        'icon': '📅',
        'help': 'Schedule tweets for later'
    },
    {
        'key': 'settings',
        'label': 'Settings',
        'icon': '⚙️',
        'help': 'Twitter account and API settings'
    }
]

DEFAULT_QUICK_ACTIONS = [
    {
        'key': 'new_tweet',
        'label': 'New Tweet',
        'icon': '✍️',
        'help': 'Create a new tweet'
    },
    {
        'key': 'ai_generate',
        'label': 'AI Generate',
        'icon': '🤖',
        'help': 'Generate tweets with AI'
    },
    {
        'key': 'view_analytics',
        'label': 'View Analytics',
        'icon': '📈',
        'help': 'Check tweet performance'
    }
] 