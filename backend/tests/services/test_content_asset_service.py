import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVICE_PATH = ROOT / 'backend' / 'services' / 'content_asset_service.py'
MODELS_PATH = ROOT / 'backend' / 'models' / 'content_asset_models.py'

models_spec = importlib.util.spec_from_file_location('content_asset_models', MODELS_PATH)
models = importlib.util.module_from_spec(models_spec)
models_spec.loader.exec_module(models)
AssetSource = models.AssetSource

service_spec = importlib.util.spec_from_file_location('content_asset_service', SERVICE_PATH)
service_module = importlib.util.module_from_spec(service_spec)
service_spec.loader.exec_module(service_module)
ContentAssetService = service_module.ContentAssetService


class DummyQuery:
    def __init__(self):
        self.filters = []

    def filter(self, expr):
        self.filters.append(expr)
        return self

    def count(self): return 0
    def order_by(self, *_args, **_kwargs): return self
    def limit(self, *_args, **_kwargs): return self
    def offset(self, *_args, **_kwargs): return self
    def all(self): return []


class DummyDB:
    def __init__(self): self.query_obj = DummyQuery()
    def query(self, *_args, **_kwargs): return self.query_obj


def test_get_user_assets_accepts_multiple_source_modules_filter():
    db = DummyDB()
    service = ContentAssetService(db)

    assets, total = service.get_user_assets(
        user_id="user-1",
        source_modules=[AssetSource.BLOG_WRITER, AssetSource.YOUTUBE],
    )

    assert assets == []
    assert total == 0
    assert len(db.query_obj.filters) >= 2
