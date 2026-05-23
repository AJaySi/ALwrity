from pathlib import Path

from services.user_workspace_manager import UserWorkspaceManager


def _configure_temp_workspace(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspace"
    monkeypatch.setattr("services.database.WORKSPACE_DIR", str(workspace_root))
    monkeypatch.setattr("services.workspace_dirs.WORKSPACE_DIR", str(workspace_root))
    monkeypatch.setattr("services.user_workspace_manager.WORKSPACE_DIR", str(workspace_root))
    monkeypatch.setattr("services.user_workspace_manager.init_user_database", lambda user_id: None)
    return workspace_root


def _assert_required_contract(user_dir: Path):
    assert user_dir.exists()
    assert (user_dir / "db").exists()
    assert (user_dir / "assets").exists()
    assert (user_dir / "media").exists()
    assert (user_dir / "content").exists()
    assert (user_dir / "config" / "user_config.json").exists()


def test_create_user_workspace_development_contract(monkeypatch, tmp_path):
    workspace_root = _configure_temp_workspace(monkeypatch, tmp_path)
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("RAILWAY", raising=False)
    monkeypatch.delenv("HEROKU", raising=False)
    monkeypatch.delenv("ALWRITY_FILESYSTEM_MINIMAL_MODE", raising=False)

    manager = UserWorkspaceManager(db_session=None)
    result = manager.create_user_workspace("dev-user")

    expected = workspace_root / "workspace_dev-user"
    _assert_required_contract(expected)
    assert result["workspace_path"] == str(expected)
    assert result["mode"] == "development"
    assert {"db", "assets", "media", "content", "config/user_config.json"}.issubset(set(result["dirs_created"]))


def test_create_user_workspace_production_filesystem_minimal_contract(monkeypatch, tmp_path):
    workspace_root = _configure_temp_workspace(monkeypatch, tmp_path)
    monkeypatch.setenv("RENDER", "1")
    monkeypatch.setenv("ALWRITY_FILESYSTEM_MINIMAL_MODE", "1")

    manager = UserWorkspaceManager(db_session=None)
    result = manager.create_user_workspace("prod-user")

    expected = workspace_root / "workspace_prod-user"
    _assert_required_contract(expected)
    assert result["workspace_path"] == str(expected)
    assert result["mode"] == "filesystem_minimal"
    assert {"db", "assets", "media", "content", "config/user_config.json"}.issubset(set(result["dirs_created"]))
