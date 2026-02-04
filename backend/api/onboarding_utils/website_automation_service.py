"""
Onboarding Website Automation Utilities
Adds generated page images to markdown output for deployment.
"""

from typing import Dict


PAGE_LABELS = {
    "home": "Home",
    "about": "About",
    "contact": "Contact",
    "products": "Products",
}


def add_page_images_to_markdown(pages: Dict[str, str], page_images: Dict[str, str]) -> Dict[str, str]:
    """Prepend page images to markdown content for supported pages."""
    if not pages:
        return {}

    updated_pages = dict(pages)
    for page_key, markdown in pages.items():
        image_base64 = (page_images or {}).get(page_key)
        if not image_base64:
            continue
        image_src = image_base64 if image_base64.startswith("data:") else f"data:image/png;base64,{image_base64}"
        label = PAGE_LABELS.get(page_key, page_key.title())
        image_markdown = f"![{label} page image]({image_src})\n\n"
        updated_pages[page_key] = f"{image_markdown}{markdown or ''}"
    return updated_pages
