from __future__ import annotations

from typing import Iterable


def _render_shop_page(shop_data: dict) -> str:
    title = shop_data.get("title", "Shop")
    description = shop_data.get("description", "")
    product_assets = shop_data.get("product_assets", [])

    sections = [f"# {title}"]
    if description:
        sections.append(description)

    assets_markdown = _render_product_assets_markdown(product_assets)
    if assets_markdown:
        sections.append("## Product Assets")
        sections.append(assets_markdown)

    return "\n\n".join(sections).strip()


def _render_product_assets_markdown(product_assets: Iterable[object]) -> str:
    if not product_assets:
        return ""

    lines: list[str] = []
    for asset in product_assets:
        url, alt_text = _normalize_asset(asset)
        if not url:
            continue
        lines.append(f"- {alt_text}: {url}")
        lines.append(f"![{alt_text}]({url})")

    return "\n".join(lines)


def _normalize_asset(asset: object) -> tuple[str, str]:
    if isinstance(asset, str):
        return asset, "Product image"
    if isinstance(asset, dict):
        url = (
            asset.get("url")
            or asset.get("asset_url")
            or asset.get("image_url")
            or asset.get("image")
            or ""
        )
        alt_text = asset.get("alt") or asset.get("title") or asset.get("name") or "Product image"
        return url, alt_text
    return "", "Product image"
