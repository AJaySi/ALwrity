"""
Enhanced FAQ Generator

This module provides a comprehensive FAQ generation system that can create detailed,
well-researched FAQs from various content sources with customizable options.
"""

import sys
import json
import re
from typing import Dict, List, Optional, Union
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from loguru import logger

from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from lib.ai_web_researcher.google_serp_search import google_search
from lib.ai_web_researcher.tavily_ai_search import do_tavily_ai_search
from lib.ai_web_researcher.metaphor_basic_neural_web_search import metaphor_search_articles

logger.remove()
logger.add(sys.stdout,
        colorize=True,
          format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}")

class TargetAudience(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class FAQStyle(Enum):
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"

class SearchDepth(Enum):
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    EXPERT = "expert"

@dataclass
class FAQConfig:
    """Configuration for FAQ generation."""
    num_faqs: int = 5
    target_audience: TargetAudience = TargetAudience.INTERMEDIATE
    faq_style: FAQStyle = FAQStyle.PROFESSIONAL
    include_emojis: bool = True
    include_code_examples: bool = True
    include_references: bool = True
    search_depth: SearchDepth = SearchDepth.COMPREHENSIVE
    time_range: str = "last_6_months"
    exclude_domains: List[str] = None
    language: str = "English"
    selected_search_queries: List[str] = None

@dataclass
class FAQItem:
    """Individual FAQ item with metadata."""
    question: str
    answer: str
    category: str
    code_example: Optional[str] = None
    references: List[Dict[str, str]] = None
    confidence_score: float = 0.0
    last_updated: str = None

class FAQGenerator:
    """Enhanced FAQ Generator with research capabilities."""
    
    def __init__(self, config: Optional[FAQConfig] = None):
        """Initialize the FAQ generator with optional configuration."""
        self.config = config or FAQConfig()
        self.faqs: List[FAQItem] = []
        self.research_results = {}
        self.search_queries = []
        
    def generate_search_queries(self, content: str) -> List[str]:
        """Generate search queries based on the content."""
        try:
            prompt = f"""Based on the following content, generate 5 specific search queries that would help create comprehensive FAQs.
            Content: {content}
            
            Guidelines for search queries:
            1. Focus on key concepts and terms
            2. Include common questions users might have
            3. Cover technical aspects that need clarification
            4. Include best practices and recommendations
            5. Make queries specific and focused
            
            Please provide exactly 5 search queries, one per line.
            Do not include numbers or bullet points in the queries.
            """
            
            response = llm_text_gen(prompt)
            # Clean up the queries by removing numbers and extra spaces
            queries = []
            for line in response.split('\n'):
                # Remove any leading numbers, dots, or spaces
                cleaned = re.sub(r'^\d+\.\s*', '', line.strip())
                if cleaned:
                    queries.append(cleaned)
            
            self.search_queries = queries[:5]  # Ensure we only get 5 queries
            return self.search_queries
            
        except Exception as err:
            logger.error(f"Failed to generate search queries: {err}")
            return []
    
    def _clean_search_query(self, query: str) -> str:
        """Clean up a search query by removing numbers and extra formatting."""
        # Remove any leading numbers, dots, or spaces
        cleaned = re.sub(r'^\d+\.\s*', '', query.strip())
        # Remove any quotes
        cleaned = cleaned.replace('"', '').replace("'", '')
        # Remove any extra spaces
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def generate_faqs(self, content: str, content_type: str = "general") -> List[FAQItem]:
        """Generate FAQs from the given content with research integration."""
        try:
            if not self.config.selected_search_queries:
                raise ValueError("No search queries selected. Please select queries to proceed.")
            
            # Clean up selected queries
            cleaned_queries = [self._clean_search_query(q) for q in self.config.selected_search_queries]
            self.config.selected_search_queries = cleaned_queries
            
            # Step 1: Research the topic using selected queries
            research_results = self._conduct_research(content)
            
            # Step 2: Generate initial FAQs
            initial_faqs = self._generate_initial_faqs(content, research_results)
            
            # Step 3: Enhance FAQs with research
            enhanced_faqs = self._enhance_faqs_with_research(initial_faqs, research_results)
            
            # Step 4: Add code examples if requested
            if self.config.include_code_examples:
                enhanced_faqs = self._add_code_examples(enhanced_faqs)
            
            # Step 5: Add references if requested
            if self.config.include_references:
                enhanced_faqs = self._add_references(enhanced_faqs, research_results)
            
            self.faqs = enhanced_faqs
            return enhanced_faqs
            
        except Exception as err:
            logger.error(f"Failed to generate FAQs: {err}")
            raise
    
    def _conduct_research(self, content: str) -> Dict:
        """Conduct online research based on the selected search queries."""
        try:
            research_results = {}
            
            for query in self.config.selected_search_queries:
                try:
                    # Clean the query before searching
                    cleaned_query = self._clean_search_query(query)
                    logger.info(f"Researching query: {cleaned_query}")
                    
                    # Select search function based on search depth
                    if self.config.search_depth == SearchDepth.BASIC:
                        results = google_search(cleaned_query)
                    elif self.config.search_depth == SearchDepth.COMPREHENSIVE:
                        results = do_tavily_ai_search(cleaned_query)
                    elif self.config.search_depth == SearchDepth.EXPERT:
                        results = metaphor_search_articles(cleaned_query)
                    else:
                        logger.warning(f"Unknown search depth: {self.config.search_depth}, defaulting to Google search")
                        results = google_search(cleaned_query)
                    
                    research_results[query] = results
                    logger.info(f"Research completed for query: {query}")
                    
                except Exception as err:
                    logger.error(f"Failed to research query '{query}': {err}")
                    continue
            
            return research_results
            
        except Exception as err:
            logger.error(f"Failed to conduct research: {err}")
            return {}
    
    def _generate_initial_faqs(self, content: str, research_results: Dict) -> List[FAQItem]:
        """Generate initial FAQs using LLM."""
        try:
            system_prompt = f"""You are an expert FAQ generator with deep knowledge in content creation and technical writing.
            Your task is to create comprehensive FAQs based on the given content and research.

            Guidelines:
            1. Target Audience: {self.config.target_audience.value}
            2. Style: {self.config.faq_style.value}
            3. Include emojis: {self.config.include_emojis}
            4. Language: {self.config.language}
            5. Number of FAQs: {self.config.num_faqs}

            Create FAQs that are:
            - Clear and concise
            - Well-structured
            - Technically accurate
            - Engaging and informative
            - Based on the provided research
            - Relevant to the target audience
            - Written in the specified style

            Format each FAQ exactly as follows:
            Q: [Your question here]
            A: [Your detailed answer here]
            Category: [Category name]
            Confidence: [Score between 0 and 1]
            ---
            """
            
            prompt = f"""Content to generate FAQs from:
            {content}

            Research Results:
            {json.dumps(research_results, indent=2)}

            Please generate {self.config.num_faqs} FAQs following the guidelines above.
            Each FAQ must be separated by '---' and include all required fields.
            """
            
            response = llm_text_gen(prompt, system_prompt=system_prompt)
            logger.info(f"LLM Response: {response}")
            
            # Parse the response into FAQItem objects
            faqs = []
            current_faq = None
            
            for line in response.split('\n'):
                line = line.strip()
                if not line or line == '---':
                    if current_faq and current_faq.question and current_faq.answer:
                        faqs.append(current_faq)
                        current_faq = None
                    continue
                
                if line.startswith('Q:'):
                    if current_faq and current_faq.question and current_faq.answer:
                        faqs.append(current_faq)
                    current_faq = FAQItem(question=line[2:].strip(), answer="", category="")
                elif line.startswith('A:'):
                    if current_faq:
                        current_faq.answer = line[2:].strip()
                elif line.startswith('Category:'):
                    if current_faq:
                        current_faq.category = line[9:].strip()
                elif line.startswith('Confidence:'):
                    if current_faq:
                        try:
                            current_faq.confidence_score = float(line[11:].strip())
                        except ValueError:
                            current_faq.confidence_score = 0.5
            
            # Add the last FAQ if it exists and is complete
            if current_faq and current_faq.question and current_faq.answer:
                faqs.append(current_faq)
            
            logger.info(f"Generated {len(faqs)} FAQs")
            return faqs
            
        except Exception as err:
            logger.error(f"Failed to generate initial FAQs: {err}")
            raise
    
    def _enhance_faqs_with_research(self, faqs: List[FAQItem], research_results: Dict) -> List[FAQItem]:
        """Enhance FAQs with research findings."""
        try:
            enhanced_faqs = []
            
            for faq in faqs:
                # Find relevant research for this FAQ
                relevant_research = self._find_relevant_research(faq, research_results)
                
                if relevant_research:
                    # Enhance the answer with research findings
                    enhancement_prompt = f"""Enhance the following FAQ answer with the provided research:
                    
                    Question: {faq.question}
                    Current Answer: {faq.answer}
                    
                    Research:
                    {json.dumps(relevant_research, indent=2)}
                    
                    Please enhance the answer while:
                    1. Maintaining the original style and tone
                    2. Adding relevant information from the research
                    3. Ensuring technical accuracy
                    4. Keeping the answer concise and clear
                    """
                    
                    enhanced_answer = llm_text_gen(enhancement_prompt)
                    faq.answer = enhanced_answer
                
                enhanced_faqs.append(faq)
            
            return enhanced_faqs
            
        except Exception as err:
            logger.error(f"Failed to enhance FAQs with research: {err}")
            return faqs
    
    def _add_code_examples(self, faqs: List[FAQItem]) -> List[FAQItem]:
        """Add code examples to FAQs where applicable."""
        try:
            for faq in faqs:
                if self._is_technical_question(faq.question):
                    code_prompt = f"""Generate a code example for the following FAQ:
                    Question: {faq.question}
                    Answer: {faq.answer}
                    
                    Please provide a relevant code example that demonstrates the concept.
                    Include comments and explanations where necessary.
                    """
                    
                    code_example = llm_text_gen(code_prompt)
                    faq.code_example = code_example
            
            return faqs
            
        except Exception as err:
            logger.error(f"Failed to add code examples: {err}")
            return faqs
    
    def _add_references(self, faqs: List[FAQItem], research_results: Dict) -> List[FAQItem]:
        """Add references to FAQs based on research results."""
        try:
            for faq in faqs:
                relevant_research = self._find_relevant_research(faq, research_results)
                if relevant_research:
                    references = []
                    for source, content in relevant_research.items():
                        references.append({
                            "source": source,
                            "content": content
                        })
                    faq.references = references
            
            return faqs
            
        except Exception as err:
            logger.error(f"Failed to add references: {err}")
            return faqs
    
    def _find_relevant_research(self, faq: FAQItem, research_results: Dict) -> Dict:
        """Find research results relevant to a specific FAQ."""
        relevant_research = {}
        for topic, results in research_results.items():
            if any(keyword in faq.question.lower() for keyword in topic.lower().split()):
                relevant_research[topic] = results
        return relevant_research
    
    def _is_technical_question(self, question: str) -> bool:
        """Determine if a question is technical and might benefit from a code example."""
        technical_keywords = ["code", "program", "function", "method", "class", "api", "syntax", "error", "debug"]
        return any(keyword in question.lower() for keyword in technical_keywords)
    
    def to_markdown(self) -> str:
        """Convert FAQs to markdown format."""
        markdown = "# Frequently Asked Questions\n\n"
        
        for faq in self.faqs:
            markdown += f"## {faq.question}\n\n"
            markdown += f"{faq.answer}\n\n"
            
            if faq.code_example:
                markdown += "```\n"
                markdown += f"{faq.code_example}\n"
                markdown += "```\n\n"
            
            if faq.references:
                markdown += "### References\n"
                for ref in faq.references:
                    markdown += f"- {ref['source']}\n"
                markdown += "\n"
        
        return markdown
    
    def to_html(self) -> str:
        """Convert FAQs to HTML format."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Frequently Asked Questions</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .faq { margin-bottom: 30px; }
                .question { font-weight: bold; font-size: 1.2em; color: #2c3e50; }
                .answer { margin: 10px 0; }
                .code-example { background: #f8f9fa; padding: 15px; border-radius: 4px; }
                .references { margin-top: 15px; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <h1>Frequently Asked Questions</h1>
        """
        
        for faq in self.faqs:
            html += f"""
            <div class="faq">
                <div class="question">{faq.question}</div>
                <div class="answer">{faq.answer}</div>
            """
            
            if faq.code_example:
                html += f"""
                <div class="code-example">
                    <pre><code>{faq.code_example}</code></pre>
                </div>
                """
            
            if faq.references:
                html += """
                <div class="references">
                    <h3>References</h3>
                    <ul>
                """
                for ref in faq.references:
                    html += f"""
                        <li>{ref['source']}</li>
                    """
                html += """
                    </ul>
                </div>
                """
            
            html += """
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
