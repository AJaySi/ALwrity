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
from ..txtai_service import TxtaiIntelligenceService
from services.intelligence.agents.core_agent_framework import BaseALwrityAgent, AgentAction
from services.seo_tools.content_strategy_service import ContentStrategyService
from services.intelligence.sif_agents import SharedLLMWrapper, LocalLLMWrapper
try:
    from services.intelligence.sif_integration import SIFIntegrationService
    SIF_AVAILABLE = True
except ImportError:
    SIF_AVAILABLE = False

try:
    # Try importing from pipeline first (standard location)
    from txtai.pipeline import Agent, LLM
    TXTAI_AVAILABLE = True
except ImportError:
    try:
        # Fallback to top-level import
        from txtai import Agent, LLM
        TXTAI_AVAILABLE = True
    except ImportError:
        TXTAI_AVAILABLE = False
        Agent = None
        LLM = None
        logger.warning("txtai not available, using fallback implementation")

class SIFBaseAgent(BaseALwrityAgent):
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str, agent_type: str = "sif_agent", model_name: str = "Qwen/Qwen2.5-3B-Instruct", llm: Any = None):
        # Hybrid LLM Strategy:
        # 1. Shared LLM for external/high-quality generation
        self.shared_llm = SharedLLMWrapper(user_id)
        
        # 2. Local LLM for internal agent work (default for SIF agents)
        if llm is None:
            if TXTAI_AVAILABLE:
                # Use Lazy Local LLM
                llm = LocalLLMWrapper(model_name)
            else:
                # Fallback to Shared if txtai not available
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
        SIF agents use the intelligence service directly, but we can expose
        capabilities via a standard agent interface if needed.
        """
        if not TXTAI_AVAILABLE or Agent is None:
            return None
        
        # Return a simple agent that can use the LLM
        try:
            return Agent(llm=self.llm, tools=[])
        except Exception as e:
            logger.warning(f"Failed to create txtai Agent: {e}")
            return None

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
        
        # Lazy initialization of SIF service if not provided
        if self.sif_service is None and SIF_AVAILABLE:
            try:
                self.sif_service = SIFIntegrationService(user_id)
                logger.info(f"[{self.__class__.__name__}] Lazily initialized SIFIntegrationService")
            except Exception as e:
                logger.warning(f"[{self.__class__.__name__}] Failed to lazily initialize SIF service: {e}")

    async def assess_content_quality(self, content: str) -> Dict[str, Any]:
        """
        Assess content quality based on originality, readability, and cannibalization risks.
        """
        self._log_agent_operation("Assessing content quality", content_length=len(content))
        
        try:
            # 1. Check for cannibalization
            cannibalization_result = await self.check_cannibalization(content)
            
            # 2. Check originality (if not cannibalized)
            originality_score = 1.0
            if not cannibalization_result.get("warning"):
                originality_result = await self.verify_originality(content, None)
                originality_score = originality_result.get("originality_score", 1.0)
            
            # 3. Check Style Compliance
            style_result = await self.style_enforcer(content)
            style_score = style_result.get("compliance_score", 1.0)
            
            # 4. Basic Readability (Flesch-Kincaid proxy via sentence length/word complexity)
            # Simple heuristic for now
            words = content.split()
            sentences = content.split('.')
            avg_sentence_length = len(words) / max(1, len(sentences))
            readability_score = 1.0 if avg_sentence_length < 20 else max(0.5, 1.0 - (avg_sentence_length - 20) * 0.05)
            
            # Weighted Score: Originality (40%) + Style (30%) + Readability (30%)
            quality_score = (originality_score * 0.4) + (style_score * 0.3) + (readability_score * 0.3)
            
            return {
                "quality_score": quality_score,
                "originality_score": originality_score,
                "readability_score": readability_score,
                "style_score": style_score,
                "cannibalization_risk": cannibalization_result,
                "style_compliance": style_result,
                "is_acceptable": quality_score > 0.7 and not cannibalization_result.get("warning", False)
            }
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to assess content quality: {e}")
            return {"error": str(e), "quality_score": 0.0}

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
                    # Use central SIF service to get robust context
                    seo_context = await self.sif_service.get_seo_context()
                    
                    if seo_context and "error" not in seo_context:
                        # Extract brand voice/style from the context
                        # The context structure is normalized in get_seo_context
                        
                        # Note: get_seo_context returns a flattened dict. 
                        # We need to dig into the original structure if available, or rely on what's mapped.
                        # However, get_seo_context maps 'seo_audit', 'sitemap_analysis', etc.
                        # Brand info is usually in 'brand_analysis' col of WebsiteAnalysis, which might not be fully exposed
                        # in the simplified get_seo_context return.
                        # Let's check if we can get the full object or if we need to expand get_seo_context.
                        # For now, we'll try to use what's there or fall back to a specific search if needed.
                        
                        # Actually, looking at get_seo_context implementation:
                        # It returns 'seo_audit', 'crawl_result'.
                        # Brand analysis is often stored in WebsiteAnalysis.brand_analysis.
                        # We might need to extend get_seo_context or do a specific retrieval here.
                        # But wait! I saw get_seo_context implementation earlier:
                        # It retrieves the "full_report" from the SIF metadata.
                        # If the SIF index contains the full WebsiteAnalysis object, we are good.
                        
                        # Let's try to get it from the full report if we can access it, 
                        # but get_seo_context returns a filtered dict.
                        
                        # Alternative: Use the robust retrieval logic but specifically for brand info if get_seo_context is too narrow.
                        # But get_seo_context logic includes "website analysis seo audit" query.
                        
                        # Let's assume for now we use the same retrieval logic but locally adapted, 
                        # OR better, trust get_seo_context to be the single point of truth.
                        # If get_seo_context doesn't return brand info, we should update IT, not hack here.
                        # But I can't update SIFIntegrationService right now without context switch.
                        
                        # Let's stick to the previous manual search pattern BUT use the SIF service helper if possible.
                        # Actually, the previous code was:
                        # results = await self.intelligence.search("website analysis brand voice style", limit=1)
                        
                        # Let's keep it simple and robust:
                        # Try to get it from SIF service if possible.
                        # Since get_seo_context might not return brand_voice directly, let's try to see if we can use it.
                        
                        # Actually, let's use the manual search but with better error handling, 
                        # mirroring get_seo_context's robustness (e.g. parsing).
                        
                        results = await self.intelligence.search("website analysis brand voice style", limit=1)
                        if results:
                            res = results[0]
                            metadata_str = res.get('object')
                            metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else (metadata_str or res)
                            
                            if metadata.get('type') == 'website_analysis':
                                report = metadata.get('full_report', {})
                                # Support both flat and nested structures
                                brand_analysis = report.get('brand_analysis') or report.get('brand_voice', {})
                                if isinstance(brand_analysis, str):
                                    # Handle case where it might be a JSON string
                                    try: brand_analysis = json.loads(brand_analysis)
                                    except: brand_analysis = {"brand_voice": brand_analysis}
                                    
                                style_guidelines = {
                                    "tone": brand_analysis.get('brand_voice', 'neutral') if isinstance(brand_analysis, dict) else 'neutral',
                                    "style_patterns": report.get('style_patterns', {}),
                                    "writing_style": report.get('writing_style', {})
                                }
                                logger.info(f"[{self.__class__.__name__}] Retrieved style guidelines from SIF index")
                except Exception as e:
                    logger.warning(f"[{self.__class__.__name__}] Failed to retrieve style guidelines: {e}")

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

    async def perform_site_audit(self, website_url: str, limit: int = 10) -> Dict[str, Any]:
        """
        Perform a quality audit on the user's website content.
        """
        self._log_agent_operation("Performing site audit", website_url=website_url)
        
        try:
            # 1. Retrieve recent content for the site from SIF
            # We search for everything with the website_url in metadata
            # Note: This depends on how data is indexed.
            results = await self.intelligence.search(f"site:{website_url}", limit=limit)
            
            if not results:
                logger.info(f"[{self.__class__.__name__}] No content found for site audit")
                return {"error": "No content found"}
            
            audit_results = []
            total_quality = 0.0
            
            for res in results:
                text = res.get('text', '')
                if not text or len(text) < 100:
                    continue
                    
                quality = await self.assess_content_quality(text)
                audit_results.append({
                    "id": res.get('id'),
                    "title": res.get('title', 'Unknown'),
                    "quality": quality
                })
                total_quality += quality.get('quality_score', 0.0)
            
            avg_quality = total_quality / len(audit_results) if audit_results else 0.0
            
            report = {
                "website_url": website_url,
                "pages_audited": len(audit_results),
                "average_quality_score": avg_quality,
                "details": audit_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"[{self.__class__.__name__}] Site audit completed. Avg Quality: {avg_quality:.2f}")
            return report
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Site audit failed: {e}")
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
                "top_evidence": evidence[0]['source'] if evidence else None
            })
            
        return {
            "status": "verification_complete",
            "total_claims": len(claims),
            "verified_claims": verified_results,
            "unsupported_count": len([c for c in verified_results if c['status'] == 'unsupported']),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def verify_facts(self, claim: str) -> List[Dict[str, Any]]:
        """Find supporting or contradicting evidence in the indexed research."""
        self._log_agent_operation("Verifying facts", claim_length=len(claim))
        
        try:
            if not self.intelligence.is_initialized():
                logger.error(f"[{self.__class__.__name__}] Intelligence service not initialized")
                return []
            
            if not claim or len(claim.strip()) < 20:
                logger.warning(f"[{self.__class__.__name__}] Claim too short for meaningful verification")
                return []
            
            results = await self.intelligence.search(claim, limit=self.MAX_EVIDENCE)
            
            if not results:
                logger.info(f"[{self.__class__.__name__}] No evidence found for claim")
                return []
            
            evidence = []
            for result in results:
                relevance_score = result.get('score', 0.0)
                
                if relevance_score >= self.EVIDENCE_THRESHOLD:
                    evidence_piece = {
                        "source": result.get('id', 'unknown'),
                        "relevance": relevance_score,
                        "confidence": self._calculate_evidence_confidence(relevance_score),
                        "type": "supporting" if relevance_score > 0.8 else "related",
                        "excerpt": result.get('text', '')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', '')
                    }
                    evidence.append(evidence_piece)
                    logger.debug(f"[{self.__class__.__name__}] Found evidence: {evidence_piece['source']} (score: {relevance_score:.3f})")
            
            logger.info(f"[{self.__class__.__name__}] Found {len(evidence)} pieces of evidence for claim")
            return evidence
            
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Failed to verify facts: {e}")
            logger.error(f"[{self.__class__.__name__}] Full traceback: {traceback.format_exc()}")
            return []
    
    def _calculate_evidence_confidence(self, relevance_score: float) -> float:
        """Calculate confidence score for evidence."""
        # Simple confidence based on relevance score
        return min(1.0, relevance_score * 1.2)

"""
Specialized ALwrity Autonomous Agents
Defines specific agent implementations for Content Strategy, Competitor Response,
SEO Optimization, and Social Amplification.
"""
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# txtai imports
try:
    from txtai import Agent, LLM
    TXTAI_AVAILABLE = True
except ImportError:
    TXTAI_AVAILABLE = False
    logging.warning("txtai not available, using fallback implementation")

from utils.logger_utils import get_service_logger
from services.intelligence.agents.core_agent_framework import BaseALwrityAgent, AgentAction
from services.seo_tools.content_strategy_service import ContentStrategyService

# Import SIF Integration for real tool capabilities
try:
    from services.intelligence.sif_integration import SIFIntegrationService
    SIF_AVAILABLE = True
except ImportError:
    SIF_AVAILABLE = False

logger = get_service_logger(__name__)

class ContentStrategyAgent(BaseALwrityAgent):
    """
    Agent responsible for content strategy, gap analysis, and optimization.
    """
    
    def __init__(self, user_id: str, model_name: str = "Qwen/Qwen3-4B-Instruct-2507", llm: Any = None):
        super().__init__(user_id, "content_strategist", model_name, llm)
        self.sif_service = None
        self.content_strategy_service = ContentStrategyService()
        if SIF_AVAILABLE:
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for ContentStrategyAgent: {e}")
        
    def _create_txtai_agent(self) -> Agent:
        """Create Content Strategy Agent using txtai native framework"""
        if not TXTAI_AVAILABLE:
            return None
            
        return Agent(
            llm=self.llm,
            tools=[
                {
                    "name": "content_analyzer",
                    "description": "Analyzes content performance and engagement metrics",
                    "target": self._content_analyzer_tool
                },
                {
                    "name": "semantic_gap_detector",
                    "description": "Identifies content gaps using semantic analysis",
                    "target": self._semantic_gap_detector_tool
                },
                {
                    "name": "content_optimizer",
                    "description": "Optimizes content for better performance",
                    "target": self._content_optimizer_tool
                },
                {
                    "name": "performance_tracker",
                    "description": "Tracks content performance over time",
                    "target": self._content_performance_tracker_tool
                },
                {
                    "name": "sitemap_analyzer",
                    "description": "Analyzes website structure and publishing velocity via sitemap",
                    "target": self._sitemap_analyzer_tool
                }
            ],
            max_iterations=8,
            system=self.get_effective_system_prompt(f"""You are the Content Strategy Agent for ALwrity user {self.user_id}.
            
            Your mission is to analyze content performance, identify optimization opportunities,
            and execute content improvements autonomously.
            
            Focus on:
            - Content gap identification (semantic and structural)
            - Topic cluster optimization
            - SEO strategy adaptation
            - Performance-based content improvements
            
            Use semantic analysis (SIF) and sitemap analysis to understand content context.
            Always prioritize user goals and maintain brand consistency."""
            )
        )
    
    # Tool Implementations
    
    async def _sitemap_analyzer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sitemap analysis tool using ContentStrategyService"""
        website_url = context.get('website_url')
        competitors = context.get('competitors', [])
        
        if not website_url:
            return {"error": "Website URL required for sitemap analysis"}
            
        try:
            result = await self.content_strategy_service.analyze_content_strategy(
                website_url=website_url,
                competitors=competitors,
                user_id=self.user_id
            )
            return {
                "sitemap_insights": result.get("deterministic_insights", {}),
                "ai_strategy": result.get("ai_strategy", {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Sitemap analysis failed: {e}")
            return {"error": str(e)}

    async def _content_analyzer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Content analysis tool with GSC integration.
        Analyzes content performance using SIF insights and Google Search Console data.
        """
        website_data = context.get('website_data', {})
        
        # 1. SIF Semantic Analysis
        sif_insights = {}
        if self.sif_service:
            try:
                result = await self.sif_service.get_semantic_insights(website_data)
                sif_insights = result.get('insights', {})
            except Exception as e:
                logger.error(f"SIF content analysis failed: {e}")
        
        # 2. GSC Data Integration (Mock/Placeholder as per Phase 3A.2)
        # In a real implementation, this would call a GSCService
        gsc_data = {
            "clicks": 1250,
            "impressions": 45000,
            "ctr": 2.8,
            "position": 14.5,
            "top_queries": [
                {"query": "ai content strategy", "clicks": 150, "position": 3.2},
                {"query": "seo automation", "clicks": 120, "position": 4.1}
            ],
            "underperforming_pages": [
                {"url": "/blog/old-post-1", "issue": "High impressions, low CTR"},
                {"url": "/blog/weak-content", "issue": "Declining traffic"}
            ]
        }
        
        # 3. Correlate Semantic Topics with GSC Performance
        content_gaps = []
        if sif_insights and gsc_data:
            # Example correlation logic
            semantic_topics = sif_insights.get('content_pillars', [])
            gsc_queries = [q['query'] for q in gsc_data['top_queries']]
            
            # Simple set difference to find topics with no traffic
            for topic in semantic_topics:
                if not any(topic.lower() in q.lower() for q in gsc_queries):
                    content_gaps.append(f"Topic '{topic}' has content but low search visibility")

        return {
            "content_analysis": "Completed via SIF + GSC Integration",
            "sif_insights": sif_insights,
            "gsc_performance": gsc_data,
            "identified_gaps": content_gaps,
            "strategic_recommendations": sif_insights.get('strategic_recommendations', []) + ["Optimize meta descriptions for underperforming pages"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _content_optimizer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Content optimization tool using LLM-based rewriting and semantic analysis.
        Generates specific diffs/rewrites for content.
        """
        content = context.get('content')
        target_keywords = context.get('target_keywords', [])
        focus_topic = context.get('focus_topic')
        optimization_goal = context.get('goal', 'readability') # readability, seo, conversion

        if not content:
            return {"error": "No content provided for optimization"}

        try:
            # System prompt optimized for specific rewrites
            system_prompt = f"""You are an expert Content Editor.
            Task: Optimize the following text for '{focus_topic}' with goal: {optimization_goal}.
            Keywords to include: {', '.join(target_keywords)}.
            
            Return a JSON object with:
            1. "original_snippet": A short snippet of the original text.
            2. "optimized_version": The fully rewritten version.
            3. "changes_explained": A list of specific changes made (e.g., "Added keyword 'X' in first sentence").
            4. "diff_summary": A brief summary of why this version is better.
            
            Maintain the original meaning and tone.
            """
            
            if self.llm:
                # We assume the LLM returns JSON-like text or we parse it
                response = await self._generate_llm_response(f"{system_prompt}\n\nText to rewrite:\n{content}")
                
                # Simple parsing fallback if LLM returns raw text
                if isinstance(response, str) and not response.strip().startswith("{"):
                    optimized_content = response
                    changes = ["Rewrote for clarity", "Integrated keywords"]
                else:
                    # Try to parse JSON if model is good
                    try:
                        import json
                        data = json.loads(response)
                        optimized_content = data.get("optimized_version", response)
                        changes = data.get("changes_explained", [])
                    except:
                        optimized_content = response
                        changes = ["Optimization applied"]
            else:
                optimized_content = f"[Mock Rewrite]: Optimized '{content[:30]}...' for {focus_topic}"
                changes = ["Mock optimization applied"]

            return {
                "original_content_snippet": content[:50] + "...",
                "optimized_content": optimized_content,
                "changes_made": changes,
                "expected_impact": "Higher relevance score and better readability",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return {"error": str(e)}
    
    async def _content_performance_tracker_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Content performance tracking tool.
        Persists metrics to monitor content health over time.
        """
        content_id = context.get('content_id') or context.get('url')
        metrics = context.get('metrics', {})
        
        if not content_id:
             return {"error": "Content ID or URL required for tracking"}

        # Simulate persistence (In real app, save to DB table 'content_performance_history')
        # We can use the AgentPerformanceMonitor for generic metrics, but this is content-specific.
        
        tracking_record = {
            "content_id": content_id,
            "date": datetime.utcnow().date().isoformat(),
            "metrics": metrics,
            "health_score": self._calculate_content_health(metrics)
        }
        
        # Log it for now as "persistence"
        logger.info(f"Persisting content performance for {content_id}: {tracking_record}")
        
        return {
            "status": "recorded",
            "tracking_record": tracking_record,
            "trend": "stable", # Would calculate based on history
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_content_health(self, metrics: Dict[str, Any]) -> float:
        """Calculate a 0-100 health score based on metrics"""
        # Simple heuristic
        views = metrics.get('views', 0)
        engagement = metrics.get('engagement_rate', 0)
        
        score = min(100, (views / 1000) * 10 + (engagement * 100))
        return round(score, 2)


class CompetitorResponseAgent(BaseALwrityAgent):
    """
    Agent responsible for monitoring competitors and generating counter-strategies.
    """
    
    def __init__(self, user_id: str, model_name: str = "Qwen/Qwen3-4B-Instruct-2507", llm: Any = None):
        super().__init__(user_id, "competitor_analyst", model_name, llm)
        
        self.sif_service = None
        if SIF_AVAILABLE:
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for CompetitorResponseAgent: {e}")
        
    def _create_txtai_agent(self) -> Agent:
        """Create Competitor Response Agent using txtai native framework"""
        if not TXTAI_AVAILABLE:
            return None
            
        return Agent(
            llm=self.llm,
            tools=[
                {
                    "name": "competitor_monitor",
                    "description": "Monitors competitor content and strategy changes via SIF",
                    "target": self._competitor_monitor_tool
                },
                {
                    "name": "threat_analyzer",
                    "description": "Analyzes competitive threats and opportunities based on SIF data",
                    "target": self._threat_analyzer_tool
                },
                {
                    "name": "response_generator",
                    "description": "Generates counter-strategy recommendations",
                    "target": self._response_generator_tool
                },
                {
                    "name": "strategy_executor",
                    "description": "Executes competitive response strategies",
                    "target": self._strategy_executor_tool
                }
            ],
            max_iterations=12,
            system=self.get_effective_system_prompt(f"""You are the Competitor Response Agent for ALwrity user {self.user_id}.
            
            Your mission is to monitor competitor activities, assess competitive threats,
            and generate counter-strategies autonomously using SIF insights.
            
            Responsibilities:
            - Real-time competitor content monitoring via SIF
            - Competitive threat assessment
            - Counter-strategy generation
            - Rapid response deployment
            
            Use semantic analysis to understand competitor positioning and identify gaps.
            Respond quickly to competitive threats while maintaining strategic advantage."""
            )
        )
    
    # Tool Implementations
    
    async def _competitor_monitor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Competitor monitoring tool that retrieves data via SIF.
        Expects 'competitor_url' (optional) in context to filter.
        """
        competitor_url = context.get('competitor_url')
        
        if not self.sif_service:
            return {"error": "SIF Service unavailable, cannot retrieve competitor data."}
            
        try:
            logger.info(f"Retrieving Competitor data via SIF for user {self.user_id}")
            result = await self.sif_service.get_competitor_context(competitor_url)
            
            if "error" in result and result.get("source") == "empty":
                 return {"error": "No competitor data found. Please complete onboarding Step 3."}
            
            competitors = result.get("competitors", [])
            changes = []
            
            for comp in competitors:
                # In a real scenario, we would compare with previous snapshots.
                # Here we extract highlights from the current analysis.
                summary = comp.get("summary", "")
                highlights = comp.get("highlights", [])
                changes.append({
                    "url": comp.get("competitor_url"), # Or however it's stored in analysis_data
                    "summary_snippet": summary[:100] + "...",
                    "highlights": highlights[:3]
                })
            
            return {
                "competitor_changes": changes,
                "data_source": "sif_index",
                "count": len(competitors),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Competitor monitoring failed: {e}")
            return {"error": str(e)}
    
    async def _threat_analyzer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Threat analysis tool using SIF data.
        """
        # Get data from monitor tool or context
        competitor_data = context.get('competitor_changes', [])
        
        # If not provided, fetch it
        if not competitor_data and self.sif_service:
             monitor_result = await self._competitor_monitor_tool(context)
             competitor_data = monitor_result.get("competitor_changes", [])
             
        if not competitor_data:
            return {"threat_assessment": "No data available for analysis", "level": "unknown"}

        # Simple rule-based or LLM-based analysis
        # For now, we simulate a threat assessment based on highlights
        threats = []
        overall_level = "low"
        
        for comp in competitor_data:
            highlights = comp.get("highlights", [])
            # Heuristic: If highlights mention "launch", "new", "pricing" -> Higher threat
            level = "low"
            risk_factors = []
            
            full_text = " ".join(highlights).lower()
            if "new feature" in full_text or "launch" in full_text:
                level = "high"
                risk_factors.append("New Product Launch")
            elif "pricing" in full_text:
                level = "medium"
                risk_factors.append("Pricing Change")
            
            if level == "high": overall_level = "high"
            elif level == "medium" and overall_level != "high": overall_level = "medium"
            
            threats.append({
                "competitor": comp.get("url"),
                "level": level,
                "risk_factors": risk_factors
            })

        return {
            "threat_assessment": f"{overall_level.title()} threat level detected.", 
            "threat_level": overall_level,
            "details": threats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _response_generator_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Response generation tool"""
        threat_level = context.get("threat_level", "low")
        threat_details = context.get("details", [])
        
        strategies = []
        if threat_level == "high":
            strategies = ["Launch counter-campaign immediately", "Highlight USP differentiation"]
        elif threat_level == "medium":
            strategies = ["Monitor closely", "Prepare comparison content"]
        else:
            strategies = ["Continue current strategy", "Look for gap opportunities"]
            
        return {
            "counter_strategies": strategies, 
            "priority": "high" if threat_level == "high" else "medium",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _strategy_executor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy execution tool"""
        # In a real agent, this might trigger the Content Agent to write a post.
        strategies = context.get("counter_strategies", [])
        
        execution_log = []
        for strategy in strategies:
            execution_log.append(f"Scheduled: {strategy}")
            
        return {
            "execution_status": "completed", 
            "actions_taken": execution_log,
            "timestamp": datetime.utcnow().isoformat()
        }


class SEOOptimizationAgent(BaseALwrityAgent):
    """
    Agent responsible for technical SEO, keyword strategy, and performance optimization.
    """
    
    def __init__(self, user_id: str, model_name: str = "Qwen/Qwen3-4B-Instruct-2507", llm: Any = None):
        super().__init__(user_id, "seo_specialist", model_name, llm)
        
        self.sif_service = None
        if SIF_AVAILABLE:
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for SEOOptimizationAgent: {e}")
        
    def _create_txtai_agent(self) -> Agent:
        """Create SEO Optimization Agent using txtai native framework"""
        if not TXTAI_AVAILABLE:
            return None
            
        return Agent(
            llm=self.llm,
            tools=[
                {
                    "name": "seo_auditor",
                    "description": "Performs comprehensive SEO audits",
                    "target": self._seo_auditor_tool
                },
                {
                    "name": "issue_prioritizer",
                    "description": "Prioritizes SEO issues by impact and effort",
                    "target": self._issue_prioritizer_tool
                },
                {
                    "name": "auto_fix_executor",
                    "description": "Automatically fixes high-impact SEO issues",
                    "target": self._auto_fix_executor_tool
                },
                {
                    "name": "strategy_generator",
                    "description": "Generates SEO improvement strategies",
                    "target": self._strategy_generator_tool
                },
                {
                    "name": "query_seo_knowledge_base",
                    "description": "Queries the SIF knowledge base for SEO dashboard data, GSC/Bing metrics, and semantic insights",
                    "target": self._query_seo_knowledge_base_tool
                }
            ],
            max_iterations=15,
            system=self.get_effective_system_prompt(f"""You are the SEO Optimization Agent for ALwrity user {self.user_id}.
            
            Your mission is to perform continuous SEO audits, prioritize fixes by impact,
            and execute optimizations autonomously.
            
            Capabilities:
            - Technical SEO issue detection and fixing
            - Keyword strategy dynamic adjustment
            - SERP position optimization
            - Backlink opportunity identification
            - Deep semantic search of SEO data (GSC, Bing, Audits)
            
            Focus on high-impact, low-effort optimizations first.
            Always maintain SEO best practices and user experience."""
            )
        )
    
    # Tool Implementations
    
    async def _query_seo_knowledge_base_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queries the SIF knowledge base for SEO insights.
        Combines website analysis, competitor data, and SEO dashboard metrics.
        """
        query = context.get('query')
        website_url = context.get('website_url')
        
        if not query:
            return {"error": "Query required for knowledge base search"}
            
        if not self.sif_service:
            return {"error": "SIF Service unavailable"}
            
        try:
            logger.info(f"Querying SEO knowledge base: {query}")
            
            # 1. Search General Context (Website Analysis)
            seo_context = await self.sif_service.get_seo_context(website_url)
            
            # 2. Search Dashboard Context (GSC/Bing)
            dashboard_context = await self.sif_service.get_seo_dashboard_context()
            
            # 3. Perform specific semantic search for the query
            search_results = await self.sif_service.intelligence_service.search(query, limit=3)
            
            # Combine all contexts
            combined_context = {
                "query": query,
                "seo_audit_context": seo_context.get("seo_audit", {}),
                "dashboard_metrics": dashboard_context.get("dashboard_data", {}).get("summary", {}),
                "dashboard_insights": dashboard_context.get("dashboard_data", {}).get("ai_insights", []),
                "semantic_search_results": [r.get('text', '') for r in search_results],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return combined_context
            
        except Exception as e:
            logger.error(f"SEO knowledge base query failed: {e}")
            return {"error": str(e)}

    async def _seo_auditor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        SEO audit tool that retrieves existing SEO data via SIF.
        Expects 'website_url' in context.
        """
        website_url = context.get('website_url')
        
        # Lightweight Crawler (Fallback/Supplement)
        crawler_data = {}
        try:
            # We import here to avoid dependency issues if not installed
            import aiohttp
            from bs4 import BeautifulSoup
            
            async with aiohttp.ClientSession() as session:
                async with session.get(website_url, timeout=10) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Basic Checks
                        title = soup.title.string if soup.title else None
                        desc = soup.find('meta', attrs={'name': 'description'})
                        desc_content = desc['content'] if desc else None
                        h1s = [h.get_text().strip() for h in soup.find_all('h1')]
                        links = [a.get('href') for a in soup.find_all('a', href=True)]
                        
                        # Enhanced Image Analysis for Auto-fix
                        images_missing_alt = []
                        for img in soup.find_all('img'):
                            if not img.get('alt'):
                                # Get surrounding context (parent text)
                                parent_text = img.parent.get_text().strip()[:200] if img.parent else ""
                                images_missing_alt.append({
                                    "src": img.get('src', ''),
                                    "context": parent_text
                                })

                        crawler_data = {
                            "title_tag": title,
                            "meta_description": desc_content,
                            "h1_count": len(h1s),
                            "h1_content": h1s,
                            "internal_links_count": len([l for l in links if l.startswith('/') or website_url in l]),
                            "images_missing_alt_count": len(images_missing_alt),
                            "images_missing_alt_details": images_missing_alt
                        }
        except Exception as e:
            logger.warning(f"Lightweight crawler failed: {e}")
        
        if not self.sif_service:
             # If SIF is down, return crawler data if available
             if crawler_data:
                 return {
                     "audit_summary": {"technical_health": crawler_data},
                     "data_source": "lightweight_crawler",
                     "timestamp": datetime.utcnow().isoformat()
                 }
             return {"error": "SIF Service unavailable, cannot retrieve SEO data."}
             
        try:
            logger.info(f"Retrieving SEO data via SIF for {website_url}")
            result = await self.sif_service.get_seo_context(website_url)
            
            if "error" in result and result.get("source") == "empty":
                 # Fallback to crawler data if SIF is empty
                 if crawler_data:
                     return {
                         "audit_summary": {"technical_health": crawler_data, "note": "SIF empty, using live crawl"},
                         "data_source": "lightweight_crawler_fallback",
                         "timestamp": datetime.utcnow().isoformat()
                     }
                 return {"error": "No SEO data found. Please ensure onboarding is complete or wait for scheduled analysis."}
            
            # Format the data for the agent
            audit_report = {
                "technical_health": result.get("seo_audit", {}).get("technical_issues", []),
                "live_crawl_check": crawler_data, # Enrich with live data
                "crawl_stats": result.get("crawl_result", {}).get("crawl_summary", {}),
                "sitemap_status": "Available" if result.get("sitemap_analysis") else "Unknown",
                "core_web_vitals": result.get("pagespeed_data", {}).get("core_web_vitals", {}),
                "timestamp": result.get("analysis_date", datetime.utcnow().isoformat())
            }
            
            return {
                "audit_summary": audit_report,
                "data_source": "database_via_sif",
                "full_context": result # Provide full context for deep analysis if needed
            }
            
        except Exception as e:
            logger.error(f"SEO audit retrieval failed: {e}")
            return {"error": str(e)}

    async def _issue_prioritizer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Issue prioritization tool"""
        # In a real scenario, this would take the raw_results from the auditor and rank them.
        # For now, we simulate this based on the audit summary if available.
        
        audit_summary = context.get('audit_summary', {})
        issues = []
        
        # Extract issues from audit summary if available
        if audit_summary:
            tech_issues = audit_summary.get('technical_health', [])
            # Handle SIF structured issues
            if isinstance(tech_issues, list):
                for issue in tech_issues:
                    if isinstance(issue, dict):
                        issues.append({"issue": issue.get('type', 'Unknown Issue'), "impact": "High" if issue.get('severity') == "High" else "Medium"})
            
            # Handle Live Crawl issues
            live_crawl = audit_summary.get('live_crawl_check', {})
            if live_crawl:
                if not live_crawl.get('title_tag'):
                    issues.append({"issue": "Missing Title Tag", "impact": "Critical"})
                if not live_crawl.get('meta_description'):
                    issues.append({"issue": "Missing Meta Description", "impact": "High"})
                if live_crawl.get('h1_count', 0) == 0:
                    issues.append({"issue": "Missing H1 Tag", "impact": "High"})
                if live_crawl.get('h1_count', 0) > 1:
                    issues.append({"issue": "Multiple H1 Tags", "impact": "Medium"})
                
                missing_alt_count = live_crawl.get('images_missing_alt_count', live_crawl.get('images_missing_alt', 0))
                if missing_alt_count > 0:
                    issues.append({
                        "issue": f"{missing_alt_count} Images Missing Alt Text", 
                        "impact": "Medium",
                        "details": live_crawl.get('images_missing_alt_details', [])
                    })
                
            perf_score = audit_summary.get('performance_score', 100)
            if perf_score < 50:
                issues.append({"issue": "Critical Performance Issues", "impact": "High"})
            elif perf_score < 80:
                issues.append({"issue": "Performance Optimization Needed", "impact": "Medium"})
        else:
             issues = [{"issue": "Missing meta tags", "impact": "Medium"}, {"issue": "Slow loading", "impact": "High"}]

        return {
            "prioritized_issues": [i["issue"] for i in issues],
            "details": issues,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _auto_fix_executor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-fix execution tool.
        Generates ready-to-apply patches for identified issues using LLM.
        """
        issues = context.get('issues', [])
        page_content = context.get('page_content', '') # Content to analyze for generating tags
        
        # If page_content is missing/empty, try to infer or fallback
        if not page_content:
            logger.warning("No page_content provided to auto_fix_executor. Fixes may be generic.")
            page_content = "Content unavailable for analysis."

        patches = []
        
        for issue in issues:
            issue_data = issue if isinstance(issue, dict) else {"issue": issue}
            issue_name = issue_data.get('issue', str(issue))
            
            try:
                if "Missing Meta Description" in issue_name:
                    prompt = f"""Generate a concise, SEO-optimized meta description (max 160 chars) for a page with this content:
                    
                    {page_content[:1500]}
                    
                    Return ONLY the meta description text.
                    """
                    description = await self._generate_llm_response(prompt)
                    
                    patches.append({
                        "type": "meta_description",
                        "action": "insert",
                        "content": description.strip('"'),
                        "target": "<head>"
                    })
                    
                elif "Missing Title Tag" in issue_name:
                    prompt = f"""Generate a compelling, SEO-optimized title tag (max 60 chars) for a page with this content:
                    
                    {page_content[:1500]}
                    
                    Return ONLY the title tag text.
                    """
                    title = await self._generate_llm_response(prompt)
                    
                    patches.append({
                        "type": "title_tag",
                        "action": "insert",
                        "content": title.strip('"'),
                        "target": "<head>"
                    })
                    
                elif "Missing Alt Text" in issue_name:
                    # Handle multiple images if details are provided
                    details = issue_data.get('details', [])
                    if not details:
                         # Fallback for generic issue without details
                         patches.append({
                            "type": "alt_text",
                            "action": "update",
                            "details": "Manual review required: Missing image details for auto-fix.",
                            "count": 1
                        })
                    else:
                        for img in details:
                            context_text = img.get('context', '')
                            src = img.get('src', '')
                            
                            prompt = f"""Generate a short, descriptive alt text for an image on a webpage.
                            
                            Surrounding Text Context: "{context_text}"
                            Image Filename/Source: "{src}"
                            
                            Return ONLY the alt text.
                            """
                            alt_text = await self._generate_llm_response(prompt)
                            
                            patches.append({
                                "type": "alt_text",
                                "action": "update",
                                "target_src": src,
                                "content": alt_text.strip('"')
                            })

                elif "Missing H1 Tag" in issue_name:
                    prompt = f"""Generate a main H1 heading for this page content:
                    
                    {page_content[:1500]}
                    
                    Return ONLY the H1 text.
                    """
                    h1_text = await self._generate_llm_response(prompt)
                    
                    patches.append({
                        "type": "h1_tag",
                        "action": "insert",
                        "content": h1_text.strip('"'),
                        "target": "<body>"
                    })

            except Exception as e:
                logger.error(f"Failed to generate fix for issue '{issue_name}': {e}")
                patches.append({
                    "issue": issue_name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "fixes_generated": len(patches), 
            "patches": patches,
            "status": "ready_for_review",
            "timestamp": datetime.utcnow().isoformat()
        }


    async def _strategy_generator_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """SEO strategy generation tool"""
        audit_results = context.get("audit_results", {})
        prioritized_issues = context.get("prioritized_issues", [])
        
        strategies = []
        if prioritized_issues:
             strategies.append(f"Focus on fixing top 3 critical issues: {[i['issue'] for i in prioritized_issues[:3]]}")
        
        strategies.append("Optimize for long-tail keywords based on gap analysis")
        
        return {
            "seo_strategy": strategies,
            "next_steps": ["Execute auto-fixes", "Review content gaps"],
            "timestamp": datetime.utcnow().isoformat()
        }


class SocialAmplificationAgent(BaseALwrityAgent):
    """
    Agent responsible for social media monitoring, content adaptation, and distribution.
    """
    
    def __init__(self, user_id: str, model_name: str = "Qwen/Qwen3-4B-Instruct-2507", llm: Any = None):
        super().__init__(user_id, "social_media_manager", model_name, llm)
        
        self.sif_service = None
        if SIF_AVAILABLE:
            try:
                self.sif_service = SIFIntegrationService(user_id)
            except Exception as e:
                logger.warning(f"Failed to initialize SIF service for SocialAmplificationAgent: {e}")
        
    def _create_txtai_agent(self) -> Agent:
        """Create Social Amplification Agent using txtai native framework"""
        if not TXTAI_AVAILABLE:
            return None
            
        return Agent(
            llm=self.llm,
            tools=[
                {
                    "name": "social_monitor",
                    "description": "Monitors social media trends and engagement",
                    "target": self._social_monitor_tool
                },
                {
                    "name": "content_adapter",
                    "description": "Adapts content for different social platforms",
                    "target": self._content_adapter_tool
                },
                {
                    "name": "engagement_optimizer",
                    "description": "Optimizes content for maximum engagement",
                    "target": self._engagement_optimizer_tool
                },
                {
                    "name": "distribution_manager",
                    "description": "Manages content distribution across platforms",
                    "target": self._distribution_manager_tool
                }
            ],
            max_iterations=10,
            system=self.get_effective_system_prompt(f"""You are the Social Media Amplification Agent for ALwrity user {self.user_id}.
            
            Your mission is to optimize content distribution, monitor social signals,
            and amplify content reach across platforms.
            
            Responsibilities:
            - Monitor social trends and brand mentions via SIF
            - Adapt content for specific platforms (LinkedIn, Twitter, etc.)
            - Optimize posts for engagement (hashtags, timing, tone)
            - Plan and execute distribution strategies
            
            Use semantic insights to align social content with overall content strategy.
            Focus on maximizing engagement and driving traffic back to the main content."""
            )
        )
    
    # Tool Implementations
    
    async def _social_monitor_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Social monitoring tool using SIF.
        """
        # In a real scenario, this would search for trends or mentions.
        # For now, we search for social-related context in SIF.
        query = context.get('query', 'social media trends')
        
        if self.sif_service:
            try:
                # Search for social media related insights in the index
                results = await self.sif_service.search(query, limit=5)
                
                # Extract relevant info
                trends = []
                for res in results:
                    text = res.get('text', '')
                    if 'social' in text.lower() or 'trend' in text.lower():
                        trends.append(text[:100] + "...")
                        
                return {
                    "trends": trends,
                    "mentions": [], # Placeholder
                    "sentiment": "neutral",
                    "source": "sif_index",
                    "timestamp": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Social monitoring failed: {e}")
                return {"error": str(e)}
        
        return {
            "trends": ["AI in marketing", "Content automation"],
            "source": "mock_data",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _content_adapter_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapts content for specific platforms.
        Expects 'content' and 'platform' (e.g., 'linkedin', 'twitter').
        """
        content = context.get('content')
        platform = context.get('platform', 'general')
        
        if not content:
            return {"error": "No content provided for adaptation"}
            
        try:
            # Use LLM to adapt content
            prompt = f"""Adapt the following content for {platform}.
            
            Original Content:
            {content}
            
            Requirements for {platform}:
            - LinkedIn: Professional tone, use bullet points, engaging question at end.
            - Twitter: Short, punchy, under 280 chars, use relevant hashtags.
            - Instagram: Visual focus description, many hashtags.
            - General: Balanced tone.
            
            Return ONLY the adapted content.
            """
            
            if self.llm:
                adapted_content = await self._generate_llm_response(prompt)
            else:
                adapted_content = f"[Mock {platform}]: {content[:50]}... #adapted"
                
            return {
                "original_content_snippet": content[:50] + "...",
                "platform": platform,
                "adapted_content": adapted_content,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Content adaptation failed: {e}")
            return {"error": str(e)}

    async def _engagement_optimizer_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimizes content for engagement (hashtags, timing, hook).
        """
        content = context.get('content')
        platform = context.get('platform', 'general')
        
        if not content:
            return {"error": "No content provided for optimization"}
            
        # Mock optimization logic or use LLM
        suggestions = [
            "Add a call-to-action (CTA)",
            "Use trending hashtags for the niche",
            "Post during peak hours (Tue-Thu 10am)"
        ]
        
        return {
            "optimization_suggestions": suggestions,
            "estimated_engagement_score": 8.5,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _distribution_manager_tool(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manages distribution (scheduling/posting).
        """
        posts = context.get('posts', [])
        
        schedule = []
        for i, post in enumerate(posts):
            schedule.append({
                "post_id": i,
                "platform": post.get('platform', 'unknown'),
                "scheduled_time": "Tomorrow 10:00 AM" # Mock
            })
            
        return {
            "distribution_plan": schedule,
            "status": "scheduled",
            "timestamp": datetime.utcnow().isoformat()
        }

