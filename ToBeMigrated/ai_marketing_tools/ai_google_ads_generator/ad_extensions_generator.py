"""
Ad Extensions Generator Module

This module provides functions for generating various types of Google Ads extensions.
"""

from typing import Dict, List, Any, Optional
import re
from ...gpt_providers.text_generation.main_text_generation import llm_text_gen

def generate_extensions(business_name: str, business_description: str, industry: str, 
primary_keywords: List[str], unique_selling_points: List[str],
landing_page: str) -> Dict:
"""
Generate a complete set of ad extensions based on business information.

Args:
business_name: Name of the business
business_description: Description of the business
industry: Industry of the business
primary_keywords: List of primary keywords
unique_selling_points: List of unique selling points
landing_page: Landing page URL

Returns:
Dictionary with generated extensions
"""
# Generate sitelinks
sitelinks = generate_sitelinks(business_name, business_description, industry, primary_keywords, landing_page)

# Generate callouts
callouts = generate_callouts(business_name, unique_selling_points, industry)

# Generate structured snippets
snippets = generate_structured_snippets(business_name, business_description, industry, primary_keywords)

# Return all extensions
return {
"sitelinks": sitelinks,
"callouts": callouts,
"structured_snippets": snippets
}

def generate_sitelinks(business_name: str, business_description: str, industry: str, 
primary_keywords: List[str], landing_page: str) -> List[Dict]:
"""
Generate sitelink extensions based on business information.

Args:
business_name: Name of the business
business_description: Description of the business
industry: Industry of the business
primary_keywords: List of primary keywords
landing_page: Landing page URL

Returns:
List of dictionaries with sitelink information
"""
# Define common sitelink types by industry
industry_sitelinks = {
"E-commerce": ["Shop Now", "Best Sellers", "New Arrivals", "Sale Items", "Customer Reviews", "About Us"],
"SaaS/Technology": ["Features", "Pricing", "Demo", "Case Studies", "Support", "Blog"],
"Healthcare": ["Services", "Locations", "Providers", "Insurance", "Patient Portal", "Contact Us"],
"Education": ["Programs", "Admissions", "Campus", "Faculty", "Student Life", "Apply Now"],
"Finance": ["Services", "Rates", "Calculators", "Locations", "Apply Now", "About Us"],
"Real Estate": ["Listings", "Sell Your Home", "Neighborhoods", "Agents", "Mortgage", "Contact Us"],
"Legal": ["Practice Areas", "Attorneys", "Results", "Testimonials", "Free Consultation", "Contact"],
"Travel": ["Destinations", "Deals", "Book Now", "Reviews", "FAQ", "Contact Us"],
"Food & Beverage": ["Menu", "Locations", "Order Online", "Reservations", "Catering", "About Us"]
}

# Get sitelinks for the specified industry, or use default
sitelink_types = industry_sitelinks.get(industry, ["About Us", "Services", "Products", "Contact Us", "Testimonials", "FAQ"])

# Generate sitelinks
sitelinks = []
base_url = landing_page.rstrip('/') if landing_page else ""

for sitelink_type in sitelink_types:
# Generate URL path based on sitelink type
path = sitelink_type.lower().replace(' ', '-')
url = f"{base_url}/{path}" if base_url else f"https://example.com/{path}"

# Generate description based on sitelink type
description = ""
if sitelink_type == "About Us":
description = f"Learn more about {business_name} and our mission."
elif sitelink_type == "Services" or sitelink_type == "Products":
description = f"Explore our range of {primary_keywords[0] if primary_keywords else 'offerings'}."
elif sitelink_type == "Contact Us":
description = f"Get in touch with our team for assistance."
elif sitelink_type == "Testimonials" or sitelink_type == "Reviews":
description = f"See what our customers say about us."
elif sitelink_type == "FAQ":
description = f"Find answers to common questions."
elif sitelink_type == "Pricing" or sitelink_type == "Rates":
description = f"View our competitive pricing options."
elif sitelink_type == "Shop Now" or sitelink_type == "Order Online":
description = f"Browse and purchase our {primary_keywords[0] if primary_keywords else 'products'} online."

# Add the sitelink
sitelinks.append({
"text": sitelink_type,
"url": url,
"description": description
})

return sitelinks

