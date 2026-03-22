# GitHub Blog Generator

A powerful AI-powered content generation system that automatically creates comprehensive documentation, tutorials, and guides from GitHub repositories. This module transforms GitHub repository data into various types of high-quality technical content.

## Features

### 1. Content Generation Types

The system can generate the following types of content from GitHub repositories:

- **Getting Started Guides**
  - Introduction and Overview
  - Prerequisites and Setup
  - Installation Instructions
  - Basic Usage Examples
  - Common Use Cases
  - Best Practices
  - Next Steps and Resources

- **Technical Documentation**
  - Architecture Overview
  - Core Components
  - Technical Specifications
  - Integration Points
  - Performance Considerations
  - Security Features
  - API Documentation
  - Configuration Options
  - Deployment Guidelines
  - Troubleshooting Guide

- **Tutorial Series**
  - Beginner Tutorials
    - Basic concepts
    - Simple examples
    - Step-by-step instructions
  - Intermediate Tutorials
    - Advanced features
    - Real-world examples
    - Best practices
  - Advanced Tutorials
    - Complex use cases
    - Performance optimization
    - Integration patterns

- **Comparison Analysis**
  - Feature Comparison
  - Performance Analysis
  - Use Case Suitability
  - Community and Support
  - Learning Curve
  - Integration Capabilities
  - Future Prospects

- **Case Studies**
  - Problem Statement
  - Solution Implementation
  - Technical Challenges
  - Results and Benefits
  - Lessons Learned
  - Future Improvements

- **Contribution Guides**
  - Development Setup
  - Code Style Guidelines
  - Testing Requirements
  - Documentation Standards
  - Pull Request Process
  - Review Guidelines
  - Community Guidelines

- **Security Guides**
  - Security Architecture
  - Authentication & Authorization
  - Data Protection
  - Secure Configuration
  - Vulnerability Management
  - Incident Response
  - Compliance Requirements

- **Performance Guides**
  - Performance Metrics
  - Optimization Techniques
  - Benchmarking Guidelines
  - Resource Management
  - Scaling Strategies
  - Monitoring Setup
  - Troubleshooting

### 2. GitHub Content Scraping

The module includes a sophisticated GitHub content scraper with the following capabilities:

- **Rate Limiting**
  - Configurable API call limits
  - Automatic request throttling
  - Concurrent request management

- **Caching System**
  - Configurable cache duration (TTL)
  - Automatic cache invalidation
  - Efficient storage of scraped content

- **Content Extraction**
  - Repository metadata
  - README content
  - File contents
  - Repository topics
  - Contributor information
  - License information

### 3. Content Enhancement

- **Online Research Integration**
  - Automatic topic research
  - Related content discovery
  - Industry trend analysis

- **FAQ Generation**
  - Automatic FAQ creation
  - Common question identification
  - Comprehensive answers

- **Metadata Generation**
  - SEO-optimized titles
  - Meta descriptions
  - Tags and categories
  - Content structuring

## Usage Examples

### Basic Usage

```python
from lib.ai_writers.github_blogs import GitHubBlogGenerator

# Initialize the generator
generator = GitHubBlogGenerator()

# Generate content for a GitHub repository
content = await generator.generate_content(
    github_url="https://github.com/owner/repo",
    content_types=["getting_started", "technical_docs", "tutorials"]
)

# Save the generated content
generator.save_content(content, "my_repository")
```

### Advanced Usage

```python
from lib.ai_writers.github_blogs import GitHubBlogGenerator

# Initialize with custom settings
generator = GitHubBlogGenerator(
    cache_dir=".custom_cache",
    ttl_hours=48
)

# Generate all content types
content_types = [
    "getting_started",
    "technical_docs",
    "tutorials",
    "comparison",
    "case_studies",
    "contribution",
    "security",
    "performance"
]

# Generate content for multiple repositories
urls = [
    "https://github.com/owner/repo1",
    "https://github.com/owner/repo2"
]

for url in urls:
    content = await generator.generate_content(url, content_types)
    generator.save_content(content, url.split("/")[-1])
```

## Configuration Options

### GitHubBlogGenerator

- `cache_dir` (str): Directory for caching scraped content (default: ".github_cache")
- `ttl_hours` (int): Time-to-live for cached content in hours (default: 24)

### Content Generation

- `gpt_provider` (str): Choice of AI provider ("gemini" or "openai")
- `content_types` (List[str]): Types of content to generate
- `github_url` (str): URL of the GitHub repository

## Output Format

All generated content is saved in Markdown format with the following structure:

```markdown
# [Title]

[Generated content based on content type]

## Metadata
- Title: [SEO-optimized title]
- Description: [Meta description]
- Tags: [Generated tags]
- Categories: [Generated categories]
```

## Best Practices

1. **Rate Limiting**
   - Configure appropriate rate limits based on your GitHub API quota
   - Use caching to minimize API calls
   - Implement proper error handling for rate limit exceeded scenarios

2. **Content Generation**
   - Start with basic content types before generating advanced content
   - Review generated content for accuracy and completeness
   - Customize prompts for specific repository types

3. **Caching**
   - Set appropriate TTL based on repository update frequency
   - Clear cache when repository content changes significantly
   - Monitor cache size and performance

4. **Error Handling**
   - Implement proper error handling for API failures
   - Log errors for debugging
   - Provide fallback mechanisms for failed content generation

## Dependencies

- Python 3.8+
- aiohttp
- beautifulsoup4
- loguru
- pydantic
- requests
- pandas

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Support

For support, please [create an issue](https://github.com/your-repo/issues) or contact the maintainers. 