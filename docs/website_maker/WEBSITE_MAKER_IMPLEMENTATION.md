# Website Maker Implementation Details

## Purpose
The Website Maker workflow renders shop preview content (HTML for web previews and Markdown for onboarding summaries) with product asset images included inline. This ensures:

- Shop previews show visual assets inside the page body rather than only link lists.
- Onboarding output includes Markdown image embeds so downstream previews and generated content can render visuals.
- The Open Graph (OG) image builder can still prefer product asset images (handled elsewhere), while the page body itself surfaces those same images for consistency.

## High-Level Architecture
The implementation is split into two rendering surfaces:

1. **HTML renderer** (backend service layer): `WebsiteAutomationService._render_shop_assets_html`.
2. **Markdown renderer** (onboarding utilities): `_render_shop_page` and `_render_product_assets_markdown`.

These functions are intentionally small, deterministic, and pure string renderers. They do not fetch remote assets or resolve URLs; they only format the provided data.

## HTML Rendering Path (Service Layer)
**Location:** `backend/services/website_automation_service.py`.

### Entry Point
`WebsiteAutomationService._render_shop_assets_html(product_assets: Iterable[object]) -> str`

### Inputs
- `product_assets`: an iterable of asset payloads. Each payload can be:
  - **String URL** (e.g., `"https://cdn.site.com/img.jpg"`).
  - **Dict** containing URL/metadata fields.

### Output
- Returns a string of HTML wrapping all assets, or an empty string if nothing valid is provided.
- Layout structure:
  ```html
  <div class="shop-assets">
    <figure class="product-asset">
      <a href="{url}" target="_blank" rel="noopener noreferrer">
        <img src="{url}" alt="{alt}" loading="lazy" />
      </a>
      <figcaption>{caption}</figcaption>
    </figure>
  </div>
  ```

### Asset Normalization
`_normalize_asset` extracts the URL, alt text, and optional caption.

#### Supported shapes
- String: used as the URL, alt defaults to `"Product image"`.
- Dict: URL is determined by first non-empty match in:
  - `url`, `asset_url`, `image_url`, `image`
- Alt text (first non-empty):
  - `alt`, `title`, `name` (fallback: `"Product image"`)
- Caption (optional):
  - `caption`, `label`

### Output rules
- Assets without a valid URL are dropped.
- HTML is escaped via `html.escape` for URL, alt text, and captions.
- The `<img>` tag is wrapped in an `<a>` tag to allow full-size viewing.
- Captions are only rendered when provided.

### Extension points
- **Styling**: target `.shop-assets` and `.product-asset` in CSS to control layout (grid, spacing, etc.).
- **Additional metadata**: extend `_normalize_asset` to support new keys (e.g., `"thumbnail_url"`, `"description"`).
- **Accessibility**: supply better `alt` text upstream for descriptive images.

## Markdown Rendering Path (Onboarding Utilities)
**Location:** `backend/api/onboarding_utils/website_automation_service.py`.

### Entry Point
`_render_shop_page(shop_data: dict) -> str`

### Inputs
- `shop_data` dictionary with:
  - `title`: page title (defaults to `"Shop"`).
  - `description`: optional description paragraph.
  - `product_assets`: list of asset payloads (same shapes as HTML renderer).

### Output
A Markdown string with the following structure:

```markdown
# {title}

{description}

## Product Assets
- {alt_text}: {url}
![{alt_text}]({url})
```

### Asset Markdown Format
The helper `_render_product_assets_markdown` emits **two lines per asset**:
1. A bullet line including label and URL: `- {alt_text}: {url}`.
2. A Markdown image embed: `![{alt_text}]({url})`.

This ensures both a textual link and a visual embed are present in previews.

### Asset Normalization
`_normalize_asset` follows the same URL/alt rules as the HTML renderer, ensuring consistent data interpretation across preview surfaces.

### Output rules
- If no valid assets are present, no Product Assets section is added.
- Markdown output is intentionally plain; URL escaping is not performed here (expecting well-formed inputs).

### Extension points
- Add per-asset captions by extending normalization and emitting text blocks under each image.
- Inject additional sections (pricing, variants, CTA links) by appending new Markdown blocks in `_render_shop_page`.

## Data Flow Summary
1. Upstream code constructs `shop_data` with `product_assets` populated.
2. HTML preview path uses `WebsiteAutomationService._render_shop_assets_html` to embed images for browser previews.
3. Onboarding preview path uses `_render_shop_page` for Markdown with inline images.
4. OG image selection can still prefer product assets (handled elsewhere) while the page body displays the same assets.

## Error Handling & Guardrails
- Both renderers silently skip invalid/empty asset URLs.
- Empty input returns an empty string (HTML) or omits the assets section (Markdown).
- There are no external calls, so output is deterministic and fast.

## Testing Notes
- There are no automated tests today for these rendering helpers.
- Suggested tests when adding coverage:
  - Input with string URL renders correct HTML/Markdown.
  - Dict with `image_url` and `title` uses those values.
  - Invalid URLs are skipped and do not render empty tags.
  - Captions render in HTML only when provided.

## Example Inputs/Outputs

### Example Input
```json
{
  "title": "Winter Collection",
  "description": "Warm essentials for the season.",
  "product_assets": [
    "https://cdn.store.com/coat.jpg",
    {"image_url": "https://cdn.store.com/boots.jpg", "title": "Leather Boots"},
    {"url": "https://cdn.store.com/hat.jpg", "alt": "Wool Hat", "caption": "Limited edition"}
  ]
}
```

### HTML Output (excerpt)
```html
<div class="shop-assets">
  <figure class="product-asset">
    <a href="https://cdn.store.com/coat.jpg" target="_blank" rel="noopener noreferrer">
      <img src="https://cdn.store.com/coat.jpg" alt="Product image" loading="lazy" />
    </a>
  </figure>
  <figure class="product-asset">
    <a href="https://cdn.store.com/boots.jpg" target="_blank" rel="noopener noreferrer">
      <img src="https://cdn.store.com/boots.jpg" alt="Leather Boots" loading="lazy" />
    </a>
  </figure>
  <figure class="product-asset">
    <a href="https://cdn.store.com/hat.jpg" target="_blank" rel="noopener noreferrer">
      <img src="https://cdn.store.com/hat.jpg" alt="Wool Hat" loading="lazy" />
    </a>
    <figcaption>Limited edition</figcaption>
  </figure>
</div>
```

### Markdown Output (excerpt)
```markdown
# Winter Collection

Warm essentials for the season.

## Product Assets
- Product image: https://cdn.store.com/coat.jpg
![Product image](https://cdn.store.com/coat.jpg)
- Leather Boots: https://cdn.store.com/boots.jpg
![Leather Boots](https://cdn.store.com/boots.jpg)
- Wool Hat: https://cdn.store.com/hat.jpg
![Wool Hat](https://cdn.store.com/hat.jpg)
```

## Implementation Files
- `backend/services/website_automation_service.py`
- `backend/api/onboarding_utils/website_automation_service.py`

These modules are the authoritative source for rendering shop assets in HTML and Markdown.
