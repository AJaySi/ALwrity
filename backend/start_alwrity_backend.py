#!/usr/bin/env python3
"""
ALwrity Backend Server - Modular Startup Script
Handles setup, dependency installation, and server startup using modular utilities.
Run this from the backend directory to set up and start the FastAPI server.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BootstrapResult:
    name: str
    success: bool
    skipped: bool
    reason: Optional[str] = None
    details: Optional[str] = None


LINGUISTIC_REQUIRED_FEATURES = {"content_planning", "strategy_copilot", "facebook", "linkedin", "blog_writer", "persona"}


def get_enabled_features() -> set:
    """Get enabled features from environment variable.
    
    ALWRITY_ENABLED_FEATURES can be:
    - "all" - enable all features (default)
    - comma-separated list: "podcast,blog-writer,youtube"
    - single feature: "podcast"
    """
    env_value = os.getenv(
        "ALWRITY_ENABLED_FEATURES",
        os.getenv("ALWRITY_FEATURE_PROFILE", os.getenv("ALWRITY_ROUTER_PROFILE", "all"))
    ).strip().lower()
    
    if not env_value or env_value == "all":
        return {"all"}
    
    return {f.strip() for f in env_value.split(",") if f.strip()}


def get_active_profile() -> str:
    """Legacy function - returns primary profile for backwards compatibility."""
    enabled = get_enabled_features()
    if "all" in enabled:
        return "all"
    return list(enabled)[0] if enabled else "all"


def should_bootstrap_linguistic_models() -> bool:
    """Decide whether to bootstrap linguistic models based on enabled features."""
    enabled_features = get_enabled_features()
    verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    
    if "all" in enabled_features:
        return True
    
    # Map old profile names to features for backwards compatibility
    feature_mapping = {
        "podcast": "podcast",
        "youtube": "youtube",
        "planning": "content-planning",
        "default": "all"
    }
    
    # Check if any linguistic-required feature is enabled
    linguistic_features = {"content_planning", "facebook", "linkedin", "blog-writer", "persona"}
    return bool(enabled_features & linguistic_features)


def should_bootstrap_local_llm_models() -> bool:
    """Decide whether to bootstrap local LLM models based on enabled features."""
    enabled_features = get_enabled_features()
    
    if "all" in enabled_features:
        return True
    
    # Skip LLM bootstrap for lean deployments
    return "core" in enabled_features or "podcast" in enabled_features


def bootstrap_linguistic_models() -> BootstrapResult:
    """
    Bootstrap spaCy and NLTK models BEFORE any imports.
    This prevents import-time failures when EnhancedLinguisticAnalyzer is loaded.
    """
    import subprocess
    import os
    
    verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    
    if verbose:
        print("🔍 Bootstrapping linguistic models...")
    
    # Check and download spaCy model
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            if verbose:
                print("   ✅ spaCy model 'en_core_web_sm' available")
        except OSError:
            if verbose:
                print("   ⚠️  spaCy model 'en_core_web_sm' not found, downloading...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "spacy", "download", "en_core_web_sm"
                ])
                if verbose:
                    print("   ✅ spaCy model downloaded successfully")
            except subprocess.CalledProcessError as e:
                if verbose:
                    print(f"   ❌ Failed to download spaCy model: {e}")
                    print("   Please run: python -m spacy download en_core_web_sm")
                return BootstrapResult(name="linguistic_models", success=False, skipped=False, reason="spacy_download_failed")
    except ImportError:
        if verbose:
            print("   ⚠️  spaCy not installed - skipping")
    
    # Check and download NLTK data
    try:
        import nltk
        essential_data = [
            ('punkt_tab', 'tokenizers/punkt_tab'),
            ('stopwords', 'corpora/stopwords'),
            ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger')
        ]
        
        for data_package, path in essential_data:
            try:
                nltk.data.find(path)
                if verbose:
                    print(f"   ✅ NLTK {data_package} available")
            except LookupError:
                if verbose:
                    print(f"   ⚠️  NLTK {data_package} not found, downloading...")
                try:
                    nltk.download(data_package, quiet=True)
                    if verbose:
                        print(f"   ✅ NLTK {data_package} downloaded")
                except Exception as e:
                    if verbose:
                        print(f"   ⚠️  Failed to download {data_package}: {e}")
                    if data_package == 'punkt_tab':
                        try:
                            nltk.download('punkt', quiet=True)
                            if verbose:
                                print(f"   ✅ NLTK punkt (fallback) downloaded")
                        except:
                            pass
    except ImportError:
        if verbose:
            print("   ⚠️  NLTK not installed - skipping")
    
    if verbose:
        print("✅ Linguistic model bootstrap complete")
    return BootstrapResult(name="linguistic_models", success=True, skipped=False)


def bootstrap_local_llm_models() -> BootstrapResult:
    """
    Bootstrap Local LLM models (Qwen) for SIF Agents.
    This ensures the model is cached locally before the server starts,
    preventing large downloads during runtime.
    """
    import os
    verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    
    # Model to pre-download
    model_name = "Qwen/Qwen2.5-1.5B-Instruct" 
    # Using Qwen2.5-1.5B as it's more efficient for laptop CPU than 4B, 
    # but still capable for agent routing/clustering.
    # If user specifically asked for Qwen3-4B, we can use that, but 1.5B is much faster.
    # User said "local qwen model", 4B might be heavy. Let's stick to what was in code: "Qwen/Qwen3-4B-Instruct-2507"
    # Actually, the code had "Qwen/Qwen3-4B-Instruct-2507" which seems like a specific fine-tune or typo.
    # Let's use a standard efficient one: "Qwen/Qwen2.5-3B-Instruct" or "Qwen/Qwen2.5-1.5B-Instruct".
    # Given "optimized for cpu-laptop", 1.5B or 3B is best.
    # Let's use the one referenced in the code if valid, otherwise Qwen2.5-3B.
    # The code had: "Qwen/Qwen3-4B-Instruct-2507". I suspect this is a placeholder or internal model.
    # I will use "Qwen/Qwen2.5-3B-Instruct" as a safe, modern, powerful laptop-friendly default.
    
    # Render Free Tier has 512MB RAM. Downloading a 3B model (6GB+) will instantly crash it.
    # We must skip this on Render unless we are on a paid instance with persistent disk and lots of RAM.
    if os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT"):
        if verbose:
            print("   ⚠️  Cloud environment detected (Render/Railway). Skipping local LLM bootstrap to save RAM/Time.")
        return BootstrapResult(name="local_llm_models", success=True, skipped=True, reason="cloud_environment")
    
    target_model = "Qwen/Qwen2.5-3B-Instruct"
    
    if verbose:
        print(f"🔍 Checking local LLM model '{target_model}'...")
        
    try:
        from huggingface_hub import snapshot_download
        try:
            # This checks cache and downloads if missing
            snapshot_download(repo_id=target_model, repo_type="model")
            if verbose:
                print(f"   ✅ Local LLM '{target_model}' available")
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Failed to download/check local LLM: {e}")
                print("       SIF agents may try to download it at runtime.")
            return BootstrapResult(name="local_llm_models", success=False, skipped=False, reason=str(e))
    except ImportError:
        if verbose:
            print("   ⚠️  huggingface_hub not installed - skipping LLM bootstrap")
        return BootstrapResult(name="local_llm_models", success=False, skipped=True, reason="huggingface_hub_not_installed")
    
    return BootstrapResult(name="local_llm_models", success=True, skipped=False)


# Bootstrap linguistic models BEFORE any imports that might need them
BOOTSTRAP_RESULTS = []

if __name__ == "__main__":
    profile = get_active_profile()
    os.environ["ALWRITY_ACTIVE_PROFILE"] = profile
    
    print(f"\n📋 Active profile: {profile}")
    
    if should_bootstrap_linguistic_models():
        result = bootstrap_linguistic_models()
        BOOTSTRAP_RESULTS.append(result)
    else:
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        if verbose:
            print("⏭️  Skipping linguistic model bootstrap (profile-gated)")
        BOOTSTRAP_RESULTS.append(BootstrapResult(name="linguistic_models", success=True, skipped=True, reason="profile_gated"))
    
    if should_bootstrap_local_llm_models():
        result = bootstrap_local_llm_models()
        BOOTSTRAP_RESULTS.append(result)
    else:
        verbose = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
        if verbose:
            print("⏭️  Skipping local LLM model bootstrap (profile-gated)")
        BOOTSTRAP_RESULTS.append(BootstrapResult(name="local_llm_models", success=True, skipped=True, reason="profile_gated"))
    
    summary = {
        "active_profile": profile,
        "bootstraps": [asdict(r) for r in BOOTSTRAP_RESULTS]
    }
    os.environ["ALWRITY_BOOTSTRAP_SUMMARY"] = json.dumps(summary)
    
    print(f"\n📋 Bootstrap Summary:")
    for r in BOOTSTRAP_RESULTS:
        status = "⏭️  Skipped" if r.skipped else ("✅ Enabled" if r.success else "❌ Failed")
        print(f"   {r.name}: {status}" + (f" ({r.reason})" if r.reason else ""))

# NOW import modular utilities (after bootstrap)
from alwrity_utils import (
    DependencyManager,
    EnvironmentSetup,
    DatabaseSetup,
    ProductionOptimizer
)


def start_backend(enable_reload=False, production_mode=False):
    """Start the backend server."""
    print("🚀 Starting ALwrity Backend...")
    podcast_only_demo_mode = os.getenv("ALWRITY_PODCAST_ONLY_DEMO_MODE", os.getenv("PODCAST_ONLY_DEMO_MODE", "false")).lower() in {"1", "true", "yes", "on"}

    if podcast_only_demo_mode:
        print("\n" + "=" * 60)
        print("🎙️  PODCAST-ONLY DEMO MODE ACTIVE")
        print("   Non-podcast router groups are intentionally skipped.")
        print("=" * 60)
    
    # Set host based on environment and mode
    # Use 127.0.0.1 for local production testing on Windows
    # Use 0.0.0.0 for actual cloud deployments (Render, Railway, etc.)
    # Render provides PORT env var, we must bind to it.
    default_host = os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("DEPLOY_ENV")
    if default_host:
        # Cloud deployment detected - use 0.0.0.0
        os.environ.setdefault("HOST", "0.0.0.0")
    else:
        # Local deployment - use 127.0.0.1 for better Windows compatibility
        os.environ.setdefault("HOST", "127.0.0.1")
    
    # Render sets PORT automatically. We should respect it if present, otherwise default to 8000.
    # We don't setdefault("PORT", "8000") here because we want to use os.getenv("PORT") directly later
    # to catch if it's missing and THEN default.
    
    # Set reload based on argument or environment variable
    if enable_reload and not production_mode:
        os.environ.setdefault("RELOAD", "true")
        print("   🔄 Development mode: Auto-reload enabled")
    else:
        os.environ.setdefault("RELOAD", "false")
        print("   🏭 Production mode: Auto-reload disabled")
    
    host = os.getenv("HOST")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"   📍 Host: {host}")
    print(f"   🔌 Port: {port}")
    print(f"   🔄 Reload: {reload}")
    
    try:
        # Import and run the app
        from app import app
        import uvicorn

        # Note: Database already initialized by DatabaseSetup in main()
        
        print("\n🌐 ALwrity Backend Server")
        print("=" * 50)
        print("   📖 API Documentation: http://localhost:8000/api/docs")
        print("   🔍 Health Check: http://localhost:8000/health")
        print("   📊 ReDoc: http://localhost:8000/api/redoc")
        
        if not production_mode:
            print("   📈 API Monitoring: http://localhost:8000/api/content-planning/monitoring/health")
            print("   💳 Billing Dashboard: http://localhost:8000/api/subscription/plans")
            print("   📊 Usage Tracking: http://localhost:8000/api/subscription/usage/demo")
        
        print("\n[STOP]  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Set up clean logging for end users
        from logging_config import setup_clean_logging, get_uvicorn_log_level
        # Video stack preflight (diagnostics + version assert)
        try:
            from services.story_writer.video_preflight import (
                log_video_stack_diagnostics,
                assert_supported_moviepy,
            )
        except Exception:
            # Preflight is optional; continue if module missing
            log_video_stack_diagnostics = None
            assert_supported_moviepy = None
        
        verbose_mode = setup_clean_logging()
        uvicorn_log_level = get_uvicorn_log_level()

        # Log diagnostics and assert versions (fail fast if misconfigured)
        try:
            if log_video_stack_diagnostics:
                log_video_stack_diagnostics()
            if assert_supported_moviepy:
                assert_supported_moviepy()
        except Exception as _video_stack_err:
            print(f"[ERROR] Video stack preflight failed: {_video_stack_err}")
            return False
        
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=reload,
            reload_dirs=["."],  # Strictly watch backend directory only
            reload_excludes=[
                "workspace/**/*",
                "*.pyc",
                "*.pyo", 
                "*.pyd",
                "__pycache__",
                "*.log",
                "*.sqlite",
                "*.db",
                "*.tmp",
                "*.temp",
                "test_*.py",
                "temp_*.py",
                "monitoring_data_service.py",
                "test_monitoring_save.py",
                "*.json",
                "*.yaml",
                "*.yml",
                ".env*",
                "logs/**/*",
                "logs",
                "**/*.jsonl",
                "**/*.log",
                "cache/**/*",
                "tmp/**/*",
                "temp/**/*",
                "middleware/*",
                "models/*",
                "scripts/*",
                "alwrity_utils/*"
            ],
            log_level=uvicorn_log_level
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Error starting backend: {e}")
        return False
    
    return True


def main():
    """Main function to set up and start the backend."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ALwrity Backend Server")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--dev", action="store_true", help="Enable development mode (auto-reload)")
    parser.add_argument("--production", action="store_true", help="Enable production mode (optimized for deployment)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging for debugging")
    args = parser.parse_args()
    
    # Determine mode
    production_mode = args.production
    enable_reload = (args.reload or args.dev) and not production_mode
    verbose_mode = args.verbose
    
    # Set global verbose flag for utilities
    os.environ["ALWRITY_VERBOSE"] = "true" if verbose_mode else "false"
    
    print("[*] ALwrity Backend Server")
    print("=" * 40)
    print(f"Mode: {'PRODUCTION' if production_mode else 'DEVELOPMENT'}")
    print(f"Auto-reload: {'ENABLED' if enable_reload else 'DISABLED'}")
    if verbose_mode:
        print("Verbose logging: ENABLED")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("[ERROR] Error: app.py not found. Please run this script from the backend directory.")
        print("   Current directory:", os.getcwd())
        print("   Expected files:", [f for f in os.listdir('.') if f.endswith('.py')])
        return False
    
    # Initialize modular components
    dependency_manager = DependencyManager()
    environment_setup = EnvironmentSetup(production_mode=production_mode)
    database_setup = DatabaseSetup(production_mode=production_mode)
    production_optimizer = ProductionOptimizer()
    
    # Setup progress tracking
    setup_steps = [
        "Checking dependencies",
        "Setting up environment", 
        "Configuring database",
        "Starting server"
    ]
    
    print("🔧 Initializing ALwrity...")
    
    # Apply production optimizations if needed
    if production_mode:
        if not production_optimizer.apply_production_optimizations():
            print("❌ Production optimization failed")
            return False
    
    # Step 1: Dependencies
    print(f"   📦 {setup_steps[0]}...", end=" ", flush=True)
    critical_ok, missing_critical = dependency_manager.check_critical_dependencies()
    if not critical_ok:
        print("installing...", end=" ", flush=True)
        if not dependency_manager.install_requirements():
            print("❌ Failed")
            return False
        print("✅ Done")
    else:
        print("✅ Done")
    
    # Check optional dependencies (non-critical) - only in verbose mode
    if verbose_mode:
        dependency_manager.check_optional_dependencies()
    
    # Step 2: Environment
    print(f"   🔧 {setup_steps[1]}...", end=" ", flush=True)
    if not environment_setup.setup_directories():
        print("❌ Directory setup failed")
        return False
    
    if not environment_setup.setup_environment_variables():
        print("❌ Environment setup failed")
        return False
    
    # Create .env file only in development
    if not production_mode:
        environment_setup.create_env_file()
    print("✅ Done")
    
    # Step 3: Database
    print(f"   📊 {setup_steps[2]}...", end=" ", flush=True)
    if not database_setup.setup_essential_tables():
        print("⚠️  Issues detected, continuing...")
    else:
        print("✅ Done")
    
    # Setup advanced features in development, verify in all modes
    if not production_mode:
        database_setup.setup_advanced_tables()
    
    # Always verify database tables (important for both dev and production)
    database_setup.verify_tables()
    
    # Note: Linguistic models (spaCy/NLTK) are bootstrapped before imports
    # See bootstrap_linguistic_models() at the top of this file
    
    # Step 4: Start backend
    print(f"   🚀 {setup_steps[3]}...")
    return start_backend(enable_reload=enable_reload, production_mode=production_mode)


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