def generate_callouts(business_name: str, unique_selling_points: List[str], industry: str) -> List[str]:
"""
Generate callout extensions based on business information.

Args:
business_name: Name of the business
unique_selling_points: List of unique selling points
industry: Industry of the business

Returns:
List of callout texts
"""
# Use provided USPs if available
if unique_selling_points and len(unique_selling_points) >= 4:
# Ensure callouts are not too long (25 characters max)
callouts = []
for usp in unique_selling_points:
if len(usp) <= 25:
callouts.append(usp)
else:
# Try to truncate at a space
truncated = usp[:22] + "..."
callouts.append(truncated)

return callouts[:8]  # Return up to 8 callouts

# Define common callouts by industry
industry_callouts = {
"E-commerce": ["Free Shipping", "24/7 Customer Service", "Secure Checkout", "Easy Returns", "Price Match Guarantee", "Next Day Delivery", "Satisfaction Guaranteed", "Exclusive Deals"],
"SaaS/Technology": ["24/7 Support", "Free Trial", "No Credit Card Required", "Easy Integration", "Data Security", "Cloud-Based", "Regular Updates", "Customizable"],
"Healthcare": ["Board Certified", "Most Insurance Accepted", "Same-Day Appointments", "Compassionate Care", "State-of-the-Art Facility", "Experienced Staff", "Convenient Location", "Telehealth Available"],
"Education": ["Accredited Programs", "Expert Faculty", "Financial Aid", "Career Services", "Small Class Sizes", "Flexible Schedule", "Online Options", "Hands-On Learning"],
"Finance": ["FDIC Insured", "No Hidden Fees", "Personalized Service", "Online Banking", "Mobile App", "Low Interest Rates", "Financial Planning", "Retirement Services"],
"Real Estate": ["Free Home Valuation", "Virtual Tours", "Experienced Agents", "Local Expertise", "Financing Available", "Property Management", "Commercial & Residential", "Investment Properties"],
"Legal": ["Free Consultation", "No Win No Fee", "Experienced Attorneys", "24/7 Availability", "Proven Results", "Personalized Service", "Multiple Practice Areas", "Aggressive Representation"]
}

# Get callouts for the specified industry, or use default
callouts = industry_callouts.get(industry, ["Professional Service", "Experienced Team", "Customer Satisfaction", "Quality Guaranteed", "Competitive Pricing", "Fast Service", "Personalized Solutions", "Trusted Provider"])

return callouts

def generate_structured_snippets(business_name: str, business_description: str, industry: str, primary_keywords: List[str]) -> Dict:
"""
Generate structured snippet extensions based on business information.

Args:
business_name: Name of the business
business_description: Description of the business
industry: Industry of the business
primary_keywords: List of primary keywords

Returns:
Dictionary with structured snippet information
"""
# Define common snippet headers and values by industry
industry_snippets = {
"E-commerce": {
"header": "Brands",
"values": ["Nike", "Adidas", "Apple", "Samsung", "Sony", "LG", "Dell", "HP"]
},
"SaaS/Technology": {
"header": "Services",
"values": ["Cloud Storage", "Data Analytics", "CRM", "Project Management", "Email Marketing", "Cybersecurity", "API Integration", "Automation"]
},
"Healthcare": {
"header": "Services",
"values": ["Preventive Care", "Diagnostics", "Treatment", "Surgery", "Rehabilitation", "Counseling", "Telemedicine", "Wellness Programs"]
},
"Education": {
"header": "Courses",
"values": ["Business", "Technology", "Healthcare", "Design", "Engineering", "Education", "Arts", "Sciences"]
},
"Finance": {
"header": "Services",
"values": ["Checking Accounts", "Savings Accounts", "Loans", "Mortgages", "Investments", "Retirement Planning", "Insurance", "Wealth Management"]
},
"Real Estate": {
"header": "Types",
"values": ["Single-Family Homes", "Condos", "Townhouses", "Apartments", "Commercial", "Land", "New Construction", "Luxury Homes"]
},
"Legal": {
"header": "Services",
"values": ["Personal Injury", "Family Law", "Criminal Defense", "Estate Planning", "Business Law", "Immigration", "Real Estate Law", "Intellectual Property"]
}
}

