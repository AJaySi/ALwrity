import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from tenacity import retry, wait_random_exponential, stop_after_attempt

def title_and_description():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🔍 QUEST Copywriting Generator</h2>
        <p>Create compelling copy that guides your audience through a journey using the QUEST (Question-Unpack-Emphasize-Solution-Transform) framework.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about QUEST copywriting
    with st.expander("📚 What is QUEST Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding the QUEST Copywriting Framework
        
        QUEST is an acronym for Question-Unpack-Emphasize-Solution-Transform. It's a copywriting framework that focuses on guiding the audience through different stages:
        
        - **Question**: Presenting a thought-provoking question to engage the audience
        - **Unpack**: Unpacking the question by elaborating on its implications and relevance
        - **Emphasize**: Emphasizing the importance or significance of the topic
        - **Solution**: Presenting your product or service as the solution to the question
        - **Transform**: Describing the transformation or improvement your solution offers
        
        ### Why QUEST Copywriting Works
        
        The QUEST framework works because it:
        
        - Creates a natural flow that guides readers through a journey
        - Engages readers by starting with a question they care about
        - Builds credibility by showing deep understanding of the problem
        - Demonstrates value by clearly connecting the solution to the problem
        - Inspires action by showing the transformation that's possible
        
        ### When to Use QUEST Copywriting
        
        The QUEST framework is particularly effective for:
        
        - Educational content and blog posts
        - Product launches and feature announcements
        - Problem-solution marketing
        - Thought leadership content
        - Content that needs to guide readers through a journey
        - Marketing materials that need to explain complex solutions
        """)

def input_section():
    # Main input form
    with st.expander("✍️ Create Your QUEST Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**🏢 Brand/Company Name**', 
                                      placeholder="e.g., Alwrity",
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**👥 Target Audience**', 
                                          placeholder="e.g., Small business owners, Tech professionals",
                                          help="Who is your ideal customer? Be specific about demographics and psychographics.")
            
            question = st.text_area('**❓ Thought-Provoking Question**', 
                                  placeholder="e.g., What if you could create content 10x faster without sacrificing quality?",
                                  help="Pose a question that resonates with your audience and highlights a problem they face.")
            
            unpack = st.text_area('**📦 Unpack the Question**', 
                                placeholder="e.g., Content creation is time-consuming and often results in inconsistent quality...",
                                help="Elaborate on the implications of the question and provide context that your audience can relate to.")
            
        with col2:
            description = st.text_input('**📝 Brand Description** (In 2-3 words)', 
                                      placeholder="e.g., AI writing tools",
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**💎 Unique Selling Point**', 
                                               placeholder="e.g., 10x faster content creation",
                                               help="What makes your product/service different from competitors?")
            
            emphasize = st.text_area('**💪 Emphasize Importance**', 
                                   placeholder="e.g., In today's fast-paced digital world, efficient content creation is essential for business growth...",
                                   help="Highlight the relevance and impact of addressing this problem.")
            
            solution = st.text_area('**🔧 Present Your Solution**', 
                                  placeholder="e.g., Our AI-powered writing assistant helps you create high-quality content in a fraction of the time...",
                                  help="Introduce your product or service as the solution to the question.")
            
            transform = st.text_area('**✨ Describe the Transformation**', 
                                   placeholder="e.g., Imagine having more time to focus on strategy while maintaining consistent, high-quality content...",
                                   help="Describe the transformation or improvement your solution offers to your audience.")
        
        tone_style = st.selectbox(
            '**🎭 Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**🚀 Generate QUEST Copy**', type="primary"):
            if not brand_name or not description or not question or not unpack or not emphasize or not solution or not transform:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, and all QUEST elements)!")
            else:
                with st.spinner("✨ Crafting compelling QUEST copy..."):
                    quest_copy = generate_quest_copy(
                        brand_name, 
                        description, 
                        question,
                        unpack,
                        emphasize,
                        solution,
                        transform,
                        target_audience,
                        unique_selling_point,
                        tone_style
                    )
                    
                    if quest_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>🔍 Your QUEST Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(quest_copy)
                        
                        # Add copy button
                        st.markdown("""
                        <div style='margin-top: 20px;'>
                            <button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;'>
                                Copy to Clipboard
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add tips for using the copy
                        with st.expander("💡 Tips for Using Your QUEST Copy", expanded=False):
                            st.markdown("""
                            ### How to Use Your QUEST Copy Effectively
                            
                            1. **Follow the journey**: The QUEST framework creates a natural flow - make sure your copy maintains this progression
                            
                            2. **Test different questions**: A/B test different opening questions to see which resonates most with your audience
                            
                            3. **Pair with visuals**: Combine your copy with images that reinforce each stage of the QUEST journey
                            
                            4. **Consider the context**: Adapt the copy based on where it will appear (blog post, landing page, email, etc.)
                            
                            5. **Measure results**: Track engagement metrics to see how your QUEST copy performs
                            
                            6. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                            """)
                    else:
                        st.error("💥 **Failed to generate QUEST Copy. Please try again!**")


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_quest_copy(brand_name, description, question, unpack, emphasize, solution, transform, 
                       target_audience, unique_selling_point, tone_style):
    system_prompt = """You are an expert copywriter specializing in the QUEST (Question-Unpack-Emphasize-Solution-Transform) framework. 
    Your expertise is in creating compelling, narrative-driven marketing copy that guides readers through a journey. 
    Your copy is authentic, specific to the brand, and focused on connecting with the audience's needs and desires."""
    
    prompt = f"""Create 3 different marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    UNIQUE SELLING POINT: {unique_selling_point}
    TONE & STYLE: {tone_style}
    
    Use the QUEST framework with these elements:
    - **Question**: {question}
    - **Unpack**: {unpack}
    - **Emphasize**: {emphasize}
    - **Solution**: {solution}
    - **Transform**: {transform}

    For each campaign:
    1. Start with the thought-provoking question to engage the audience
    2. Unpack the question by elaborating on its implications
    3. Emphasize the importance of addressing this issue
    4. Present your solution clearly and convincingly
    5. Describe the transformation that your solution offers
    6. End with a strong call to action

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None