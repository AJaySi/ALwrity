"""
Ad Analyzer Module

This module provides functions for analyzing and scoring Google Ads.
"""

import re
from typing import Dict, List, Any, Tuple
import random
from urllib.parse import urlparse

def analyze_ad_quality(ad: Dict, primary_keywords: List[str], secondary_keywords: List[str], 
business_name: str, call_to_action: str) -> Dict:
"""
Analyze the quality of a Google Ad based on best practices.

Args:
ad: Dictionary containing ad details
primary_keywords: List of primary keywords
secondary_keywords: List of secondary keywords
business_name: Name of the business
call_to_action: Call to action text

Returns:
Dictionary with analysis results
"""
# Initialize results
strengths = []
improvements = []

# Get ad components
headlines = ad.get("headlines", [])
descriptions = ad.get("descriptions", [])
path1 = ad.get("path1", "")
path2 = ad.get("path2", "")

# Check headline count
if len(headlines) >= 10:
strengths.append("Good number of headlines (10+) for optimization")
elif len(headlines) >= 5:
strengths.append("Adequate number of headlines for testing")
else:
improvements.append("Add more headlines (aim for 10+) to give Google's algorithm more options")

# Check description count
if len(descriptions) >= 4:
strengths.append("Good number of descriptions (4+) for optimization")
elif len(descriptions) >= 2:
strengths.append("Adequate number of descriptions for testing")
else:
improvements.append("Add more descriptions (aim for 4+) to give Google's algorithm more options")

# Check headline length
long_headlines = [h for h in headlines if len(h) > 30]
if long_headlines:
improvements.append(f"{len(long_headlines)} headline(s) exceed 30 characters and may be truncated")
else:
strengths.append("All headlines are within the recommended length")

# Check description length
long_descriptions = [d for d in descriptions if len(d) > 90]
if long_descriptions:
improvements.append(f"{len(long_descriptions)} description(s) exceed 90 characters and may be truncated")
else:
strengths.append("All descriptions are within the recommended length")

# Check keyword usage in headlines
headline_keywords = []
for kw in primary_keywords:
if any(kw.lower() in h.lower() for h in headlines):
headline_keywords.append(kw)

if len(headline_keywords) == len(primary_keywords):
strengths.append("All primary keywords are used in headlines")
elif headline_keywords:
strengths.append(f"{len(headline_keywords)} out of {len(primary_keywords)} primary keywords used in headlines")
missing_kw = [kw for kw in primary_keywords if kw not in headline_keywords]
improvements.append(f"Add these primary keywords to headlines: {', '.join(missing_kw)}")
else:
improvements.append("No primary keywords found in headlines - add keywords to improve relevance")

# Check keyword usage in descriptions
desc_keywords = []
for kw in primary_keywords:
if any(kw.lower() in d.lower() for d in descriptions):
desc_keywords.append(kw)

if len(desc_keywords) == len(primary_keywords):
strengths.append("All primary keywords are used in descriptions")
elif desc_keywords:
strengths.append(f"{len(desc_keywords)} out of {len(primary_keywords)} primary keywords used in descriptions")
missing_kw = [kw for kw in primary_keywords if kw not in desc_keywords]
improvements.append(f"Add these primary keywords to descriptions: {', '.join(missing_kw)}")
else:
improvements.append("No primary keywords found in descriptions - add keywords to improve relevance")

# Check for business name
if any(business_name.lower() in h.lower() for h in headlines):
strengths.append("Business name is included in headlines")
else:
improvements.append("Consider adding your business name to at least one headline")

# Check for call to action
if any(call_to_action.lower() in h.lower() for h in headlines) or any(call_to_action.lower() in d.lower() for d in descriptions):
strengths.append("Call to action is included in the ad")
else:
improvements.append(f"Add your call to action '{call_to_action}' to at least one headline or description")

# Check for numbers and statistics
has_numbers = any(bool(re.search(r'\d+', h)) for h in headlines) or any(bool(re.search(r'\d+', d)) for d in descriptions)
if has_numbers:
strengths.append("Ad includes numbers or statistics which can improve CTR")
else:
improvements.append("Consider adding numbers or statistics to increase credibility and CTR")