# Get snippets for the specified industry, or use default
snippet_info = industry_snippets.get(industry, {
"header": "Services",
"values": ["Consultation", "Assessment", "Implementation", "Support", "Maintenance", "Training", "Customization", "Analysis"]
})

# If we have primary keywords, try to incorporate them
if primary_keywords:
# Try to determine a better header based on keywords
service_keywords = ["service", "support", "consultation", "assistance", "help"]
product_keywords = ["product", "item", "good", "merchandise"]
brand_keywords = ["brand", "make", "manufacturer"]

for kw in primary_keywords:
kw_lower = kw.lower()
if any(service_word in kw_lower for service_word in service_keywords):
snippet_info["header"] = "Services"
break
elif any(product_word in kw_lower for product_word in product_keywords):
snippet_info["header"] = "Products"
break
elif any(brand_word in kw_lower for brand_word in brand_keywords):
snippet_info["header"] = "Brands"
break

return snippet_info

def generate_custom_extensions(business_info: Dict, extension_type: str) -> Any:
"""
Generate custom extensions using AI based on business information.

Args:
business_info: Dictionary with business information
extension_type: Type of extension to generate

Returns:
Generated extension data
"""
# Extract business information
business_name = business_info.get("business_name", "")
business_description = business_info.get("business_description", "")
industry = business_info.get("industry", "")
primary_keywords = business_info.get("primary_keywords", [])
unique_selling_points = business_info.get("unique_selling_points", [])

# Create a prompt based on extension type
if extension_type == "sitelinks":
prompt = f"""
Generate 6 sitelink extensions for a Google Ads campaign for the following business:

Business Name: {business_name}
Business Description: {business_description}
Industry: {industry}
Keywords: {', '.join(primary_keywords)}

For each sitelink, provide:
1. Link text (max 25 characters)
2. Description line 1 (max 35 characters)
3. Description line 2 (max 35 characters)

Format the response as a JSON array of objects with "text", "description1", and "description2" fields.
"""
elif extension_type == "callouts":
prompt = f"""
Generate 8 callout extensions for a Google Ads campaign for the following business:

Business Name: {business_name}
Business Description: {business_description}
Industry: {industry}
Keywords: {', '.join(primary_keywords)}
Unique Selling Points: {', '.join(unique_selling_points)}

Each callout should:
1. Be 25 characters or less
2. Highlight a feature, benefit, or unique selling point
3. Be concise and impactful

Format the response as a JSON array of strings.
"""
elif extension_type == "structured_snippets":
prompt = f"""
Generate structured snippet extensions for a Google Ads campaign for the following business:

Business Name: {business_name}
Business Description: {business_description}
Industry: {industry}
Keywords: {', '.join(primary_keywords)}

Provide:
1. The most appropriate header type (e.g., Brands, Services, Products, Courses, etc.)
2. 8 values that are relevant to the business (each 25 characters or less)

Format the response as a JSON object with "header" and "values" fields.
"""
else:
return None

# Generate the extensions using the LLM
try:
response = llm_text_gen(prompt)

# Process the response based on extension type
# In a real implementation, you would parse the JSON response
# For this example, we'll return a placeholder

if extension_type == "sitelinks":
return [
{"text": "About Us", "description1": "Learn about our company", "description2": "Our history and mission"},
{"text": "Services", "description1": "Explore our service offerings", "description2": "Solutions for your needs"},
{"text": "Products", "description1": "Browse our product catalog", "description2": "Quality items at great prices"},
{"text": "Contact Us", "description1": "Get in touch with our team", "description2": "We're here to help you"},
{"text": "Testimonials", "description1": "See what customers say", "description2": "Real reviews from real people"},
{"text": "FAQ", "description1": "Frequently asked questions", "description2": "Find quick answers here"}
]
elif extension_type == "callouts":
return ["Free Shipping", "24/7 Support", "Money-Back Guarantee", "Expert Team", "Premium Quality", "Fast Service", "Affordable Prices", "Satisfaction Guaranteed"]
elif extension_type == "structured_snippets":
return {"header": "Services", "values": ["Consultation", "Installation", "Maintenance", "Repair", "Training", "Support", "Design", "Analysis"]}
else:
return None

except Exception as e:
print(f"Error generating extensions: {str(e)}")
return None