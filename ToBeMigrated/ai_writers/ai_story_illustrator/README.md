# AI Story Illustrator

The AI Story Illustrator is a powerful tool that generates beautiful illustrations for stories using Google's Gemini AI. This module allows users to input stories via text, file upload, or URL, and automatically generates appropriate illustrations for different scenes in the story.

## Features

- **Multiple Input Methods**: Input stories via direct text entry, file upload, or URL extraction
- **Intelligent Scene Segmentation**: Automatically divides stories into logical segments for illustration
- **Customizable Illustration Styles**: Choose from various artistic styles or define your own
- **Scene Element Extraction**: Analyzes story segments to identify key visual elements
- **Multiple Export Options**: Export as PDF storybook or ZIP archive of individual images
- **Customizable Aspect Ratios**: Support for different image dimensions (16:9, 4:3, 1:1)
- **Advanced Settings**: Control the number of segments to illustrate and other parameters

## Usage

The Story Illustrator is integrated into the Alwrity platform and can be accessed through the main interface. The workflow consists of three main steps:

1. **Story Input**: Enter your story text, upload a file, or provide a URL
2. **Illustration Settings**: Configure the style, aspect ratio, and other parameters
3. **Generate & Export**: Generate illustrations for all or individual segments and export the results

## Technical Details

### Dependencies

- Streamlit: For the user interface
- Gemini AI: For image generation
- BeautifulSoup: For URL text extraction
- ReportLab: For PDF generation (optional)
- PIL: For image processing

### Key Functions

- `segment_story()`: Divides a story into logical segments for illustration
- `extract_scene_elements()`: Analyzes story segments to identify key visual elements
- `generate_illustration_prompt()`: Creates detailed prompts for the AI image generator
- `create_illustration()`: Generates an illustration for a story segment
- `create_storybook_pdf()`: Combines story text and illustrations into a PDF
- `create_zip_archive()`: Creates a ZIP archive of individual illustrations

## Example

```python
from lib.ai_writers.ai_story_illustrator.story_illustrator import write_story_illustrator

# Run the Story Illustrator app
write_story_illustrator()
```

## Best Practices

- **Provide Clear Segments**: The system works best with stories that have clear scene transitions
- **Be Specific with Styles**: More specific style descriptions yield better results
- **Balance Text and Images**: For best results, aim for segments of 100-500 words per illustration
- **Review and Regenerate**: If an illustration doesn't capture the scene well, use the regenerate option

## Future Enhancements

- Support for more export formats (EPUB, HTML)
- Enhanced character consistency across illustrations
- Animation options for digital storytelling
- Voice narration integration
- Custom character design options

## Troubleshooting

- If illustrations are not generating, check your internet connection and API access
- If PDF export fails, ensure ReportLab is installed (`pip install reportlab`)
- If URL extraction fails, try copying the text manually
- For large stories, consider processing in smaller batches

## Credits

This module uses Google's Gemini AI for image generation and leverages various open-source libraries for text processing and document generation.