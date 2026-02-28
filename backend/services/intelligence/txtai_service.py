"""
Txtai Intelligence Service
Core service for semantic indexing, search, and clustering using txtai.
Designed to run on modest hardware using lightweight models.
Enhanced with intelligent caching for performance optimization.
"""

import os
import traceback
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from datetime import datetime
from .semantic_cache import semantic_cache_manager, semantic_cache_decorator

# txtai imports (will be available after pip install)
try:
    from txtai import Embeddings
    from txtai.pipeline import Labels, Extractor
    TXTAI_AVAILABLE = True
except ImportError:
    logger.warning("txtai not installed. Some features will be disabled.")
    Embeddings = None
    Labels = None
    Extractor = None
    TXTAI_AVAILABLE = False

class TxtaiIntelligenceService:
    _instances = {}

    def __new__(cls, user_id: str, *args, **kwargs):
        if user_id not in cls._instances:
            cls._instances[user_id] = super(TxtaiIntelligenceService, cls).__new__(cls)
        return cls._instances[user_id]

    def __init__(self, user_id: str, model_path: Optional[str] = None, enable_caching: bool = True):
        # Singleton: prevent re-initialization if already initialized
        if getattr(self, "_singleton_initialized", False):
            return
            
        self.user_id = user_id
        self.model_path = model_path or "sentence-transformers/all-MiniLM-L6-v2"
        self.index_path = f"workspace/workspace_{user_id}/indices/txtai"
        self.embeddings = None
        self._initialized = False
        self.enable_caching = enable_caching
        self.cache_manager = semantic_cache_manager if enable_caching else None
        self._backend = "faiss"  # Default backend
        
        # Mark as initialized for singleton pattern
        self._singleton_initialized = True
        
        # Lazy initialization - do not initialize embeddings on startup
        # self._initialize_embeddings()

    def _ensure_initialized(self):
        """Lazy initialization helper."""
        if not self._initialized:
            self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize txtai embeddings with local storage support and comprehensive error handling."""
        if not TXTAI_AVAILABLE:
            logger.error("txtai is not available. Please install with: pip install txtai[pipeline,similarity]")
            return

        try:
            logger.info(f"Initializing txtai embeddings for user {self.user_id}")
            logger.debug(f"Model path: {self.model_path}")
            logger.debug(f"Index path: {self.index_path}")
            
            # Close existing embeddings if any to release file locks
            if self.embeddings:
                try:
                    if hasattr(self.embeddings, 'close'):
                        self.embeddings.close()
                    self.embeddings = None
                except Exception as close_err:
                    logger.warning(f"Error closing existing embeddings: {close_err}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            logger.debug(f"Created index directory: {os.path.dirname(self.index_path)}")
            
            # Initialize embeddings with optimal configuration for ALwrity use case
            # Hardening: Disabling quantization by default as it causes 'IndexIDMap' attribute errors with small indices on Windows
            self.embeddings = Embeddings({
                "path": self.model_path,
                "content": True,  # Enable content storage for retrieval
                "objects": True,  # Enable object storage for metadata
                "backend": self._backend,  # Use Faiss for efficient similarity search
                "batch": 32,  # Batch size for processing
                "gpu": False,  # Force CPU usage for compatibility
                "limit": 1000  # Maximum number of results for queries
            })
            
            logger.info("Embeddings instance created successfully")
            
            # Check if existing index exists and load it
            if os.path.exists(self.index_path):
                logger.info(f"Loading existing txtai index from {self.index_path}")
                try:
                    self.embeddings.load(self.index_path)
                    logger.info(f"Successfully loaded existing txtai index for user {self.user_id}")
                    # Try to log count, handle if not supported
                    try:
                        count = self.embeddings.count() if hasattr(self.embeddings, 'count') else "unknown"
                        logger.debug(f"Index contains {count} items")
                    except:
                        logger.debug("Index loaded (count unavailable)")
                except Exception as load_error:
                    logger.warning(f"Failed to load existing index: {load_error}. Creating new index.")
                    # Reset embeddings to create new index
                    self.embeddings = Embeddings({
                        "path": self.model_path,
                        "content": True,
                        "objects": True,
                        "backend": self._backend,
                        "batch": 32,
                        "gpu": False,
                        "limit": 1000
                    })
            else:
                logger.info(f"No existing index found. Creating new txtai index for user {self.user_id}")
            
            self._initialized = True
            logger.info(f"Txtai Intelligence Service initialized successfully for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Critical failure initializing txtai embeddings: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error("This may be due to:")
            logger.error("1. Missing model files - try: pip install sentence-transformers")
            logger.error("2. Insufficient memory - try using a smaller model")
            logger.error("3. Missing dependencies - try: pip install txtai[pipeline,similarity]")
            self._initialized = False

    async def index_content(self, items: List[Tuple[str, str, Dict[str, Any]]]):
        """
        Index content for semantic search and clustering.
        
        Args:
            items: List of (id, text, metadata) tuples.
        """
        self._ensure_initialized()
        if not self._initialized or not self.embeddings:
            logger.error(f"Cannot index content - service not initialized for user {self.user_id}")
            return

        try:
            logger.info(f"Starting content indexing for user {self.user_id}")
            logger.debug(f"Indexing {len(items)} items")
            
            # Validate input items
            if not items:
                logger.warning("No items provided for indexing")
                return
                
            # Index items: [(id, text, metadata)] - metadata needs to be JSON string for txtai
            import json
            processed_items = []
            for item in items:
                id_val, text, metadata = item
                # Convert metadata dict to JSON string
                metadata_json = json.dumps(metadata) if metadata else "{}"
                processed_items.append((id_val, text, metadata_json))
            
            self.embeddings.index(processed_items)
            
            # Save the index
            self.embeddings.save(self.index_path)
            logger.info(f"Successfully indexed {len(items)} items for user {self.user_id}")
            logger.debug(f"Index saved to: {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error indexing content for user {self.user_id}: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Items count: {len(items) if items else 0}")
            
            message = str(e)
            is_windows_lock_error = isinstance(e, PermissionError) or "WinError 32" in message
            if is_windows_lock_error:
                logger.warning(
                    f"Txtai index save skipped for user {self.user_id} due to file lock. "
                    f"The index will be retried on a future run."
                )
                return
            raise

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search with intelligent caching."""
        self._ensure_initialized()
        if not self._initialized or not self.embeddings:
            logger.error(f"Cannot perform search - service not initialized for user {self.user_id}")
            return []

        try:
            # Check cache first if enabled
            if self.enable_caching and self.cache_manager:
                cached_results = self.cache_manager.get_cached_query_results(
                    query=query,
                    relevance_threshold=0.5  # Lower threshold for search results
                )
                if cached_results:
                    logger.info(f"Cache hit for search query: '{query}'")
                    # Return cached results up to the requested limit
                    return cached_results[:limit]
                else:
                    logger.debug(f"Cache miss for search query: '{query}'")

            logger.debug(f"Searching for query: '{query}' with limit: {limit}")
            try:
                results = self.embeddings.search(query, limit=limit)
            except AttributeError as ae:
                if "nprobe" in str(ae):
                    logger.error(f"Detected known txtai/faiss IndexIDMap/nprobe incompatibility for user {self.user_id}. Attempting re-init with numpy backend fallback...")
                    # Switch to numpy backend which doesn't have this issue
                    self._backend = "numpy"
                    self._initialize_embeddings()
                    if self.embeddings:
                        results = self.embeddings.search(query, limit=limit)
                    else:
                        raise ae
                else:
                    raise ae
            
            # Cache the results if caching is enabled
            if self.enable_caching and self.cache_manager and results:
                self.cache_manager.cache_query_results(
                    query=query,
                    results=results,
                    relevance_threshold=0.5
                )
                logger.debug(f"Cached search results for query: '{query}'")
            
            logger.info(f"Search completed successfully for user {self.user_id}. Found {len(results)} results")
            logger.debug(f"Top result score: {results[0]['score'] if results else 'N/A'}")
            return results
        except Exception as e:
            logger.error(f"Search failed for user {self.user_id}: {e}")
            logger.error(f"Query: '{query}'")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    async def get_similarity(self, text1: str, text2: str) -> float:
        """Get semantic similarity between two texts with caching."""
        self._ensure_initialized()
        if not self._initialized or not self.embeddings:
            logger.error(f"Cannot calculate similarity - service not initialized for user {self.user_id}")
            return 0.0

        try:
            # Create cache key for similarity calculation
            cache_key = f"similarity_{self.user_id}_{hash(text1)}_{hash(text2)}"
            
            # Check cache first if enabled
            if self.enable_caching and self.cache_manager:
                cached_similarity = self.cache_manager.get_cached_semantic_insights(
                    user_id=cache_key,
                    force_refresh=False
                )
                if cached_similarity and "similarity" in cached_similarity:
                    logger.info(f"Cache hit for similarity calculation")
                    return cached_similarity["similarity"]
                else:
                    logger.debug(f"Cache miss for similarity calculation")

            logger.debug(f"Calculating similarity between texts: '{text1[:50]}...' and '{text2[:50]}...'")
            try:
                similarity = self.embeddings.similarity(text1, text2)
            except AttributeError as ae:
                if "nprobe" in str(ae):
                    logger.error(f"Detected IndexIDMap nprobe error in similarity for user {self.user_id}. Falling back to numpy backend...")
                    self._backend = "numpy"
                    self._initialize_embeddings()
                    if self.embeddings:
                        similarity = self.embeddings.similarity(text1, text2)
                    else:
                        raise ae
                else:
                    raise ae
            
            # Cache the similarity result
            if self.enable_caching and self.cache_manager:
                similarity_data = {
                    "similarity": similarity,
                    "text1_hash": hash(text1),
                    "text2_hash": hash(text2),
                    "timestamp": datetime.now().isoformat()
                }
                self.cache_manager.cache_semantic_insights(
                    user_id=cache_key,
                    insights=similarity_data,
                    ttl=3600  # 1 hour TTL for similarity results
                )
                logger.debug(f"Cached similarity result")
            
            logger.info(f"Similarity calculated successfully for user {self.user_id}: {similarity:.4f}")
            return similarity
        except Exception as e:
            logger.error(f"Similarity calculation failed for user {self.user_id}: {e}")
            logger.error(f"Text1 length: {len(text1)}, Text2 length: {len(text2)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return 0.0

    async def cluster(self, min_score: float = 0.5) -> List[List[int]]:
        """Cluster indexed content to find semantic pillars using graph-based clustering with caching."""
        self._ensure_initialized()
        if not self._initialized or not self.embeddings:
            logger.error(f"Cannot cluster content - service not initialized for user {self.user_id}")
            return []

        try:
            # Check cache first if enabled
            if self.enable_caching and self.cache_manager:
                cache_key = f"cluster_{self.user_id}_{min_score}"
                cached_clusters = self.cache_manager.get_cached_semantic_insights(
                    user_id=cache_key,
                    force_refresh=False
                )
                if cached_clusters and "clusters" in cached_clusters:
                    logger.info(f"Cache hit for clustering with min_score: {min_score}")
                    return cached_clusters["clusters"]
                else:
                    logger.debug(f"Cache miss for clustering with min_score: {min_score}")

            logger.info(f"Starting content clustering for user {self.user_id} with min_score: {min_score}")
            
            # Check if we have graph functionality available
            if not hasattr(self.embeddings, 'graph') or not self.embeddings.graph:
                logger.warning(f"Graph clustering not available for user {self.user_id}. Using fallback clustering.")
                return self._fallback_clustering(min_score)
            
            # Use graph-based clustering if available
            # Perform a search to get graph structure
            sample_query = "content marketing digital strategy"
            try:
                graph_results = self.embeddings.search(sample_query, limit=10, graph=True)
            except AttributeError as ae:
                if "nprobe" in str(ae):
                    logger.error(f"Detected IndexIDMap nprobe error in cluster for user {self.user_id}. Falling back to numpy backend...")
                    self._backend = "numpy"
                    self._initialize_embeddings()
                    if self.embeddings:
                        graph_results = self.embeddings.search(sample_query, limit=10, graph=True)
                    else:
                        raise ae
                else:
                    raise ae
            
            if not graph_results:
                logger.warning(f"No graph results for clustering user {self.user_id}")
                return self._fallback_clustering(min_score)
            
            # Extract clusters from graph results
            clusters = self._extract_clusters_from_graph(graph_results, min_score)
            
            # Cache the clustering results
            if self.enable_caching and self.cache_manager:
                cluster_data = {
                    "clusters": clusters,
                    "cluster_count": len(clusters),
                    "min_score": min_score,
                    "timestamp": datetime.now().isoformat()
                }
                self.cache_manager.cache_semantic_insights(
                    user_id=f"cluster_{self.user_id}_{min_score}",
                    insights=cluster_data,
                    ttl=1800  # 30 minutes TTL for clustering results
                )
                logger.debug(f"Cached clustering results for user {self.user_id}")
            
            logger.info(f"Clustering completed successfully. Found {len(clusters)} clusters for user {self.user_id}")
            logger.debug(f"Cluster sizes: {[len(c) for c in clusters]}")
            return clusters
            
        except Exception as e:
            logger.error(f"Clustering failed for user {self.user_id}: {e}")
            logger.error(f"Min score: {min_score}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._fallback_clustering(min_score)
    
    async def _fallback_clustering(self, min_score: float) -> List[List[int]]:
        """Fallback clustering method when graph clustering is not available."""
        logger.info(f"Using fallback clustering for user {self.user_id}")
        
        # Simple clustering based on semantic similarity
        # This is a placeholder - in production, you'd implement a proper clustering algorithm
        try:
            # Get a sample of indexed items to analyze
            sample_queries = ["marketing", "SEO", "content", "social media", "email marketing"]
            all_clusters = []
            
            for query in sample_queries:
                # Use our search wrapper for hardening
                results = await self.search(query, limit=5)
                if results and results[0].get("score", 0) >= min_score:
                    # Create a cluster from similar results
                    cluster = [i for i, result in enumerate(results) if result.get("score", 0) >= min_score]
                    if cluster:
                        all_clusters.append(cluster)
            
            # Remove duplicate clusters
            unique_clusters = []
            for cluster in all_clusters:
                if cluster not in unique_clusters:
                    unique_clusters.append(cluster)
            
            return unique_clusters
            
        except Exception as e:
            logger.error(f"Fallback clustering failed for user {self.user_id}: {e}")
            return []
    
    def _extract_clusters_from_graph(self, graph_results: List[Dict], min_score: float) -> List[List[int]]:
        """Extract clusters from graph search results."""
        logger.debug(f"Extracting clusters from graph results for user {self.user_id}")
        
        clusters = []
        
        try:
            # Group results by similarity score threshold
            current_cluster = []
            
            for i, result in enumerate(graph_results):
                score = result.get("score", 0)
                if score >= min_score:
                    current_cluster.append(i)
                else:
                    if current_cluster:
                        clusters.append(current_cluster)
                        current_cluster = []
            
            # Add final cluster if exists
            if current_cluster:
                clusters.append(current_cluster)
            
            return clusters
            
        except Exception as e:
            logger.error(f"Graph cluster extraction failed for user {self.user_id}: {e}")
            return []

    async def classify(self, text: str, labels: List[str]) -> List[Tuple[str, float]]:
        """Classify text using zero-shot classification."""
        self._ensure_initialized()
        if not self._initialized or not Labels:
            logger.error(f"Cannot classify text - service not initialized or Labels not available for user {self.user_id}")
            return []

        try:
            logger.debug(f"Classifying text: '{text[:100]}...' with labels: {labels}")
            classifier = Labels()
            results = classifier(text, labels)
            logger.info(f"Classification completed successfully for user {self.user_id}. Found {len(results)} results")
            logger.debug(f"Classification results: {results}")
            return results
        except Exception as e:
            logger.error(f"Classification failed for user {self.user_id}: {e}")
            logger.error(f"Text length: {len(text)}")
            logger.error(f"Labels count: {len(labels)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index."""
        if not self._initialized or not self.embeddings:
            return {"status": "not_initialized", "user_id": self.user_id}
        
        try:
            # Get count of indexed items
            index_size = "unknown"
            if hasattr(self.embeddings, 'count'):
                try:
                    index_size = self.embeddings.count()
                except:
                    pass
            
            return {
                "status": "active",
                "user_id": self.user_id,
                "index_size": index_size,
                "model_path": self.model_path,
                "index_path": self.index_path,
                "initialized": self._initialized
            }
        except Exception as e:
            logger.error(f"Error getting index stats for user {self.user_id}: {e}")
            return {"status": "error", "user_id": self.user_id, "error": str(e)}

    def is_initialized(self) -> bool:
        """Check if the service is properly initialized, triggering lazy init if needed."""
        if not self._initialized:
            self._ensure_initialized()
        return self._initialized and self.embeddings is not None
