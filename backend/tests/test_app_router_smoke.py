"""Smoke tests for backend app/router registration."""

from importlib import import_module
from pathlib import Path
import sys
import types
import os


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Keep smoke test lightweight in CI/dev environments without spaCy model data.
if "spacy" not in sys.modules:
    sys.modules["spacy"] = types.SimpleNamespace(load=lambda _name: object())


os.environ.setdefault("STRIPE_PLAN_PRICE_MAPPING_TEST", "{\"basic\": {\"monthly\": \"price_basic_monthly\"}, \"pro\": {\"monthly\": \"price_pro_monthly\"}}")


def test_app_import_and_seo_dashboard_routes_registered():
    """Ensure importing app succeeds and expected SEO dashboard routes are present."""
    app_module = import_module("app")
    app = app_module.app

    registered_paths = {route.path for route in app.routes}

    assert "/api/seo-dashboard/sif-health" in registered_paths
    assert "/api/seo-dashboard/cache-stats" in registered_paths
