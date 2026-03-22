import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from tenacity import retry, wait_random_exponential, stop_after_attempt

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🎯 FAB Copywriting Generator</h2>
        <p>Create compelling copy that follows the FAB (Features-Advantages-Benefits) framework to drive conversions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about FAB copywriting
    with st.expander("📚 What is FAB Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the FAB Copywriting Framework
        
        FAB is an acronym for Features-Advantages-Benefits. It's a powerful copywriting framework that focuses on translating product features into customer benefits:
        
        - **Features**: The specific characteristics, attributes, or capabilities of your product or service
        - **Advantages**: How these features compare to or outperform competitors
        - **Benefits**: The positive outcomes or results that customers will experience when using your product or service
        
        ### Why FAB Copywriting Works
        
        The FAB framework works because it:
        
        - Focuses on customer value rather than just product specifications
        - Translates technical features into meaningful benefits
        - Addresses the "what's in it for me" question that customers ask
        - Creates a clear connection between product capabilities and customer outcomes
        - Helps customers understand why they should choose your product over alternatives
        
        ### When to Use FAB Copywriting
        
        The FAB framework is particularly effective for:
        
        - Product descriptions and specifications
        - Technical products with complex features
        - Comparison marketing
        - B2B marketing where features matter
        - Content that needs to explain product capabilities
        - Marketing materials that need to address feature-based objections
        """)
    
    # Main input form
    with st.expander("✍️ Create Your FAB Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            product_name = st.text_input('**🏢 Product/Service Name**', 
                                       placeholder="e.g., Alwrity AI Writer",
                                       help="Enter the name of your product or service.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Content marketers",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            features = st.text_area('**🔧 Features**', 
                                  placeholder="e.g., AI-powered content generation, Multiple copywriting frameworks, SEO optimization",
                                  help="List the specific characteristics, attributes, or capabilities of your product or service.")
            
            advantages = st.text_area('**💪 Advantages**', 
                                    placeholder="e.g., 10x faster than manual writing, Supports 12+ copywriting frameworks, Built-in SEO analysis",
                                    help="How do these features compare to or outperform competitors?")
            
        with col2:
            product_description = st.text_input('**📝 Product Description** (In 5-6 words)', 
                                              placeholder="e.g., AI writing assistant",
                                              help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., All-in-one AI copywriting platform",
                                               help="What makes your product/service different from competitors?")
            
            benefits = st.text_area('**✨ Benefits**', 
                                  placeholder="e.g., Save 20+ hours per week on content creation, Increase conversion rates by 35%, Improve SEO rankings",
                                  help="What positive outcomes or results will customers experience when using your product or service?")
            
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
        
        if st.button('**🚀 Generate FAB Copy**', type="primary"):
            if not product_name or not product_description or not features or not advantages or not benefits:
                st.error("⚠️ Please fill in all required fields (Product Name, Description, Features, Advantages, and Benefits)!")
            else:
                with st.spinner("✨ Crafting compelling FAB copy..."):
                    fab_copy = generate_fab_copy(
                        product_name, 
                        product_description, 
                        features,
                        advantages,
                        benefits,
                        target_audience,
                        unique_selling_point,
                        call_to_action,
                        landing_page_url,
                        platform,
                        language,
                        tone_style
                    )
                    
                    if fab_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>🎯 Your FAB Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(fab_copy)
                        
                        # Add copy button
                        st.markdown("""
                        <div style='margin-top: 20px;'>
                            <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                                Copy to Clipboard
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add tips for using the copy
                        with st.expander("💡 Tips for Using Your FAB Copy", expanded=False):
                            st.markdown("""
                            ### How to Use Your FAB Copy Effectively
                            
                            1. **Follow the sequence**: The FAB framework creates a natural progression - make sure your copy maintains this flow
                            
                            2. **Balance features and benefits**: While benefits are most important, don't neglect features for technical audiences
                            
                            3. **Be specific**: Use concrete numbers, statistics, and examples to make your advantages and benefits more compelling
                            
                            4. **Pair with visuals**: Combine your copy with images that showcase your product features and the resulting benefits
                            
                            5. **Consider the context**: Adapt the copy based on where it will appear (landing page, email, social media, etc.)
                            
                            6. **Measure results**: Track conversion metrics to see how your FAB copy performs
                            
                            7. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                            """)
                    else:
                        st.error("💥 **Failed to generate FAB Copy. Please try again!**")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_fab_copy(product_name, product_description, features, advantages, benefits, 
                     target_audience, unique_selling_point, call_to_action, 
                     landing_page_url, platform, language, tone_style):
    system_prompt = """You are an expert copywriter specializing in the FAB (Features-Advantages-Benefits) framework. 
    Your expertise is in creating compelling, conversion-focused marketing copy that translates product features into meaningful customer benefits. 
    Your copy is authentic, specific to the brand, and focused on driving measurable results."""
    
    prompt = f"""Create 3 different marketing campaigns for {product_name}, which is a {product_description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    PLATFORM: {platform}
    LANGUAGE: {language}
    TONE & STYLE: {tone_style}
    
    Use the FAB framework with these elements:
    - **Features**: {features}
    - **Advantages**: {advantages}
    - **Benefits**: {benefits}
    - **Call to Action**: {call_to_action}
    """
    
    if landing_page_url:
        prompt += f"\nInclude the landing page URL ({landing_page_url}) in your call to action."
    
    prompt += """
    For each campaign:
    1. Start by highlighting the key features of the product or service
    2. Explain the advantages these features provide compared to alternatives
    3. Connect these advantages to specific benefits that customers will experience
    4. End with a strong call to action

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None