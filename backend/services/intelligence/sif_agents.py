"""
SIF Agent Interfaces
Defines the specialized agents for digital marketing and SEO.
Each agent leverages TxtaiIntelligenceService for semantic operations.
"""

import traceback
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from .txtai_service import TxtaiIntelligenceService, TXTAI_AVAILABLE
from services.intelligence.agents.core_agent_framework import BaseALwrityAgent
from services.llm_providers.main_text_generation import llm_text_gen

# Optional txtai imports (align with core agent framework)
try:
    from txtai import Agent, LLM
except ImportError:
    Agent = None
    LLM = None

class SharedLLMWrapper:
    """Wraps the shared ALwrity LLM service to look like a txtai LLM."""
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the shared LLM provider."""
        try:
            # We ignore kwargs like 'max_tokens' as llm_text_gen handles defaults,
            # but we could map them if needed.
            return llm_text_gen(prompt, user_id=self.user_id)
        except Exception as e:
            logger.error(f"SharedLLMWrapper failed to generate text: {e}")
            return f"[ERROR: Shared LLM generation failed for user {self.user_id}]"
        
    def __call__(self, prompt: str, **kwargs) -> str:
        return self.generate(prompt, **kwargs)

class LocalLLMWrapper:
    """
    Lazily loads a local LLM via txtai.
    This prevents blocking server startup with heavy model loads.
    """
    def __init__(self, model_path: str, task: str = "text-generation"):
        self.model_path = model_path
        self.task = task
        self._llm = None
        
    @property
    def llm(self):
        if self._llm is None:
            if LLM is None:
                raise ImportError("txtai.pipeline.LLM is not available")
            logger.info(f"Loading local LLM: {self.model_path} with task: {self.task}")
            # Explicitly set task to avoid 'text2text-generation' default failures
            self._llm = LLM(path=self.model_path, task=self.task)
        return self._llm
        
    def __call__(self, prompt: str, **kwargs) -> str:
        return self.llm(prompt, **kwargs)
        
    def generate(self, prompt: str, **kwargs) -> str:
        return self.llm(prompt, **kwargs)

class SIFBaseAgent(BaseALwrityAgent):
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str, agent_type: str = "sif_agent", model_name: str = "Qwen/Qwen2.5-3B-Instruct", llm: Any = None):
        # Hybrid LLM Strategy:
        # 1. Shared LLM for external/high-quality generation (available to all agents)
        self.shared_llm = SharedLLMWrapper(user_id)
        
        # 2. Local LLM for internal agent work (default for SIF agents)
        if llm is None:
            if TXTAI_AVAILABLE and LLM is not None:
                # Use Lazy Local LLM when txtai LLM is available
                # Hardening: Specify 'text-generation' task to avoid text2text defaults
                llm = LocalLLMWrapper(model_name, task="text-generation")
            else:
                # Fallback to Shared if txtai or LLM is not available
                llm = self.shared_llm
            
        super().__init__(user_id, agent_type, model_name, llm)
        self.intelligence = intelligence_service
        
    def _log_agent_operation(self, operation: str, **kwargs):
        """Standardized logging for agent operations."""
        logger.info(f"[{self.__class__.__name__}] {operation}")
        if kwargs:
            logger.debug(f"[{self.__class__.__name__}] Parameters: {kwargs}")

    def _create_txtai_agent(self):
        """
        SIF agents primarily use the intelligence service directly, but we can expose
        capabilities via a standard agent interface if available.
        """
        if not TXTAI_AVAILABLE or Agent is None:
            logger.debug(f"[{self.__class__.__name__}] txtai Agent not available, using fallback agent")
            return self._create_fallback_agent()

        try:
            return Agent(llm=self.llm, tools=[])
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Failed to create txtai Agent: {e}")
            return self._create_fallback_agent()

class StrategyArchitectAgent(SIFBaseAgent):
    """Agent for discovering content pillars and identifying strategic gaps."""
    
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str):
        super().__init__(intelligence_service, user_id, agent_type="strategy_architect")
    
    async def discover_pillars(self) -> List[Dict[str, Any]]:
        """Identify content pillars through semantic clustering."""
        self._log_agent_operation("Discovering content pillars")
        
        try:
            # Check if intelligence service is initialized
            if not self.intelligence.is_initialized():
                logger.error(f"[{self.__class__.__name__}] Intelligence service not initialized")
                return []
            
            clusters = await self.intelligence.cluster(min_score=0.6)
            
            if not clusters:
                logger.warning(f"[{self.__class__.__name__}] No clusters found")
                return []
            
            # Create pillar objects with metadata
            pillars = []
            for i, cluster_indices in enumerate(clusters):
                pillar = {
                    "pillar_id": f"pillar_{i}",
                    "indices": cluster_indices,
                    "size": len(cluster_indices),
                    "confidence": self._calculate_cluster_confidence(cluster_indices)
                }
                pillars.append(pillar)
                logger.debug(f"[{self.__class__.__name__}] Created pillar {pillar['pillar_id']} with {pillar['size']} items")
            
            logger.info(f"[{self.__class__.__name__}] Discovered {len(pillars)} content pillars")
            return pillars
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to discover pillars: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return []

    async def analyze_content_strategy(self, website_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze content strategy based on website data and semantic insights.
        
        Args:
            website_data: Dictionary containing website analysis data
            
        Returns:
            List of strategic recommendations
        """
        self._log_agent_operation("Analyzing content strategy")
        
        try:
            recommendations = []
            
            # 1. Discover existing pillars
            pillars = await self.discover_pillars()
            
            # 2. Analyze gaps based on pillars (simplified logic for now)
            if not pillars:
                recommendations.append({
                    "type": "strategy_gap",
                    "priority": "high",
                    "title": "Establish Core Content Pillars",
                    "description": "No clear content clusters found. Focus on defining 3-5 core topics to build authority."
                })
            else:
                # Suggest strengthening weak pillars
                for pillar in pillars:
                    if pillar['size'] < 3:
                        recommendations.append({
                            "type": "content_depth",
                            "priority": "medium",
                            "title": f"Strengthen Pillar {pillar['pillar_id']}",
                            "description": "This topic cluster has few articles. Create more content to establish authority.",
                            "pillar_id": pillar['pillar_id']
                        })
            
            # 3. Add generic recommendations based on website data if available
            if website_data:
                if not website_data.get('description'):
                     recommendations.append({
                        "type": "metadata",
                        "priority": "high",
                        "title": "Missing Meta Description",
                        "description": "Website is missing a meta description. Add one to improve SEO CTR."
                    })
            
            logger.info(f"[{self.__class__.__name__}] Generated {len(recommendations)} strategic recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to analyze content strategy: {e}")
            return []
    
    def _calculate_cluster_confidence(self, cluster_indices: List[int]) -> float:
        """Calculate confidence score for a cluster based on its size and coherence."""
        # Simple confidence based on cluster size - larger clusters are more reliable
        return min(1.0, len(cluster_indices) / 10.0)

    async def find_semantic_gaps(self, competitor_indices: List[int]) -> List[Dict[str, Any]]:
        """Compare user content vs competitor content to find missing topics."""
        self._log_agent_operation("Finding semantic content gaps", competitor_count=len(competitor_indices))
        
        try:
            # STUB: Implement cross-index comparison
            # This would involve:
            # 1. Getting user content topics/themes
            # 2. Getting competitor content topics/themes  
            # 3. Finding topics competitors cover but user doesn't
            
            logger.info(f"[{self.__class__.__name__}] Found semantic gaps analysis stub")
            return [
                {"topic": "Topic A", "priority": "high", "reason": "Competitor coverage gap"},
                {"topic": "Topic B", "priority": "medium", "reason": "Emerging trend"}
            ]
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to find semantic gaps: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return []

