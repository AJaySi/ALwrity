"""
Google Ads Generator Module

This module provides a comprehensive UI for generating high-converting Google Ads
based on user inputs and best practices.
"""

import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime
import re
import random
from typing import Dict, List, Tuple, Any, Optional

# Import internal modules
from ...gpt_providers.text_generation.main_text_generation import llm_text_gen
from .ad_analyzer import analyze_ad_quality, calculate_quality_score, analyze_keyword_relevance
from .ad_templates import get_industry_templates, get_ad_type_templates
from .ad_extensions_generator import generate_extensions

def write_google_ads():
"""Main function to render the Google Ads Generator UI."""

# Page title and description
st.title("🚀 AI Google Ads Generator")
st.markdown("""
Create high-converting Google Ads that drive clicks and conversions. 
Our AI-powered tool follows Google Ads best practices to help you maximize your ad spend ROI.
""")

# Initialize session state for storing generated ads
if "generated_ads" not in st.session_state:
st.session_state.generated_ads = []

if "selected_ad_index" not in st.session_state:
st.session_state.selected_ad_index = None

if "ad_history" not in st.session_state:
st.session_state.ad_history = []

# Create tabs for different sections
tabs = st.tabs(["Ad Creation", "Ad Performance", "Ad History", "Best Practices"])

with tabs[0]:
render_ad_creation_tab()

with tabs[1]:
render_ad_performance_tab()

with tabs[2]:
render_ad_history_tab()

with tabs[3]:
render_best_practices_tab()

def render_ad_creation_tab():
"""Render the Ad Creation tab with all input fields."""

# Create columns for a better layout
col1, col2 = st.columns([2, 1])

with col1:
st.subheader("Campaign Details")

# Business information
business_name = st.text_input(
"Business Name", 
help="Enter your business or brand name"
)

business_description = st.text_area(
"Business Description", 
help="Briefly describe your business, products, or services (100-200 characters recommended)",
max_chars=500
)

# Industry selection
industries = [
"E-commerce", "SaaS/Technology", "Healthcare", "Education", 
"Finance", "Real Estate", "Legal", "Travel", "Food & Beverage",
"Fashion", "Beauty", "Fitness", "Home Services", "B2B Services",
"Entertainment", "Automotive", "Non-profit", "Other"
]

industry = st.selectbox(
"Industry", 
industries,
help="Select the industry that best matches your business"
)

# Campaign objective
objectives = [
"Sales", "Leads", "Website Traffic", "Brand Awareness", 
"App Promotion", "Local Store Visits", "Product Consideration"
]

campaign_objective = st.selectbox(
"Campaign Objective", 
objectives,
help="What is the main goal of your advertising campaign?"
)

# Target audience
target_audience = st.text_area(
"Target Audience", 
help="Describe your ideal customer (age, interests, pain points, etc.)",
max_chars=300
)

# Create a container for the keyword section
keyword_container = st.container()

with keyword_container:
st.subheader("Keywords & Targeting")

# Primary keywords
primary_keywords = st.text_area(
"Primary Keywords (1 per line)", 
help="Enter your main keywords (1-5 recommended). These will be prominently featured in your ads.",
height=100
)

# Secondary keywords
secondary_keywords = st.text_area(
"Secondary Keywords (1 per line)", 
help="Enter additional relevant keywords that can be included when appropriate.",
height=100
)

# Negative keywords
negative_keywords = st.text_area(
"Negative Keywords (1 per line)", 
help="Enter terms you want to avoid in your ads.",
height=100
)

# Match type selection
match_types = st.multiselect(
"Keyword Match Types",
["Broad Match", "Phrase Match", "Exact Match"],
default=["Phrase Match"],
help="Select the match types you want to use for your keywords"
)

with col2:
st.subheader("Ad Specifications")

# Ad type
ad_types = [
"Responsive Search Ad", 
"Expanded Text Ad",
"Call-Only Ad",
"Dynamic Search Ad"
]

ad_type = st.selectbox(
"Ad Type", 
ad_types,
help="Select the type of Google Ad you want to create"
)

# Number of ad variations
num_variations = st.slider(
"Number of Ad Variations", 
min_value=1, 
max_value=5, 
value=3,
help="Generate multiple ad variations for A/B testing"
)

# Unique selling points
usp = st.text_area(
"Unique Selling Points (1 per line)", 
help="What makes your product/service unique? (e.g., Free shipping, 24/7 support)",
height=100
)

# Call to action
cta_options = [
"Shop Now", "Learn More", "Sign Up", "Get Started", 
"Contact Us", "Book Now", "Download", "Request a Demo",
"Get a Quote", "Subscribe", "Join Now", "Apply Now",
"Custom"
]

cta_selection = st.selectbox(
"Call to Action", 
cta_options,
help="Select a primary call to action for your ads"
)

if cta_selection == "Custom":
custom_cta = st.text_input(
"Custom Call to Action",
help="Enter your custom call to action (keep it short and action-oriented)"
)

# Landing page URL
landing_page = st.text_input(
"Landing Page URL", 
help="Enter the URL where users will be directed after clicking your ad"
)

# Ad tone
tone_options = [
"Professional", "Conversational", "Urgent", "Informative", 
"Persuasive", "Empathetic", "Authoritative", "Friendly"
]

ad_tone = st.selectbox(
"Ad Tone", 
tone_options,
help="Select the tone of voice for your ads"
)

# Ad Extensions section
st.subheader("Ad Extensions")
st.markdown("Ad extensions improve visibility and provide additional information to potential customers.")

