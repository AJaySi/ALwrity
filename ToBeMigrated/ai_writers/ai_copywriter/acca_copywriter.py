import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🚀 ACCA Copywriting Generator</h2>
        <p>Create persuasive marketing copy using the proven ACCA (Awareness-Curiosity-Conviction-Action) formula.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about ACCA copywriting
    with st.expander("📚 What is ACCA Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the ACCA Copywriting Formula
        
        The ACCA formula is a powerful copywriting framework that guides your audience through a journey from problem recognition to action:
        
        - **Awareness**: Highlight the problem or pain point your audience faces
        - **Curiosity**: Agitate the problem by emphasizing its negative impact
        - **Conviction**: Present your solution and build confidence in it
        - **Action**: Provide a clear, compelling call to action
        
        ### Why ACCA Copywriting Works
        
        The ACCA formula works because it:
        
        - Follows the natural decision-making process of your audience
        - Creates a logical progression from problem to solution
        - Builds emotional investment before asking for commitment
        - Addresses objections before they arise
        - Ends with a clear next step
        
        ### When to Use ACCA Copywriting
        
        The ACCA formula is particularly effective for:
        
        - Product launches
        - Service promotions
        - Problem-solving offers
        - Educational content
        - Sales pages
        - Email marketing sequences
        """)
    
    # Main input form
    with st.expander("✍️ Create Your ACCA Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                      placeholder="e.g., Alwrity",
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Tech professionals",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            awareness = st.text_input('❓ **Awareness (Problem)**', 
                                    placeholder="e.g., Struggling to manage finances",
                                    help="What problem or pain point does your audience face?")
            
        with col2:
            description = st.text_input('**📝 Brand Description** (In 5-6 words)', 
                                      placeholder="e.g., AI writing tools",
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., 10x faster content creation",
                                               help="What makes your product/service different from competitors?")
            
            curiosity = st.text_input('🔥 **Curiosity (Agitation)**', 
                                    placeholder="e.g., Leads to financial instability and stress",
                                    help="Why is this problem serious for your audience? Highlight the negative impact.")
        
        conviction = st.text_input('💡 **Conviction (Solution)**', 
                                 placeholder="e.g., Provides easy-to-use budgeting tools with AI insights",
                                 help="How does your product/service solve this problem? Explain the benefits.")
        
        call_to_action = st.text_input('🎯 **Action (Call to Action)**', 
                                      placeholder="e.g., Start your free trial today",
                                      help="What specific action do you want your audience to take?")
        
        tone_style = st.selectbox(
            '**🎭 Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**🚀 Generate ACCA Copy**', type="primary"):
            if not brand_name or not description or not awareness or not curiosity or not conviction:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, Awareness, Curiosity, and Conviction)!")
            else:
                with st.spinner("✨ Crafting persuasive ACCA copy..."):
                    acca_copy = generate_acca_copy(
                        brand_name, 
                        description, 
                        awareness,
                        curiosity,
                        conviction,
                        target_audience,
                        unique_selling_point,
                        call_to_action,
                        tone_style
                    )
                    
                    if acca_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>✨ Your ACCA Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(acca_copy)
                        
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
                            <h3 style='color: #333;'>💡 Tips for Using Your ACCA Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        ### How to Use Your ACCA Copy Effectively
                        
                        1. **Test different versions**: A/B test your copy to see which version resonates most with your audience
                        
                        2. **Pair with visuals**: Combine your copy with images that reinforce each stage of the ACCA formula
                        
                        3. **Consider the platform**: Adapt your copy based on where it will appear (social media, email, website, etc.)
                        
                        4. **Measure results**: Track conversion metrics to see how your ACCA copy performs
                        
                        5. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                        """)
                    else:
                        st.error("💥 **Failed to generate ACCA Copy. Please try again!**")


def generate_acca_copy(brand_name, description, awareness, curiosity, conviction, target_audience, 
                      unique_selling_point, call_to_action, tone_style):
    system_prompt = """You are an expert copywriter specializing in the ACCA (Awareness-Curiosity-Conviction-Action) formula. 
    Your expertise is in creating compelling, persuasive marketing copy that guides audiences through a journey from problem 
    recognition to taking action. Your copy is authentic, specific to the brand, and focused on the target audience's needs."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    TONE & STYLE: {tone_style}
    
    Use the ACCA formula with these elements:
    - **Awareness**: {awareness}
    - **Curiosity**: {curiosity}
    - **Conviction**: {conviction}
    - **Action**: {call_to_action}

    For each campaign:
    1. Create a compelling headline that captures attention
    2. Write 2-3 paragraphs that follow the ACCA formula
    3. End with a strong call to action
    4. Explain how each element of the ACCA formula is used in the copy

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None