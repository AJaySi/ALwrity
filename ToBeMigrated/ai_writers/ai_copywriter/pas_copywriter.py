import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from tenacity import retry, wait_random_exponential, stop_after_attempt

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🎯 PAS Copywriting Generator</h2>
        <p>Create compelling copy that follows the PAS (Problem-Agitate-Solution) framework to drive conversions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about PAS copywriting
    with st.expander("📚 What is PAS Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the PAS Copywriting Framework
        
        PAS is an acronym for Problem-Agitate-Solution. It's a powerful copywriting framework that focuses on identifying and solving customer pain points:
        
        - **Problem**: Identifying a specific problem or pain point that your target audience faces
        - **Agitate**: Amplifying the problem by highlighting its negative consequences and emotional impact
        - **Solution**: Presenting your product or service as the ideal solution to the problem
        
        ### Why PAS Copywriting Works
        
        The PAS framework works because it:
        
        - Addresses real customer pain points and needs
        - Creates emotional resonance by highlighting the consequences of inaction
        - Positions your product/service as the hero that solves the problem
        - Follows a natural problem-solving narrative that readers can relate to
        - Focuses on the customer's journey rather than just product features
        
        ### When to Use PAS Copywriting
        
        The PAS framework is particularly effective for:
        
        - Products or services that solve specific problems
        - Marketing to audiences with clear pain points
        - Content that needs to drive specific actions
        - Landing pages and sales pages
        - Email marketing campaigns
        - Direct response advertising
        """)
    
    # Main input form
    with st.expander("✍️ Create Your PAS Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                      placeholder="e.g., Alwrity",
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Tech professionals",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            problem = st.text_area('**❌ Problem**', 
                                 placeholder="e.g., Struggling to create high-quality content that converts",
                                 help="Identify a specific problem or pain point that your target audience faces.")
            
            agitate = st.text_area('**😫 Agitate**', 
                                 placeholder="e.g., Without effective content, you're losing potential customers and revenue every day...",
                                 help="Amplify the problem by highlighting its negative consequences and emotional impact.")
            
        with col2:
            description = st.text_input('**📝 Brand Description** (In 5-6 words)', 
                                      placeholder="e.g., AI writing tools",
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., 10x faster content creation",
                                               help="What makes your product/service different from competitors?")
            
            solution = st.text_area('**✨ Solution**', 
                                  placeholder="e.g., Our AI-powered platform creates high-converting content in minutes...",
                                  help="Present your product or service as the ideal solution to the problem.")
            
            call_to_action = st.text_area('**🚀 Call to Action**', 
                                        placeholder="e.g., Start creating converting content today with our 14-day free trial...",
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
        
        if st.button('**🚀 Generate PAS Copy**', type="primary"):
            if not brand_name or not description or not problem or not agitate or not solution:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, Problem, Agitate, and Solution)!")
            else:
                with st.spinner("✨ Crafting compelling PAS copy..."):
                    pas_copy = generate_pas_copy(
                        brand_name, 
                        description, 
                        problem,
                        agitate,
                        solution,
                        target_audience,
                        unique_selling_point,
                        call_to_action,
                        landing_page_url,
                        platform,
                        language,
                        tone_style
                    )
                    
                    if pas_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>🎯 Your PAS Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(pas_copy)
                        
                        # Add copy button
                        st.markdown("""
                        <div style='margin-top: 20px;'>
                            <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                                Copy to Clipboard
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add tips for using the copy
                        with st.expander("💡 Tips for Using Your PAS Copy", expanded=False):
                            st.markdown("""
                            ### How to Use Your PAS Copy Effectively
                            
                            1. **Follow the sequence**: The PAS framework creates a natural progression - make sure your copy maintains this flow
                            
                            2. **Be specific about the problem**: The more specific and relatable the problem, the more effective your copy will be
                            
                            3. **Balance agitation**: Don't over-agitate to the point of creating anxiety; find the right balance to motivate action
                            
                            4. **Pair with visuals**: Combine your copy with images that reinforce each stage of the PAS journey
                            
                            5. **Consider the context**: Adapt the copy based on where it will appear (landing page, email, social media, etc.)
                            
                            6. **Measure results**: Track conversion metrics to see how your PAS copy performs
                            
                            7. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                            """)
                    else:
                        st.error("💥 **Failed to generate PAS Copy. Please try again!**")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_pas_copy(brand_name, description, problem, agitate, solution, 
                     target_audience, unique_selling_point, call_to_action, 
                     landing_page_url, platform, language, tone_style):
    system_prompt = """You are an expert copywriter specializing in the PAS (Problem-Agitate-Solution) framework. 
    Your expertise is in creating compelling, conversion-focused marketing copy that identifies customer pain points, 
    amplifies their impact, and positions your product or service as the ideal solution. 
    Your copy is authentic, specific to the brand, and focused on driving measurable results."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    PLATFORM: {platform}
    LANGUAGE: {language}
    TONE & STYLE: {tone_style}
    
    Use the PAS framework with these elements:
    - **Problem**: {problem}
    - **Agitate**: {agitate}
    - **Solution**: {solution}
    - **Call to Action**: {call_to_action}
    """
    
    if landing_page_url:
        prompt += f"\nInclude the landing page URL ({landing_page_url}) in your call to action."
    
    prompt += """
    For each campaign:
    1. Start by identifying the specific problem or pain point
    2. Amplify the problem by highlighting its negative consequences and emotional impact
    3. Present your product or service as the ideal solution to the problem
    4. End with a strong call to action

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None