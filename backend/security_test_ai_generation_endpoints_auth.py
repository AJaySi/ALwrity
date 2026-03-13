from pathlib import Path
import ast


SOURCE_PATH = Path("backend/api/content_planning/api/content_strategy/endpoints/ai_generation_endpoints.py")
SOURCE = SOURCE_PATH.read_text()
MODULE = ast.parse(SOURCE)


def _get_async_function(name: str) -> ast.AsyncFunctionDef:
    for node in MODULE.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Function {name} not found")


def _arg_names(node: ast.AsyncFunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args]


def test_public_routes_use_current_user_not_client_user_id_param():
    route_names = [
        "generate_comprehensive_strategy",
        "generate_strategy_component",
        "get_strategy_generation_status",
        "generate_comprehensive_strategy_polling",
        "get_strategy_generation_status_by_task",
        "get_latest_generated_strategy",
    ]

    for name in route_names:
        fn = _get_async_function(name)
        arg_names = _arg_names(fn)
        assert "current_user" in arg_names
        assert "user_id" not in arg_names


def test_polling_route_derives_user_id_from_authenticated_claims_only():
    fn = _get_async_function("generate_comprehensive_strategy_polling")
    fn_source = ast.get_source_segment(SOURCE, fn)

    assert 'user_id = _get_authenticated_user_id(current_user)' in fn_source
    assert 'request.get("user_id"' not in fn_source
    assert 'request.get("user_id", 1)' not in fn_source


def test_task_status_route_enforces_task_owner_authorization_check():
    fn = _get_async_function("get_strategy_generation_status_by_task")
    fn_source = ast.get_source_segment(SOURCE, fn)

    assert 'if str(task_status.get("user_id")) != user_id:' in fn_source
    assert 'status_code=403' in fn_source
    assert 'Not authorized to access this task status' in fn_source


def test_missing_authenticated_user_id_returns_401():
    assert 'raise HTTPException(status_code=401, detail="Authenticated user ID is required")' in SOURCE
