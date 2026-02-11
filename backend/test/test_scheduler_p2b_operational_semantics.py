from pathlib import Path


def _function_block(content: str, start_token: str, end_token: str) -> str:
    start = content.index(start_token)
    end = content.index(end_token, start)
    return content[start:end]


def test_platform_status_get_is_read_only():
    source = Path(__file__).resolve().parents[1] / "api" / "scheduler" / "platform.py"
    content = source.read_text()

    get_block = _function_block(
        content,
        "async def get_platform_insights_status(",
        "@router.post(\"/platform-insights/reconcile/{user_id}\")",
    )

    assert "create_platform_insights_task" not in get_block
    assert "db.commit(" not in get_block
    assert "db.add(" not in get_block


def test_reconcile_endpoints_exist_for_explicit_mutation_paths():
    platform_source = Path(__file__).resolve().parents[1] / "api" / "scheduler" / "platform.py"
    dashboard_source = Path(__file__).resolve().parents[1] / "api" / "scheduler" / "dashboard.py"

    platform_content = platform_source.read_text()
    dashboard_content = dashboard_source.read_text()

    assert "@router.post(\"/platform-insights/reconcile/{user_id}\")" in platform_content
    assert "@router.post(\"/dashboard/cumulative-stats/reconcile\")" in dashboard_content


def test_dashboard_get_cumulative_stats_has_no_write_side_effects():
    source = Path(__file__).resolve().parents[1] / "api" / "scheduler" / "dashboard.py"
    content = source.read_text()

    block = _function_block(content, "def _get_cumulative_stats(db: Session)", "def _extract_user_id_from_job")
    assert "db.commit(" not in block
    assert "db.add(" not in block


def test_platform_insights_unique_index_migration_present():
    migration = Path(__file__).resolve().parents[1] / "database" / "migrations" / "008_platform_insights_unique_user_platform.sql"
    content = migration.read_text()

    assert "CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_insights_user_platform" in content
    assert "DELETE FROM platform_insights_tasks" in content
