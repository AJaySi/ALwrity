"""Static typing assertions for integration registry.

Run with a static type checker, e.g.:
    PYTHONPATH=backend mypy --ignore-missing-imports backend/tests/integrations/test_registry_typing.py
"""

from typing import cast
from typing_extensions import assert_type

from services.integrations.base import IntegrationProvider
from services.integrations.registry import get_provider


def test_get_provider_known_keys_are_optional_provider() -> None:
    assert_type(cast(IntegrationProvider | None, get_provider("gsc")), IntegrationProvider | None)
    assert_type(cast(IntegrationProvider | None, get_provider("bing")), IntegrationProvider | None)
    assert_type(cast(IntegrationProvider | None, get_provider("wordpress")), IntegrationProvider | None)
    assert_type(cast(IntegrationProvider | None, get_provider("wix")), IntegrationProvider | None)