# Check for questions
has_questions = any('?' in h for h in headlines) or any('?' in d for d in descriptions)
if has_questions:
strengths.append("Ad includes questions which can engage users")
else:
improvements.append("Consider adding a question to engage users")

# Check for emotional triggers
emotional_words = ['you', 'free', 'because', 'instantly', 'new', 'save', 'proven', 'guarantee', 'love', 'discover']
has_emotional = any(any(word in h.lower() for word in emotional_words) for h in headlines) or \
any(any(word in d.lower() for word in emotional_words) for d in descriptions)

if has_emotional:
strengths.append("Ad includes emotional trigger words which can improve engagement")
else:
improvements.append("Consider adding emotional trigger words to increase engagement")

# Check for path relevance
if any(kw.lower() in path1.lower() or kw.lower() in path2.lower() for kw in primary_keywords):
strengths.append("Display URL paths include keywords which improves relevance")
else:
improvements.append("Add keywords to your display URL paths to improve relevance")

# Return the analysis results
return {
"strengths": strengths,
"improvements": improvements
}

def calculate_quality_score(ad: Dict, primary_keywords: List[str], landing_page: str, ad_type: str) -> Dict:
"""
Calculate a quality score for a Google Ad based on best practices.

Args:
ad: Dictionary containing ad details
primary_keywords: List of primary keywords
landing_page: Landing page URL
ad_type: Type of Google Ad

Returns:
Dictionary with quality score components
"""
# Initialize scores
keyword_relevance = 0
ad_relevance = 0
cta_effectiveness = 0
landing_page_relevance = 0

# Get ad components
headlines = ad.get("headlines", [])
descriptions = ad.get("descriptions", [])
path1 = ad.get("path1", "")
path2 = ad.get("path2", "")

# Calculate keyword relevance (0-10)
# Check if keywords are in headlines, descriptions, and paths
keyword_in_headline = sum(1 for kw in primary_keywords if any(kw.lower() in h.lower() for h in headlines))
keyword_in_description = sum(1 for kw in primary_keywords if any(kw.lower() in d.lower() for d in descriptions))
keyword_in_path = sum(1 for kw in primary_keywords if kw.lower() in path1.lower() or kw.lower() in path2.lower())

# Calculate score based on keyword presence
if len(primary_keywords) > 0:
headline_score = min(10, (keyword_in_headline / len(primary_keywords)) * 10)
description_score = min(10, (keyword_in_description / len(primary_keywords)) * 10)
path_score = min(10, (keyword_in_path / len(primary_keywords)) * 10)

# Weight the scores (headlines most important)
keyword_relevance = (headline_score * 0.6) + (description_score * 0.3) + (path_score * 0.1)
else:
keyword_relevance = 5  # Default score if no keywords provided

# Calculate ad relevance (0-10)
# Check for ad structure and content quality

# Check headline count and length
headline_count_score = min(10, (len(headlines) / 10) * 10)  # Ideal: 10+ headlines
headline_length_score = 10 - min(10, (sum(1 for h in headlines if len(h) > 30) / max(1, len(headlines))) * 10)

# Check description count and length
description_count_score = min(10, (len(descriptions) / 4) * 10)  # Ideal: 4+ descriptions
description_length_score = 10 - min(10, (sum(1 for d in descriptions if len(d) > 90) / max(1, len(descriptions))) * 10)

# Check for emotional triggers, questions, numbers
emotional_words = ['you', 'free', 'because', 'instantly', 'new', 'save', 'proven', 'guarantee', 'love', 'discover']
emotional_score = min(10, sum(1 for h in headlines if any(word in h.lower() for word in emotional_words)) + 
sum(1 for d in descriptions if any(word in d.lower() for word in emotional_words)))

question_score = min(10, (sum(1 for h in headlines if '?' in h) + sum(1 for d in descriptions if '?' in d)) * 2)

number_score = min(10, (sum(1 for h in headlines if bool(re.search(r'\d+', h))) + 
sum(1 for d in descriptions if bool(re.search(r'\d+', d)))) * 2)

