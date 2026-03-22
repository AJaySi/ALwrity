import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🔍 APP Copywriting Generator</h2>
        <p>Create compelling marketing copy using the proven APP (Agree-Promise-Preview) formula.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about APP copywriting
    with st.expander("📚 What is APP Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the APP Copywriting Formula
        
        The APP formula is a powerful copywriting framework that creates a natural connection with your audience:
        
        - **Agree**: Acknowledge a shared problem or pain point your audience faces
        - **Promise**: Make a compelling promise or offer a solution to that problem
        - **Preview**: Provide a preview of how your solution will deliver on that promise
        
        ### Why APP Copywriting Works
        
        The APP formula works because it:
        
        - Creates immediate rapport by showing you understand your audience's challenges
        - Builds trust by acknowledging problems before selling solutions
        - Reduces resistance by connecting on a human level first
        - Demonstrates empathy and understanding
        - Follows a natural conversation flow that feels authentic
        
        ### When to Use APP Copywriting
        
        The APP formula is particularly effective for:
        
        - Building trust with new audiences
        - Introducing new products or services
        - Addressing common objections
        - Creating relatable content
        - Establishing your brand as a solution provider
        - Email marketing sequences
        """)
    
    # Main input form
    with st.expander("✍️ Create Your APP Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                      placeholder="e.g., Alwrity",
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Tech professionals",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            agree = st.text_area('**🤝 Agree (Shared Problem)**', 
                               placeholder="We all face..., Like you, I've..., Safety, Unprofessionalism..",
                               help="Connect with the audience by acknowledging a shared problem or pain point they face.")
            
        with col2:
            description = st.text_input('**📝 Brand Description** (In 2-3 words)', 
                                      placeholder="e.g., AI writing tools",
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., 10x faster content creation",
                                               help="What makes your product/service different from competitors?")
            
            promise = st.text_area('**✨ Promise (Solution)**', 
                                 placeholder="We guarantee..., Our solution ensures..., You'll never have to worry about...",
                                 help="Make a compelling promise or offer a solution to the problem.")
        
        preview = st.text_area('**🔮 Preview (Proof)**', 
                              placeholder="Here's how..., Our customers have experienced..., You'll see results like...",
                              help="Provide a preview of how your solution will deliver on the promise.")
        
        tone_style = st.selectbox(
            '**🎭 Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**🚀 Generate APP Copy**', type="primary"):
            if not brand_name or not description or not agree or not promise or not preview:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, Agree, Promise, and Preview)!")
            else:
                with st.spinner("✨ Crafting compelling APP copy..."):
                    app_copy = generate_app_copy(
                        brand_name, 
                        description, 
                        agree,
                        target_audience,
                        unique_selling_point,
                        promise,
                        preview,
                        tone_style
                    )
                    
                    if app_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>✨ Your APP Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(app_copy)
                        
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
                            <h3 style='color: #333;'>💡 Tips for Using Your APP Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        ### How to Use Your APP Copy Effectively
                        
                        1. **Test different versions**: A/B test your copy to see which version resonates most with your audience
                        
                        2. **Pair with visuals**: Combine your copy with images that reinforce each stage of the APP formula
                        
                        3. **Consider the platform**: Adapt your copy based on where it will appear (social media, email, website, etc.)
                        
                        4. **Measure results**: Track engagement metrics to see how your APP copy performs
                        
                        5. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                        """)
                    else:
                        st.error("💥 **Failed to generate APP Copy. Please try again!**")


def generate_app_copy(brand_name, description, agree, target_audience, unique_selling_point, 
                     promise, preview, tone_style):
    system_prompt = """You are an expert copywriter specializing in the APP (Agree-Promise-Preview) formula. 
    Your expertise is in creating compelling, persuasive marketing copy that builds rapport with audiences by 
    acknowledging their problems, making promises, and providing previews of solutions. Your copy is authentic, 
    specific to the brand, and focused on the target audience's needs."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    TONE & STYLE: {tone_style}
    
    Use the APP formula with these elements:
    - **Agree**: {agree}
    - **Promise**: {promise}
    - **Preview**: {preview}

    For each campaign:
    1. Create a compelling headline that captures attention
    2. Write 2-3 paragraphs that follow the APP formula
    3. End with a strong call to action
    4. Explain how each element of the APP formula is used in the copy

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None