# Create columns for extension types
ext_col1, ext_col2 = st.columns(2)

with ext_col1:
# Sitelink extensions
st.markdown("##### Sitelink Extensions")
num_sitelinks = st.slider("Number of Sitelinks", 0, 6, 4)

sitelinks = []
if num_sitelinks > 0:
for i in range(num_sitelinks):
col1, col2 = st.columns(2)
with col1:
link_text = st.text_input(f"Sitelink {i+1} Text", key=f"sitelink_text_{i}")
with col2:
link_url = st.text_input(f"Sitelink {i+1} URL", key=f"sitelink_url_{i}")

link_desc = st.text_input(
f"Sitelink {i+1} Description (optional)", 
key=f"sitelink_desc_{i}",
help="Optional: Add 1-2 description lines (max 35 chars each)"
)

if link_text and link_url:
sitelinks.append({
"text": link_text,
"url": link_url,
"description": link_desc
})

# Callout extensions
st.markdown("##### Callout Extensions")
callout_text = st.text_area(
"Callout Extensions (1 per line)", 
help="Add short phrases highlighting your business features (e.g., '24/7 Customer Service')",
height=100
)

with ext_col2:
# Structured snippet extensions
st.markdown("##### Structured Snippet Extensions")
snippet_headers = [
"Brands", "Courses", "Degree Programs", "Destinations", 
"Featured Hotels", "Insurance Coverage", "Models", 
"Neighborhoods", "Service Catalog", "Services", 
"Shows", "Styles", "Types"
]

snippet_header = st.selectbox("Snippet Header", snippet_header_options)
snippet_values = st.text_area(
"Snippet Values (1 per line)", 
help="Add values related to the selected header (e.g., for 'Services': 'Cleaning', 'Repairs')",
height=100
)

# Call extensions
st.markdown("##### Call Extension")
include_call = st.checkbox("Include Call Extension")
if include_call:
phone_number = st.text_input("Phone Number")

# Advanced options in an expander
with st.expander("Advanced Options"):
col1, col2 = st.columns(2)

with col1:
# Device preference
device_preference = st.multiselect(
"Device Preference",
["Mobile", "Desktop", "Tablet"],
default=["Mobile", "Desktop"],
help="Select which devices to optimize ads for"
)

# Location targeting
location_targeting = st.text_input(
"Location Targeting", 
help="Enter locations to target (e.g., 'New York, Los Angeles')"
)

with col2:
# Competitor analysis
competitor_urls = st.text_area(
"Competitor URLs (1 per line)", 
help="Enter URLs of competitors for analysis (optional)",
height=100
)

# Budget information
daily_budget = st.number_input(
"Daily Budget ($)", 
min_value=1.0, 
value=50.0, 
help="Enter your daily budget for this campaign"
)

# Generate button
if st.button("Generate Google Ads", type="primary"):
if not business_name or not business_description or not primary_keywords:
st.error("Please fill in the required fields: Business Name, Business Description, and Primary Keywords.")
return

with st.spinner("Generating high-converting Google Ads..."):
# Process keywords
primary_kw_list = [kw.strip() for kw in primary_keywords.split("\n") if kw.strip()]
secondary_kw_list = [kw.strip() for kw in secondary_keywords.split("\n") if kw.strip()]
negative_kw_list = [kw.strip() for kw in negative_keywords.split("\n") if kw.strip()]

# Process USPs
usp_list = [point.strip() for point in usp.split("\n") if point.strip()]

# Process callouts
callout_list = [callout.strip() for callout in callout_text.split("\n") if callout.strip()]

# Process snippets
snippet_list = [snippet.strip() for snippet in snippet_values.split("\n") if snippet.strip()]

# Get the CTA
final_cta = custom_cta if cta_selection == "Custom" else cta_selection

# Generate ads
generated_ads = generate_google_ads(
business_name=business_name,
business_description=business_description,
industry=industry,
campaign_objective=campaign_objective,
target_audience=target_audience,
primary_keywords=primary_kw_list,
secondary_keywords=secondary_kw_list,
negative_keywords=negative_kw_list,
match_types=match_types,
ad_type=ad_type,
num_variations=num_variations,
unique_selling_points=usp_list,
call_to_action=final_cta,
landing_page=landing_page,
ad_tone=ad_tone,
sitelinks=sitelinks,
callouts=callout_list,
snippet_header=snippet_header,
snippet_values=snippet_list,
phone_number=phone_number if include_call else None,
device_preference=device_preference,
location_targeting=location_targeting,
competitor_urls=[url.strip() for url in competitor_urls.split("\n") if url.strip()],
daily_budget=daily_budget
)

if generated_ads:
# Store the generated ads in session state
st.session_state.generated_ads = generated_ads

# Add to history
st.session_state.ad_history.append({
"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
"business_name": business_name,
"industry": industry,
"campaign_objective": campaign_objective,
"ads": generated_ads
})

# Display the generated ads
display_generated_ads(generated_ads)
else:
st.error("Failed to generate ads. Please try again with different inputs.")

def generate_google_ads(**kwargs) -> List[Dict]:
"""
Generate Google Ads based on user inputs.

Args:
**kwargs: All the user inputs from the form

Returns:
List of dictionaries containing generated ads and their metadata
"""
# Extract key parameters
business_name = kwargs.get("business_name", "")
business_description = kwargs.get("business_description", "")
industry = kwargs.get("industry", "")
campaign_objective = kwargs.get("campaign_objective", "")
target_audience = kwargs.get("target_audience", "")
primary_keywords = kwargs.get("primary_keywords", [])
secondary_keywords = kwargs.get("secondary_keywords", [])
negative_keywords = kwargs.get("negative_keywords", [])
ad_type = kwargs.get("ad_type", "Responsive Search Ad")
num_variations = kwargs.get("num_variations", 3)
unique_selling_points = kwargs.get("unique_selling_points", [])
call_to_action = kwargs.get("call_to_action", "Learn More")
landing_page = kwargs.get("landing_page", "")
ad_tone = kwargs.get("ad_tone", "Professional")

