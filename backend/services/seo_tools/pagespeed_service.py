"""
Google PageSpeed Insights Service

AI-enhanced PageSpeed analysis service that provides comprehensive
performance insights with actionable recommendations for optimization.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import os

from ..llm_providers.main_text_generation import llm_text_gen
from middleware.logging_middleware import seo_logger


class PageSpeedService:
    """Service for Google PageSpeed Insights analysis with AI enhancement"""
    
    def __init__(self):
        """Initialize the PageSpeed service"""
        self.service_name = "pagespeed_analyzer"
        self.api_key = os.getenv("GOOGLE_PAGESPEED_API_KEY")
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        logger.info(f"Initialized {self.service_name}")
    
    async def analyze_pagespeed(
        self,
        url: str,
        strategy: str = "DESKTOP",
        locale: str = "en",
        categories: List[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze website performance using Google PageSpeed Insights
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy (DESKTOP/MOBILE)
            locale: Locale for analysis
            categories: Categories to analyze
            
        Returns:
            Dictionary containing performance analysis and AI insights
        """
        try:
            start_time = datetime.utcnow()
            
            if categories is None:
                categories = ["performance", "accessibility", "best-practices", "seo"]
            
            # Validate inputs
            if not url:
                raise ValueError("URL is required")
            
            if strategy not in ["DESKTOP", "MOBILE"]:
                raise ValueError("Strategy must be DESKTOP or MOBILE")
            
            logger.info(f"Analyzing PageSpeed for URL: {url} (Strategy: {strategy})")
            
            # Fetch PageSpeed data
            pagespeed_data = await self._fetch_pagespeed_data(url, strategy, locale, categories)
            
            if not pagespeed_data:
                raise Exception("Failed to fetch PageSpeed data")
            
            # Extract and structure the data
            structured_results = self._structure_pagespeed_results(pagespeed_data)
            
            # Generate AI-enhanced insights
            ai_insights = await self._generate_ai_insights(structured_results, url, strategy, user_id=user_id)
            
            # Calculate optimization priority
            optimization_plan = self._create_optimization_plan(structured_results)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "url": url,
                "strategy": strategy,
                "analysis_date": datetime.utcnow().isoformat(),
                "core_web_vitals": structured_results.get("core_web_vitals", {}),
                "category_scores": structured_results.get("category_scores", {}),
                "metrics": structured_results.get("metrics", {}),
                "opportunities": structured_results.get("opportunities", []),
                "diagnostics": structured_results.get("diagnostics", []),
                "ai_insights": ai_insights,
                "optimization_plan": optimization_plan,
                "raw_data": {
                    "lighthouse_version": pagespeed_data.get("lighthouseResult", {}).get("lighthouseVersion"),
                    "fetch_time": pagespeed_data.get("analysisUTCTimestamp"),
                    "categories_analyzed": categories
                },
                "execution_time": execution_time
            }
            
            # Log the operation
            await seo_logger.log_tool_usage(
                tool_name=self.service_name,
                input_data={
                    "url": url,
                    "strategy": strategy,
                    "locale": locale,
                    "categories": categories
                },
                output_data=result,
                success=True
            )
            
            await seo_logger.log_external_api_call(
                api_name="Google PageSpeed Insights",
                endpoint=self.base_url,
                response_code=200,
                response_time=execution_time,
                request_data={"url": url, "strategy": strategy}
            )
            
            logger.info(f"PageSpeed analysis completed for {url}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing PageSpeed for {url}: {e}")
            
            # Log the error
            await seo_logger.log_tool_usage(
                tool_name=self.service_name,
                input_data={
                    "url": url,
                    "strategy": strategy,
                    "locale": locale,
                    "categories": categories
                },
                output_data={"error": str(e)},
                success=False
            )
            
            raise
    
    async def _fetch_pagespeed_data(
        self,
        url: str,
        strategy: str,
        locale: str,
        categories: List[str]
    ) -> Dict[str, Any]:
        """Fetch data from Google PageSpeed Insights API"""
        
        # Build API URL
        api_url = f"{self.base_url}?url={url}&strategy={strategy}&locale={locale}"
        
        # Add categories
        for category in categories:
            api_url += f"&category={category}"
        
        # Add API key if available
        if self.api_key:
            api_url += f"&key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"PageSpeed API error {response.status}: {error_text}")
                        
                        if response.status == 429:
                            raise Exception("PageSpeed API rate limit exceeded")
                        elif response.status == 400:
                            raise Exception(f"Invalid URL or parameters: {error_text}")
                        else:
                            raise Exception(f"PageSpeed API error: {response.status}")
                        
        except asyncio.TimeoutError:
            raise Exception("PageSpeed API request timed out")
        except Exception as e:
            logger.error(f"Error fetching PageSpeed data: {e}")
            raise
    
    def _structure_pagespeed_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure PageSpeed results into organized format"""
        
        lighthouse_result = data.get("lighthouseResult", {})
        categories = lighthouse_result.get("categories", {})
        audits = lighthouse_result.get("audits", {})
        
        # Extract category scores
        category_scores = {}
        for category_name, category_data in categories.items():
            category_scores[category_name] = {
                "score": round(category_data.get("score", 0) * 100),
                "title": category_data.get("title", ""),
                "description": category_data.get("description", "")
            }
        
        # Extract Core Web Vitals
        core_web_vitals = {}
        cwv_metrics = ["largest-contentful-paint", "first-input-delay", "cumulative-layout-shift"]
        
        for metric in cwv_metrics:
            if metric in audits:
                audit_data = audits[metric]
                core_web_vitals[metric] = {
                    "score": audit_data.get("score"),
                    "displayValue": audit_data.get("displayValue"),
                    "numericValue": audit_data.get("numericValue"),
                    "title": audit_data.get("title"),
                    "description": audit_data.get("description")
                }
        
        # Extract key metrics
        key_metrics = {}
        important_metrics = [
            "first-contentful-paint",
            "speed-index", 
            "largest-contentful-paint",
            "interactive",
            "total-blocking-time",
            "cumulative-layout-shift"
        ]
        
        for metric in important_metrics:
            if metric in audits:
                audit_data = audits[metric]
                key_metrics[metric] = {
                    "score": audit_data.get("score"),
                    "displayValue": audit_data.get("displayValue"),
                    "numericValue": audit_data.get("numericValue"),
                    "title": audit_data.get("title")
                }
        
        # Extract opportunities (performance improvements)
        opportunities = []
        for audit_id, audit_data in audits.items():
            if (audit_data.get("scoreDisplayMode") == "numeric" and 
                audit_data.get("score") is not None and 
                audit_data.get("score") < 1 and
                audit_data.get("details", {}).get("overallSavingsMs", 0) > 0):
                
                opportunities.append({
                    "id": audit_id,
                    "title": audit_data.get("title", ""),
                    "description": audit_data.get("description", ""),
                    "score": audit_data.get("score", 0),
                    "savings_ms": audit_data.get("details", {}).get("overallSavingsMs", 0),
                    "savings_bytes": audit_data.get("details", {}).get("overallSavingsBytes", 0),
                    "displayValue": audit_data.get("displayValue", "")
                })
        
        # Sort opportunities by potential savings
        opportunities.sort(key=lambda x: x["savings_ms"], reverse=True)
        
        # Extract diagnostics
        diagnostics = []
        for audit_id, audit_data in audits.items():
            if (audit_data.get("scoreDisplayMode") == "informative" or
                (audit_data.get("score") is not None and audit_data.get("score") < 1)):
                
                if audit_id not in [op["id"] for op in opportunities]:
                    diagnostics.append({
                        "id": audit_id,
                        "title": audit_data.get("title", ""),
                        "description": audit_data.get("description", ""),
                        "score": audit_data.get("score"),
                        "displayValue": audit_data.get("displayValue", "")
                    })
        
        return {
            "category_scores": category_scores,
            "core_web_vitals": core_web_vitals,
            "metrics": key_metrics,
            "opportunities": opportunities[:10],  # Top 10 opportunities
            "diagnostics": diagnostics[:10]  # Top 10 diagnostics
        }
    
    async def _generate_ai_insights(
        self,
        structured_results: Dict[str, Any],
        url: str,
        strategy: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations"""
        
        try:
            # Prepare data for AI analysis
            performance_score = structured_results.get("category_scores", {}).get("performance", {}).get("score", 0)
            opportunities = structured_results.get("opportunities", [])
            core_web_vitals = structured_results.get("core_web_vitals", {})
            
            # Build AI prompt
            prompt = self._build_ai_analysis_prompt(
                url, strategy, performance_score, opportunities, core_web_vitals
            )
            
            # Generate AI insights
            ai_response = llm_text_gen(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                user_id=user_id
            )
            
            # Parse AI response
            insights = self._parse_ai_insights(ai_response)
            
            # Log AI analysis
            await seo_logger.log_ai_analysis(
                tool_name=self.service_name,
                prompt=prompt,
                response=ai_response,
                model_used="gemini-2.0-flash-001"
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                "summary": "AI analysis unavailable",
                "priority_actions": [],
                "technical_recommendations": [],
                "business_impact": "Analysis could not be completed"
            }
    
    def _build_ai_analysis_prompt(
        self,
        url: str,
        strategy: str,
        performance_score: int,
        opportunities: List[Dict],
        core_web_vitals: Dict
    ) -> str:
        """Build AI prompt for performance analysis"""
        
        opportunities_text = "\n".join([
            f"- {opp['title']}: {opp['displayValue']} (Potential savings: {opp['savings_ms']}ms)"
            for opp in opportunities[:5]
        ])
        
        cwv_text = "\n".join([
            f"- {metric.replace('-', ' ').title()}: {data.get('displayValue', 'N/A')}"
            for metric, data in core_web_vitals.items()
        ])
        
        prompt = f"""
Analyze this website performance data and provide actionable insights for digital marketers and content creators:

Website: {url}
Device: {strategy}
Performance Score: {performance_score}/100

Core Web Vitals:
{cwv_text}

Top Performance Opportunities:
{opportunities_text}

Please provide:
1. Executive Summary (2-3 sentences for non-technical users)
2. Top 3 Priority Actions (specific, actionable steps)
3. Technical Recommendations (for developers)
4. Business Impact Assessment (how performance affects conversions, SEO, user experience)
5. Quick Wins (easy improvements that can be implemented immediately)

Focus on practical advice that content creators and digital marketers can understand and act upon.
"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI analysis"""
        return """You are a web performance expert specializing in translating technical PageSpeed data into actionable business insights. 
        Your audience includes content creators, digital marketers, and solopreneurs who need to understand how website performance impacts their business goals.
        
        Provide clear, actionable recommendations that balance technical accuracy with business practicality.
        Always explain the "why" behind recommendations and their potential impact on user experience, SEO, and conversions.
        """
    
    def _parse_ai_insights(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured insights"""
        
        # Initialize default structure
        insights = {
            "summary": "",
            "priority_actions": [],
            "technical_recommendations": [],
            "business_impact": "",
            "quick_wins": []
        }
        
        try:
            # Split response into sections
            sections = ai_response.split('\n\n')
            
            current_section = None
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Identify section type
                if 'executive summary' in section.lower() or 'summary' in section.lower():
                    insights["summary"] = self._extract_content(section)
                elif 'priority actions' in section.lower() or 'top 3' in section.lower():
                    insights["priority_actions"] = self._extract_list_items(section)
                elif 'technical recommendations' in section.lower():
                    insights["technical_recommendations"] = self._extract_list_items(section)
                elif 'business impact' in section.lower():
                    insights["business_impact"] = self._extract_content(section)
                elif 'quick wins' in section.lower():
                    insights["quick_wins"] = self._extract_list_items(section)
            
            # Fallback parsing if sections not clearly identified
            if not any(insights.values()):
                insights["summary"] = ai_response[:300] + "..." if len(ai_response) > 300 else ai_response
                
        except Exception as e:
            logger.error(f"Error parsing AI insights: {e}")
            insights["summary"] = "AI analysis completed but parsing failed"
        
        return insights
    
    def _extract_content(self, section: str) -> str:
        """Extract content from a section, removing headers"""
        lines = section.split('\n')
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.endswith(':') and not line.startswith('#'):
                content_lines.append(line)
        
        return ' '.join(content_lines)
    
    def _extract_list_items(self, section: str) -> List[str]:
        """Extract list items from a section"""
        items = []
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or 
                        line[0].isdigit() and '.' in line[:3]):
                # Remove bullet points and numbering
                clean_line = line.lstrip('-*0123456789. ').strip()
                if clean_line:
                    items.append(clean_line)
        
        return items[:5]  # Limit to 5 items per section
    
    def _create_optimization_plan(self, structured_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a prioritized optimization plan"""
        
        opportunities = structured_results.get("opportunities", [])
        category_scores = structured_results.get("category_scores", {})
        
        # Calculate priority score for each opportunity
        prioritized_opportunities = []
        for opp in opportunities:
            priority_score = self._calculate_priority_score(opp)
            prioritized_opportunities.append({
                **opp,
                "priority_score": priority_score,
                "difficulty": self._estimate_difficulty(opp["id"]),
                "impact": self._estimate_impact(opp["savings_ms"])
            })
        
        # Sort by priority score
        prioritized_opportunities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Create implementation phases
        phases = {
            "immediate": [],  # High impact, low difficulty
            "short_term": [],  # Medium impact or difficulty
            "long_term": []   # High difficulty but important
        }
        
        for opp in prioritized_opportunities:
            if opp["difficulty"] == "Low" and opp["impact"] in ["High", "Medium"]:
                phases["immediate"].append(opp)
            elif opp["difficulty"] in ["Low", "Medium"]:
                phases["short_term"].append(opp)
            else:
                phases["long_term"].append(opp)
        
        return {
            "overall_assessment": self._generate_overall_assessment(category_scores),
            "prioritized_opportunities": prioritized_opportunities[:10],
            "implementation_phases": phases,
            "estimated_improvement": self._estimate_total_improvement(prioritized_opportunities[:5])
        }
    
    def _calculate_priority_score(self, opportunity: Dict[str, Any]) -> int:
        """Calculate priority score for an opportunity"""
        savings_ms = opportunity.get("savings_ms", 0)
        savings_bytes = opportunity.get("savings_bytes", 0)
        
        # Base score from time savings
        score = min(savings_ms / 100, 50)  # Cap at 50 points
        
        # Add points for byte savings
        score += min(savings_bytes / 10000, 25)  # Cap at 25 points
        
        # Bonus points for specific high-impact optimizations
        high_impact_audits = [
            "unused-javascript",
            "render-blocking-resources", 
            "largest-contentful-paint-element",
            "cumulative-layout-shift"
        ]
        
        if opportunity.get("id") in high_impact_audits:
            score += 25
        
        return min(int(score), 100)
    
    def _estimate_difficulty(self, audit_id: str) -> str:
        """Estimate implementation difficulty"""
        
        easy_fixes = [
            "unused-css-rules",
            "unused-javascript",
            "render-blocking-resources",
            "image-size-responsive"
        ]
        
        medium_fixes = [
            "largest-contentful-paint-element",
            "cumulative-layout-shift",
            "total-blocking-time"
        ]
        
        if audit_id in easy_fixes:
            return "Low"
        elif audit_id in medium_fixes:
            return "Medium"
        else:
            return "High"
    
    def _estimate_impact(self, savings_ms: int) -> str:
        """Estimate performance impact"""
        if savings_ms >= 1000:
            return "High"
        elif savings_ms >= 500:
            return "Medium"
        else:
            return "Low"
    
    def _generate_overall_assessment(self, category_scores: Dict[str, Any]) -> str:
        """Generate overall performance assessment"""
        
        performance_score = category_scores.get("performance", {}).get("score", 0)
        
        if performance_score >= 90:
            return "Excellent performance with minor optimization opportunities"
        elif performance_score >= 70:
            return "Good performance with some areas for improvement"
        elif performance_score >= 50:
            return "Average performance requiring attention to key areas"
        else:
            return "Poor performance requiring immediate optimization efforts"
    
    def _estimate_total_improvement(self, top_opportunities: List[Dict]) -> Dict[str, Any]:
        """Estimate total improvement from top opportunities"""
        
        total_savings_ms = sum(opp.get("savings_ms", 0) for opp in top_opportunities)
        total_savings_mb = sum(opp.get("savings_bytes", 0) for opp in top_opportunities) / (1024 * 1024)
        
        # Estimate score improvement (rough calculation)
        estimated_score_gain = min(total_savings_ms / 200, 30)  # Conservative estimate
        
        return {
            "potential_time_savings": f"{total_savings_ms/1000:.1f} seconds",
            "potential_size_savings": f"{total_savings_mb:.1f} MB",
            "estimated_score_improvement": f"+{estimated_score_gain:.0f} points",
            "confidence": "Medium" if total_savings_ms > 1000 else "Low"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the PageSpeed service"""
        try:
            # Test with a simple URL
            test_url = "https://example.com"
            result = await self.analyze_pagespeed(test_url, "DESKTOP", "en", ["performance"])
            
            return {
                "status": "operational",
                "service": self.service_name,
                "api_key_configured": bool(self.api_key),
                "test_passed": bool(result.get("category_scores")),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "service": self.service_name,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
