"""Quick route-level audit to enforce user-scoped access checks."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Tuple

ROUTES_DIR = Path(__file__).resolve().parent


def _decorator_path(decorator: ast.AST) -> str | None:
    """Extract route path from decorators like @router.get("/usage/{user_id}")."""
    if not isinstance(decorator, ast.Call):
        return None
    if not isinstance(decorator.func, ast.Attribute):
        return None
    if not decorator.args:
        return None

    first_arg = decorator.args[0]
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        return first_arg.value
    return None


def _has_current_user_dependency(fn_node: ast.AsyncFunctionDef) -> bool:
    for arg in fn_node.args.args:
        if arg.arg != "current_user":
            continue
        default_index = fn_node.args.args.index(arg) - (len(fn_node.args.args) - len(fn_node.args.defaults))
        if default_index < 0:
            continue
        default_node = fn_node.args.defaults[default_index]
        if not isinstance(default_node, ast.Call):
            continue
        if isinstance(default_node.func, ast.Name) and default_node.func.id == "Depends":
            if default_node.args and isinstance(default_node.args[0], ast.Name):
                return default_node.args[0].id == "get_current_user"
    return False


def _has_verify_user_access_call(fn_node: ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(fn_node):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "verify_user_access":
            return True
    return False


def run_access_audit() -> List[Tuple[str, str]]:
    """Return (file, function) pairs for user-scoped routes missing auth checks."""
    failures: List[Tuple[str, str]] = []

    for route_file in ROUTES_DIR.glob("*.py"):
        if route_file.name in {"__init__.py", Path(__file__).name}:
            continue

        tree = ast.parse(route_file.read_text(), filename=str(route_file))
        for node in tree.body:
            if not isinstance(node, ast.AsyncFunctionDef):
                continue

            route_paths = [p for d in node.decorator_list if (p := _decorator_path(d))]
            if not any("{user_id}" in p for p in route_paths):
                continue

            if not _has_current_user_dependency(node) or not _has_verify_user_access_call(node):
                failures.append((route_file.name, node.name))

    return failures


if __name__ == "__main__":
    issues = run_access_audit()
    if issues:
        for file_name, fn_name in issues:
            print(f"FAIL: {file_name}:{fn_name} missing get_current_user/verify_user_access pattern")
        raise SystemExit(1)

    print("PASS: all user-scoped routes include get_current_user and verify_user_access")
