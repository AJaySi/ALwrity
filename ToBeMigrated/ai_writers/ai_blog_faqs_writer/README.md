# AI-Powered FAQ Generator

A sophisticated FAQ generation system that creates comprehensive, well-researched FAQs from various content sources. This tool leverages AI to analyze content, conduct web research, and generate detailed FAQs with customizable options.

## Features

### Content Processing
- **Multiple Input Sources**
  - Direct text input
  - File uploads (DOCX, TXT)
  - URL content extraction
  - Support for any content type (general, technical, educational, etc.)

### Research Capabilities
- **Multi-level Search Depth**
  - **Basic**: Google Search for quick, general information
  - **Comprehensive**: Tavily AI for detailed, in-depth research
  - **Expert**: Metaphor AI for specialized, expert-level content

### Customization Options
- **Target Audience**
  - Beginner
  - Intermediate
  - Expert

- **FAQ Style**
  - Technical
  - Conversational
  - Professional

- **Advanced Features**
  - Emoji inclusion
  - Code example generation
  - Reference integration
  - Customizable time range for research
  - Multi-language support

### Output Formats
- Interactive preview
- Markdown
- HTML
- JSON

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```python
from lib.ai_writers.ai_blog_faqs_writer.faqs_generator_blog import FAQGenerator, FAQConfig

# Initialize with default configuration
generator = FAQGenerator()

# Generate FAQs from content
faqs = await generator.generate_faqs("Your content here")
```

### Advanced Configuration
```python
from lib.ai_writers.ai_blog_faqs_writer.faqs_generator_blog import (
    FAQGenerator, FAQConfig, TargetAudience, FAQStyle, SearchDepth
)

# Custom configuration
config = FAQConfig(
    num_faqs=10,
    target_audience=TargetAudience.INTERMEDIATE,
    faq_style=FAQStyle.TECHNICAL,
    include_emojis=True,
    include_code_examples=True,
    include_references=True,
    search_depth=SearchDepth.COMPREHENSIVE,
    time_range="last_6_months",
    language="English"
)

generator = FAQGenerator(config)
```

### Web Interface
Run the Streamlit interface:
```bash
streamlit run lib/ai_writers/ai_blog_faqs_writer/faqs_ui.py
```

## Research Process

1. **Content Analysis**
   - Identifies key topics and concepts
   - Extracts potential questions
   - Determines research requirements

2. **Web Research**
   - Selects appropriate search function based on depth
   - Gathers relevant information
   - Validates and cross-references data

3. **FAQ Generation**
   - Creates comprehensive questions
   - Provides detailed answers
   - Includes code examples (if applicable)
   - Adds references and citations

## Output Structure

Each FAQ item includes:
- Question
- Detailed answer
- Category
- Code example (if applicable)
- References
- Confidence score
- Last updated timestamp

## Configuration Options

### FAQConfig Parameters
- `num_faqs`: Number of FAQs to generate (default: 5)
- `target_audience`: Target audience level (default: INTERMEDIATE)
- `faq_style`: Writing style (default: PROFESSIONAL)
- `include_emojis`: Whether to include emojis (default: True)
- `include_code_examples`: Whether to include code examples (default: True)
- `include_references`: Whether to include references (default: True)
- `search_depth`: Research depth level (default: COMPREHENSIVE)
- `time_range`: Time range for research (default: "last_6_months")
- `language`: Output language (default: "English")

## Research Depth Options

### Basic (Google Search)
- Quick, general information
- Broad coverage
- Suitable for basic topics

### Comprehensive (Tavily AI)
- Detailed, in-depth research
- Multiple source integration
- Best for most use cases

### Expert (Metaphor AI)
- Specialized, expert-level content
- Advanced topic coverage
- Technical and academic focus

## Best Practices

1. **Content Preparation**
   - Provide clear, well-structured content
   - Include key terms and concepts
   - Specify target audience and style

2. **Research Selection**
   - Use Basic for general topics
   - Choose Comprehensive for detailed analysis
   - Select Expert for technical subjects

3. **Output Review**
   - Verify accuracy of information
   - Check code examples
   - Validate references

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.

## Acknowledgments

- OpenAI for GPT integration
- Google Search API
- Tavily AI
- Metaphor AI
- BeautifulSoup for web scraping
- Streamlit for UI 