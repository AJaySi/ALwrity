import streamlit as st
import importlib
import sys
import os
from pathlib import Path
import time
import json
from typing import Dict, List, Callable, Optional, Tuple

# Add the parent directory to the path to allow importing from lib
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent.parent
sys.path.append(str(root_dir))

# Dictionary to store the input section functions
input_sections = {}

# List of copywriter modules to import
copywriter_modules = [
    "ai_emotional_copywriter",
    "acca_copywriter",
    "app_copywriter",
    "star_copywriter",
    "oath_copywriter",
    "quest_copywriter",
    "aidppc_copywriter",
    "aida_copywriter",
    "pas_copywriter",
    "fab_copywriter",
    "4c_copywriter",
    "4r_copywriter"
]

# Define formula categories for better organization
formula_categories = {
    "Emotional Appeal": ["ai_emotional_copywriter", "oath_copywriter"],
    "Structured Framework": ["acca_copywriter", "app_copywriter", "star_copywriter", "quest_copywriter"],
    "Sales Funnel": ["aidppc_copywriter", "aida_copywriter"],
    "Problem-Solution": ["pas_copywriter"],
    "Feature-Benefit": ["fab_copywriter"],
    "Messaging Framework": ["4c_copywriter", "4r_copywriter"]
}

# Define formula metadata for better display and filtering
formula_metadata = {
    "ai_emotional_copywriter": {
        "name": "Emotional Copywriter",
        "icon": "🎭",
        "description": "Create copy that resonates with your audience's emotions and drives action.",
        "color": "#FF6B6B",
        "difficulty": "Intermediate",
        "best_for": ["Landing Pages", "Email", "Social Media"],
        "tags": ["emotional", "persuasive", "engagement"]
    },
    "acca_copywriter": {
        "name": "ACCA Copywriter",
        "icon": "🎯",
        "description": "Use the ACCA (Attention, Context, Content, Action) framework to create compelling copy.",
        "color": "#4ECDC4",
        "difficulty": "Beginner",
        "best_for": ["Ads", "Email", "Landing Pages"],
        "tags": ["structured", "conversion", "clear"]
    },
    "app_copywriter": {
        "name": "APP Copywriter",
        "icon": "🤝",
        "description": "Implement the APP (Agree, Promise, Preview) formula to create persuasive copy.",
        "color": "#45B7D1",
        "difficulty": "Beginner",
        "best_for": ["Blog Posts", "Sales Pages", "Email"],
        "tags": ["persuasive", "agreement", "preview"]
    },
    "star_copywriter": {
        "name": "STAR Copywriter",
        "icon": "⭐",
        "description": "Use the STAR (Situation, Task, Action, Result) framework to tell compelling stories.",
        "color": "#FFD166",
        "difficulty": "Intermediate",
        "best_for": ["Case Studies", "Testimonials", "About Pages"],
        "tags": ["storytelling", "results", "case-study"]
    },
    "oath_copywriter": {
        "name": "OATH Copywriter",
        "icon": "📜",
        "description": "Apply the OATH (Oblivious, Apathetic, Thinking, Hurting) framework to target specific audience mindsets.",
        "color": "#06D6A0",
        "difficulty": "Advanced",
        "best_for": ["Ads", "Landing Pages", "Email Sequences"],
        "tags": ["audience", "mindset", "targeting"]
    },
    "quest_copywriter": {
        "name": "QUEST Copywriter",
        "icon": "🔍",
        "description": "Use the QUEST (Question, Unpack, Emphasize, Solution, Transform) framework for narrative-driven copy.",
        "color": "#118AB2",
        "difficulty": "Intermediate",
        "best_for": ["Long-form Content", "Sales Pages", "Video Scripts"],
        "tags": ["narrative", "transformation", "solution"]
    },
    "aidppc_copywriter": {
        "name": "AIDPPC Copywriter",
        "icon": "💰",
        "description": "Implement the AIDPPC (Attention, Interest, Desire, Proof, Persuasion, Call to Action) framework for PPC ads.",
        "color": "#073B4C",
        "difficulty": "Advanced",
        "best_for": ["PPC Ads", "Social Ads", "Display Ads"],
        "tags": ["advertising", "ppc", "conversion"]
    },
    "aida_copywriter": {
        "name": "AIDA Copywriter",
        "icon": "🎬",
        "description": "Use the AIDA (Attention, Interest, Desire, Action) framework to guide customers through the sales funnel.",
        "color": "#EF476F",
        "difficulty": "Beginner",
        "best_for": ["Sales Pages", "Email", "Product Descriptions"],
        "tags": ["sales", "funnel", "conversion"]
    },
    "pas_copywriter": {
        "name": "PAS Copywriter",
        "icon": "🔧",
        "description": "Apply the PAS (Problem, Agitate, Solution) formula to address pain points and offer solutions.",
        "color": "#7209B7",
        "difficulty": "Beginner",
        "best_for": ["Ads", "Email", "Landing Pages"],
        "tags": ["problem-solving", "pain-points", "solutions"]
    },
    "fab_copywriter": {
        "name": "FAB Copywriter",
        "icon": "💎",
        "description": "Use the FAB (Features, Advantages, Benefits) framework to highlight product value.",
        "color": "#3A0CA3",
        "difficulty": "Beginner",
        "best_for": ["Product Descriptions", "Sales Pages", "Brochures"],
        "tags": ["product", "features", "benefits"]
    },
    "4c_copywriter": {
        "name": "4C Copywriter",
        "icon": "📝",
        "description": "Implement the 4C (Clear, Concise, Credible, Compelling) framework for effective messaging.",
        "color": "#4361EE",
        "difficulty": "Intermediate",
        "best_for": ["Brand Messaging", "Mission Statements", "Value Propositions"],
        "tags": ["clarity", "concise", "credibility"]
    },
    "4r_copywriter": {
        "name": "4R Copywriter",
        "icon": "🔄",
        "description": "Use the 4R (Relevance, Resonance, Response, Results) framework to connect with your audience.",
        "color": "#F72585",
        "difficulty": "Intermediate",
        "best_for": ["Content Marketing", "Email", "Social Media"],
        "tags": ["relevance", "resonance", "results"]
    }
}

