import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>⭐ STAR Copywriting Generator</h2>
        <p>Create compelling marketing copy using the proven STAR (Situation-Task-Action-Result) framework.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about STAR copywriting
    with st.expander("📚 What is STAR Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the STAR Copywriting Framework
        
        The STAR framework is a powerful storytelling structure that creates compelling narratives:
        
        - **Situation**: Set the context and background for the problem or need
        - **Task**: Describe the specific challenge or objective that needs to be addressed
        - **Action**: Explain the specific actions taken to address the challenge
        - **Result**: Highlight the positive outcomes and benefits achieved
        
        ### Why STAR Copywriting Works
        
        The STAR framework works because it:
        
        - Creates a complete narrative arc that engages readers
        - Demonstrates problem-solving capabilities
        - Shows concrete results and benefits
        - Builds credibility through specific examples
        - Makes abstract benefits tangible through storytelling
        
        ### When to Use STAR Copywriting
        
        The STAR framework is particularly effective for:
        
        - Case studies and success stories
        - Product or service demonstrations
        - Customer testimonials
        - Company achievements and milestones
        - Problem-solution marketing
        - Portfolio showcases
        """)
    
    # Main input form
    with st.expander("✍️ Create Your STAR Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                      placeholder="e.g., Alwrity",
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Tech professionals",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            situation = st.text_area('**🌍 Situation (Context)**', 
                                   placeholder="In a busy city, Late Delivery, Unsafe Activities, Unprofessional Service..",
                                   help="Describe the background context or problem that needs to be addressed.")
            
            action = st.text_area('**⚡ Action (Solution)**', 
                                placeholder="New strategy, launched campaign, better service, New product...",
                                help="Describe the specific actions taken to address the challenge or objective.")
            
        with col2:
            description = st.text_input('**📝 Brand Description** (In 2-3 words)', 
                                      placeholder="e.g., AI writing tools",
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., 10x faster content creation",
                                               help="What makes your product/service different from competitors?")
            
            task = st.text_area('**🎯 Task (Challenge)**', 
                              placeholder="Increase website traffic by 30%, improve customer satisfaction, Safe Travels...",
                              help="Describe the specific challenge or objective that needs to be addressed.")
            
            result = st.text_area('**✨ Result (Outcome)**', 
                                placeholder="Improved customer engagement, sales revenue, Happy customers, Improved Service X...",
                                help="Highlight the positive outcomes and benefits achieved from the actions taken.")
        
        tone_style = st.selectbox(
            '**🎭 Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**🚀 Generate STAR Copy**', type="primary"):
            if not brand_name or not description or not situation or not task or not action or not result:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, Situation, Task, Action, and Result)!")
            else:
                with st.spinner("✨ Crafting compelling STAR copy..."):
                    star_copy = generate_star_copy(
                        brand_name, 
                        description, 
                        situation,
                        task,
                        action,
                        result,
                        target_audience,
                        unique_selling_point,
                        tone_style
                    )
                    
                    if star_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>⭐ Your STAR Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(star_copy)
                        
                        # Add copy button
                        st.markdown("""
                        <div style='margin-top: 20px;'>
                            <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                                Copy to Clipboard
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add tips for using the copy - using a container instead of an expander
                        st.markdown("""
                        <div style='background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #333;'>💡 Tips for Using Your STAR Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        ### How to Use Your STAR Copy Effectively
                        
                        1. **Test different versions**: A/B test your copy to see which version resonates most with your audience
                        
                        2. **Pair with visuals**: Combine your copy with images that illustrate each stage of the STAR framework
                        
                        3. **Consider the platform**: Adapt your copy based on where it will appear (social media, email, website, etc.)
                        
                        4. **Measure results**: Track engagement metrics to see how your STAR copy performs
                        
                        5. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                        """)
                    else:
                        st.error("💥 **Failed to generate STAR Copy. Please try again!**")


def generate_star_copy(brand_name, description, situation, task, action, result, target_audience, 
                      unique_selling_point, tone_style):
    system_prompt = """You are an expert copywriter specializing in the STAR (Situation-Task-Action-Result) framework. 
    Your expertise is in creating compelling, narrative-driven marketing copy that tells a complete story from problem to solution. 
    Your copy is authentic, specific to the brand, and focused on demonstrating concrete results and benefits."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    TONE & STYLE: {tone_style}
    
    Use the STAR framework with these elements:
    - **Situation**: {situation}
    - **Task**: {task}
    - **Action**: {action}
    - **Result**: {result}

    For each campaign:
    1. Create a compelling headline that captures attention
    2. Write 2-3 paragraphs that follow the STAR framework
    3. End with a strong call to action
    4. Explain how each element of the STAR framework is used in the copy

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None