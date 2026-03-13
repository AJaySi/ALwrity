"""
AI Generation Endpoints
Handles AI-powered strategy generation endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

# Import database
from services.database import get_db_session
from middleware.auth_middleware import get_current_user

# Import services
from ....services.content_strategy.ai_generation import AIStrategyGenerator, StrategyGenerationConfig
from ....services.enhanced_strategy_service import EnhancedStrategyService
from ....services.enhanced_strategy_db_service import EnhancedStrategyDBService
from services.shared_state_backend import SharedStateBackend

# Import educational content manager
from .content_strategy.educational_content import EducationalContentManager

# Import utilities
from ....utils.error_handlers import ContentPlanningErrorHandler
from ....utils.response_builders import ResponseBuilder
from ....utils.constants import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(tags=["AI Strategy Generation"])

# Helper function to get database session
def get_db():
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/generate-comprehensive-strategy")
async def generate_comprehensive_strategy(
    user_id: int,
    strategy_name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a comprehensive AI-powered content strategy."""
    try:
        logger.info(f"🚀 Generating comprehensive AI strategy for user: {user_id}")
        
        # Get user context and onboarding data
        db_service = EnhancedStrategyDBService(db)
        enhanced_service = EnhancedStrategyService(db_service)
        
        # Get onboarding data for context
        onboarding_data = await enhanced_service._get_onboarding_data(user_id)
        
        # Build context for AI generation
        context = {
            "onboarding_data": onboarding_data,
            "user_id": user_id,
            "generation_config": config or {}
        }
        
        # Create strategy generation config
        generation_config = StrategyGenerationConfig(
            include_competitive_analysis=config.get("include_competitive_analysis", True) if config else True,
            include_content_calendar=config.get("include_content_calendar", True) if config else True,
            include_performance_predictions=config.get("include_performance_predictions", True) if config else True,
            include_implementation_roadmap=config.get("include_implementation_roadmap", True) if config else True,
            include_risk_assessment=config.get("include_risk_assessment", True) if config else True,
            max_content_pieces=config.get("max_content_pieces", 50) if config else 50,
            timeline_months=config.get("timeline_months", 12) if config else 12
        )
        
        # Initialize AI strategy generator
        strategy_generator = AIStrategyGenerator(generation_config)
        
        # Generate comprehensive strategy
        comprehensive_strategy = await strategy_generator.generate_comprehensive_strategy(
            user_id=user_id,
            context=context,
            strategy_name=strategy_name
        )
        
        logger.info(f"✅ Comprehensive AI strategy generated successfully for user: {user_id}")
        
        return ResponseBuilder.create_success_response(
            message="Comprehensive AI strategy generated successfully",
            data=comprehensive_strategy
        )
        
    except RuntimeError as e:
        logger.error(f"❌ AI service error generating comprehensive strategy: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Error generating comprehensive strategy: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "generate_comprehensive_strategy")

@router.post("/generate-strategy-component")
async def generate_strategy_component(
    user_id: int,
    component_type: str,
    base_strategy: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a specific strategy component using AI."""
    try:
        logger.info(f"🚀 Generating strategy component '{component_type}' for user: {user_id}")
        
        # Validate component type
        valid_components = [
            "strategic_insights",
            "competitive_analysis", 
            "content_calendar",
            "performance_predictions",
            "implementation_roadmap",
            "risk_assessment"
        ]
        
        if component_type not in valid_components:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid component type. Must be one of: {valid_components}"
            )
        
        # Get context if not provided
        if not context:
            db_service = EnhancedStrategyDBService(db)
            enhanced_service = EnhancedStrategyService(db_service)
            onboarding_data = await enhanced_service._get_onboarding_data(user_id)
            context = {"onboarding_data": onboarding_data, "user_id": user_id}
        
        # Get base strategy if not provided
        if not base_strategy:
            # Generate base strategy using autofill
            from ....services.content_strategy.autofill.ai_structured_autofill import AIStructuredAutofillService
            autofill_service = AIStructuredAutofillService()
            autofill_result = await autofill_service.generate_autofill_fields(user_id, context)
            base_strategy = autofill_result.get("fields", {})
        
        # Initialize AI strategy generator
        strategy_generator = AIStrategyGenerator()
        
        # Generate specific component
        if component_type == "strategic_insights":
            component = await strategy_generator._generate_strategic_insights(base_strategy, context)
        elif component_type == "competitive_analysis":
            component = await strategy_generator._generate_competitive_analysis(base_strategy, context)
        elif component_type == "content_calendar":
            component = await strategy_generator._generate_content_calendar(base_strategy, context)
        elif component_type == "performance_predictions":
            component = await strategy_generator._generate_performance_predictions(base_strategy, context)
        elif component_type == "implementation_roadmap":
            component = await strategy_generator._generate_implementation_roadmap(base_strategy, context)
        elif component_type == "risk_assessment":
            component = await strategy_generator._generate_risk_assessment(base_strategy, context)
        
        logger.info(f"✅ Strategy component '{component_type}' generated successfully for user: {user_id}")
        
        return ResponseBuilder.create_success_response(
            message=f"Strategy component '{component_type}' generated successfully",
            data={
                "component_type": component_type,
                "component_data": component,
                "generated_at": datetime.utcnow().isoformat(),
                "user_id": user_id
            }
        )
        
    except RuntimeError as e:
        logger.error(f"❌ AI service error generating strategy component: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service temporarily unavailable for {component_type}: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating strategy component: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "generate_strategy_component")

@router.get("/strategy-generation-status")
async def get_strategy_generation_status(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the status of strategy generation for a user."""
    try:
        logger.info(f"Getting strategy generation status for user: {user_id}")
        
        # Get user's strategies
        db_service = EnhancedStrategyDBService(db)
        enhanced_service = EnhancedStrategyService(db_service)
        
        strategies_data = await enhanced_service.get_enhanced_strategies(user_id, None, db)
        
        # Analyze generation status
        strategies = strategies_data.get("strategies", [])
        
        status_data = {
            "user_id": user_id,
            "total_strategies": len(strategies),
            "ai_generated_strategies": len([s for s in strategies if s.get("ai_generated", False)]),
            "last_generation": None,
            "generation_stats": {
                "comprehensive_strategies": 0,
                "partial_strategies": 0,
                "manual_strategies": 0
            }
        }
        
        if strategies:
            # Find most recent AI-generated strategy
            ai_strategies = [s for s in strategies if s.get("ai_generated", False)]
            if ai_strategies:
                latest_ai = max(ai_strategies, key=lambda x: x.get("created_at", ""))
                status_data["last_generation"] = latest_ai.get("created_at")
            
            # Categorize strategies
            for strategy in strategies:
                if strategy.get("ai_generated", False):
                    if strategy.get("comprehensive", False):
                        status_data["generation_stats"]["comprehensive_strategies"] += 1
                    else:
                        status_data["generation_stats"]["partial_strategies"] += 1
                else:
                    status_data["generation_stats"]["manual_strategies"] += 1
        
        logger.info(f"✅ Strategy generation status retrieved for user: {user_id}")
        
        return ResponseBuilder.create_success_response(
            message="Strategy generation status retrieved successfully",
            data=status_data
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting strategy generation status: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "get_strategy_generation_status")

@router.post("/optimize-existing-strategy")
async def optimize_existing_strategy(
    strategy_id: int,
    optimization_type: str = "comprehensive",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Optimize an existing strategy using AI."""
    try:
        logger.info(f"🚀 Optimizing existing strategy {strategy_id} with type: {optimization_type}")
        
        # Get existing strategy
        db_service = EnhancedStrategyDBService(db)
        enhanced_service = EnhancedStrategyService(db_service)
        
        strategies_data = await enhanced_service.get_enhanced_strategies(strategy_id=strategy_id, db=db)
        
        if strategies_data.get("status") == "not_found" or not strategies_data.get("strategies"):
            raise HTTPException(
                status_code=404,
                detail=f"Strategy with ID {strategy_id} not found"
            )
        
        existing_strategy = strategies_data["strategies"][0]
        user_id = existing_strategy.get("user_id")
        
        # Get user context
        onboarding_data = await enhanced_service._get_onboarding_data(user_id)
        context = {"onboarding_data": onboarding_data, "user_id": user_id}
        
        # Initialize AI strategy generator
        strategy_generator = AIStrategyGenerator()
        
        # Generate optimization based on type
        if optimization_type == "comprehensive":
            # Generate comprehensive optimization
            optimized_strategy = await strategy_generator.generate_comprehensive_strategy(
                user_id=user_id,
                context=context,
                strategy_name=f"Optimized: {existing_strategy.get('name', 'Strategy')}"
            )
        else:
            # Generate specific component optimization
            component = await strategy_generator._generate_strategic_insights(existing_strategy, context)
            optimized_strategy = {
                "optimization_type": optimization_type,
                "original_strategy": existing_strategy,
                "optimization_data": component,
                "optimized_at": datetime.utcnow().isoformat()
            }
        
        logger.info(f"✅ Strategy {strategy_id} optimized successfully")
        
        return ResponseBuilder.create_success_response(
            message="Strategy optimized successfully",
            data=optimized_strategy
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error optimizing strategy: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "optimize_existing_strategy") 

@router.post("/generate-comprehensive-strategy-polling")
async def generate_comprehensive_strategy_polling(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a comprehensive AI-powered content strategy using polling approach."""
    try:
        authenticated_user_id = str(current_user.get("id", "")).strip()
        if not authenticated_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        request_user_id = request.get("user_id")
        if request_user_id and str(request_user_id) != authenticated_user_id:
            logger.warning(
                f"Ignoring mismatched request user_id={request_user_id}; using authenticated user {authenticated_user_id}"
            )

        strategy_name = request.get("strategy_name")
        config = request.get("config", {})

        logger.info(f"🚀 Starting polling-based AI strategy generation for user: {authenticated_user_id}")

        db_service = EnhancedStrategyDBService(db)
        enhanced_service = EnhancedStrategyService(db_service)
        onboarding_data = await enhanced_service._get_onboarding_data(authenticated_user_id)

        context = {
            "onboarding_data": onboarding_data,
            "user_id": authenticated_user_id,
            "generation_config": config or {},
        }

        generation_config = StrategyGenerationConfig(
            include_competitive_analysis=config.get("include_competitive_analysis", True) if config else True,
            include_content_calendar=config.get("include_content_calendar", True) if config else True,
            include_performance_predictions=config.get("include_performance_predictions", True) if config else True,
            include_implementation_roadmap=config.get("include_implementation_roadmap", True) if config else True,
            include_risk_assessment=config.get("include_risk_assessment", True) if config else True,
            max_content_pieces=config.get("max_content_pieces", 50) if config else 50,
            timeline_months=config.get("timeline_months", 12) if config else 12,
        )

        strategy_generator = AIStrategyGenerator(generation_config)

        import asyncio
        import uuid

        task_id = str(uuid.uuid4())
        state_backend = SharedStateBackend(db)
        state_backend.cleanup_expired()

        generation_status = {
            "task_id": task_id,
            "user_id": authenticated_user_id,
            "status": "started",
            "progress": 0,
            "step": 0,
            "message": "Initializing AI strategy generation...",
            "started_at": datetime.utcnow().isoformat(),
            "strategy": None,
            "error": None,
            "educational_content": EducationalContentManager.get_initialization_content(),
        }
        state_backend.set_task_status(authenticated_user_id, task_id, generation_status)

        async def generate_strategy_background():
            try:
                updates = [
                    {"step": 1, "progress": 20, "message": "Analyzing onboarding context...", "educational_content": EducationalContentManager.get_step_content(1)},
                    {"step": 2, "progress": 45, "message": "Generating strategic insights...", "educational_content": EducationalContentManager.get_step_content(2)},
                    {"step": 3, "progress": 70, "message": "Building comprehensive strategy...", "educational_content": EducationalContentManager.get_step_content(8)},
                ]
                for patch in updates:
                    state_backend.update_task_status(authenticated_user_id, task_id, patch)

                comprehensive_strategy = await strategy_generator.generate_comprehensive_strategy(
                    user_id=authenticated_user_id,
                    context=context,
                    strategy_name=strategy_name,
                )

                final_status = {
                    "step": 8,
                    "progress": 100,
                    "status": "completed",
                    "message": "Strategy generation completed successfully!",
                    "strategy": comprehensive_strategy,
                    "completed_at": datetime.utcnow().isoformat(),
                    "educational_content": EducationalContentManager.get_step_content(8),
                }
                state_backend.update_task_status(authenticated_user_id, task_id, final_status)
                state_backend.set_latest_strategy(
                    authenticated_user_id,
                    {
                        "strategy": comprehensive_strategy,
                        "completed_at": datetime.utcnow().isoformat(),
                        "task_id": task_id,
                        "user_id": authenticated_user_id,
                    },
                )
                logger.info(f"✅ Background strategy generation completed for task: {task_id}")
            except Exception as e:
                logger.error(f"❌ Error in background strategy generation for task {task_id}: {str(e)}")
                state_backend.update_task_status(
                    authenticated_user_id,
                    task_id,
                    {
                        "status": "failed",
                        "error": str(e),
                        "message": f"Strategy generation failed: {str(e)}",
                        "failed_at": datetime.utcnow().isoformat(),
                    },
                )

        asyncio.create_task(generate_strategy_background())

        return ResponseBuilder.create_success_response(
            message="AI strategy generation started successfully",
            data={
                "task_id": task_id,
                "status": "started",
                "message": "Strategy generation is running in the background. Use the task_id to check progress.",
                "polling_endpoint": f"/api/content-planning/content-strategy/ai-generation/strategy-generation-status/{task_id}",
                "estimated_completion": "2-3 minutes",
            },
        )

    except Exception as e:
        logger.error(f"❌ Error starting polling-based strategy generation: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "generate_comprehensive_strategy_polling")


@router.get("/strategy-generation-status/{task_id}")
async def get_strategy_generation_status_by_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get the status of strategy generation for a specific task."""
    try:
        authenticated_user_id = str(current_user.get("id", "")).strip()
        if not authenticated_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        state_backend = SharedStateBackend(db)
        state_backend.cleanup_expired()
        task_status = state_backend.get_task_status(authenticated_user_id, task_id)

        if not task_status:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found for this user. It may have expired or never existed.",
            )

        return ResponseBuilder.create_success_response(
            message="Strategy generation status retrieved successfully",
            data=task_status,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting strategy generation status: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "get_strategy_generation_status_by_task")


@router.get("/latest-strategy")
async def get_latest_generated_strategy(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get the latest generated strategy from shared state backend or database."""
    try:
        authenticated_user_id = str(current_user.get("id", "")).strip()
        if not authenticated_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        from models.enhanced_strategy_models import EnhancedContentStrategy
        from sqlalchemy import desc

        latest_db_strategy = db.query(EnhancedContentStrategy).filter(
            EnhancedContentStrategy.user_id == authenticated_user_id,
            EnhancedContentStrategy.comprehensive_ai_analysis.isnot(None),
        ).order_by(desc(EnhancedContentStrategy.created_at)).first()

        if latest_db_strategy and latest_db_strategy.comprehensive_ai_analysis:
            return ResponseBuilder.create_success_response(
                message="Latest generated strategy retrieved successfully from database",
                data={
                    "user_id": authenticated_user_id,
                    "strategy": latest_db_strategy.comprehensive_ai_analysis,
                    "completed_at": latest_db_strategy.created_at.isoformat(),
                    "strategy_id": latest_db_strategy.id,
                },
            )

        state_backend = SharedStateBackend(db)
        state_backend.cleanup_expired()
        latest_strategy = state_backend.get_latest_strategy(authenticated_user_id)

        if latest_strategy:
            return ResponseBuilder.create_success_response(
                message="Latest generated strategy retrieved successfully from shared state",
                data=latest_strategy,
            )

        return ResponseBuilder.create_success_response(
            data={"user_id": authenticated_user_id, "strategy": None},
            message="No completed strategy generation found",
            status_code=200,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting latest generated strategy: {str(e)}")
        raise ContentPlanningErrorHandler.handle_general_error(e, "get_latest_generated_strategy")
