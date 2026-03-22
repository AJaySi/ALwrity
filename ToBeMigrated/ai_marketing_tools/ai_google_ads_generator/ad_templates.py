"""
Ad Templates Module

This module provides templates for different ad types and industries.
"""

from typing import Dict, List, Any

def get_industry_templates(industry: str) -> Dict:
"""
Get ad templates specific to an industry.

Args:
industry: The industry to get templates for

Returns:
Dictionary with industry-specific templates
"""
# Define templates for different industries
templates = {
"E-commerce": {
"headline_templates": [
"{product} - {benefit} | {business_name}",
"Shop {product} - {discount} Off Today",
"Top-Rated {product} - Free Shipping",
"{benefit} with Our {product}",
"New {product} Collection - {benefit}",
"{discount}% Off {product} - Limited Time",
"Buy {product} Online - Fast Delivery",
"{product} Sale Ends {timeframe}",
"Best-Selling {product} from {business_name}",
"Premium {product} - {benefit}"
],
"description_templates": [
"Shop our selection of {product} and enjoy {benefit}. Free shipping on orders over ${amount}. Order now!",
"Looking for quality {product}? Get {benefit} with our {product}. {discount} off your first order!",
"{business_name} offers premium {product} with {benefit}. Shop online or visit our store today!",
"Discover our {product} collection. {benefit} guaranteed or your money back. Order now and save {discount}!"
],
"emotional_triggers": ["exclusive", "limited time", "sale", "discount", "free shipping", "bestseller", "new arrival"],
"call_to_actions": ["Shop Now", "Buy Today", "Order Online", "Get Yours", "Add to Cart", "Save Today"]
},
"SaaS/Technology": {
"headline_templates": [
"{product} Software - {benefit}",
"Try {product} Free for {timeframe}",
"{benefit} with Our {product} Platform",
"{product} - Rated #1 for {feature}",
"New {feature} in Our {product} Software",
"{business_name} - {benefit} Software",
"Streamline {pain_point} with {product}",
"{product} Software - {discount} Off",
"Enterprise-Grade {product} for {audience}",
"{product} - {benefit} Guaranteed"
],
"description_templates": [
"{business_name}'s {product} helps you {benefit}. Try it free for {timeframe}. No credit card required.",
"Struggling with {pain_point}? Our {product} provides {benefit}. Join {number}+ satisfied customers.",
"Our {product} platform offers {feature} to help you {benefit}. Rated {rating}/5 by {source}.",
"{product} by {business_name}: {benefit} for your business. Plans starting at ${price}/month."
],
"emotional_triggers": ["efficient", "time-saving", "seamless", "integrated", "secure", "scalable", "innovative"],
"call_to_actions": ["Start Free Trial", "Request Demo", "Learn More", "Sign Up Free", "Get Started", "See Plans"]
},
"Healthcare": {
"headline_templates": [
"{service} in {location} | {business_name}",
"Expert {service} - {benefit}",
"Quality {service} for {audience}",
"{business_name} - {credential} {professionals}",
"Same-Day {service} Appointments",
"{service} Specialists in {location}",
"Affordable {service} - {benefit}",
"{symptom}? Get {service} Today",
"Advanced {service} Technology",
"Compassionate {service} Care"
],
"description_templates": [
"{business_name} provides expert {service} with {benefit}. Our {credential} team is ready to help. Schedule today!",
"Experiencing {symptom}? Our {professionals} offer {service} with {benefit}. Most insurance accepted.",
"Quality {service} in {location}. {benefit} from our experienced team. Call now to schedule your appointment.",
"Our {service} center provides {benefit} for {audience}. Open {days} with convenient hours."
],
"emotional_triggers": ["trusted", "experienced", "compassionate", "advanced", "personalized", "comprehensive", "gentle"],
"call_to_actions": ["Schedule Now", "Book Appointment", "Call Today", "Free Consultation", "Learn More", "Find Relief"]
},
"Real Estate": {
"headline_templates": [
"{property_type} in {location} | {business_name}",
"{property_type} for {price_range} - {location}",
"Find Your Dream {property_type} in {location}",
"{feature} {property_type} - {location}",
"New {property_type} Listings in {location}",
"Sell Your {property_type} in {timeframe}",
"{business_name} - {credential} {professionals}",
"{property_type} {benefit} - {location}",
"Exclusive {property_type} Listings",
"{number}+ {property_type} Available Now"
],
"description_templates": [
"Looking for {property_type} in {location}? {business_name} offers {benefit}. Browse our listings or call us today!",
"Sell your {property_type} in {location} with {business_name}. Our {professionals} provide {benefit}. Free valuation!",
"{business_name}: {credential} {professionals} helping you find the perfect {property_type} in {location}. Call now!",
"Discover {feature} {property_type} in {location}. Prices from {price_range}. Schedule a viewing today!"
],
"emotional_triggers": ["dream home", "exclusive", "luxury", "investment", "perfect location", "spacious", "modern"],
"call_to_actions": ["View Listings", "Schedule Viewing", "Free Valuation", "Call Now", "Learn More", "Get Pre-Approved"]
}
}

