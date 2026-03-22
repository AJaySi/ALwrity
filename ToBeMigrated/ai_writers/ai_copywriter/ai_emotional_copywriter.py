import streamlit as st
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

def input_section():
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #1E88E5;'>🎭 Emotional Copywriting Generator</h2>
        <p>Create compelling copy that resonates with your audience's emotions and drives action.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational content about emotional copywriting
    with st.expander("📚 What is Emotional Copywriting?", expanded=False):
        st.markdown("""
        ### Understanding Emotional Copywriting
        
        Emotional copywriting is a powerful marketing technique that connects with your audience on a deeper level by:
        
        - **Triggering specific emotions** (joy, fear, urgency, trust, etc.)
        - **Creating personal connections** with your audience
        - **Addressing pain points** and offering solutions
        - **Building trust and credibility**
        - **Creating a sense of belonging** or exclusivity
        
        ### Why Emotional Copywriting Works
        
        Research shows that people make purchasing decisions based on emotions first, then justify with logic. By tapping into the right emotions, you can:
        
        - Increase engagement and response rates
        - Build stronger brand loyalty
        - Drive more conversions
        - Create memorable brand experiences
        
        ### Common Emotional Triggers
        
        - **Fear of Missing Out (FOMO)**: Limited time offers, exclusive access
        - **Trust**: Testimonials, guarantees, social proof
        - **Joy/Happiness**: Benefits, positive outcomes, aspirational messaging
        - **Urgency**: Time-sensitive offers, countdown timers
        - **Belonging**: Community, exclusivity, shared values
        """)
    
    # Main input form
    with st.expander("✍️ Create Your Emotional Copy", expanded=True):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            brand_name = st.text_input('**Brand/Company Name**', 
                                      help="Enter the name of your brand or company.")
            
            target_audience = st.text_input('**Target Audience**', 
                                          help="Who is your ideal customer? (e.g., 'busy moms', 'tech-savvy millennials')")
            
            emotional_trigger = st.selectbox(
                '**Primary Emotional Trigger**',
                options=['Trust', 'Fear of Missing Out', 'Joy/Happiness', 'Urgency', 'Belonging', 'Exclusivity'],
                help="Select the primary emotion you want to evoke in your audience."
            )
            
        with col2:
            description = st.text_input('**Brand Description** (In 5-6 words)', 
                                      help="Describe your product or service briefly.")
            
            unique_selling_point = st.text_input('**Unique Selling Point**', 
                                               help="What makes your product/service different from competitors?")
            
            call_to_action = st.text_input('**Desired Call to Action**', 
                                         help="What action do you want your audience to take? (e.g., 'Sign up now', 'Buy today')")
        
        trust_elements = st.text_area('**Trust Elements**',
                                    help="Build trust and credibility by showcasing testimonials, guarantees, or endorsements.",
                                    placeholder="Testimonials from satisfied customers...\nOur guarantee that...\nIndustry certifications...")
        
        tone_style = st.selectbox(
            '**Copy Tone & Style**',
            options=['Professional', 'Conversational', 'Humorous', 'Authoritative', 'Empathetic', 'Aspirational'],
            help="Select the tone and style for your copy."
        )
        
        if st.button('**Generate Emotional Copy**', type="primary"):
            if not brand_name or not description or not trust_elements:
                st.error("⚠️ Please fill in all required fields (Brand Name, Description, and Trust Elements)!")
            else:
                with st.spinner("✨ Crafting emotionally compelling copy..."):
                    emotional_copy = generate_emotional_copy(
                        brand_name, 
                        description, 
                        trust_elements,
                        target_audience,
                        emotional_trigger,
                        unique_selling_point,
                        call_to_action,
                        tone_style
                    )
                    
                    if emotional_copy:
                        st.markdown("""
                        <div style='background-color: #e6f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #0066cc;'>🎯 Your Emotional Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the copy with a nice format
                        st.markdown(emotional_copy)
                        
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
                            <h3 style='color: #333;'>💡 Tips for Using Your Emotional Copy</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("""
                        ### How to Use Your Emotional Copy Effectively
                        
                        1. **Test different versions**: A/B test your copy to see which emotional triggers resonate most with your audience
                        
                        2. **Pair with visuals**: Combine your copy with images that reinforce the emotional message
                        
                        3. **Consider the context**: Adapt the copy based on where it will appear (social media, email, website, etc.)
                        
                        4. **Measure results**: Track engagement metrics to see how your emotional copy performs
                        
                        5. **Refine over time**: Continuously improve your copy based on audience feedback and performance data
                        """)
                    else:
                        st.error("💥 **Failed to generate Emotional Copy. Please try again!**")


def generate_emotional_copy(brand_name, description, trust_elements, target_audience, emotional_trigger, 
                           unique_selling_point, call_to_action, tone_style):
    system_prompt = """You are an expert emotional copywriter with years of experience in creating compelling marketing copy 
    that resonates with audiences on a deep emotional level. Your specialty is crafting copy that triggers specific emotions 
    and drives action while maintaining authenticity and credibility."""
    
    prompt = f"""Create 3 different emotional marketing campaigns for {brand_name}, which is a {description}.

    TARGET AUDIENCE: {target_audience}
    PRIMARY EMOTIONAL TRIGGER: {emotional_trigger}
    UNIQUE SELLING POINT: {unique_selling_point}
    DESIRED CALL TO ACTION: {call_to_action}
    TONE & STYLE: {tone_style}
    TRUST ELEMENTS: {trust_elements}

    For each campaign:
    1. Create a compelling headline that captures attention
    2. Write 2-3 paragraphs of body copy that builds emotional connection
    3. End with a strong call to action
    4. Explain which emotional triggers you used and why they're effective for this audience

    Format each campaign clearly with "CAMPAIGN 1:", "CAMPAIGN 2:", etc. as headers.
    Make the copy authentic, specific to the brand, and focused on the target audience's needs and desires.
    """
    
    try:
        return llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as e:
        st.error(f"Error generating copy: {str(e)}")
        return None