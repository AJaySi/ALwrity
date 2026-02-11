import importlib.util
import sys
import types
from pathlib import Path

from fastapi import HTTPException


def _load_module(module_name: str, file_path: Path):
    parts = module_name.split('.')
    for i in range(1, len(parts)):
        pkg_name = '.'.join(parts[:i])
        if pkg_name not in sys.modules:
            pkg = types.ModuleType(pkg_name)
            pkg.__path__ = [str(file_path.parent)]
            sys.modules[pkg_name] = pkg

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


BACKEND = Path(__file__).resolve().parents[1]
VALIDATORS = _load_module("api.scheduler.validators", BACKEND / "api" / "scheduler" / "validators.py")


def test_validate_user_access_allows_owner():
    current_user = {"sub": "user_a"}
    assert VALIDATORS.validate_user_access("user_a", current_user, require_ownership=True) == "user_a"


def test_validate_user_access_blocks_cross_tenant_with_403():
    current_user = {"sub": "user_a"}

    try:
        VALIDATORS.validate_user_access("user_b", current_user, require_ownership=True)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 403
        assert "Access denied" in str(exc.detail)


def test_validate_user_access_401_without_authenticated_identity():
    current_user = {}

    try:
        VALIDATORS.validate_user_access("user_a", current_user, require_ownership=True)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401