# Return templates for the specified industry, or a default if not found
return templates.get(industry, {
"headline_templates": [
"{product/service} - {benefit} | {business_name}",
"Professional {product/service} - {benefit}",
"{benefit} with Our {product/service}",
"{business_name} - {credential} {product/service}",
"Quality {product/service} for {audience}",
"Affordable {product/service} - {benefit}",
"{product/service} in {location}",
"{feature} {product/service} by {business_name}",
"Experienced {product/service} Provider",
"{product/service} - Satisfaction Guaranteed"
],
"description_templates": [
"{business_name} offers professional {product/service} with {benefit}. Contact us today to learn more!",
"Looking for quality {product/service}? {business_name} provides {benefit}. Call now for more information.",
"Our {product/service} helps you {benefit}. Trusted by {number}+ customers. Contact us today!",
"{business_name}: {credential} {product/service} provider. We offer {benefit} for {audience}. Learn more!"
],
"emotional_triggers": ["professional", "quality", "trusted", "experienced", "affordable", "reliable", "satisfaction"],
"call_to_actions": ["Contact Us", "Learn More", "Call Now", "Get Quote", "Visit Website", "Schedule Consultation"]
})

def get_ad_type_templates(ad_type: str) -> Dict:
"""
Get templates specific to an ad type.

Args:
ad_type: The ad type to get templates for

Returns:
Dictionary with ad type-specific templates
"""
# Define templates for different ad types
templates = {
"Responsive Search Ad": {
"headline_count": 15,
"description_count": 4,
"headline_max_length": 30,
"description_max_length": 90,
"best_practices": [
"Include at least 3 headlines with keywords",
"Create headlines with different lengths",
"Include at least 1 headline with a call to action",
"Include at least 1 headline with your brand name",
"Create descriptions that complement each other",
"Include keywords in at least 2 descriptions",
"Include a call to action in at least 1 description"
]
},
"Expanded Text Ad": {
"headline_count": 3,
"description_count": 2,
"headline_max_length": 30,
"description_max_length": 90,
"best_practices": [
"Include keywords in Headline 1",
"Use a call to action in Headline 2 or 3",
"Include your brand name in one headline",
"Make descriptions complementary but able to stand alone",
"Include keywords in at least one description",
"Include a call to action in at least one description"
]
},
"Call-Only Ad": {
"headline_count": 2,
"description_count": 2,
"headline_max_length": 30,
"description_max_length": 90,
"best_practices": [
"Focus on encouraging phone calls",
"Include language like 'Call now', 'Speak to an expert', etc.",
"Mention phone availability (e.g., '24/7', 'Available now')",
"Include benefits of calling rather than clicking",
"Be clear about who will answer the call",
"Include any special offers for callers"
]
},
"Dynamic Search Ad": {
"headline_count": 0,  # Headlines are dynamically generated
"description_count": 2,
"headline_max_length": 0,  # N/A
"description_max_length": 90,
"best_practices": [
"Create descriptions that work with any dynamically generated headline",
"Focus on your unique selling points",
"Include a strong call to action",
"Highlight benefits that apply across your product/service range",
"Avoid specific product mentions that might not match the dynamic headline"
]
}
}

# Return templates for the specified ad type, or a default if not found
return templates.get(ad_type, {
"headline_count": 3,
"description_count": 2,
"headline_max_length": 30,
"description_max_length": 90,
"best_practices": [
"Include keywords in headlines",
"Use a call to action",
"Include your brand name",
"Make descriptions informative and compelling",
"Include keywords in descriptions",
"Highlight unique selling points"
]
})