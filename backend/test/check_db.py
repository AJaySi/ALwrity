#!/usr/bin/env python3
"""
Database check and sample data creation script
"""

from services.database import get_db_session
from models.content_planning import ContentStrategy, ContentGapAnalysis, AIAnalysisResult
from sqlalchemy.orm import Session
import json

def check_database():
    """Check what data exists in the database"""
    db = get_db_session()
    
    try:
        # Check strategies
        strategies = db.query(ContentStrategy).all()
        print(f"Found {len(strategies)} strategies")
        for strategy in strategies:
            print(f"  Strategy {strategy.id}: {strategy.name} - {strategy.industry}")
        
        # Check gap analyses
        gap_analyses = db.query(ContentGapAnalysis).all()
        print(f"Found {len(gap_analyses)} gap analyses")
        
        # Check AI analytics
        ai_analytics = db.query(AIAnalysisResult).all()
        print(f"Found {len(ai_analytics)} AI analytics")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

def create_sample_data():
    """Create sample data for Strategic Intelligence and Keyword Research tabs"""
    db = get_db_session()
    
    try:
        # Create a sample strategy if none exists
        existing_strategies = db.query(ContentStrategy).all()
        if not existing_strategies:
            sample_strategy = ContentStrategy(
                name="Sample Content Strategy",
                industry="Digital Marketing",
                target_audience={"demographics": "Small to medium businesses", "interests": ["marketing", "technology"]},
                content_pillars=["Educational Content", "Thought Leadership", "Case Studies"],
                ai_recommendations={
                    "market_positioning": {
                        "score": 75,
                        "strengths": ["Strong brand voice", "Consistent content quality"],
                        "weaknesses": ["Limited video content", "Slow content production"]
                    },
                    "competitive_advantages": [
                        {"advantage": "AI-powered content creation", "impact": "High", "implementation": "In Progress"},
                        {"advantage": "Data-driven strategy", "impact": "Medium", "implementation": "Complete"}
                    ],
                    "strategic_risks": [
                        {"risk": "Content saturation in market", "probability": "Medium", "impact": "High"},
                        {"risk": "Algorithm changes affecting reach", "probability": "High", "impact": "Medium"}
                    ]
                },
                user_id=1
            )
            db.add(sample_strategy)
            db.commit()
            print("Created sample strategy")
        
        # Create sample gap analysis
        existing_gaps = db.query(ContentGapAnalysis).all()
        if not existing_gaps:
            sample_gap = ContentGapAnalysis(
                website_url="https://example.com",
                competitor_urls=["competitor1.com", "competitor2.com"],
                target_keywords=["content marketing", "digital strategy", "SEO"],
                analysis_results={
                    "gaps": ["Video content gap", "Local SEO opportunities"],
                    "opportunities": [
                        {"keyword": "AI content tools", "search_volume": "5K-10K", "competition": "Low", "cpc": "$2.50"},
                        {"keyword": "content marketing ROI", "search_volume": "1K-5K", "competition": "Medium", "cpc": "$4.20"}
                    ]
                },
                recommendations=[
                    {
                        "type": "content",
                        "title": "Create video tutorials",
                        "description": "Address the video content gap",
                        "priority": "high"
                    },
                    {
                        "type": "seo",
                        "title": "Optimize for local search",
                        "description": "Target local keywords",
                        "priority": "medium"
                    }
                ],
                user_id=1
            )
            db.add(sample_gap)
            db.commit()
            print("Created sample gap analysis")
        
        # Create sample AI analytics
        existing_ai = db.query(AIAnalysisResult).all()
        if not existing_ai:
            sample_ai = AIAnalysisResult(
                analysis_type="strategic_intelligence",
                insights=[
                    "Focus on video content to address market gap",
                    "Leverage AI tools for competitive advantage",
                    "Monitor algorithm changes closely"
                ],
                recommendations=[
                    {
                        "type": "content",
                        "title": "Increase video content production",
                        "description": "Address the video content gap identified in analysis",
                        "priority": "high"
                    },
                    {
                        "type": "strategy",
                        "title": "Implement AI-powered content creation",
                        "description": "Leverage AI tools for competitive advantage",
                        "priority": "medium"
                    }
                ],
                performance_metrics={
                    "content_engagement": 78.5,
                    "traffic_growth": 25.3,
                    "conversion_rate": 2.1
                },
                personalized_data_used={
                    "onboarding_data": True,
                    "user_preferences": True,
                    "historical_performance": True
                },
                processing_time=15.2,
                ai_service_status="operational",
                user_id=1
            )
            db.add(sample_ai)
            db.commit()
            print("Created sample AI analytics")
            
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Checking database...")
    check_database()
    
    print("\nCreating sample data...")
    create_sample_data()
    
    print("\nFinal database state:")
    check_database() 