"""
LinkedIn Carousel PDF Renderer

Renders text-based carousel slides into visually appealing PNG images
and composes them into a LinkedIn-compatible PDF document (1.91:1 ratio).
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, PageBreak

logger = logging.getLogger(__name__)


class LinkedInCarouselPDFRenderer:

    COLOR_SCHEMES = {
        'professional': {
            'background_start': (25, 55, 109),
            'background_end': (41, 128, 185),
            'title_color': (255, 255, 255),
            'content_color': (236, 240, 241),
            'accent_color': (52, 152, 219),
        },
        'creative': {
            'background_start': (142, 68, 173),
            'background_end': (231, 76, 60),
            'title_color': (255, 255, 255),
            'content_color': (245, 245, 245),
            'accent_color': (241, 196, 15),
        },
        'industry': {
            'background_start': (39, 174, 96),
            'background_end': (44, 62, 80),
            'title_color': (255, 255, 255),
            'content_color': (236, 240, 241),
            'accent_color': (46, 204, 113),
        },
        'dark': {
            'background_start': (20, 20, 30),
            'background_end': (60, 60, 80),
            'title_color': (255, 255, 255),
            'content_color': (200, 200, 210),
            'accent_color': (100, 200, 255),
        },
        'minimal': {
            'background_start': (245, 245, 250),
            'background_end': (255, 255, 255),
            'title_color': (44, 62, 80),
            'content_color': (80, 80, 90),
            'accent_color': (52, 152, 219),
        },
    }

    def __init__(self, output_dir: str = None):
        self.slide_width = 1200
        self.slide_height = 627
        self.slide_aspect_ratio = "1.91:1"
        self.max_file_size_bytes = 100 * 1024 * 1024
        self.max_slides = 300
        self.output_dir = output_dir or "data/media/linkedin_carousels"

    async def render_carousel_to_pdf(
        self,
        carousel_data: Dict[str, Any],
        color_scheme: str = 'professional',
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        start_time = datetime.now()
        os.makedirs(self.output_dir, exist_ok=True)

        try:
            slides = carousel_data.get('slides', [])
            if not slides:
                return {'success': False, 'error': 'No slides to render'}

            title = carousel_data.get('title', 'LinkedIn Carousel')
            cover_slide = carousel_data.get('cover_slide')
            cta_slide = carousel_data.get('cta_slide')
            total_slides = len(slides) + (1 if cover_slide else 0) + (1 if cta_slide else 0)

            if total_slides > self.max_slides:
                error = f'Too many slides: {total_slides} exceeds max {self.max_slides}'
                return {'success': False, 'error': error}

            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_paths = []

            if cover_slide:
                path = self._render_slide(
                    slide=cover_slide, slide_number=0, session_id=session_id,
                    color_scheme=color_scheme, is_cover=True, carousel_title=title,
                )
                if path:
                    image_paths.append(path)

            for i, slide in enumerate(slides):
                path = self._render_slide(
                    slide=slide, slide_number=i + 1, session_id=session_id,
                    color_scheme=color_scheme, is_cover=False,
                )
                if path:
                    image_paths.append(path)

            if cta_slide:
                path = self._render_slide(
                    slide=cta_slide, slide_number=len(slides) + 1, session_id=session_id,
                    color_scheme=color_scheme, is_cta=True,
                )
                if path:
                    image_paths.append(path)

            if not image_paths:
                return {'success': False, 'error': 'No slide images generated'}

            pdf_filename = f"linkedin_carousel_{session_id}.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            pdf_bytes = self._compose_pdf(image_paths, pdf_path)

            file_size = len(pdf_bytes)
            if file_size > self.max_file_size_bytes:
                logger.warning("PDF size %.2f MB exceeds max %.2f MB",
                               file_size / (1024 * 1024), self.max_file_size_bytes / (1024 * 1024))

            generation_time = (datetime.now() - start_time).total_seconds()

            return {
                'success': True,
                'pdf_bytes': pdf_bytes,
                'pdf_path': pdf_path,
                'metadata': {
                    'slide_count': len(image_paths),
                    'generation_time': generation_time,
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'dimensions': f'{self.slide_width}x{self.slide_height}',
                    'aspect_ratio': self.slide_aspect_ratio,
                }
            }

        except Exception as e:
            logger.error("Error rendering carousel PDF: %s", str(e))
            return {'success': False, 'error': f'Carousel PDF rendering failed: {str(e)}'}

    def _render_slide(
        self,
        slide: Dict[str, Any],
        slide_number: int,
        session_id: str,
        color_scheme: str = 'professional',
        is_cover: bool = False,
        is_cta: bool = False,
        carousel_title: str = '',
    ) -> Optional[str]:
        try:
            colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES['professional'])

            img = Image.new('RGB', (self.slide_width, self.slide_height))
            draw = ImageDraw.Draw(img)

            self._draw_gradient(draw, colors)

            draw.rectangle([0, self.slide_height - 6, self.slide_width, self.slide_height], fill=colors['accent_color'])

            if is_cover:
                self._draw_centered_text(draw, carousel_title or slide.get('title', ''),
                                         (self.slide_width // 2, 180), colors['title_color'],
                                         font_size=42, max_width=self.slide_width - 160)

                subtitle = slide.get('content', '')
                if subtitle:
                    self._draw_centered_text(draw, subtitle,
                                             (self.slide_width // 2, 320), colors['content_color'],
                                             font_size=24, max_width=self.slide_width - 200, max_lines=3)

                self._draw_centered_text(draw, "Swipe to explore →",
                                         (self.slide_width // 2, 480), colors['accent_color'],
                                         font_size=18)
            elif is_cta:
                self._draw_text(draw, slide.get('title', ''), (60, 160), colors['title_color'],
                                font_size=36, max_width=self.slide_width - 120, max_lines=2)

                content = slide.get('content', '')
                if content:
                    self._draw_text(draw, content, (60, 260), colors['content_color'],
                                    font_size=22, max_width=self.slide_width - 120, max_lines=6)

                btn_x, btn_y = self.slide_width // 2 - 200, 440
                draw.rounded_rectangle([btn_x, btn_y, btn_x + 400, btn_y + 55], radius=27, fill=colors['accent_color'])
                self._draw_centered_text(draw, "Share Your Thoughts →",
                                         (self.slide_width // 2, btn_y + 27), (255, 255, 255), font_size=22)
            else:
                self._draw_text(draw, str(slide_number),
                                (self.slide_width - 50, 20), colors['accent_color'], font_size=16)

                title = slide.get('title', '')
                if title:
                    self._draw_text(draw, title, (60, 50), colors['title_color'],
                                    font_size=30, max_width=self.slide_width - 120, max_lines=2)

                content = slide.get('content', '')
                if content:
                    self._draw_text(draw, content, (60, 145), colors['content_color'],
                                    font_size=20, max_width=self.slide_width - 120, max_lines=10)

                visual_elements = slide.get('visual_elements', [])
                if visual_elements:
                    self._draw_visual_elements(draw, visual_elements, colors)

            filename = f"slide_{session_id}_{slide_number:03d}.png"
            filepath = os.path.join(self.output_dir, filename)
            img.save(filepath, 'PNG', optimize=True)
            return filepath

        except Exception as e:
            logger.error("Error rendering slide %d: %s", slide_number, str(e))
            return None

    def _draw_gradient(self, draw: ImageDraw.Draw, colors: Dict):
        sr, sg, sb = colors['background_start']
        er, eg, eb = colors['background_end']
        for y in range(self.slide_height):
            t = y / self.slide_height
            draw.line([(0, y), (self.slide_width, y)],
                      fill=(int(sr + (er - sr) * t), int(sg + (eg - sg) * t), int(sb + (eb - sb) * t)))

    def _draw_text(self, draw: ImageDraw.Draw, text: str, position: tuple, color: tuple,
                   font_size: int = 20, max_width: int = None, max_lines: int = None, bold: bool = False):
        font = self._get_font(font_size, bold)
        x, y = position

        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bb = draw.textbbox((0, 0), test_line, font=font)
            tw = bb[2] - bb[0]
            if max_width and tw > max_width and current_line:
                lines.append(current_line)
                if max_lines and len(lines) >= max_lines:
                    lines[-1] = lines[-1][:-3] + "..."
                    break
                current_line = word
            else:
                current_line = test_line
        if current_line and (not max_lines or len(lines) < max_lines):
            lines.append(current_line)

        line_height = int(font_size * 1.4)
        for i, line in enumerate(lines):
            draw.text((x, y + i * line_height), line, fill=color, font=font)

    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str, center: tuple, color: tuple,
                            font_size: int = 20, max_width: int = None, max_lines: int = None, bold: bool = False):
        font = self._get_font(font_size, bold)
        cx, cy = center

        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bb = draw.textbbox((0, 0), test_line, font=font)
            tw = bb[2] - bb[0]
            if max_width and tw > max_width and current_line:
                lines.append(current_line)
                if max_lines and len(lines) >= max_lines:
                    lines[-1] = lines[-1][:-3] + "..."
                    break
                current_line = word
            else:
                current_line = test_line
        if current_line and (not max_lines or len(lines) < max_lines):
            lines.append(current_line)

        line_height = int(font_size * 1.4)
        total_height = len(lines) * line_height
        start_y = cy - total_height // 2

        for i, line in enumerate(lines):
            bb = draw.textbbox((0, 0), line, font=font)
            tw = bb[2] - bb[0]
            x = cx - tw // 2
            draw.text((x, start_y + i * line_height), line, fill=color, font=font)

    def _draw_visual_elements(self, draw: ImageDraw.Draw, elements: List[str], colors: Dict):
        y_start = self.slide_height - 60
        x_start = 60
        for i, element in enumerate(elements[:4]):
            cx = x_start + i * 280
            draw.ellipse([cx, y_start, cx + 12, y_start + 12], fill=colors['accent_color'])
            font = self._get_font(12, False)
            draw.text((cx + 20, y_start - 2), element[:25], fill=colors['content_color'], font=font)

    def _get_font(self, size: int, bold: bool = False):
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
        except (IOError, OSError):
            try:
                return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
            except (IOError, OSError):
                return ImageFont.load_default()

    def _compose_pdf(self, image_paths: List[str], output_path: str) -> bytes:
        pw = self.slide_width
        ph = self.slide_height
        # Leave 1pt margin to avoid ReportLab frame size issues
        m = 1
        iw = pw - 2 * m
        ih = ph - 2 * m

        from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
        from reportlab.lib.pagesizes import landscape

        frame = Frame(m, m, iw, ih, id="slide_frame",
                       leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        template = PageTemplate(id="slide", frames=[frame], pagesize=(pw, ph))
        doc = BaseDocTemplate(output_path, pagesize=(pw, ph))
        doc.addPageTemplates([template])

        story = []
        for i, img_path in enumerate(image_paths):
            story.append(RLImage(img_path, width=iw, height=ih))
            if i < len(image_paths) - 1:
                story.append(PageBreak())

        doc.build(story)

        with open(output_path, 'rb') as f:
            return f.read()