def load_user_preferences() -> Dict:
    """Load user preferences from session state or initialize if not present."""
    if "copywriter_preferences" not in st.session_state:
        st.session_state.copywriter_preferences = {
            "recent_formulas": [],
            "favorite_formulas": [],
            "comparison_formulas": [],
            "view_mode": "grid"  # or "list"
        }
    return st.session_state.copywriter_preferences

def save_user_preferences(preferences: Dict) -> None:
    """Save user preferences to session state."""
    st.session_state.copywriter_preferences = preferences

def add_recent_formula(module_name: str) -> None:
    """Add a formula to the recent formulas list."""
    preferences = load_user_preferences()
    
    # Remove if already exists
    if module_name in preferences["recent_formulas"]:
        preferences["recent_formulas"].remove(module_name)
    
    # Add to the beginning of the list
    preferences["recent_formulas"].insert(0, module_name)
    
    # Keep only the 5 most recent
    preferences["recent_formulas"] = preferences["recent_formulas"][:5]
    
    save_user_preferences(preferences)

def toggle_favorite_formula(module_name: str) -> bool:
    """Toggle a formula as favorite and return the new state."""
    preferences = load_user_preferences()
    
    if module_name in preferences["favorite_formulas"]:
        preferences["favorite_formulas"].remove(module_name)
        is_favorite = False
    else:
        preferences["favorite_formulas"].append(module_name)
        is_favorite = True
    
    save_user_preferences(preferences)
    return is_favorite

def is_favorite_formula(module_name: str) -> bool:
    """Check if a formula is in the favorites list."""
    preferences = load_user_preferences()
    return module_name in preferences["favorite_formulas"]

