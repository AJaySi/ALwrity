import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from tenacity import retry, wait_random_exponential, stop_after_attempt

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🎯 4R Copywriting Generator</h2>
        <p>Create compelling copy that follows the 4R (Relevance, Resonance, Response, Results) framework to drive conversions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about 4R copywriting
    with st.expander("📚 What is 4R Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the 4R Copywriting Framework
        
        The 4R framework is a powerful copywriting approach that ensures your message connects with your audience and drives action:
        
        - **Relevance**: Your message addresses the specific needs, interests, or pain points of your target audience
        - **Resonance**: Your copy creates an emotional connection with the audience, making them feel understood
        - **Response**: Your message prompts the audience to take a specific action
        - **Results**: Your copy clearly communicates the positive outcomes or benefits the audience will experience
        
        ### Why 4R Copywriting Works
        
        The 4R framework works because it:
        
        - Ensures your message is targeted to the right audience
        - Creates emotional connections that build trust and loyalty
        - Drives specific actions that lead to conversions
        - Focuses on the outcomes that matter most to your audience
        - Creates a complete journey from awareness to action
        - Works across all marketing channels and platforms
        
        ### When to Use 4R Copywriting
        
        The 4R framework is particularly effective for:
        
        - Email marketing campaigns
        - Landing pages and sales pages
        - Social media posts and ads
        - Product descriptions
        - Service offerings
        - Any marketing content where audience connection and action are essential
        """)
    
    # Main input form
    with st.expander("✍️ Create Your 4R Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                     placeholder="e.g., Alwrity AI Writer",
                                     help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Content marketers",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            relevance = st.text_area('**🎯 Relevance**', 
                                   placeholder="e.g., Struggling with writer's block? Our AI assistant helps you create high-quality content in minutes",
                                   help="How does your product/service address the specific needs or pain points of your target audience?")
            
        with col2:
            brand_description = st.text_input('**📋 Brand Description** (In 2-3 words)', 
                                            placeholder="e.g., AI writing platform",
                                            help="Describe what your company does briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., All-in-one AI copywriting platform",
                                               help="What makes your product/service different from competitors?")
            
            resonance = st.text_area('**💖 Resonance**', 
                                   placeholder="e.g., We understand the frustration of staring at a blank page. Our AI assistant feels like having a professional writer by your side",
                                   help="How can you create an emotional connection with your audience? What language or imagery will resonate with them?")
            
            response = st.text_area('**🚀 Response**', 
                                  placeholder="e.g., Start creating high-converting content today with our 14-day free trial",
                                  help="What specific action do you want your audience to take?")
            
            results = st.text_area('**✨ Results**', 
                                 placeholder="e.g., Save 20+ hours per week on content creation, increase conversion rates by 35%, improve SEO rankings",
                                 help="What positive outcomes or benefits will your audience experience?")
            
            landing_page_url = st.text_input('**🌐 Landing Page URL** (Optional)', 
                                           placeholder="e.g., https://alwrity.com",
                                           help="Provide a URL to include in your call to action.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            platform = st.selectbox(
                '**📱 Content Platform**',
                options=['Social media copy', 'Email copy', 'Website copy', 'Ad copy', 'Product copy'],
                help="Select the platform where your copy will be used."
            )
            
        with col2:
            language = st.selectbox(
                '**🌍 Language**',
                options=['English', 'Hindustani', 'Chinese', 'Hindi', 'Spanish'],
                help="Select the language for your copy."
            )
            
        tone_style = st.selectbox(
            '**🎭 Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**🚀 Generate 4R Copy**', type="primary"):
            if not brand_name or not brand_description or not relevance or not resonance or not response or not results:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, Relevance, Resonance, Response, and Results)!")
            else:
                with st.spinner("✨ Crafting compelling 4R copy..."):
                    four_r_copy = generate_four_r_copy(
                        brand_name, 
                        brand_description, 
                        relevance,
                        resonance,
                        response,
                        results,
                        target_audience,
                        unique_selling_point,
                        landing_page_url,
                        platform,
                        language,
                        tone_style
                    )
                    
                    if four_r_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>🎯 Your 4R Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(four_r_copy)
                        
                        # Add copy button
                        st.markdown("""
                        <div style='margin-top: 20px;'>
                            <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                                Copy to Clipboard
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add tips for using the copy
                        with st.expander("💡 Tips for Using Your 4R Copy", expanded=False):
                            st.markdown("""
                            ### How to Use Your 4R Copy Effectively
                            
                            1. **Test for relevance**: Ensure your copy speaks directly to your target audience's needs and interests
                            
                            2. **Enhance emotional resonance**: Use language and imagery that creates a deeper connection with your audience
                            
                            3. **Clarify the response**: Make sure your call to action is clear, specific, and compelling
                            
                            4. **Quantify results**: Use specific numbers, statistics, and examples to make your results more tangible
                            
                            5. **Consider the context**: Adapt the copy based on where it will appear (landing page, email, social media, etc.)
                            
                            6. **Measure performance**: Track conversion metrics to see how your 4R copy performs
                            
                            7. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                            """)
                    else:
                        st.error("💥 **Failed to generate 4R Copy. Please try again!**")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_four_r_copy(brand_name, brand_description, relevance, resonance, response, results, 
                        target_audience, unique_selling_point, landing_page_url, platform, 
                        language, tone_style):
    system_prompt = """You are an expert copywriter specializing in the 4R (Relevance, Resonance, Response, Results) framework. 
    Your expertise is in creating compelling marketing copy that connects with audiences on a deep level and drives specific actions. 
    Your copy is authentic, specific to the brand, and focused on driving measurable results."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {brand_description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    PLATFORM: {platform}
    LANGUAGE: {language}
    TONE & STYLE: {tone_style}
    
    Use the 4R framework with these elements:
    - **Relevance**: {relevance}
    - **Resonance**: {resonance}
    - **Response**: {response}
    - **Results**: {results}
    """
    
    if landing_page_url:
        prompt += f"\nInclude the landing page URL ({landing_page_url}) in your call to action."
    
    prompt += """
    For each campaign:
    1. Start by establishing relevance to your target audience's needs or pain points
    2. Create emotional resonance by connecting with your audience's feelings and experiences
    3. Clearly communicate the specific action you want your audience to take
    4. End by highlighting the positive results or benefits they will experience

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None 