class ContentGuardianAgent(SIFBaseAgent):
    """Agent for preventing cannibalization and ensuring content originality."""
    
    CANNIBALIZATION_THRESHOLD = 0.85  # Similarity threshold for cannibalization warning
    ORIGINALITY_THRESHOLD = 0.75  # Minimum originality score
    
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str, sif_service: Any = None):
        super().__init__(intelligence_service, user_id, agent_type="content_guardian")
        self.sif_service = sif_service

    async def assess_content_quality(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall content quality based on website data."""
        self._log_agent_operation("Assessing content quality")
        try:
             # Extract sample text or description from website_data
             text_to_analyze = website_data.get('description', '') or website_data.get('title', '')
             if not text_to_analyze:
                 return {"score": 0.5, "reason": "No content to analyze"}
                 
             # Run style check
             style_result = await self.style_enforcer(text_to_analyze)
             
             # Run safety check
             safety_result = await self.safety_filter(text_to_analyze)
             
             # Calculate aggregate score
             base_score = style_result.get('compliance_score', 0.8)
             if safety_result.get('action') == 'flag_for_review':
                 base_score *= 0.5
                 
             return {
                 "score": base_score,
                 "style_analysis": style_result,
                 "safety_analysis": safety_result,
                 "analyzed_text_length": len(text_to_analyze)
             }
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Quality assessment failed: {e}")
            return {"score": 0.0, "error": str(e)}

    async def check_cannibalization(self, new_draft: str) -> Dict[str, Any]:
        """Check if a new draft competes semantically with existing pages."""
        self._log_agent_operation("Checking for semantic cannibalization", draft_length=len(new_draft))
        
        try:
            if not self.intelligence.is_initialized():
                logger.error(f"[{self.__class__.__name__}] Intelligence service not initialized")
                return {"warning": False, "error": "Service not initialized"}
            
            if not new_draft or len(new_draft.strip()) < 50:
                logger.warning(f"[{self.__class__.__name__}] Draft too short for meaningful analysis")
                return {"warning": False, "reason": "Draft too short"}
            
            results = await self.intelligence.search(new_draft, limit=1)
            
            if not results:
                logger.info(f"[{self.__class__.__name__}] No similar content found - draft is unique")
                return {"warning": False, "uniqueness_score": 1.0}
            
            top_result = results[0]
            similarity_score = top_result.get('score', 0.0)
            
            logger.debug(f"[{self.__class__.__name__}] Top similarity score: {similarity_score:.4f}")
            
            if similarity_score > self.CANNIBALIZATION_THRESHOLD:
                warning_data = {
                    "warning": True,
                    "similar_to": top_result.get('id', 'unknown'),
                    "score": similarity_score,
                    "threshold": self.CANNIBALIZATION_THRESHOLD,
                    "recommendation": "Consider revising the draft to target a different angle or merge with existing content"
                }
                logger.warning(f"[{self.__class__.__name__}] Cannibalization detected: {warning_data}")
                return warning_data
            
            logger.info(f"[{self.__class__.__name__}] No cannibalization detected. Draft is sufficiently unique.")
            return {"warning": False, "uniqueness_score": 1.0 - similarity_score}
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to check cannibalization: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return {"warning": False, "error": str(e)}

    async def verify_originality(self, text: str, competitor_index: Any) -> Dict[str, Any]:
        """Verify originality against competitor content index."""
        self._log_agent_operation("Verifying originality against competitors", text_length=len(text))
        
        try:
            if not text or len(text.strip()) < 50:
                logger.warning(f"[{self.__class__.__name__}] Text too short for meaningful originality check")
                return {"originality_score": 0.0, "reason": "Text too short"}
            
            # STUB: Implement cross-index search against competitor content
            # This would search the text against a competitor-specific index
            
            logger.info(f"[{self.__class__.__name__}] Originality verification stub completed")
            return {
                "originality_score": 0.95,  # Placeholder
                "confidence": 0.8,
                "method": "semantic_comparison",
                "notes": "Competitor index integration pending"
            }
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to verify originality: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return {"originality_score": 0.0, "error": str(e)}

    async def style_enforcer(self, text: str, style_guidelines: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Tool: Ensures content adheres to brand voice and style guidelines.
        """
        self._log_agent_operation("Enforcing style guidelines", text_length=len(text))
        
        try:
            if not text:
                return {"compliance_score": 0.0, "issues": ["No text provided"]}

            # 1. Fetch Style Guidelines from SIF if not provided
            if not style_guidelines and self.sif_service:
                try:
                    # Search for website analysis to get brand voice/style
                    # We assume the most relevant 'website_analysis' doc contains the guidelines
                    results = await self.intelligence.search("website analysis brand voice style", limit=1)
                    if results:
                        import json
                        res = results[0]
                        metadata_str = res.get('object')
                        metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else (metadata_str or res)
                        
                        if metadata.get('type') == 'website_analysis':
                            report = metadata.get('full_report', {})
                            style_guidelines = {
                                "tone": report.get('brand_analysis', {}).get('brand_voice', 'neutral'),
                                "style_patterns": report.get('style_patterns', {}),
                                "writing_style": report.get('writing_style', {})
                            }
                            logger.info(f"[{self.__class__.__name__}] Retrieved style guidelines from SIF: {style_guidelines.get('tone')}")
                except Exception as e:
                    logger.warning(f"[{self.__class__.__name__}] Failed to retrieve style guidelines from SIF: {e}")

            issues = []
            score = 1.0
            
            # Basic Heuristic Checks (Placeholder for LLM-based style analysis)
            
            # 1. Tone Check (e.g., formal vs casual)
            # If guidelines specify 'formal', check for contractions
            tone = style_guidelines.get('tone', '').lower() if style_guidelines else ''
            if 'formal' in tone or 'professional' in tone:
                contractions = ["can't", "won't", "don't", "it's"]
                found_contractions = [c for c in contractions if c in text.lower()]
                if found_contractions:
                    issues.append(f"Found contractions in formal text: {', '.join(found_contractions[:3])}...")
                    score -= 0.1
            
            # 2. Length/Sentence Structure (simple metric)
            sentences = text.split('.')
            avg_len = sum(len(s.split()) for s in sentences if s) / max(1, len(sentences))
            if avg_len > 25:
                issues.append("Average sentence length is too high (>25 words). Consider shortening.")
                score -= 0.1
                
            return {
                "compliance_score": max(0.0, score),
                "issues": issues,
                "is_compliant": score > 0.8,
                "guidelines_source": "sif_index" if not style_guidelines and self.sif_service else "provided"
            }
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Style enforcement failed: {e}")
            return {"error": str(e)}

    async def safety_filter(self, text: str) -> Dict[str, Any]:
        """
        Tool: Flags potentially harmful, offensive, or sensitive content.
        """
        self._log_agent_operation("Running safety filter", text_length=len(text))
        
        try:
            # Basic Keyword Blocklist (Placeholder for LLM/Safety Model)
            # In production, this should call a dedicated safety API (e.g., OpenAI Moderation, Llama Guard)
            unsafe_keywords = [
                "hate", "kill", "murder", "attack", "destroy", # Violent
                "scam", "fraud", "steal", # Illegal
                "explicit", "adult" # NSFW
            ]
            
            found_flags = []
            text_lower = text.lower()
            
            for keyword in unsafe_keywords:
                if f" {keyword} " in text_lower: # Simple word boundary check
                    found_flags.append(keyword)
            
            is_safe = len(found_flags) == 0
            
            return {
                "is_safe": is_safe,
                "flags": found_flags,
                "safety_score": 1.0 if is_safe else 0.0,
                "action": "approve" if is_safe else "flag_for_review"
            }
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Safety filter failed: {e}")
            return {"error": str(e)}

class LinkGraphAgent(SIFBaseAgent):
    """
    Agent for internal link suggestions, graph management, and authority analysis.
    Implements the semantic link graph using SIF and GSC/Bing data.
    """
    
    RELEVANCE_THRESHOLD = 0.6  # Minimum relevance score for link suggestions
    MAX_SUGGESTIONS = 10  # Maximum number of link suggestions
    
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str, sif_service: Any = None):
        super().__init__(intelligence_service, user_id, agent_type="link_graph")
        self.sif_service = sif_service
    
    async def suggest_internal_links(self, draft: str) -> List[Dict[str, Any]]:
        """Suggest internal links based on semantic proximity and authority."""
        return await self.link_suggester(draft)

    async def link_suggester(self, draft: str) -> List[Dict[str, Any]]:
        """
        Tool: Suggests internal links.
        Analyzes draft content and finds semantically relevant pages, boosted by authority.
        """
        self._log_agent_operation("Suggesting internal links", draft_length=len(draft))
        
        try:
            if not self.intelligence.is_initialized():
                logger.error(f"[{self.__class__.__name__}] Intelligence service not initialized")
                return []
            
            if not draft or len(draft.strip()) < 50: # Reduced threshold for testing
                logger.warning(f"[{self.__class__.__name__}] Draft too short for meaningful link suggestions")
                return []
            
            # 1. Get Semantic Candidates
            results = await self.intelligence.search(draft, limit=self.MAX_SUGGESTIONS)
            
            if not results:
                logger.info(f"[{self.__class__.__name__}] No relevant internal pages found")
                return []
            
            # 2. Get Authority Data (if available)
            authority_map = {}
            if self.sif_service:
                try:
                    # Fetch dashboard context to get top performing content
                    # Note: This relies on what's available in the SIF index/dashboard summary
                    dashboard_context = await self.sif_service.get_seo_dashboard_context()
                    
                    if "error" not in dashboard_context:
                         # Extract top queries/pages if available in summary
                         # Ideally, we'd have a map of URL -> Authority Score
                         # For now, we'll try to extract what we can
                         data = dashboard_context.get("dashboard_data", {})
                         summary = data.get("summary", {})
                         
                         # Example: Boost if site health is good (general confidence)
                         site_health = data.get("health_score", {}).get("score", 0)
                         
                         # If we had top pages in the summary, we'd use them.
                         # For now, we'll use a placeholder authority map or just the site health
                         pass
                except Exception as e:
                    logger.warning(f"Failed to fetch authority data: {e}")

            suggestions = []
            for result in results:
                relevance_score = result.get('score', 0.0)
                url = result.get('id', 'unknown')
                
                # Apply authority boost (placeholder logic)
                # In a full implementation, we'd look up 'url' in authority_map
                authority_boost = 1.0
                
                final_score = relevance_score * authority_boost
                
                if final_score >= self.RELEVANCE_THRESHOLD:
                    suggestion = {
                        "url": url,
                        "relevance": relevance_score,
                        "final_score": final_score,
                        "confidence": self._calculate_link_confidence(final_score),
                        "reason": f"Semantic similarity: {relevance_score:.3f}"
                    }
                    suggestions.append(suggestion)
                    logger.debug(f"[{self.__class__.__name__}] Added link suggestion: {url} (score: {final_score:.3f})")
            
            # Sort by final score
            suggestions.sort(key=lambda x: x['final_score'], reverse=True)
            
            logger.info(f"[{self.__class__.__name__}] Generated {len(suggestions)} internal link suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to suggest internal links: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return []
    
    async def graph_builder(self) -> Dict[str, Any]:
        """
        Tool: Builds/Visualizes the semantic link graph.
        Returns the structure of the graph (nodes and edges) for visualization or analysis.
        """
        self._log_agent_operation("Building semantic link graph")
        
        try:
            if not self.intelligence.is_initialized():
                return {"error": "Intelligence service not initialized"}
                
            # This is a resource-intensive operation in a real vector DB.
            # Here we simulate the graph structure based on recent content or clusters.
            
            # 1. Get Clusters (Nodes)
            clusters = await self.intelligence.cluster(min_score=0.5)
            
            nodes = []
            edges = []
            
            for i, cluster in enumerate(clusters):
                cluster_id = f"cluster_{i}"
                nodes.append({
                    "id": cluster_id,
                    "type": "topic_cluster",
                    "size": len(cluster)
                })
                
                # Add content items as nodes linked to cluster
                for item_idx in cluster:
                    # We need to retrieve item metadata. 
                    # txtai cluster returns indices. We might need to query by index or ID.
                    # For this implementation, we'll return a simplified view.
                    pass
            
            return {
                "graph_stats": {
                    "total_clusters": len(clusters),
                    "total_nodes": sum(len(c) for c in clusters)
                },
                "structure": "hierarchical", # vs flat
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to build graph: {e}")
            return {"error": str(e)}

    async def authority_analyzer(self, target_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Tool: Analyzes the authority of the site or specific pages using GSC/Bing data.
        """
        self._log_agent_operation("Analyzing authority", target_url=target_url)
        
        if not self.sif_service:
            return {"error": "SIF Service unavailable for authority analysis"}
            
        try:
            # 1. Get Dashboard Context
            context = await self.sif_service.get_seo_dashboard_context()
            
            if "error" in context:
                return context
                
            data = context.get("dashboard_data", {})
            summary = data.get("summary", {})
            health = data.get("health_score", {})
            
            # 2. Extract Authority Metrics
            authority_report = {
                "domain_authority_proxy": {
                    "health_score": health.get("score"),
                    "total_clicks": summary.get("clicks"),
                    "avg_position": summary.get("position")
                },
                "page_authority": "Page-level authority requires granular GSC data (Planned)", # Placeholder
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return authority_report
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Authority analysis failed: {e}")
            return {"error": str(e)}

    def _calculate_link_confidence(self, relevance_score: float) -> float:
        """Calculate confidence score for a link suggestion."""
        # Simple confidence based on relevance score
        return min(1.0, relevance_score * 1.5)

    async def optimize_anchor_text(self, target_url: str, context: str) -> str:
        """Suggest the best anchor text for a given link based on target page context."""
        self._log_agent_operation("Optimizing anchor text", target_url=target_url, context_length=len(context))
        
        try:
            # In a real implementation, we would fetch the target page content via SIF
            # and use an LLM to generate the anchor text.
            
            # Placeholder for LLM call
            # if self.llm: ...
            
            logger.info(f"[{self.__class__.__name__}] Anchor text optimization stub completed")
            return "relevant anchor text"  # Placeholder
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to optimize anchor text: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return "click here"  # Fallback anchor text

class CitationExpert(SIFBaseAgent):
    """
    Agent for fact-checking, citation generation, and evidence verification.
    """
    
    EVIDENCE_THRESHOLD = 0.7  # Minimum relevance score for evidence
    MAX_EVIDENCE = 5  # Maximum number of evidence pieces to return
    
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str):
        super().__init__(intelligence_service, user_id, agent_type="citation_expert")
        
    async def fact_checker(self, claim: str) -> List[Dict[str, Any]]:
        """
        Tool: Verifies facts against trusted research data.
        Returns supporting or contradicting evidence.
        """
        return await self.verify_facts(claim)

    async def citation_finder(self, topic: str) -> List[Dict[str, Any]]:
        """
        Tool: Suggests authoritative citations for a given topic.
        """
        self._log_agent_operation("Finding citations", topic=topic)
        
        try:
            if not self.intelligence.is_initialized():
                return []
            
            # Search for highly relevant content
            results = await self.intelligence.search(topic, limit=self.MAX_EVIDENCE)
            
            citations = []
            for result in results:
                relevance = result.get('score', 0.0)
                if relevance > 0.6:
                    citations.append({
                        "source": result.get('id'),
                        "title": result.get('text', '')[:100] + "...",
                        "relevance": relevance,
                        "citation_text": f"Source: {result.get('id')} (Relevance: {relevance:.2f})"
                    })
            
            return citations
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Citation finder failed: {e}")
            return []

    async def claim_verifier(self, content: str) -> Dict[str, Any]:
        """
        Tool: Detects unsupported statements and hallucinations.
        """
        self._log_agent_operation("Verifying claims in content", content_length=len(content))
        
        # 1. Extract potential claims (heuristic: numbers, 'research shows', etc.)
        # This is a simplified extraction. A real implementation would use NLP/LLM.
        claims = []
        sentences = content.split('.')
        for sent in sentences:
            if any(char.isdigit() for char in sent) or "show" in sent.lower() or "study" in sent.lower():
                if len(sent.strip()) > 20:
                    claims.append(sent.strip())
        
        if not claims:
             return {"status": "no_claims_detected", "verified_claims": []}
             
        verified_results = []
        for claim in claims[:5]: # Limit to top 5 claims for performance
            evidence = await self.verify_facts(claim)
            status = "supported" if evidence else "unsupported"
            verified_results.append({
                "claim": claim,
                "status": status,
                "evidence_count": len(evidence),
                "top_evidence": evidence[0] if evidence else None
            })
            
        return {
            "status": "completed",
            "verified_claims": verified_results,
            "verification_score": len([c for c in verified_results if c['status'] == 'supported']) / len(verified_results)
        }

    async def verify_facts(self, claim: str) -> List[Dict[str, Any]]:
        """Verify a single claim against intelligence data."""
        results = await self.intelligence.search(claim, limit=3)
        
        evidence = []
        for result in results:
            if result.get('score', 0) > self.EVIDENCE_THRESHOLD:
                evidence.append({
                    "text": result.get('text'),
                    "source": result.get('id'),
                    "confidence": result.get('score')
                })
        return evidence
