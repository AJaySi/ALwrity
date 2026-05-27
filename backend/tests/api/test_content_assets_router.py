import importlib.util
from pathlib import Path
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[3]
ROUTER_PATH = ROOT / 'backend' / 'api' / 'content_assets' / 'router.py'
MODELS_PATH = ROOT / 'backend' / 'models' / 'content_asset_models.py'

models_spec = importlib.util.spec_from_file_location('content_asset_models', MODELS_PATH)
models = importlib.util.module_from_spec(models_spec)
models_spec.loader.exec_module(models)
AssetSource = models.AssetSource

router_spec = importlib.util.spec_from_file_location('content_assets_router', ROUTER_PATH)
router = importlib.util.module_from_spec(router_spec)
router_spec.loader.exec_module(router)


def test_parse_source_modules_supports_repeated_and_csv_values():
    parsed = router._parse_source_modules(["blog_writer", "youtube,podcast"])
    assert parsed == [AssetSource.BLOG_WRITER, AssetSource.YOUTUBE, AssetSource.PODCAST]


def test_parse_source_modules_raises_for_invalid_values():
    try:
        router._parse_source_modules(["blog_writer,unknown"])
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "Invalid source module" in exc.detail
    else:
        raise AssertionError("Expected HTTPException for invalid source module")