def add_to_comparison(module_name: str) -> None:
    """Add a formula to the comparison list."""
    preferences = load_user_preferences()
    
    if module_name not in preferences["comparison_formulas"]:
        preferences["comparison_formulas"].append(module_name)
        
    # Keep only up to 3 formulas for comparison
    preferences["comparison_formulas"] = preferences["comparison_formulas"][:3]
    
    save_user_preferences(preferences)

def remove_from_comparison(module_name: str) -> None:
    """Remove a formula from the comparison list."""
    preferences = load_user_preferences()
    
    if module_name in preferences["comparison_formulas"]:
        preferences["comparison_formulas"].remove(module_name)
    
    save_user_preferences(preferences)

def clear_comparison() -> None:
    """Clear the comparison list."""
    preferences = load_user_preferences()
    preferences["comparison_formulas"] = []
    save_user_preferences(preferences)

def lazy_load_module(module_name: str) -> Optional[Callable]:
    """Lazily load a module and return its input_section function."""
    if module_name in input_sections:
        return input_sections[module_name]
    
    try:
        module_path = f"lib.ai_writers.ai_copywriter.{module_name}"
        module = importlib.import_module(module_path)
        if hasattr(module, "input_section"):
            input_sections[module_name] = module.input_section
            return module.input_section
        else:
            st.warning(f"Module {module_name} does not have an input_section function.")
            return None
    except Exception as e:
        st.error(f"Error loading module {module_name}: {str(e)}")
        return None