# Get templates based on industry and ad type
industry_templates = get_industry_templates(industry)
ad_type_templates = get_ad_type_templates(ad_type)

# Prepare the prompt for the LLM
system_prompt = """You are an expert Google Ads copywriter with years of experience creating high-converting ads. 
Your task is to create Google Ads that follow best practices, maximize Quality Score, and drive high CTR and conversion rates.

For each ad, provide:
1. Headlines (3-15 depending on ad type)
2. Descriptions (2-4 depending on ad type)
3. Display URL path (2 fields)
4. A brief explanation of why this ad would be effective

Format your response as valid JSON with the following structure for each ad:
{
"headlines": ["Headline 1", "Headline 2", ...],
"descriptions": ["Description 1", "Description 2", ...],
"path1": "path-one",
"path2": "path-two",
"explanation": "Brief explanation of the ad's strengths"
}

IMPORTANT GUIDELINES:
- Include primary keywords in headlines and descriptions
- Ensure headlines are 30 characters or less
- Ensure descriptions are 90 characters or less
- Include the call to action in at least one headline or description
- Make the ad relevant to the search intent
- Highlight unique selling points
- Use emotional triggers appropriate for the industry
- Ensure the ad is compliant with Google Ads policies
- Create distinct variations that test different approaches
"""

prompt = f"""
Create {num_variations} high-converting Google {ad_type}s for the following business:

BUSINESS INFORMATION:
Business Name: {business_name}
Business Description: {business_description}
Industry: {industry}
Campaign Objective: {campaign_objective}
Target Audience: {target_audience}
Landing Page: {landing_page}

KEYWORDS:
Primary Keywords: {', '.join(primary_keywords)}
Secondary Keywords: {', '.join(secondary_keywords)}
Negative Keywords: {', '.join(negative_keywords)}

UNIQUE SELLING POINTS:
{', '.join(unique_selling_points)}

SPECIFICATIONS:
Ad Type: {ad_type}
Call to Action: {call_to_action}
Tone: {ad_tone}

ADDITIONAL INSTRUCTIONS:
- For Responsive Search Ads, create 10-15 headlines and 2-4 descriptions
- For Expanded Text Ads, create 3 headlines and 2 descriptions
- For Call-Only Ads, focus on encouraging calls
- For Dynamic Search Ads, create compelling descriptions that work with dynamically generated headlines
- Include at least one headline with the primary keyword
- Include the call to action in at least one headline and one description
- Ensure all headlines are 30 characters or less
- Ensure all descriptions are 90 characters or less
- Use the business name in at least one headline
- Create distinct variations that test different approaches and angles
- Format the response as a valid JSON array of ad objects

Return ONLY the JSON array with no additional text or explanation.
"""

try:
# Generate the ads using the LLM
response = llm_text_gen(prompt, system_prompt=system_prompt)

# Parse the JSON response
try:
# Try to parse the response as JSON
ads_data = json.loads(response)

# If the response is not a list, wrap it in a list
if not isinstance(ads_data, list):
ads_data = [ads_data]

# Process each ad
processed_ads = []
for i, ad in enumerate(ads_data):
# Analyze the ad quality
quality_analysis = analyze_ad_quality(
ad, 
primary_keywords, 
secondary_keywords, 
business_name, 
call_to_action
)

# Calculate quality score
quality_score = calculate_quality_score(
ad,
primary_keywords,
landing_page,
ad_type
)

