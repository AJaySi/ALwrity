"""Helper script to fetch the Wix OAuth re-consent URL for manual testing.

This script does NOT change any backend behaviour. It simply calls the
unauthenticated `/api/wix/test/auth/url` endpoint (which already exists for
testing) to retrieve the authorization URL that includes all required scopes
and prints it to the console. Optionally it can open the URL in the default
web browser to start the re-consent flow.

Usage:

    python scripts/wix_reconsent_helper.py --base-url http://localhost:8000 --open

Options:
    --base-url   Base URL where the ALwrity backend is running. Defaults to
                 http://localhost:8000.
    --open       If provided, the script will attempt to open the URL in the
                 system default web browser after fetching it.
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from typing import Optional

import requests


TEST_AUTH_ENDPOINT = "/api/wix/test/auth/url"


def fetch_authorization_url(base_url: str) -> str:
    """Fetch the Wix authorization URL from the test endpoint."""

    endpoint = base_url.rstrip("/") + TEST_AUTH_ENDPOINT
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - simple helper
        raise SystemExit(f"Failed to fetch authorization URL: {exc}") from exc

    payload = response.json() or {}
    url: Optional[str] = payload.get("url") or payload.get("authorization_url")
    if not url:
        raise SystemExit(
            "Test endpoint did not return an authorization URL. "
            "Ensure the backend is running and the endpoint is available."
        )

    # Provide a small summary for the caller.
    scope = None
    if "scope=" in url:
        scope = url.split("scope=")[-1].split("&")[0]

    print("✅ Wix authorization URL fetched successfully:\n")
    print(url)
    if scope:
        print("\nScopes requested:")
        for item in scope.split(","):
            print(f"  - {item}")

    return url


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Wix OAuth re-consent URL")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the ALwrity backend (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the fetched URL in the default web browser",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    url = fetch_authorization_url(args.base_url)

    if args.open:
        print("\nOpening web browser for re-consent...")
        webbrowser.open(url)


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()
