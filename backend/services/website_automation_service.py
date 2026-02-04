from __future__ import annotations

from html import escape
from typing import Iterable


class WebsiteAutomationService:
    def _render_shop_assets_html(self, product_assets: Iterable[object]) -> str:
        if not product_assets:
            return ""

        rendered_assets: list[str] = []
        for asset in product_assets:
            url, alt_text, caption = self._normalize_asset(asset)
            if not url:
                continue
            img_tag = (
                f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer">'
                f'<img src="{escape(url)}" alt="{escape(alt_text)}" loading="lazy" />'
                "</a>"
            )
            if caption:
                rendered_assets.append(
                    f'<figure class="product-asset">{img_tag}'
                    f"<figcaption>{escape(caption)}</figcaption>"
                    "</figure>"
                )
            else:
                rendered_assets.append(f'<figure class="product-asset">{img_tag}</figure>')

        if not rendered_assets:
            return ""

        return '<div class="shop-assets">' + "".join(rendered_assets) + "</div>"

    @staticmethod
    def _normalize_asset(asset: object) -> tuple[str, str, str | None]:
        if isinstance(asset, str):
            return asset, "Product image", None
        if isinstance(asset, dict):
            url = (
                asset.get("url")
                or asset.get("asset_url")
                or asset.get("image_url")
                or asset.get("image")
                or ""
            )
            alt_text = asset.get("alt") or asset.get("title") or asset.get("name") or "Product image"
            caption = asset.get("caption") or asset.get("label")
            return url, alt_text, caption
        return "", "Product image", None
