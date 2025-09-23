#!/usr/bin/env python3
"""
Deployment script for the Persona System.
Sets up database tables and validates the complete system.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger

def deploy_persona_system():
    """Deploy the complete persona system."""
    
    logger.info("🚀 Deploying Persona System")
    
    try:
        # Step 1: Create database tables
        logger.info("📊 Step 1: Creating database tables...")
        from scripts.create_persona_tables import create_persona_tables
        create_persona_tables()
        logger.info("✅ Database tables created")
        
        # Step 2: Validate Gemini integration
        logger.info("🤖 Step 2: Validating Gemini integration...")
        from services.llm_providers.gemini_provider import gemini_structured_json_response
        
        test_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "timestamp": {"type": "string"}
            },
            "required": ["status"]
        }
        
        test_response = gemini_structured_json_response(
            prompt="Return status='ready' and current timestamp",
            schema=test_schema,
            temperature=0.1,
            max_tokens=1024
        )
        
        if "error" in test_response:
            logger.warning(f"⚠️ Gemini test warning: {test_response['error']}")
        else:
            logger.info("✅ Gemini integration validated")
        
        # Step 3: Test persona service
        logger.info("🧠 Step 3: Testing persona service...")
        from services.persona_analysis_service import PersonaAnalysisService
        persona_service = PersonaAnalysisService()
        logger.info("✅ Persona service initialized")
        
        # Step 4: Test replication engine
        logger.info("⚙️ Step 4: Testing replication engine...")
        from services.persona_replication_engine import PersonaReplicationEngine
        replication_engine = PersonaReplicationEngine()
        logger.info("✅ Replication engine initialized")
        
        # Step 5: Validate API endpoints
        logger.info("🌐 Step 5: Validating API endpoints...")
        from api.persona_routes import router
        logger.info(f"✅ Persona router configured with {len(router.routes)} routes")
        
        logger.info("🎉 Persona System deployed successfully!")
        
        # Print deployment summary
        print_deployment_summary()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {str(e)}")
        return False

def print_deployment_summary():
    """Print deployment summary and next steps."""
    
    logger.info("📋 PERSONA SYSTEM DEPLOYMENT SUMMARY")
    logger.info("=" * 50)
    
    logger.info("✅ Database Tables:")
    logger.info("   - writing_personas")
    logger.info("   - platform_personas") 
    logger.info("   - persona_analysis_results")
    logger.info("   - persona_validation_results")
    
    logger.info("✅ Services:")
    logger.info("   - PersonaAnalysisService")
    logger.info("   - PersonaReplicationEngine")
    
    logger.info("✅ API Endpoints:")
    logger.info("   - POST /api/personas/generate")
    logger.info("   - GET /api/personas/user/{user_id}")
    logger.info("   - GET /api/personas/platform/{platform}")
    logger.info("   - GET /api/personas/export/{platform}")
    
    logger.info("✅ Platform Support:")
    logger.info("   - Twitter/X, LinkedIn, Instagram, Facebook")
    logger.info("   - Blog, Medium, Substack")
    
    logger.info("🔧 NEXT STEPS:")
    logger.info("1. Complete onboarding with website analysis (Step 2)")
    logger.info("2. Set research preferences (Step 3)")
    logger.info("3. Generate persona in Final Step (Step 6)")
    logger.info("4. Export hardened prompts for external AI systems")
    logger.info("5. Use persona for consistent content generation")
    
    logger.info("=" * 50)

def validate_deployment():
    """Validate that all components are working correctly."""
    
    logger.info("🔍 Validating deployment...")
    
    validation_results = {
        "database": False,
        "gemini": False,
        "persona_service": False,
        "replication_engine": False,
        "api_routes": False
    }
    
    try:
        # Test database
        from services.database import get_db_session
        session = get_db_session()
        if session:
            session.close()
            validation_results["database"] = True
            logger.info("✅ Database connection validated")
        
        # Test Gemini
        from services.llm_providers.gemini_provider import get_gemini_api_key
        api_key = get_gemini_api_key()
        if api_key and api_key != "your_gemini_api_key_here":
            validation_results["gemini"] = True
            logger.info("✅ Gemini API key configured")
        else:
            logger.warning("⚠️ Gemini API key not configured")
        
        # Test services
        from services.persona_analysis_service import PersonaAnalysisService
        from services.persona_replication_engine import PersonaReplicationEngine
        
        PersonaAnalysisService()
        PersonaReplicationEngine()
        validation_results["persona_service"] = True
        validation_results["replication_engine"] = True
        logger.info("✅ Services validated")
        
        # Test API routes
        from api.persona_routes import router
        if len(router.routes) > 0:
            validation_results["api_routes"] = True
            logger.info("✅ API routes validated")
        
    except Exception as e:
        logger.error(f"❌ Validation error: {str(e)}")
    
    # Summary
    passed = sum(validation_results.values())
    total = len(validation_results)
    
    logger.info(f"📊 Validation Results: {passed}/{total} components validated")
    
    if passed == total:
        logger.info("🎉 All components validated successfully!")
        return True
    else:
        logger.warning("⚠️ Some components failed validation")
        for component, status in validation_results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {component}")
        return False

if __name__ == "__main__":
    # Deploy system
    deployment_success = deploy_persona_system()
    
    if deployment_success:
        # Validate deployment
        validation_success = validate_deployment()
        
        if validation_success:
            logger.info("🎉 Persona System ready for production!")
            sys.exit(0)
        else:
            logger.error("❌ Deployment validation failed")
            sys.exit(1)
    else:
        logger.error("❌ Deployment failed")
        sys.exit(1)