# Add metadata to the ad
processed_ad = {
"id": f"ad_{int(time.time())}_{i}",
"type": ad_type,
"headlines": ad.get("headlines", []),
"descriptions": ad.get("descriptions", []),
"path1": ad.get("path1", ""),
"path2": ad.get("path2", ""),
"final_url": landing_page,
"business_name": business_name,
"primary_keywords": primary_keywords,
"quality_analysis": quality_analysis,
"quality_score": quality_score,
"explanation": ad.get("explanation", ""),
"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

processed_ads.append(processed_ad)

return processed_ads

except json.JSONDecodeError:
# If JSON parsing fails, try to extract structured data from the text
st.warning("Failed to parse JSON response. Attempting to extract structured data from text.")

# Implement fallback parsing logic here
# This is a simplified example - you would need more robust parsing
headlines_pattern = r"Headlines?:(.*?)Descriptions?:"
descriptions_pattern = r"Descriptions?:(.*?)(?:Path|Display URL|$)"

ads_data = []
variations = re.split(r"Ad Variation \d+:|Ad \d+:", response)

for variation in variations:
if not variation.strip():
continue

headlines_match = re.search(headlines_pattern, variation, re.DOTALL)
descriptions_match = re.search(descriptions_pattern, variation, re.DOTALL)

if headlines_match and descriptions_match:
headlines = [h.strip() for h in re.findall(r'"([^"]*)"', headlines_match.group(1))]
descriptions = [d.strip() for d in re.findall(r'"([^"]*)"', descriptions_match.group(1))]

if not headlines:
headlines = [h.strip() for h in re.findall(r'- (.*)', headlines_match.group(1))]

if not descriptions:
descriptions = [d.strip() for d in re.findall(r'- (.*)', descriptions_match.group(1))]

ads_data.append({
"headlines": headlines,
"descriptions": descriptions,
"path1": f"{primary_keywords[0].lower().replace(' ', '-')}" if primary_keywords else "",
"path2": "info",
"explanation": "Generated from text response"
})

# Process each ad as before
processed_ads = []
for i, ad in enumerate(ads_data):
quality_analysis = analyze_ad_quality(
ad, 
primary_keywords, 
secondary_keywords, 
business_name, 
call_to_action
)

quality_score = calculate_quality_score(
ad,
primary_keywords,
landing_page,
ad_type
)

processed_ad = {
"id": f"ad_{int(time.time())}_{i}",
"type": ad_type,
"headlines": ad.get("headlines", []),
"descriptions": ad.get("descriptions", []),
"path1": ad.get("path1", ""),
"path2": ad.get("path2", ""),
"final_url": landing_page,
"business_name": business_name,
"primary_keywords": primary_keywords,
"quality_analysis": quality_analysis,
"quality_score": quality_score,
"explanation": ad.get("explanation", ""),
"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

processed_ads.append(processed_ad)

return processed_ads

except Exception as e:
st.error(f"Error generating ads: {str(e)}")
return []

def display_generated_ads(ads: List[Dict]):
"""
Display the generated ads in a user-friendly format.

Args:
ads: List of dictionaries containing generated ads and their metadata
"""
st.subheader("Generated Google Ads")
st.write(f"Generated {len(ads)} ad variations. Click on each ad to see details.")

# Create tabs for different views
ad_tabs = st.tabs(["Preview", "Performance Analysis", "Export"])

with ad_tabs[0]:
# Display each ad in an expander
for i, ad in enumerate(ads):
ad_type = ad.get("type", "Google Ad")
quality_score = ad.get("quality_score", {}).get("overall_score", 0)

# Create a color based on quality score
if quality_score >= 8:
quality_color = "green"
elif quality_score >= 6:
quality_color = "orange"
else:
quality_color = "red"

with st.expander(f"Ad Variation {i+1} - Quality Score: {quality_score}/10", expanded=(i==0)):
# Create columns for preview and details
col1, col2 = st.columns([3, 2])

with col1:
# Display ad preview
st.markdown("### Ad Preview")

# Display headlines
for j, headline in enumerate(ad.get("headlines", [])[:3]):  # Show first 3 headlines
st.markdown(f"**{headline}**")

# Display URL
display_url = f"{ad.get('final_url', '').replace('https://', '').replace('http://', '').split('/')[0]}/{ad.get('path1', '')}/{ad.get('path2', '')}"
st.markdown(f"<span style='color: green;'>{display_url}</span>", unsafe_allow_html=True)

# Display descriptions
for description in ad.get("descriptions", []):
st.markdown(f"{description}")

# Display explanation
if ad.get("explanation"):
st.markdown("#### Why this ad works:")
st.markdown(f"_{ad.get('explanation')}_")

with col2:
# Display quality analysis
st.markdown("### Quality Analysis")

quality_analysis = ad.get("quality_analysis", {})
quality_score_details = ad.get("quality_score", {})

# Display quality score
st.markdown(f"**Overall Quality Score:** <span style='color: {quality_color};'>{quality_score}/10</span>", unsafe_allow_html=True)

# Display individual metrics
metrics = [
("Keyword Relevance", quality_score_details.get("keyword_relevance", 0)),
("Ad Relevance", quality_score_details.get("ad_relevance", 0)),
("CTA Effectiveness", quality_score_details.get("cta_effectiveness", 0)),
("Landing Page Relevance", quality_score_details.get("landing_page_relevance", 0))
]

for metric_name, metric_score in metrics:
if metric_score >= 8:
metric_color = "green"
elif metric_score >= 6:
metric_color = "orange"
else:
metric_color = "red"

st.markdown(f"**{metric_name}:** <span style='color: {metric_color};'>{metric_score}/10</span>", unsafe_allow_html=True)

# Display strengths and improvements
if quality_analysis.get("strengths"):
st.markdown("#### Strengths:")
for strength in quality_analysis.get("strengths", []):
st.markdown(f"✅ {strength}")

if quality_analysis.get("improvements"):
st.markdown("#### Improvement Opportunities:")
for improvement in quality_analysis.get("improvements", []):
st.markdown(f"🔍 {improvement}")

# Add buttons for actions
col1, col2, col3 = st.columns(3)

with col1:
if st.button("Select This Ad", key=f"select_ad_{i}"):
st.session_state.selected_ad_index = i
st.success(f"Ad Variation {i+1} selected!")

with col2:
if st.button("Edit This Ad", key=f"edit_ad_{i}"):
# This would open an editing interface
st.info("Ad editing feature coming soon!")

with col3:
if st.button("Generate Similar", key=f"similar_ad_{i}"):
st.info("Similar ad generation feature coming soon!")

with ad_tabs[1]:
# Display performance analysis
st.subheader("Ad Performance Analysis")

# Create a DataFrame for comparison
comparison_data = []
for i, ad in enumerate(ads):
quality_score = ad.get("quality_score", {})

comparison_data.append({
"Ad Variation": f"Ad {i+1}",
"Overall Score": quality_score.get("overall_score", 0),
"Keyword Relevance": quality_score.get("keyword_relevance", 0),
"Ad Relevance": quality_score.get("ad_relevance", 0),
"CTA Effectiveness": quality_score.get("cta_effectiveness", 0),
"Landing Page Relevance": quality_score.get("landing_page_relevance", 0),
"Est. CTR": f"{quality_score.get('estimated_ctr', 0):.2f}%",
"Est. Conv. Rate": f"{quality_score.get('estimated_conversion_rate', 0):.2f}%"
})

# Create a DataFrame and display it
df = pd.DataFrame(comparison_data)
st.dataframe(df, use_container_width=True)

# Display a bar chart comparing overall scores
st.subheader("Quality Score Comparison")
chart_data = pd.DataFrame({
"Ad Variation": [f"Ad {i+1}" for i in range(len(ads))],
"Overall Score": [ad.get("quality_score", {}).get("overall_score", 0) for ad in ads]
})

st.bar_chart(chart_data, x="Ad Variation", y="Overall Score", use_container_width=True)

# Display keyword analysis
st.subheader("Keyword Analysis")

if ads and len(ads) > 0:
# Get the primary keywords from the first ad
primary_keywords = ads[0].get("primary_keywords", [])

# Analyze keyword usage across all ads
keyword_data = []
for keyword in primary_keywords:
keyword_data.append({
"Keyword": keyword,
"Headline Usage": sum(1 for ad in ads if any(keyword.lower() in headline.lower() for headline in ad.get("headlines", []))),
"Description Usage": sum(1 for ad in ads if any(keyword.lower() in desc.lower() for desc in ad.get("descriptions", []))),
"Path Usage": sum(1 for ad in ads if keyword.lower() in ad.get("path1", "").lower() or keyword.lower() in ad.get("path2", "").lower())
})

# Create a DataFrame and display it
kw_df = pd.DataFrame(keyword_data)
st.dataframe(kw_df, use_container_width=True)

with ad_tabs[2]:
# Export options
st.subheader("Export Options")

# Select export format
export_format = st.selectbox(
"Export Format",
["CSV", "Excel", "Google Ads Editor CSV", "JSON"]
)

# Select which ads to export
export_selection = st.radio(
"Export Selection",
["All Generated Ads", "Selected Ad Only", "Ads Above Quality Score Threshold"]
)

if export_selection == "Ads Above Quality Score Threshold":
quality_threshold = st.slider("Minimum Quality Score", 1, 10, 7)

# Export button
if st.button("Export Ads", type="primary"):
# Determine which ads to export
if export_selection == "All Generated Ads":
ads_to_export = ads
elif export_selection == "Selected Ad Only":
if st.session_state.selected_ad_index is not None:
ads_to_export = [ads[st.session_state.selected_ad_index]]
else:
st.warning("Please select an ad first.")
ads_to_export = []
else:  # Above threshold
ads_to_export = [ad for ad in ads if ad.get("quality_score", {}).get("overall_score", 0) >= quality_threshold]

if ads_to_export:
# Prepare the export data based on format
if export_format == "CSV" or export_format == "Google Ads Editor CSV":
# Create CSV data
if export_format == "CSV":
# Simple CSV format
export_data = []
for ad in ads_to_export:
export_data.append({
"Ad Type": ad.get("type", ""),
"Headlines": " | ".join(ad.get("headlines", [])),
"Descriptions": " | ".join(ad.get("descriptions", [])),
"Path 1": ad.get("path1", ""),
"Path 2": ad.get("path2", ""),
"Final URL": ad.get("final_url", ""),
"Quality Score": ad.get("quality_score", {}).get("overall_score", 0)
})
else:
# Google Ads Editor format
export_data = []
for ad in ads_to_export:
base_row = {
"Action": "Add",
"Campaign": "",  # User would fill this in
"Ad Group": "",  # User would fill this in
"Status": "Enabled",
"Final URL": ad.get("final_url", ""),
"Path 1": ad.get("path1", ""),
"Path 2": ad.get("path2", "")
}

# Add headlines and descriptions based on ad type
if ad.get("type") == "Responsive Search Ad":
for i, headline in enumerate(ad.get("headlines", []), 1):
base_row[f"Headline {i}"] = headline

for i, desc in enumerate(ad.get("descriptions", []), 1):
base_row[f"Description {i}"] = desc
else:
# For other ad types
for i, headline in enumerate(ad.get("headlines", [])[:3], 1):
base_row[f"Headline {i}"] = headline

for i, desc in enumerate(ad.get("descriptions", [])[:2], 1):
base_row[f"Description {i}"] = desc

export_data.append(base_row)

# Convert to DataFrame and then to CSV
df = pd.DataFrame(export_data)
csv = df.to_csv(index=False)

# Create a download button
st.download_button(
label="Download CSV",
data=csv,
file_name=f"google_ads_export_{int(time.time())}.csv",
mime="text/csv"
)

elif export_format == "Excel":
# Create Excel data
export_data = []
for ad in ads_to_export:
export_data.append({
"Ad Type": ad.get("type", ""),
"Headlines": " | ".join(ad.get("headlines", [])),
"Descriptions": " | ".join(ad.get("descriptions", [])),
"Path 1": ad.get("path1", ""),
"Path 2": ad.get("path2", ""),
"Final URL": ad.get("final_url", ""),
"Quality Score": ad.get("quality_score", {}).get("overall_score", 0)
})

# Convert to DataFrame and then to Excel
df = pd.DataFrame(export_data)

# Create a temporary Excel file
excel_file = f"google_ads_export_{int(time.time())}.xlsx"
df.to_excel(excel_file, index=False)

# Read the file and create a download button
with open(excel_file, "rb") as f:
st.download_button(
label="Download Excel",
data=f,
file_name=excel_file,
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

else:  # JSON
# Convert to JSON
json_data = json.dumps(ads_to_export, indent=2)

# Create a download button
st.download_button(
label="Download JSON",
data=json_data,
file_name=f"google_ads_export_{int(time.time())}.json",
mime="application/json"
)
else:
st.warning("No ads to export based on your selection.")

def render_ad_performance_tab():
"""Render the Ad Performance tab with analytics and insights."""

st.subheader("Ad Performance Simulator")
st.write("Simulate how your ads might perform based on industry benchmarks and our predictive model.")

# Check if we have generated ads
if not st.session_state.generated_ads:
st.info("Generate ads first to see performance predictions.")
return

# Get the selected ad or the first one
selected_index = st.session_state.selected_ad_index if st.session_state.selected_ad_index is not None else 0

if selected_index >= len(st.session_state.generated_ads):
selected_index = 0

selected_ad = st.session_state.generated_ads[selected_index]

# Display the selected ad
st.markdown(f"### Selected Ad (Variation {selected_index + 1})")

# Create columns for the ad preview
col1, col2 = st.columns([3, 2])

with col1:
# Display headlines
for headline in selected_ad.get("headlines", [])[:3]:
st.markdown(f"**{headline}**")

# Display URL
display_url = f"{selected_ad.get('final_url', '').replace('https://', '').replace('http://', '').split('/')[0]}/{selected_ad.get('path1', '')}/{selected_ad.get('path2', '')}"
st.markdown(f"<span style='color: green;'>{display_url}</span>", unsafe_allow_html=True)

# Display descriptions
for description in selected_ad.get("descriptions", []):
st.markdown(f"{description}")

with col2:
# Display quality score
quality_score = selected_ad.get("quality_score", {}).get("overall_score", 0)

# Create a color based on quality score
if quality_score >= 8:
quality_color = "green"
elif quality_score >= 6:
quality_color = "orange"
else:
quality_color = "red"

st.markdown(f"**Quality Score:** <span style='color: {quality_color};'>{quality_score}/10</span>", unsafe_allow_html=True)

# Display estimated metrics
est_ctr = selected_ad.get("quality_score", {}).get("estimated_ctr", 0)
est_conv_rate = selected_ad.get("quality_score", {}).get("estimated_conversion_rate", 0)

st.markdown(f"**Estimated CTR:** {est_ctr:.2f}%")
st.markdown(f"**Estimated Conversion Rate:** {est_conv_rate:.2f}%")

# Performance simulation
st.subheader("Performance Simulation")

# Create columns for inputs
col1, col2, col3 = st.columns(3)

with col1:
daily_budget = st.number_input("Daily Budget ($)", min_value=1.0, value=50.0)
cost_per_click = st.number_input("Average CPC ($)", min_value=0.1, value=1.5, step=0.1)

with col2:
avg_conversion_value = st.number_input("Avg. Conversion Value ($)", min_value=0.0, value=50.0)
time_period = st.selectbox("Time Period", ["Day", "Week", "Month"])

with col3:
# Use the estimated CTR and conversion rate from the ad quality score
ctr_override = st.number_input("CTR Override (%)", min_value=0.1, max_value=100.0, value=est_ctr, step=0.1)
conv_rate_override = st.number_input("Conversion Rate Override (%)", min_value=0.01, max_value=100.0, value=est_conv_rate, step=0.01)

# Calculate performance metrics
if time_period == "Day":
multiplier = 1
elif time_period == "Week":
multiplier = 7
else:  # Month
multiplier = 30

total_budget = daily_budget * multiplier
clicks = total_budget / cost_per_click
impressions = clicks * 100 / ctr_override
conversions = clicks * conv_rate_override / 100
conversion_value = conversions * avg_conversion_value
roi = ((conversion_value - total_budget) / total_budget) * 100 if total_budget > 0 else 0

# Display the results
st.subheader(f"Projected {time_period} Performance")

# Create columns for metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
st.metric("Impressions", f"{impressions:,.0f}")
st.metric("Clicks", f"{clicks:,.0f}")

with col2:
st.metric("CTR", f"{ctr_override:.2f}%")
st.metric("Cost", f"${total_budget:,.2f}")

with col3:
st.metric("Conversions", f"{conversions:,.2f}")
st.metric("Conversion Rate", f"{conv_rate_override:.2f}%")

with col4:
st.metric("Conversion Value", f"${conversion_value:,.2f}")
st.metric("ROI", f"{roi:,.2f}%")

# Display a chart
st.subheader("Performance Over Time")

# Create data for the chart
chart_data = pd.DataFrame({
"Day": list(range(1, multiplier + 1)),
"Clicks": [clicks / multiplier] * multiplier,
"Conversions": [conversions / multiplier] * multiplier,
"Cost": [daily_budget] * multiplier,
"Value": [conversion_value / multiplier] * multiplier
})

# Add some random variation to make the chart more realistic
for i in range(len(chart_data)):
variation_factor = 0.9 + (random.random() * 0.2)  # Between 0.9 and 1.1
chart_data.loc[i, "Clicks"] *= variation_factor
chart_data.loc[i, "Conversions"] *= variation_factor
chart_data.loc[i, "Value"] *= variation_factor

# Calculate cumulative metrics
chart_data["Cumulative Clicks"] = chart_data["Clicks"].cumsum()
chart_data["Cumulative Conversions"] = chart_data["Conversions"].cumsum()
chart_data["Cumulative Cost"] = chart_data["Cost"].cumsum()
chart_data["Cumulative Value"] = chart_data["Value"].cumsum()
chart_data["Cumulative ROI"] = ((chart_data["Cumulative Value"] - chart_data["Cumulative Cost"]) / chart_data["Cumulative Cost"]) * 100

# Display the chart
st.line_chart(chart_data.set_index("Day")[["Cumulative Clicks", "Cumulative Conversions"]])

# Display ROI chart
st.subheader("ROI Over Time")
st.line_chart(chart_data.set_index("Day")["Cumulative ROI"])

# Optimization recommendations
st.subheader("Optimization Recommendations")

# Generate recommendations based on the ad and performance metrics
recommendations = []

# Check if CTR is low
if ctr_override < 2.0:
recommendations.append({
"title": "Improve Click-Through Rate",
"description": "Your estimated CTR is below average. Consider testing more compelling headlines and stronger calls to action.",
"impact": "High"
})

# Check if conversion rate is low
if conv_rate_override < 3.0:
recommendations.append({
"title": "Enhance Landing Page Experience",
"description": "Your conversion rate could be improved. Ensure your landing page is relevant to your ad and provides a clear path to conversion.",
"impact": "High"
})

# Check if ROI is low
if roi < 100:
recommendations.append({
"title": "Optimize for Higher ROI",
"description": "Your ROI is below target. Consider increasing your conversion value or reducing your cost per click.",
"impact": "Medium"
})

# Check keyword usage
quality_analysis = selected_ad.get("quality_analysis", {})
if quality_analysis.get("improvements"):
for improvement in quality_analysis.get("improvements"):
if "keyword" in improvement.lower():
recommendations.append({
"title": "Improve Keyword Relevance",
"description": improvement,
"impact": "Medium"
})

# Add general recommendations
recommendations.append({
"title": "Test Multiple Ad Variations",
"description": "Continue testing different ad variations to identify the best performing combination of headlines and descriptions.",
"impact": "Medium"
})

recommendations.append({
"title": "Add Ad Extensions",
"description": "Enhance your ad with sitelinks, callouts, and structured snippets to increase visibility and provide additional information.",
"impact": "Medium"
})

# Display recommendations
for i, rec in enumerate(recommendations):
with st.expander(f"{rec['title']} (Impact: {rec['impact']})", expanded=(i==0)):
st.write(rec["description"])

def render_ad_history_tab():
"""Render the Ad History tab with previously generated ads."""

st.subheader("Ad History")
st.write("View and manage your previously generated ads.")

# Check if we have any history
if not st.session_state.ad_history:
st.info("No ad history yet. Generate some ads to see them here.")
return

# Display the history in reverse chronological order
for i, history_item in enumerate(reversed(st.session_state.ad_history)):
with st.expander(f"{history_item['timestamp']} - {history_item['business_name']} ({history_item['industry']})", expanded=(i==0)):
# Display basic info
st.write(f"**Campaign Objective:** {history_item['campaign_objective']}")
st.write(f"**Number of Ads:** {len(history_item['ads'])}")

# Add a button to view the ads
if st.button("View These Ads", key=f"view_history_{i}"):
# Set the current ads to these historical ads
st.session_state.generated_ads = history_item['ads']
st.success("Loaded ads from history. Go to the Ad Creation tab to view them.")

# Add a button to delete from history
if st.button("Delete from History", key=f"delete_history_{i}"):
# Remove this item from history
index_to_remove = len(st.session_state.ad_history) - 1 - i
if 0 <= index_to_remove < len(st.session_state.ad_history):
st.session_state.ad_history.pop(index_to_remove)
st.success("Removed from history.")
st.rerun()

def render_best_practices_tab():
"""Render the Best Practices tab with Google Ads guidelines and tips."""

st.subheader("Google Ads Best Practices")
st.write("Follow these guidelines to create high-performing Google Ads campaigns.")

# Create tabs for different best practice categories
bp_tabs = st.tabs(["Ad Copy", "Keywords", "Landing Pages", "Quality Score", "Extensions"])

with bp_tabs[0]:
st.markdown("""
### Ad Copy Best Practices

#### Headlines
- **Include Primary Keywords**: Place your main keyword in at least one headline
- **Highlight Benefits**: Focus on what the user gains, not just features
- **Use Numbers and Stats**: Specific numbers increase credibility and CTR
- **Create Urgency**: Words like "now," "today," or "limited time" drive action
- **Ask Questions**: Engage users with relevant questions
- **Keep It Short**: Aim for 25-30 characters for better display across devices

#### Descriptions
- **Expand on Headlines**: Provide more details about your offer
- **Include Secondary Keywords**: Incorporate additional relevant keywords
- **Add Specific CTAs**: Tell users exactly what action to take
- **Address Pain Points**: Show how you solve the user's problems
- **Include Proof**: Mention testimonials, reviews, or guarantees
- **Use All Available Space**: Aim for 85-90 characters per description

#### Display Path
- **Include Keywords**: Add relevant keywords to your display path
- **Create Clarity**: Use paths that indicate where users will land
- **Be Specific**: Use product categories or service types
""")

st.info("""
**Pro Tip**: Create at least 5 headlines and 4 descriptions for Responsive Search Ads to give Google's algorithm more options to optimize performance.
""")

with bp_tabs[1]:
st.markdown("""
### Keyword Best Practices

#### Keyword Selection
- **Use Specific Keywords**: More specific keywords typically have higher conversion rates
- **Include Long-Tail Keywords**: These often have less competition and lower CPCs
- **Group by Intent**: Separate keywords by search intent (informational, commercial, transactional)
- **Consider Competitor Keywords**: Include competitor brand terms if your budget allows
- **Use Location Keywords**: Add location-specific terms for local businesses

#### Match Types
- **Broad Match Modified**: Use for wider reach with some control
- **Phrase Match**: Good balance between reach and relevance
- **Exact Match**: Highest relevance but limited reach
- **Use a Mix**: Implement a tiered approach with different match types

#### Negative Keywords
- **Add Irrelevant Terms**: Exclude searches that aren't relevant to your business
- **Filter Out Window Shoppers**: Exclude terms like "free," "cheap," or "DIY" if you're selling premium services
- **Regularly Review Search Terms**: Add new negative keywords based on actual searches
- **Use Negative Keyword Lists**: Create reusable lists for common exclusions
""")

st.info("""
**Pro Tip**: Start with phrase and exact match keywords, then use the Search Terms report to identify new keyword opportunities and negative keywords.
""")

with bp_tabs[2]:
st.markdown("""
### Landing Page Best Practices

#### Relevance
- **Match Ad Copy**: Ensure your landing page content aligns with your ad
- **Use Same Keywords**: Include the same keywords from your ad in your landing page
- **Fulfill the Promise**: Deliver what your ad offered
- **Clear Value Proposition**: Communicate your unique value immediately

#### User Experience
- **Fast Loading Speed**: Optimize for quick loading (under 3 seconds)
- **Mobile Optimization**: Ensure perfect display on all devices
- **Clear Navigation**: Make it easy for users to find what they need
- **Minimal Distractions**: Remove unnecessary elements that don't support conversion

#### Conversion Optimization
- **Prominent CTA**: Make your call-to-action button stand out
- **Reduce Form Fields**: Ask for only essential information
- **Add Trust Signals**: Include testimonials, reviews, and security badges
- **A/B Test**: Continuously test different landing page elements
""")

st.info("""
**Pro Tip**: Create dedicated landing pages for each ad group rather than sending all traffic to your homepage for higher conversion rates.
""")

with bp_tabs[3]:
st.markdown("""
### Quality Score Optimization

#### What Affects Quality Score
- **Click-Through Rate (CTR)**: The most important factor
- **Ad Relevance**: How closely your ad matches the search intent
- **Landing Page Experience**: Relevance, transparency, and navigation
- **Expected Impact**: Google's prediction of how your ad will perform

#### Improving Quality Score
- **Tightly Themed Ad Groups**: Create small, focused ad groups with related keywords
- **Relevant Ad Copy**: Ensure your ads directly address the search query
- **Optimize Landing Pages**: Create specific landing pages for each ad group
- **Improve CTR**: Test different ad variations to find what drives the highest CTR
- **Use Ad Extensions**: Extensions improve visibility and relevance

#### Benefits of High Quality Score
- **Lower Costs**: Higher quality scores can reduce your CPC
- **Better Ad Positions**: Improved rank in the auction
- **Higher ROI**: Better performance for the same budget
""")

st.info("""
**Pro Tip**: A 1-point improvement in Quality Score can reduce your CPC by up to 16% according to industry studies.
""")

with bp_tabs[4]:
st.markdown("""
### Ad Extensions Best Practices

#### Sitelink Extensions
- **Use Descriptive Text**: Clearly explain where each link leads
- **Create Unique Links**: Each sitelink should go to a different landing page
- **Include 6+ Sitelinks**: Give Google options to show the most relevant ones
- **Add Descriptions**: Two description lines provide more context

#### Callout Extensions
- **Highlight Benefits**: Focus on unique selling points
- **Keep It Short**: 12-15 characters is optimal
- **Add 8+ Callouts**: Give Google plenty of options
- **Be Specific**: "24/7 Customer Support" is better than "Great Service"

#### Structured Snippet Extensions
- **Choose Relevant Headers**: Select the most applicable category
- **Add Comprehensive Values**: Include all relevant options
- **Be Concise**: Keep each value short and clear
- **Create Multiple Snippets**: Different headers for different ad groups

#### Other Extensions
- **Call Extensions**: Add your phone number for call-focused campaigns
- **Location Extensions**: Link your Google Business Profile
- **Price Extensions**: Showcase products or services with prices
- **App Extensions**: Promote your mobile app
- **Lead Form Extensions**: Collect leads directly from your ad
""")

st.info("""
**Pro Tip**: Ad extensions are free to add and can significantly increase your ad's CTR by providing additional information and increasing your ad's size on the search results page.
""")

# Additional resources
st.subheader("Additional Resources")

col1, col2, col3 = st.columns(3)

with col1:
st.markdown("""
#### Google Resources
- [Google Ads Help Center](https://support.google.com/google-ads/)
- [Google Ads Best Practices](https://support.google.com/google-ads/topic/3119143)
- [Google Ads Academy](https://skillshop.withgoogle.com/google-ads)
""")

with col2:
st.markdown("""
#### Tools
- [Google Keyword Planner](https://ads.google.com/home/tools/keyword-planner/)
- [Google Ads Editor](https://ads.google.com/home/tools/ads-editor/)
- [Google Ads Preview Tool](https://ads.google.com/aw/tools/ad-preview)
""")

with col3:
st.markdown("""
#### Learning Resources
- [Google Ads Certification](https://skillshop.withgoogle.com/google-ads)
- [Google Ads YouTube Channel](https://www.youtube.com/user/learnwithgoogle)
- [Google Ads Blog](https://blog.google/products/ads/)
""")

if __name__ == "__main__":
write_google_ads()