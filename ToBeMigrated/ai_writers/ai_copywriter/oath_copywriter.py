import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from tenacity import retry, wait_random_exponential, stop_after_attempt

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>📋 OATH Copywriting Generator</h2>
        <p>Create compelling copy that addresses different audience mindsets using the OATH (Oblivious-Apathetic-Thinking-Hurting) framework.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about OATH copywriting
    with st.expander("📚 What is OATH Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the OATH Copywriting Framework
        
        The OATH framework is a powerful copywriting approach that recognizes different audience mindsets:
        
        - **Oblivious**: People who don't know they have a problem or need
        - **Apathetic**: People who know about the problem but don't care enough to act
        - **Thinking**: People who are actively considering solutions
        - **Hurting**: People who are experiencing pain and urgently need a solution
        
        ### Why OATH Copywriting Works
        
        The OATH framework works because it:
        
        - Addresses the full spectrum of audience awareness
        - Creates targeted messaging for each mindset
        - Increases conversion rates by meeting people where they are
        - Helps you craft the right message for the right audience
        - Allows for more personalized and effective marketing campaigns
        
        ### When to Use OATH Copywriting
        
        The OATH framework is particularly effective for:
        
        - New product launches
        - Educational content
        - Problem-solution marketing
        - Awareness campaigns
        - Multi-channel marketing strategies
        - Content that needs to address different audience segments
        """)
    
    # Main input form
    with st.expander("✍️ Create Your OATH Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                      placeholder="e.g., Alwrity",
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Tech professionals",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            oblivious = st.text_area('**🔍 Oblivious Audience**', 
                                   placeholder="People who don't know they have this problem...",
                                   help="Describe the audience who doesn't know they have a problem or need your solution.")
            
            apathetic = st.text_area('**😐 Apathetic Audience**', 
                                   placeholder="People who know about the problem but don't care enough to act...",
                                   help="Describe the audience who knows about the problem but isn't motivated to solve it.")
            
        with col2:
            description = st.text_input('**📝 Brand Description** (In 2-3 words)', 
                                      placeholder="e.g., AI writing tools",
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., 10x faster content creation",
                                               help="What makes your product/service different from competitors?")
            
            thinking = st.text_area('**🤔 Thinking Audience**', 
                                  placeholder="People who are actively considering solutions...",
                                  help="Describe the audience who is actively researching solutions to their problem.")
            
            hurting = st.text_area('**😫 Hurting Audience**', 
                                 placeholder="People who are experiencing pain and urgently need a solution...",
                                 help="Describe the audience who is experiencing significant pain and urgently needs a solution.")
        
        tone_style = st.selectbox(
            '**🎭 Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**🚀 Generate OATH Copy**', type="primary"):
            if not brand_name or not description or not oblivious or not apathetic or not thinking or not hurting:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, and all audience segments)!")
            else:
                with st.spinner("✨ Crafting compelling OATH copy..."):
                    oath_copy = generate_oath_copy(
                        brand_name, 
                        description, 
                        oblivious,
                        apathetic,
                        thinking,
                        hurting,
                        target_audience,
                        unique_selling_point,
                        tone_style
                    )
                    
                    if oath_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>📋 Your OATH Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(oath_copy)
                        
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
                            <h3 style='color: #333;'>💡 Tips for Using Your OATH Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        ### How to Use Your OATH Copy Effectively
                        
                        1. **Target the right audience**: Use the appropriate OATH segment copy based on your target audience's current mindset
                        
                        2. **Create a journey**: Consider how to move audiences from one mindset to another (e.g., from Oblivious to Thinking)
                        
                        3. **Test different versions**: A/B test your copy to see which OATH segment resonates most with your audience
                        
                        4. **Pair with visuals**: Combine your copy with images that reinforce the message for each audience segment
                        
                        5. **Measure results**: Track engagement metrics to see how your OATH copy performs across different audience segments
                        
                        6. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                        """)
                    else:
                        st.error("💥 **Failed to generate OATH Copy. Please try again!**")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_oath_copy(brand_name, description, oblivious, apathetic, thinking, hurting, 
                      target_audience, unique_selling_point, tone_style):
    system_prompt = """You are an expert copywriter specializing in the OATH (Oblivious-Apathetic-Thinking-Hurting) framework. 
    Your expertise is in creating compelling, targeted marketing copy that addresses different audience mindsets and awareness levels. 
    Your copy is authentic, specific to the brand, and focused on meeting audiences where they are in their journey."""
    
    prompt = f"""Create 4 different marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    TONE & STYLE: {tone_style}
    
    Use the OATH framework with these audience segments:
    - **Oblivious**: {oblivious}
    - **Apathetic**: {apathetic}
    - **Thinking**: {thinking}
    - **Hurting**: {hurting}

    For each campaign:
    1. Create a compelling headline that captures attention
    2. Write 2-3 paragraphs that address the specific audience mindset
    3. End with a strong call to action
    4. Explain how the copy is tailored to that specific audience mindset

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None