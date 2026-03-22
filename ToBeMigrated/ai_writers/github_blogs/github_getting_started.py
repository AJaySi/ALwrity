"""
Enhanced GitHub Content Generator

This module provides various content generation capabilities from GitHub repository data,
including getting started guides, technical documentation, tutorials, and more.
"""

import sys
from typing import Dict, List, Optional
from loguru import logger

from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

logger.remove()
logger.add(sys.stdout,
          colorize=True,
          format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}")

def generate_technical_documentation(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate comprehensive technical documentation from repository data."""
    prompt = f"""As an expert technical writer, create detailed technical documentation for the following GitHub repository:

Repository Data:
{repo_data}

Please create a comprehensive technical documentation that includes:
1. Architecture Overview
2. Core Components
3. Technical Specifications
4. Integration Points
5. Performance Considerations
6. Security Features
7. API Documentation (if applicable)
8. Configuration Options
9. Deployment Guidelines
10. Troubleshooting Guide

Format the documentation in markdown with appropriate headers, code blocks, and diagrams.
Include real-world examples and best practices.
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_getting_started_guide(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate a beginner-friendly getting started guide."""
    prompt = f"""As an expert programmer and teacher, create a comprehensive getting started guide for the following GitHub repository:

Repository Data:
{repo_data}

Create a step-by-step guide that includes:
1. Introduction and Overview
2. Prerequisites and Setup
3. Installation Instructions
4. Basic Usage Examples
5. Common Use Cases
6. Best Practices
7. Next Steps and Resources

Make the guide:
- Beginner-friendly with clear explanations
- Include practical examples with code snippets
- Add emojis for better readability
- Include troubleshooting tips
- Provide links to additional resources
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_tutorial_series(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate a series of tutorials for different skill levels."""
    prompt = f"""As an expert educator, create a series of tutorials for the following GitHub repository:

Repository Data:
{repo_data}

Create a structured tutorial series that includes:
1. Beginner Tutorial
   - Basic concepts
   - Simple examples
   - Step-by-step instructions

2. Intermediate Tutorial
   - Advanced features
   - Real-world examples
   - Best practices

3. Advanced Tutorial
   - Complex use cases
   - Performance optimization
   - Integration patterns

Each tutorial should:
- Be self-contained
- Include practical examples
- Have clear learning objectives
- Include exercises and challenges
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_comparison_analysis(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate a comparison analysis with similar tools/frameworks."""
    prompt = f"""As a technical analyst, create a comprehensive comparison analysis for the following GitHub repository:

Repository Data:
{repo_data}

Create a detailed comparison that includes:
1. Feature Comparison
2. Performance Analysis
3. Use Case Suitability
4. Community and Support
5. Learning Curve
6. Integration Capabilities
7. Future Prospects

Include:
- Pros and Cons
- Real-world use cases
- Industry adoption
- Community feedback
- Future roadmap
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_case_studies(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate real-world case studies and success stories."""
    prompt = f"""As a technical writer, create compelling case studies for the following GitHub repository:

Repository Data:
{repo_data}

Create detailed case studies that include:
1. Problem Statement
2. Solution Implementation
3. Technical Challenges
4. Results and Benefits
5. Lessons Learned
6. Future Improvements

Make the case studies:
- Based on real-world scenarios
- Include technical details
- Show measurable results
- Provide actionable insights
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_contribution_guide(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate a comprehensive contribution guide."""
    prompt = f"""As an open-source maintainer, create a detailed contribution guide for the following GitHub repository:

Repository Data:
{repo_data}

Create a contribution guide that includes:
1. Development Setup
2. Code Style Guidelines
3. Testing Requirements
4. Documentation Standards
5. Pull Request Process
6. Review Guidelines
7. Community Guidelines

Make the guide:
- Clear and concise
- Include examples
- Cover all contribution types
- Provide templates
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_security_guide(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate a security best practices guide."""
    prompt = f"""As a security expert, create a comprehensive security guide for the following GitHub repository:

Repository Data:
{repo_data}

Create a security guide that includes:
1. Security Architecture
2. Authentication & Authorization
3. Data Protection
4. Secure Configuration
5. Vulnerability Management
6. Incident Response
7. Compliance Requirements

Make the guide:
- Practical and actionable
- Include security checklists
- Provide code examples
- Cover common vulnerabilities
"""
    return _get_llm_response(prompt, gpt_provider)

def generate_performance_guide(repo_data: Dict, gpt_provider: str = "gemini") -> str:
    """Generate a performance optimization guide."""
    prompt = f"""As a performance optimization expert, create a detailed performance guide for the following GitHub repository:

Repository Data:
{repo_data}

Create a performance guide that includes:
1. Performance Metrics
2. Optimization Techniques
3. Benchmarking Guidelines
4. Resource Management
5. Scaling Strategies
6. Monitoring Setup
7. Troubleshooting

Make the guide:
- Data-driven
- Include benchmarks
- Provide optimization tips
- Cover different scales
"""
    return _get_llm_response(prompt, gpt_provider)

def _get_llm_response(prompt: str, gpt_provider: str) -> str:
    """Get response from the specified LLM provider."""
    system_prompt = """You are an expert technical writer and GitHub repository analyst with deep expertise in software development, documentation, and technical communication.

  Your role is to create high-quality, accurate, and engaging content based on GitHub repository data. You should:

  1. **Technical Accuracy**
     - Ensure all technical information is precise and up-to-date
     - Verify code examples and configurations
     - Cross-reference documentation and source code
     - Maintain consistency with repository standards

  2. **Content Structure**
     - Use clear hierarchical organization
     - Include appropriate code blocks and examples
     - Add relevant diagrams and visual aids
     - Break complex topics into digestible sections

  3. **Writing Style**
     - Maintain a professional yet approachable tone
     - Use active voice and clear language
     - Include practical examples and use cases
     - Add relevant emojis for better readability

  4. **Best Practices**
     - Follow industry-standard documentation practices
     - Include troubleshooting sections
     - Add performance considerations
     - Address security implications
"""
    try:
        
        llm_response = llm_text_gen(prompt, system_prompt=system_prompt)
    except Exception as err:
        logger.error(f"Failed to get response from {gpt_provider}: {err}")
        raise
