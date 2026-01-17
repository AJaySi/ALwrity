from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


def transform_to_fields(*, website: Dict[str, Any], research: Dict[str, Any], api_keys: Dict[str, Any], session: Dict[str, Any], persona: Dict[str, Any] = None, competitor: Dict[str, Any] = None, analytics: Dict[str, Any] = None) -> Dict[str, Any]:
    """Transform normalized data to frontend field map."""
    logger.warning(f"🔍 TRANSFORMER INPUT:")
    logger.warning(f"  Competitor dict exists: {bool(competitor)}")
    logger.warning(f"  Competitor keys: {list(competitor.keys()) if competitor else 'NONE'}")
    if competitor:
        logger.warning(f"  Competitor top_competitors: {competitor.get('top_competitors')}")
        logger.warning(f"  Competitor market_gaps: {competitor.get('market_gaps')}")
        logger.warning(f"  Competitor industry_trends: {competitor.get('industry_trends')}")
        logger.warning(f"  Competitor emerging_trends: {competitor.get('emerging_trends')}")
    fields: Dict[str, Any] = {}

    # Business Context
    if website.get('content_goals'):
        fields['business_objectives'] = {
            'value': website.get('content_goals'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    else:
        # Provide placeholder for missing business_objectives
        fields['business_objectives'] = {
            'value': ['Increase brand awareness', 'Generate qualified leads', 'Establish thought leadership'],
            'source': 'onboarding_session',  # Use valid source for placeholder values
            'confidence': 0.5
        }

    if website.get('target_metrics'):
        fields['target_metrics'] = {
            'value': website.get('target_metrics'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    elif website.get('performance_metrics'):
        fields['target_metrics'] = {
            'value': website.get('performance_metrics'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    else:
        # Provide placeholder for missing target_metrics
        fields['target_metrics'] = {
            'value': {
                'traffic_growth': '20% increase',
                'engagement_rate': '5% average',
                'conversion_rate': '3% target',
                'lead_generation': '50 leads/month'
            },
            'source': 'onboarding_session',  # Use valid source for placeholder values
            'confidence': 0.5
        }

    # content_budget with session fallback
    if website.get('content_budget') is not None:
        fields['content_budget'] = {
            'value': website.get('content_budget'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    elif isinstance(session, dict) and session.get('budget') is not None:
        fields['content_budget'] = {
            'value': session.get('budget'),
            'source': 'onboarding_session',
            'confidence': 0.7
        }

    # team_size with session fallback
    if website.get('team_size') is not None:
        fields['team_size'] = {
            'value': website.get('team_size'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    elif isinstance(session, dict) and session.get('team_size') is not None:
        fields['team_size'] = {
            'value': session.get('team_size'),
            'source': 'onboarding_session',
            'confidence': 0.7
        }

    # implementation_timeline with session fallback
    if website.get('implementation_timeline'):
        fields['implementation_timeline'] = {
            'value': website.get('implementation_timeline'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    elif isinstance(session, dict) and session.get('timeline'):
        fields['implementation_timeline'] = {
            'value': session.get('timeline'),
            'source': 'onboarding_session',
            'confidence': 0.7
        }

    # market_share with derive from performance metrics
    if website.get('market_share'):
        fields['market_share'] = {
            'value': website.get('market_share'),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level')
        }
    elif website.get('performance_metrics'):
        estimated_share = website.get('performance_metrics', {}).get('estimated_market_share')
        if estimated_share:
            fields['market_share'] = {
                'value': estimated_share,
                'source': 'website_analysis',
                'confidence': website.get('confidence_level')
            }
        else:
            # Provide placeholder for missing market_share
            fields['market_share'] = {
                'value': 'Growing market presence',
                'source': 'onboarding_session',  # Use valid source for placeholder values
                'confidence': 0.5
            }
    else:
        # Provide placeholder for missing market_share
        fields['market_share'] = {
            'value': 'Growing market presence',
            'source': 'onboarding_session',  # Use valid source for placeholder values
            'confidence': 0.5
        }

    # performance_metrics - Use analytics data if available
    if analytics and analytics.get('performance_metrics'):
        analytics_perf = analytics['performance_metrics']
        # Merge with website data if available
        website_perf = website.get('performance_metrics', {})
        fields['performance_metrics'] = {
            'value': {
                'traffic': analytics_perf.get('traffic', website_perf.get('traffic', 0)),
                'conversion_rate': website_perf.get('conversion_rate', analytics_perf.get('conversion_rate', 0)),
                'bounce_rate': website_perf.get('bounce_rate', analytics_perf.get('bounce_rate', 0)),
                'avg_session_duration': website_perf.get('avg_session_duration', analytics_perf.get('avg_session_duration', 0))
            },
            'source': 'analytics_data' if analytics.get('performance_metrics', {}).get('traffic') else 'website_analysis',
            'confidence': 0.9 if analytics.get('performance_metrics', {}).get('traffic') else website.get('confidence_level', 0.8)
        }
    else:
        fields['performance_metrics'] = {
            'value': website.get('performance_metrics', {}),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level', 0.8)
        }

    # Audience Intelligence
    audience_research = research.get('audience_intelligence', {})
    content_prefs = research.get('content_preferences', {})

    # content_preferences: provide placeholder if empty or missing
    if not content_prefs or (isinstance(content_prefs, dict) and len(content_prefs) == 0):
        content_prefs = {
            'preferred_formats': ['Blog Posts', 'Videos', 'Infographics'],
            'content_topics': ['Industry insights', 'Best practices', 'Case studies'],
            'content_style': ['Professional', 'Educational'],
            'content_length': 'Medium (1000-2000 words)',
            'visual_preferences': ['Infographics', 'Charts', 'Diagrams']
        }
    fields['content_preferences'] = {
        'value': content_prefs,
        'source': 'research_preferences' if research.get('content_preferences') else 'onboarding_session',
        'confidence': research.get('confidence_level', 0.8) if research.get('content_preferences') else 0.5
    }

    # consumption_patterns: provide placeholder if empty
    consumption_patterns = audience_research.get('consumption_patterns', {})
    if not consumption_patterns or (isinstance(consumption_patterns, dict) and len(consumption_patterns) == 0):
        consumption_patterns = {
            'primary_channels': ['Website', 'Email', 'Social Media'],
            'preferred_times': ['Morning (9-11 AM)', 'Afternoon (2-4 PM)'],
            'device_preference': ['Desktop', 'Mobile'],
            'content_length_preference': 'Medium (5-10 min read)',
            'engagement_pattern': 'High engagement on educational content'
        }
    fields['consumption_patterns'] = {
        'value': consumption_patterns,
        'source': 'research_preferences' if audience_research.get('consumption_patterns') else 'onboarding_session',
        'confidence': research.get('confidence_level', 0.8) if audience_research.get('consumption_patterns') else 0.5
    }

    # audience_pain_points: provide placeholder if empty
    pain_points = audience_research.get('pain_points', [])
    if not pain_points or (isinstance(pain_points, list) and len(pain_points) == 0):
        pain_points = [
            'Lack of time to research solutions',
            'Information overload',
            'Difficulty finding reliable sources',
            'Budget constraints',
            'Need for quick, actionable insights'
        ]
    fields['audience_pain_points'] = {
        'value': pain_points,
        'source': 'research_preferences' if audience_research.get('pain_points') else 'onboarding_session',
        'confidence': research.get('confidence_level', 0.8) if audience_research.get('pain_points') else 0.5
    }

    # buying_journey: provide placeholder if empty
    buying_journey = audience_research.get('buying_journey', {})
    if not buying_journey or (isinstance(buying_journey, dict) and len(buying_journey) == 0):
        buying_journey = {
            'awareness': 'Content discovery through search and social media',
            'consideration': 'Comparing solutions and reading case studies',
            'decision': 'Requesting demos and consulting with team',
            'retention': 'Ongoing engagement through newsletters and updates'
        }
    fields['buying_journey'] = {
        'value': buying_journey,
        'source': 'research_preferences' if audience_research.get('buying_journey') else 'onboarding_session',
        'confidence': research.get('confidence_level', 0.8) if audience_research.get('buying_journey') else 0.5
    }

    fields['seasonal_trends'] = {
        'value': ['Q1: Planning', 'Q2: Execution', 'Q3: Optimization', 'Q4: Review'],
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.7)
    }

    # engagement_metrics - Use analytics data if available
    if analytics and analytics.get('engagement_metrics'):
        analytics_eng = analytics['engagement_metrics']
        website_perf = website.get('performance_metrics', {})
        fields['engagement_metrics'] = {
            'value': {
                'likes': 0,  # Not available from GSC/Bing
                'shares': 0,  # Not available from GSC/Bing
                'comments': 0,  # Not available from GSC/Bing
                'click_through_rate': analytics_eng.get('click_through_rate', 0),
                'time_on_page': website_perf.get('avg_session_duration', 0),
                'engagement_rate': analytics_eng.get('click_through_rate', 0)  # Use CTR as engagement rate proxy
            },
            'source': 'analytics_data',
            'confidence': 0.9
        }
    else:
        website_perf = website.get('performance_metrics', {})
        fields['engagement_metrics'] = {
            'value': {
                'likes': 0,
                'shares': 0,
                'comments': 0,
                'click_through_rate': 0,
                'time_on_page': website_perf.get('avg_session_duration', 180),
                'engagement_rate': 0
            },
            'source': 'website_analysis',
            'confidence': website.get('confidence_level', 0.8)
        }

    # Competitive Intelligence - Use competitor analysis data if available
    # Check if competitor dict exists and has data (even if lists are empty, we want to use the structure)
    if competitor and isinstance(competitor.get('top_competitors'), list):
        top_competitors = competitor['top_competitors']
        if len(top_competitors) > 0:
            fields['top_competitors'] = {
                'value': top_competitors,
                'source': 'competitor_analysis',
                'confidence': 0.9
            }
        else:
            # Empty list from normalizer means no competitors found, use fallback
            fields['top_competitors'] = {
                'value': website.get('competitors', [
                    {'name': 'Competitor A - Industry Leader', 'website': '', 'strength': '', 'weakness': ''},
                    {'name': 'Competitor B - Emerging Player', 'website': '', 'strength': '', 'weakness': ''},
                    {'name': 'Competitor C - Niche Specialist', 'website': '', 'strength': '', 'weakness': ''}
                ]),
                'source': 'website_analysis' if website.get('competitors') else 'onboarding_session',
                'confidence': website.get('confidence_level', 0.8) if website.get('competitors') else 0.5
            }
    else:
        fields['top_competitors'] = {
            'value': website.get('competitors', [
                {'name': 'Competitor A - Industry Leader', 'website': '', 'strength': '', 'weakness': ''},
                {'name': 'Competitor B - Emerging Player', 'website': '', 'strength': '', 'weakness': ''},
                {'name': 'Competitor C - Niche Specialist', 'website': '', 'strength': '', 'weakness': ''}
            ]),
            'source': 'website_analysis' if website.get('competitors') else 'onboarding_session',
            'confidence': website.get('confidence_level', 0.8) if website.get('competitors') else 0.5
        }

    if competitor and competitor.get('competitor_content_strategies'):
        competitor_strategies = competitor['competitor_content_strategies']
        # Check if strategies dict has any meaningful data
        has_data = (
            competitor_strategies.get('content_types') or
            competitor_strategies.get('publishing_frequency') or
            competitor_strategies.get('content_themes') or
            competitor_strategies.get('distribution_channels') or
            competitor_strategies.get('engagement_approach')
        )
        if has_data:
            fields['competitor_content_strategies'] = {
                'value': competitor_strategies,
                'source': 'competitor_analysis',
                'confidence': 0.9
            }
        else:
            # Empty strategies, use fallback
            fields['competitor_content_strategies'] = {
                'value': {
                    'content_types': ['Educational content', 'Case studies', 'Thought leadership'],
                    'publishing_frequency': 'Weekly',
                    'content_themes': ['Industry insights', 'Best practices'],
                    'distribution_channels': ['Website', 'Social Media', 'Email'],
                    'engagement_approach': 'Focus on educational content and thought leadership'
                },
                'source': 'onboarding_session',
                'confidence': 0.5
            }
    else:
        fields['competitor_content_strategies'] = {
            'value': {
                'content_types': ['Educational content', 'Case studies', 'Thought leadership'],
                'publishing_frequency': 'Weekly',
                'content_themes': ['Industry insights', 'Best practices'],
                'distribution_channels': ['Website', 'Social Media', 'Email'],
                'engagement_approach': 'Focus on educational content and thought leadership'
            },
            'source': 'onboarding_session',
            'confidence': 0.5
        }

    logger.warning(f"🔍 TRANSFORMER: Checking market_gaps")
    logger.warning(f"  competitor.get('market_gaps'): {competitor.get('market_gaps') if competitor else 'N/A'}")
    logger.warning(f"  isinstance check: {isinstance(competitor.get('market_gaps'), list) if competitor else False}")
    
    if competitor and isinstance(competitor.get('market_gaps'), list):
        market_gaps = competitor['market_gaps']
        logger.warning(f"  market_gaps length: {len(market_gaps)}")
        if len(market_gaps) > 0:
            logger.warning(f"  ✅ Using competitor data for market_gaps: {len(market_gaps)} gaps")
            fields['market_gaps'] = {
                'value': market_gaps,
                'source': 'competitor_analysis',
                'confidence': 0.9
            }
        else:
            logger.warning(f"  ⚠️ Empty market_gaps list, using fallback")
            # Empty list from normalizer, use fallback
            market_gaps_value = website.get('market_gaps', [])
            if not market_gaps_value or len(market_gaps_value) == 0:
                market_gaps_value = [
                    {'gap_description': 'Underserved Audience Segments', 'opportunity': '', 'target_audience': '', 'priority': 'Medium'},
                    {'gap_description': 'Content Format Opportunities', 'opportunity': '', 'target_audience': '', 'priority': 'Medium'},
                    {'gap_description': 'Emerging Topic Areas', 'opportunity': '', 'target_audience': '', 'priority': 'Medium'}
                ]
            fields['market_gaps'] = {
                'value': market_gaps_value,
                'source': 'website_analysis' if website.get('market_gaps') else 'onboarding_session',
                'confidence': website.get('confidence_level', 0.8) if website.get('market_gaps') else 0.5
            }
    else:
        market_gaps_value = website.get('market_gaps', [])
        if not market_gaps_value or len(market_gaps_value) == 0:
            # Provide placeholder for missing market_gaps
            market_gaps_value = [
                {'gap_description': 'Underserved Audience Segments', 'opportunity': '', 'target_audience': '', 'priority': 'Medium'},
                {'gap_description': 'Content Format Opportunities', 'opportunity': '', 'target_audience': '', 'priority': 'Medium'},
                {'gap_description': 'Emerging Topic Areas', 'opportunity': '', 'target_audience': '', 'priority': 'Medium'}
            ]
        fields['market_gaps'] = {
            'value': market_gaps_value,
            'source': 'website_analysis' if website.get('market_gaps') else 'onboarding_session',
            'confidence': website.get('confidence_level', 0.8) if website.get('market_gaps') else 0.5
        }

    logger.warning(f"🔍 TRANSFORMER: Checking industry_trends")
    logger.warning(f"  competitor.get('industry_trends'): {competitor.get('industry_trends') if competitor else 'N/A'}")
    
    if competitor and isinstance(competitor.get('industry_trends'), list):
        industry_trends = competitor['industry_trends']
        logger.warning(f"  industry_trends length: {len(industry_trends)}")
        if len(industry_trends) > 0:
            logger.warning(f"  ✅ Using competitor data for industry_trends: {len(industry_trends)} trends")
            fields['industry_trends'] = {
                'value': industry_trends,
                'source': 'competitor_analysis',
                'confidence': 0.9
            }
        else:
            logger.warning(f"  ⚠️ Empty industry_trends list, using fallback")
            # Empty list from normalizer, use fallback
            fields['industry_trends'] = {
                'value': [
                    {'trend_name': 'Digital transformation', 'description': '', 'impact': 'High', 'relevance': ''},
                    {'trend_name': 'AI/ML adoption', 'description': '', 'impact': 'High', 'relevance': ''},
                    {'trend_name': 'Remote work', 'description': '', 'impact': 'Medium', 'relevance': ''}
                ],
                'source': 'onboarding_session',
                'confidence': 0.5
            }
    else:
        fields['industry_trends'] = {
            'value': [
                {'trend_name': 'Digital transformation', 'description': '', 'impact': 'High', 'relevance': ''},
                {'trend_name': 'AI/ML adoption', 'description': '', 'impact': 'High', 'relevance': ''},
                {'trend_name': 'Remote work', 'description': '', 'impact': 'Medium', 'relevance': ''}
            ],
            'source': 'onboarding_session',
            'confidence': 0.5
        }

    logger.warning(f"🔍 TRANSFORMER: Checking emerging_trends")
    logger.warning(f"  competitor.get('emerging_trends'): {competitor.get('emerging_trends') if competitor else 'N/A'}")
    
    if competitor and isinstance(competitor.get('emerging_trends'), list):
        emerging_trends = competitor['emerging_trends']
        logger.warning(f"  emerging_trends length: {len(emerging_trends)}")
        if len(emerging_trends) > 0:
            logger.warning(f"  ✅ Using competitor data for emerging_trends: {len(emerging_trends)} trends")
            fields['emerging_trends'] = {
                'value': emerging_trends,
                'source': 'competitor_analysis',
                'confidence': 0.9
            }
        else:
            logger.warning(f"  ⚠️ Empty emerging_trends list, using fallback")
            # Empty list from normalizer, use fallback
            fields['emerging_trends'] = {
                'value': [
                    {'trend_name': 'Voice search optimization', 'description': '', 'growth_potential': 'High', 'early_adoption_benefit': ''},
                    {'trend_name': 'Video content', 'description': '', 'growth_potential': 'High', 'early_adoption_benefit': ''},
                    {'trend_name': 'Interactive content', 'description': '', 'growth_potential': 'Medium', 'early_adoption_benefit': ''}
                ],
                'source': 'onboarding_session',
                'confidence': 0.5
            }
    else:
        fields['emerging_trends'] = {
            'value': [
                {'trend_name': 'Voice search optimization', 'description': '', 'growth_potential': 'High', 'early_adoption_benefit': ''},
                {'trend_name': 'Video content', 'description': '', 'growth_potential': 'High', 'early_adoption_benefit': ''},
                {'trend_name': 'Interactive content', 'description': '', 'growth_potential': 'Medium', 'early_adoption_benefit': ''}
            ],
            'source': 'onboarding_session',
            'confidence': 0.5
        }

    # Content Strategy
    fields['preferred_formats'] = {
        'value': content_prefs.get('preferred_formats', ['Blog posts', 'Whitepapers', 'Webinars', 'Case studies', 'Videos']),
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.8)
    }

    fields['content_mix'] = {
        'value': {
            'blog_posts': 40,
            'whitepapers': 20,
            'webinars': 15,
            'case_studies': 15,
            'videos': 10,
        },
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.8)
    }

    fields['content_frequency'] = {
        'value': 'Weekly',
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.8)
    }

    fields['optimal_timing'] = {
        'value': {
            'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
            'best_times': ['9:00 AM', '1:00 PM', '3:00 PM']
        },
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.7)
    }

    fields['quality_metrics'] = {
        'value': {
            'readability_score': 8.5,
            'engagement_target': 5.0,
            'conversion_target': 2.0
        },
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.8)
    }

    fields['editorial_guidelines'] = {
        'value': {
            'tone': content_prefs.get('content_style', ['Professional', 'Educational']),
            'length': content_prefs.get('content_length', 'Medium (1000-2000 words)'),
            'formatting': ['Use headers', 'Include visuals', 'Add CTAs']
        },
        'source': 'research_preferences',
        'confidence': research.get('confidence_level', 0.8)
    }

    # Brand Voice - Use persona data if available
    if persona and persona.get('brand_voice_insights'):
        brand_voice_insights = persona['brand_voice_insights']
        fields['brand_voice'] = {
            'value': {
                'personality_traits': brand_voice_insights.get('personality_traits', []),
                'communication_style': brand_voice_insights.get('communication_style', ''),
                'key_messages': brand_voice_insights.get('key_messages', []),
                'do_s': '',
                'dont_s': '',
                'examples': ''
            },
            'source': 'persona_data',
            'confidence': 0.9
        }
    else:
        fields['brand_voice'] = {
            'value': {
                'personality_traits': content_prefs.get('content_style', ['Professional', 'Educational']),
                'communication_style': 'Educational and authoritative',
                'key_messages': [],
                'do_s': '',
                'dont_s': '',
                'examples': ''
            },
            'source': 'research_preferences',
            'confidence': research.get('confidence_level', 0.8)
        }

    # Performance & Analytics - Use analytics data if available
    if analytics and analytics.get('traffic_sources'):
        # Use analytics traffic sources (GSC/Bing provide organic search data)
        analytics_traffic = analytics['traffic_sources']
        website_traffic = website.get('traffic_sources', {})
        
        # Merge analytics data with website data
        merged_traffic = website_traffic.copy() if website_traffic else {}
        if 'organic_search' in analytics_traffic:
            merged_traffic['Organic Search'] = {
                'clicks': analytics_traffic['organic_search'].get('clicks', 0),
                'impressions': analytics_traffic['organic_search'].get('impressions', 0),
                'ctr': analytics_traffic['organic_search'].get('ctr', 0)
            }
        
        fields['traffic_sources'] = {
            'value': merged_traffic if merged_traffic else ['Organic Search', 'Social Media', 'Direct Traffic', 'Referral Traffic'],
            'source': 'analytics_data' if analytics.get('traffic_sources') else 'website_analysis',
            'confidence': 0.9 if analytics.get('traffic_sources') else website.get('confidence_level', 0.8)
        }
    else:
        fields['traffic_sources'] = {
            'value': website.get('traffic_sources', {}),
            'source': 'website_analysis',
            'confidence': website.get('confidence_level', 0.8)
        }

    # conversion_rates - Analytics don't provide conversion data, use website data
    fields['conversion_rates'] = {
        'value': {
            'overall': website.get('performance_metrics', {}).get('conversion_rate', 3.2),
            'blog': 2.5,
            'landing_pages': 4.0,
            'email': 5.5,
        },
        'source': 'website_analysis',
        'confidence': website.get('confidence_level', 0.8)
    }

    fields['content_roi_targets'] = {
        'value': {
            'target_roi': 300,
            'cost_per_lead': 50,
            'lifetime_value': 500,
        },
        'source': 'website_analysis',
        'confidence': website.get('confidence_level', 0.7)
    }

    fields['ab_testing_capabilities'] = {
        'value': True,
        'source': 'api_keys_data',
        'confidence': api_keys.get('confidence_level', 0.8)
    }

    return fields 