def render_formula_card(module_name: str, index: int, view_mode: str = "grid") -> None:
    """Render a formula card with its details."""
    metadata = formula_metadata.get(module_name, {})
    
    if not metadata:
        return
    
    is_favorite = is_favorite_formula(module_name)
    favorite_icon = "★" if is_favorite else "☆"
    favorite_tooltip = "Remove from favorites" if is_favorite else "Add to favorites"
    
    if view_mode == "grid":
        with st.container():
            st.markdown(f"""
            <div style='background-color: {metadata["color"]}; padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white; position: relative;'>
                <div style='position: absolute; top: 10px; right: 10px; font-size: 1.5em;'>{favorite_icon}</div>
                <h2 style='color: white;'>{metadata["icon"]} {metadata["name"]}</h2>
                <p>{metadata["description"]}</p>
                <div style='margin-top: 10px;'>
                    <span style='background-color: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 10px; margin-right: 5px; font-size: 0.8em;'>
                        {metadata["difficulty"]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Use {metadata['name']}", key=f"use_btn_{index}", use_container_width=True):
                    add_recent_formula(module_name)
                    st.session_state.selected_formula = {
                        "module": module_name,
                        "name": metadata["name"],
                        "icon": metadata["icon"],
                        "function": lazy_load_module(module_name)
                    }
                    st.rerun()
            
            with col2:
                if st.button(f"{favorite_icon} Favorite", key=f"fav_btn_{index}", help=favorite_tooltip, use_container_width=True):
                    toggle_favorite_formula(module_name)
                    st.rerun()
            
            with col3:
                if module_name in load_user_preferences()["comparison_formulas"]:
                    if st.button("Remove from Compare", key=f"comp_btn_{index}", use_container_width=True):
                        remove_from_comparison(module_name)
                        st.rerun()
                else:
                    if st.button("Add to Compare", key=f"comp_btn_{index}", use_container_width=True):
                        add_to_comparison(module_name)
                        st.rerun()
    else:  # list view
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style='padding: 10px; border-left: 5px solid {metadata["color"]}; margin-bottom: 10px;'>
                    <h3>{metadata["icon"]} {metadata["name"]} {favorite_icon}</h3>
                    <p>{metadata["description"]}</p>
                    <div>
                        <span style='background-color: #f0f2f6; padding: 3px 8px; border-radius: 10px; margin-right: 5px; font-size: 0.8em;'>
                            {metadata["difficulty"]}
                        </span>
                        <span style='font-size: 0.8em;'>Best for: {", ".join(metadata["best_for"][:2])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"Use", key=f"use_list_btn_{index}", use_container_width=True):
                    add_recent_formula(module_name)
                    st.session_state.selected_formula = {
                        "module": module_name,
                        "name": metadata["name"],
                        "icon": metadata["icon"],
                        "function": lazy_load_module(module_name)
                    }
                    st.rerun()
                
                if st.button(f"{favorite_icon}", key=f"fav_list_btn_{index}", help=favorite_tooltip):
                    toggle_favorite_formula(module_name)
                    st.rerun()
                
                if module_name in load_user_preferences()["comparison_formulas"]:
                    if st.button("- Compare", key=f"comp_list_btn_{index}"):
                        remove_from_comparison(module_name)
                        st.rerun()
                else:
                    if st.button("+ Compare", key=f"comp_list_btn_{index}"):
                        add_to_comparison(module_name)
                        st.rerun()

def render_formula_comparison() -> None:
    """Render a comparison of selected formulas."""
    preferences = load_user_preferences()
    comparison_formulas = preferences["comparison_formulas"]
    
    if not comparison_formulas:
        st.info("Add formulas to compare them side by side.")
        return
    
    # Create a table for comparison
    comparison_data = []
    for module_name in comparison_formulas:
        metadata = formula_metadata.get(module_name, {})
        if metadata:
            comparison_data.append({
                "Name": f"{metadata['icon']} {metadata['name']}",
                "Description": metadata["description"],
                "Difficulty": metadata["difficulty"],
                "Best For": ", ".join(metadata["best_for"][:3]),
                "Tags": ", ".join(metadata["tags"])
            })
    
    # Display the comparison table
    st.markdown("### Formula Comparison")
    
    # Create columns for each formula
    cols = st.columns(len(comparison_data))
    
    # Display headers
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"#### {comparison_data[i]['Name']}")
    
    # Display description
    st.markdown("##### Description")
    for i, col in enumerate(cols):
        with col:
            st.write(comparison_data[i]["Description"])
    
    # Display difficulty
    st.markdown("##### Difficulty")
    for i, col in enumerate(cols):
        with col:
            st.write(comparison_data[i]["Difficulty"])
    
    # Display best for
    st.markdown("##### Best For")
    for i, col in enumerate(cols):
        with col:
            st.write(comparison_data[i]["Best For"])
    
    # Display tags
    st.markdown("##### Tags")
    for i, col in enumerate(cols):
        with col:
            st.write(comparison_data[i]["Tags"])
    
    # Add buttons to use each formula
    st.markdown("##### Actions")
    for i, col in enumerate(cols):
        with col:
            module_name = comparison_formulas[i]
            if st.button(f"Use {formula_metadata[module_name]['name']}", key=f"use_comp_btn_{i}"):
                add_recent_formula(module_name)
                st.session_state.selected_formula = {
                    "module": module_name,
                    "name": formula_metadata[module_name]["name"],
                    "icon": formula_metadata[module_name]["icon"],
                    "function": lazy_load_module(module_name)
                }
                st.rerun()
    
    # Add a button to clear the comparison
    if st.button("Clear Comparison", key="clear_comparison"):
        clear_comparison()
        st.rerun()

def filter_formulas(formulas: List[str], search_term: str, category: str, difficulty: str) -> List[str]:
    """Filter formulas based on search term, category, and difficulty."""
    filtered_formulas = []
    
    for module_name in formulas:
        metadata = formula_metadata.get(module_name, {})
        if not metadata:
            continue
        
        # Check if the formula matches the search term
        name_match = search_term.lower() in metadata["name"].lower()
        desc_match = search_term.lower() in metadata["description"].lower()
        tags_match = any(search_term.lower() in tag.lower() for tag in metadata.get("tags", []))
        
        # Check if the formula matches the category
        category_match = True
        if category != "All Categories":
            category_match = module_name in formula_categories.get(category, [])
        
        # Check if the formula matches the difficulty
        difficulty_match = True
        if difficulty != "All Difficulties":
            difficulty_match = metadata.get("difficulty", "") == difficulty
        
        # Add the formula if it matches all criteria
        if (name_match or desc_match or tags_match) and category_match and difficulty_match:
            filtered_formulas.append(module_name)
    
    return filtered_formulas

def copywriter_dashboard():
    """
    Main function to display the copywriting dashboard.
    This function can be called from content_generator.py when the user selects "AI Copywriter".
    """
    # Load user preferences
    preferences = load_user_preferences()
    
    # Initialize session state for selected formula if it doesn't exist
    if "selected_formula" not in st.session_state:
        st.session_state.selected_formula = None
    
    # Initialize session state for search and filter options
    if "search_term" not in st.session_state:
        st.session_state.search_term = ""
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = "All Categories"
    if "selected_difficulty" not in st.session_state:
        st.session_state.selected_difficulty = "All Difficulties"
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = preferences["view_mode"]
    
    # Create a container for the formula input section
    formula_container = st.container()
    
    # If a formula is selected, show its input section
    if st.session_state.selected_formula is not None:
        with formula_container:
            # Display the selected formula's input section
            st.markdown("---")
            st.markdown(f"# {st.session_state.selected_formula['icon']} {st.session_state.selected_formula['name']}")
            
            # Add a back button
            if st.button("← Back to Dashboard", key="back_to_dashboard"):
                # Clear the selected formula from session state
                st.session_state.selected_formula = None
                st.rerun()
            
            # Call the input section function for the selected formula
            if st.session_state.selected_formula["function"]:
                st.session_state.selected_formula["function"]()
            else:
                st.error(f"The {st.session_state.selected_formula['name']} module is not available.")
    else:
        # Create a container for the dashboard
        dashboard_container = st.container()
        
        with dashboard_container:
            # Display the dashboard
            # Header
            st.markdown("""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h1 style='color: #1E88E5; text-align: center;'>✍️ AI Copywriting Tools</h1>
                <p style='text-align: center;'>Choose the perfect copywriting formula for your marketing needs</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create tabs for different sections
            tab1, tab2, tab3, tab4 = st.tabs(["All Formulas", "Recent & Favorites", "Compare Formulas", "Help & Guide"])
            
            with tab1:
                # Search and filter options
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    search_term = st.text_input("🔍 Search formulas", value=st.session_state.search_term)
                    if search_term != st.session_state.search_term:
                        st.session_state.search_term = search_term
                
                with col2:
                    categories = ["All Categories"] + list(formula_categories.keys())
                    selected_category = st.selectbox("Category", categories, index=categories.index(st.session_state.selected_category))
                    if selected_category != st.session_state.selected_category:
                        st.session_state.selected_category = selected_category
                
                with col3:
                    difficulties = ["All Difficulties", "Beginner", "Intermediate", "Advanced"]
                    selected_difficulty = st.selectbox("Difficulty", difficulties, index=difficulties.index(st.session_state.selected_difficulty))
                    if selected_difficulty != st.session_state.selected_difficulty:
                        st.session_state.selected_difficulty = selected_difficulty
                
                with col4:
                    view_options = {"Grid": "grid", "List": "list"}
                    view_mode = st.selectbox("View", list(view_options.keys()), index=list(view_options.values()).index(st.session_state.view_mode))
                    st.session_state.view_mode = view_options[view_mode]
                    preferences["view_mode"] = st.session_state.view_mode
                    save_user_preferences(preferences)
                
                # Filter formulas based on search and filter options
                filtered_formulas = filter_formulas(
                    copywriter_modules,
                    st.session_state.search_term,
                    st.session_state.selected_category,
                    st.session_state.selected_difficulty
                )
                
                if not filtered_formulas:
                    st.info("No formulas match your search criteria. Try adjusting your filters.")
                else:
                    # Display the formula cards
                    if st.session_state.view_mode == "grid":
                        # Create a 3-column layout for the formula cards
                        col1, col2, col3 = st.columns(3)
                        
                        # Display the formula cards
                        for i, module_name in enumerate(filtered_formulas):
                            # Determine which column to use
                            col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
                            
                            with col:
                                render_formula_card(module_name, i, st.session_state.view_mode)
                    else:  # list view
                        for i, module_name in enumerate(filtered_formulas):
                            render_formula_card(module_name, i, st.session_state.view_mode)
            
            with tab2:
                # Recent formulas
                st.subheader("Recently Used Formulas")
                recent_formulas = preferences["recent_formulas"]
                
                if not recent_formulas:
                    st.info("You haven't used any formulas yet. Start by selecting a formula from the 'All Formulas' tab.")
                else:
                    # Create a 3-column layout for the recent formula cards
                    col1, col2, col3 = st.columns(3)
                    
                    # Display the recent formula cards
                    for i, module_name in enumerate(recent_formulas):
                        # Determine which column to use
                        col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
                        
                        with col:
                            render_formula_card(module_name, i + 100, "grid")  # Use a different index to avoid key conflicts
                
                # Favorite formulas
                st.subheader("Favorite Formulas")
                favorite_formulas = preferences["favorite_formulas"]
                
                if not favorite_formulas:
                    st.info("You haven't added any formulas to your favorites yet. Click the star icon on a formula card to add it to your favorites.")
                else:
                    # Create a 3-column layout for the favorite formula cards
                    col1, col2, col3 = st.columns(3)
                    
                    # Display the favorite formula cards
                    for i, module_name in enumerate(favorite_formulas):
                        # Determine which column to use
                        col = col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3
                        
                        with col:
                            render_formula_card(module_name, i + 200, "grid")  # Use a different index to avoid key conflicts
            
            with tab3:
                # Formula comparison
                render_formula_comparison()
            
            with tab4:
                # Help and guide
                st.subheader("Copywriting Formula Guide")
                st.write("""
                This dashboard provides access to a variety of copywriting formulas, each designed for specific marketing needs.
                Here's how to make the most of these powerful tools:
                """)
                
                st.markdown("""
                #### How to Use This Dashboard
                
                1. **Browse Formulas**: Explore the available copywriting formulas in the "All Formulas" tab
                2. **Search & Filter**: Use the search box and filters to find the perfect formula for your needs
                3. **Compare Formulas**: Add up to 3 formulas to the comparison tab to see them side by side
                4. **Save Favorites**: Click the star icon to save formulas you use frequently
                5. **Access Recent**: Quickly access your recently used formulas in the "Recent & Favorites" tab
                
                #### Choosing the Right Formula
                
                Different formulas work best for different marketing goals:
                
                - **Emotional Appeal**: Use when you want to connect with your audience on an emotional level
                - **Structured Framework**: Great for organizing complex information in a compelling way
                - **Sales Funnel**: Designed to guide prospects through the buying journey
                - **Problem-Solution**: Effective for highlighting pain points and positioning your solution
                - **Feature-Benefit**: Perfect for product descriptions and technical offerings
                - **Messaging Framework**: Helps create clear, consistent messaging across channels
                
                #### Formula Difficulty Levels
                
                - **Beginner**: Easy to use with minimal copywriting experience
                - **Intermediate**: Requires some understanding of copywriting principles
                - **Advanced**: Most effective when used by experienced copywriters
                """)
                
                # Add a section about how to use the generated copy
                st.subheader("Using Your Generated Copy")
                st.write("""
                After generating copy with your chosen formula:
                
                1. **Review & Edit**: Always review and personalize the generated content
                2. **Test Different Versions**: Try multiple formulas for the same product/service
                3. **A/B Test**: Use different versions in your marketing to see which performs best
                4. **Adapt for Channels**: Modify the copy as needed for different marketing channels
                """)
                
                # Add a feedback section
                st.subheader("Feedback & Suggestions")
                st.write("We're constantly improving our copywriting tools. If you have feedback or suggestions, please let us know!")
                
                feedback = st.text_area("Your feedback", placeholder="Share your thoughts, suggestions, or report any issues...")
                if st.button("Submit Feedback"):
                    if feedback:
                        st.success("Thank you for your feedback! We'll use it to improve our tools.")
                        # In a real implementation, you would save this feedback somewhere
                    else:
                        st.warning("Please enter your feedback before submitting.")

# For standalone execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Copywriting Tools",
        page_icon="✍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    copywriter_dashboard()