# Calculate overall ad relevance score
ad_relevance = (headline_count_score * 0.15) + (headline_length_score * 0.15) + \
(description_count_score * 0.15) + (description_length_score * 0.15) + \
(emotional_score * 0.2) + (question_score * 0.1) + (number_score * 0.1)

# Calculate CTA effectiveness (0-10)
# Check for clear call to action
cta_phrases = ['get', 'buy', 'shop', 'order', 'sign up', 'register', 'download', 'learn', 'discover', 'find', 'call',
'contact', 'request', 'start', 'try', 'join', 'subscribe', 'book', 'schedule', 'apply']

cta_in_headline = any(any(phrase in h.lower() for phrase in cta_phrases) for h in headlines)
cta_in_description = any(any(phrase in d.lower() for phrase in cta_phrases) for d in descriptions)

if cta_in_headline and cta_in_description:
cta_effectiveness = 10
elif cta_in_headline:
cta_effectiveness = 8
elif cta_in_description:
cta_effectiveness = 7
else:
cta_effectiveness = 4

# Calculate landing page relevance (0-10)
# In a real implementation, this would analyze the landing page content
# For this example, we'll use a simplified approach

if landing_page:
# Check if domain seems relevant to keywords
domain = urlparse(landing_page).netloc

# Check if keywords are in the domain or path
keyword_in_url = any(kw.lower() in landing_page.lower() for kw in primary_keywords)

# Check if URL structure seems appropriate
has_https = landing_page.startswith('https://')

# Calculate landing page score
landing_page_relevance = 5  # Base score

if keyword_in_url:
landing_page_relevance += 3

if has_https:
landing_page_relevance += 2

# Cap at 10
landing_page_relevance = min(10, landing_page_relevance)
else:
landing_page_relevance = 5  # Default score if no landing page provided

# Calculate overall quality score (0-10)
overall_score = (keyword_relevance * 0.4) + (ad_relevance * 0.3) + (cta_effectiveness * 0.2) + (landing_page_relevance * 0.1)

# Calculate estimated CTR based on quality score
# This is a simplified model - in reality, CTR depends on many factors
base_ctr = {
"Responsive Search Ad": 3.17,
"Expanded Text Ad": 2.83,
"Call-Only Ad": 3.48,
"Dynamic Search Ad": 2.69
}.get(ad_type, 3.0)

# Adjust CTR based on quality score (±50%)
quality_factor = (overall_score - 5) / 5  # -1 to 1
estimated_ctr = base_ctr * (1 + (quality_factor * 0.5))

# Calculate estimated conversion rate
# Again, this is simplified - actual conversion rates depend on many factors
base_conversion_rate = 3.75  # Average conversion rate for search ads

# Adjust conversion rate based on quality score (±40%)
estimated_conversion_rate = base_conversion_rate * (1 + (quality_factor * 0.4))

# Return the quality score components
return {
"keyword_relevance": round(keyword_relevance, 1),
"ad_relevance": round(ad_relevance, 1),
"cta_effectiveness": round(cta_effectiveness, 1),
"landing_page_relevance": round(landing_page_relevance, 1),
"overall_score": round(overall_score, 1),
"estimated_ctr": round(estimated_ctr, 2),
"estimated_conversion_rate": round(estimated_conversion_rate, 2)
}

def analyze_keyword_relevance(keywords: List[str], ad_text: str) -> Dict:
"""
Analyze the relevance of keywords to ad text.

Args:
keywords: List of keywords to analyze
ad_text: Combined ad text (headlines and descriptions)

Returns:
Dictionary with keyword relevance analysis
"""
results = {}

for keyword in keywords:
# Check if keyword is in ad text
is_present = keyword.lower() in ad_text.lower()

# Check if keyword is in the first 100 characters
is_in_beginning = keyword.lower() in ad_text.lower()[:100]

# Count occurrences
occurrences = ad_text.lower().count(keyword.lower())

# Calculate density
density = (occurrences * len(keyword)) / len(ad_text) * 100 if len(ad_text) > 0 else 0

# Store results
results[keyword] = {
"present": is_present,
"in_beginning": is_in_beginning,
"occurrences": occurrences,
"density": round(density, 2),
"optimal_density": 0.5 <= density <= 2.5
}

return results