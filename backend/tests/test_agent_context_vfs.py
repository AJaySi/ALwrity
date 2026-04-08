from __future__ import annotations

import json
from pathlib import Path

from services.intelligence.agent_flat_context import AgentFlatContextStore
from services.intelligence.agent_context_vfs import AgentContextVFS


def _cleanup_workspace(user_id: str, project_id: str | None = None) -> None:
    safe_user = ''.join(c for c in str(user_id) if c.isalnum() or c in ('-', '_')) or 'unknown_user'
    root = Path(__file__).resolve().parents[2] / 'workspace'
    user_dir = root / f'workspace_{safe_user}'
    if user_dir.exists():
        import shutil
        shutil.rmtree(user_dir, ignore_errors=True)

    if project_id:
        safe_project = ''.join(c for c in str(project_id) if c.isalnum() or c in ('-', '_')) or 'default_project'
        project_dir = root / f'project_{safe_project}'
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir, ignore_errors=True)


def test_search_context_query_variants_and_can_answer():
    user_id = 'pytest_vfs_user'
    _cleanup_workspace(user_id)

    store = AgentFlatContextStore(user_id)
    payload = {
        'website_url': 'https://example.com',
        'brand_analysis': {'brand_voice': 'Authoritative'},
        'recommended_settings': {'writing_tone': 'Conversational'},
        'content_type': {'primary_type': 'Blog'},
        'target_audience': {'primary_audience': 'Founders'},
    }
    assert store.save_step2_website_analysis(payload)

    vfs = AgentContextVFS(user_id)
    result = vfs.search_context('tone')

    assert result['query'] == 'tone'
    assert 'attempted_queries' in result
    assert result['attempted_queries'][0] == 'tone'
    assert result['can_answer'] is True
    assert len(result['results']) >= 1


def test_inspect_file_large_document_summary_plus_keys():
    user_id = 'pytest_vfs_large'
    _cleanup_workspace(user_id)

    store = AgentFlatContextStore(user_id)
    large_blob = 'x' * 9000
    payload = {
        'website_url': 'https://big.example.com',
        'brand_analysis': {'brand_voice': 'Bold'},
        'recommended_settings': {'writing_tone': 'Direct'},
        'target_audience': {'primary_audience': 'Teams'},
        'crawl_result': {'raw': large_blob},
    }
    assert store.save_step2_website_analysis(payload)

    vfs = AgentContextVFS(user_id)
    out = vfs.inspect_file('step2_website_analysis.json')

    assert out['mode'] == 'summary_plus_keys'
    assert 'agent_summary' in out
    assert 'keys' in out
    assert 'crawl_result' in out['keys']


def test_write_shared_note_and_activity_log_created():
    user_id = 'pytest_collab_user'
    project_id = 'proj_abc'
    _cleanup_workspace(user_id, project_id)

    vfs = AgentContextVFS(user_id, project_id=project_id)
    write_res = vfs.write_shared_note('Draft collaboration note', agent_id='agent_one')

    assert write_res['ok'] is True
    assert write_res['file'] == 'collaboration.md'

    collab = vfs.list_context()['collaboration']
    scratchpad = Path(collab['scratchpad_dir'])
    note_file = scratchpad / 'collaboration.md'
    log_file = scratchpad / 'activity_log.jsonl'

    assert note_file.exists()
    assert log_file.exists()

    content = note_file.read_text(encoding='utf-8')
    assert 'agent_one' in content
    assert 'Draft collaboration note' in content

    lines = [json.loads(l) for l in log_file.read_text(encoding='utf-8').splitlines() if l.strip()]
    assert any(entry.get('event_type') == 'shared_note_written' for entry in lines)
