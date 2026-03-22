import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from tenacity import retry, wait_random_exponential, stop_after_attempt

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🎯 4C Copywriting Generator</h2>
        <p>Create compelling copy that follows the 4C (Clear, Concise, Credible, Compelling) framework to drive conversions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about 4C copywriting
    with st.expander("📚 What is 4C Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the 4C Copywriting Framework
        
        The 4C framework is a powerful copywriting approach that ensures your message is effective and persuasive:
        
        - **Clear**: Your message is easy to understand, with no ambiguity or confusion
        - **Concise**: Your copy is brief and to the point, without unnecessary words
        - **Credible**: Your claims are backed by evidence, testimonials, or authority
        - **Compelling**: Your message is interesting and persuasive, motivating action
        
        ### Why 4C Copywriting Works
        
        The 4C framework works because it:
        
        - Improves readability and comprehension
        - Respects the reader's time and attention
        - Builds trust and credibility
        - Increases the likelihood of conversion
        - Creates a professional, polished impression
        - Works across all marketing channels and platforms
        
        ### When to Use 4C Copywriting
        
        The 4C framework is particularly effective for:
        
        - Email marketing campaigns
        - Landing pages and sales pages
        - Social media posts and ads
        - Product descriptions
        - Service offerings
        - Any marketing content where clarity and persuasion are essential
        """)
    
    # Main input form
    with st.expander("✍️ Create Your 4C Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                     placeholder="e.g., Alwrity AI Writer",
                                     help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Content marketers",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            campaign_description = st.text_input('**📝 Campaign Description** (In 3-4 words)', 
                                               placeholder="e.g., AI writing assistant",
                                               help="Describe your campaign briefly.")
            
            clear_message = st.text_area('**🔍 Clear Message**', 
                                       placeholder="e.g., Our AI writing assistant helps you create high-quality content in minutes",
                                       help="What is the main message you want to convey? Make it easy to understand.")
            
        with col2:
            brand_description = st.text_input('**📋 Brand Description** (In 2-3 words)', 
                                            placeholder="e.g., AI writing platform",
                                            help="Describe what your company does briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., All-in-one AI copywriting platform",
                                               help="What makes your product/service different from competitors?")
            
            concise_content = st.text_area('**📏 Concise Content**', 
                                         placeholder="e.g., Create content 10x faster with our AI assistant",
                                         help="How can you express your message in the fewest words possible?")
            
            credible_elements = st.text_area('**✅ Credible Elements**', 
                                           placeholder="e.g., Trusted by 10,000+ businesses, 4.8/5 star rating, 30-day money-back guarantee",
                                           help="What evidence, testimonials, or authority can you use to build credibility?")
            
            compelling_hook = st.text_area('**🎣 Compelling Hook**', 
                                         placeholder="e.g., Stop struggling with writer's block. Our AI assistant helps you create engaging content in minutes.",
                                         help="What will grab attention and motivate action?")
            
            call_to_action = st.text_area('**🚀 Call to Action**', 
                                        placeholder="e.g., Start creating high-converting content today with our 14-day free trial...",
                                        help="Prompt your audience to take action with a strong call to action.")
            
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
        
        if st.button('**🚀 Generate 4C Copy**', type="primary"):
            if not brand_name or not brand_description or not campaign_description or not clear_message or not concise_content or not credible_elements or not compelling_hook:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, Campaign Description, Clear Message, Concise Content, Credible Elements, and Compelling Hook)!")
            else:
                with st.spinner("✨ Crafting compelling 4C copy..."):
                    four_cs_copy = generate_four_cs_copy(
                        brand_name, 
                        brand_description, 
                        campaign_description,
                        clear_message,
                        concise_content,
                        credible_elements,
                        compelling_hook,
                        target_audience,
                        unique_selling_point,
                        call_to_action,
                        landing_page_url,
                        platform,
                        language,
                        tone_style
                    )
                    
                    if four_cs_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>🎯 Your 4C Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(four_cs_copy)
                        
                        # Add copy button
                        st.markdown("""
                        <div style='margin-top: 20px;'>
                            <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                                Copy to Clipboard
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add tips for using the copy
                        with st.expander("💡 Tips for Using Your 4C Copy", expanded=False):
                            st.markdown("""
                            ### How to Use Your 4C Copy Effectively
                            
                            1. **Test for clarity**: Ask someone unfamiliar with your product to read your copy and explain what they understand
                            
                            2. **Edit ruthlessly**: Review your copy to eliminate unnecessary words and phrases
                            
                            3. **Add specific details**: Include concrete numbers, statistics, and examples to enhance credibility
                            
                            4. **Create urgency**: Add time-sensitive elements to make your compelling hook even more effective
                            
                            5. **Consider the context**: Adapt the copy based on where it will appear (landing page, email, social media, etc.)
                            
                            6. **Measure results**: Track conversion metrics to see how your 4C copy performs
                            
                            7. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                            """)
                    else:
                        st.error("💥 **Failed to generate 4C Copy. Please try again!**")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_four_cs_copy(brand_name, brand_description, campaign_description, clear_message, 
                         concise_content, credible_elements, compelling_hook, target_audience, 
                         unique_selling_point, call_to_action, landing_page_url, platform, 
                         language, tone_style):
    system_prompt = """You are an expert copywriter specializing in the 4C (Clear, Concise, Credible, Compelling) framework. 
    Your expertise is in creating effective, persuasive marketing copy that communicates clearly, builds credibility, and drives action. 
    Your copy is authentic, specific to the brand, and focused on driving measurable results."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {brand_description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    PLATFORM: {platform}
    LANGUAGE: {language}
    TONE & STYLE: {tone_style}
    
    Use the 4C framework with these elements:
    - **Clear Message**: {clear_message}
    - **Concise Content**: {concise_content}
    - **Credible Elements**: {credible_elements}
    - **Compelling Hook**: {compelling_hook}
    - **Call to Action**: {call_to_action}
    """
    
    if landing_page_url:
        prompt += f"\nInclude the landing page URL ({landing_page_url}) in your call to action."
    
    prompt += """
    For each campaign:
    1. Start with a compelling hook that grabs attention
    2. Present your clear message in a concise way
    3. Support your claims with credible elements
    4. End with a strong call to action

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None