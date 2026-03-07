"""
Self-Learning Task Memory Service (Phase 3)
Uses txtai and TaskHistory DB model to filter and improve daily task suggestions.
"""
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from loguru import logger
from sqlalchemy.orm import Session

from models.daily_workflow_models import TaskHistory, DailyWorkflowTask
from services.intelligence.txtai_service import TxtaiIntelligenceService

EXACT_DUPLICATE_LOOKBACK_DAYS = 7
SEMANTIC_SUPPRESSION_SCORE_THRESHOLD = 0.85
SUPPRESSED_STATUSES = {"dismissed", "rejected", "skipped"}

class TaskMemoryService:
    """
    Manages the long-term memory of user tasks.
    Responsibilities:
    1. Record completed/rejected tasks to DB and txtai index.
    2. Check if a proposed task is redundant or previously rejected.
    3. Retrieve relevant past tasks for context.
    """
    
    def __init__(self, user_id: str, db: Session):
        self.user_id = user_id
        self.db = db
        self.intelligence = TxtaiIntelligenceService(user_id)
        self._metrics_counters: Dict[str, int] = {}

    def _increment_metric(self, metric_name: str, increment: int = 1) -> None:
        """Increment lightweight in-memory counters for observability hooks."""
        self._metrics_counters[metric_name] = self._metrics_counters.get(metric_name, 0) + increment
        logger.debug(
            "TaskMemory metric updated user_id={} metric={} value={}",
            self.user_id,
            metric_name,
            self._metrics_counters[metric_name],
        )
        
    def _compute_hash(self, title: str, description: str) -> str:
        """Compute a consistent hash for task deduplication."""
        text = f"{title.strip().lower()}|{description.strip().lower()}"
        return hashlib.sha256(text.encode()).hexdigest()

    async def record_task_outcome(self, task: DailyWorkflowTask, feedback_score: int = 0, feedback_text: str = None):
        """
        Record a task's final status (completed, dismissed, rejected) into memory.
        """
        try:
            task_hash = self._compute_hash(task.title, task.description)
            
            # 1. Update/Create DB Record
            history = TaskHistory(
                user_id=self.user_id,
                task_hash=task_hash,
                title=task.title,
                description=task.description,
                pillar_id=task.pillar_id,
                status=task.status,
                source_agent=task.metadata_json.get("source_agent") if task.metadata_json else None,
                feedback_score=feedback_score,
                feedback_text=feedback_text,
                created_at=datetime.utcnow(),
                vector_id=str(uuid.uuid4())
            )
            self.db.add(history)
            self.db.commit()
            
            # 2. Index into txtai (if status is meaningful)
            if task.status in ["completed", "dismissed", "rejected", "skipped"]:
                # We index the task text with metadata about its outcome
                # This allows us to search: "Has the user rejected similar tasks?"
                doc = {
                    "id": history.vector_id,
                    "text": f"{task.title}. {task.description}",
                    "tags": f"task_memory {task.status} {task.pillar_id}",
                    "status": task.status,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Use Txtai service to upsert
                # Note: TxtaiService usually handles batching, but for single updates we can use add
                if hasattr(self.intelligence.embeddings, "upsert"):
                     self.intelligence.embeddings.upsert([doc])
                     # save() requires a path argument in some txtai versions, but TxtaiService manages paths
                     # If we are using the service wrapper, we should rely on its internal management
                     # However, self.intelligence.embeddings is the raw txtai object.
                     # We should check if we need to call save with the index path.
                     
                     index_path = getattr(self.intelligence, "index_path", None)
                     if index_path:
                        self.intelligence.embeddings.save(index_path)
                        logger.info(f"Indexed task outcome: {task.title} -> {task.status}")
                     else:
                        logger.warning("Could not save embeddings: index_path not found on service")

        except Exception as e:
            logger.error(f"Failed to record task outcome for user {self.user_id}: {e}")

    async def filter_redundant_proposals(self, proposals: List[Any]) -> List[Any]:
        """
        Filter out proposals that are:
        1. Exact duplicates of recently completed/rejected tasks (Hash check).
        2. Semantically too similar to recently rejected tasks (Vector check).
        """
        filtered = []
        
        # Get recent history hashes (last 7 days)
        cutoff = datetime.utcnow() - timedelta(days=EXACT_DUPLICATE_LOOKBACK_DAYS)
        recent_hashes = {
            row.task_hash for row in 
            self.db.query(TaskHistory.task_hash)
            .filter(TaskHistory.user_id == self.user_id, TaskHistory.created_at >= cutoff)
            .all()
        }
        
        for p in proposals:
            p_hash = self._compute_hash(p.title, p.description)
            
            # 1. Exact Match Check
            if p_hash in recent_hashes:
                logger.info(f"Filtering redundant task (exact match): {p.title}")
                continue
                
            # 2. Semantic Similarity Check (only for potential rejections)
            # If we have the vector index ready
            is_semantic_duplicate = False
            try:
                # Check if similar tasks were REJECTED recently
                results = await self.intelligence.search(
                    f"{p.title} {p.description}", 
                    limit=1
                )
                
                if results:
                    top = results[0]
                    top_score = float(top.get("score", 0))
                    if top_score >= SEMANTIC_SUPPRESSION_SCORE_THRESHOLD:
                        indexed_status = self._extract_indexed_status(top)
                        if indexed_status in SUPPRESSED_STATUSES:
                            logger.info(
                                f"Filtering redundant task (semantic {top_score:.2f}, indexed status={indexed_status}): {p.title}"
                            )
                            is_semantic_duplicate = True
                        else:
                            vector_id = top.get("id") or top.get("vector_id")
                            if vector_id:
                                history = (
                                    self.db.query(TaskHistory.status)
                                    .filter(
                                        TaskHistory.user_id == self.user_id,
                                        TaskHistory.vector_id == str(vector_id),
                                    )
                                    .order_by(TaskHistory.created_at.desc())
                                    .first()
                                )
                                history_status = getattr(history, "status", None)
                                if history_status in SUPPRESSED_STATUSES:
                                    logger.info(
                                        f"Filtering redundant task (semantic {top_score:.2f}, history status={history_status}): {p.title}"
                                    )
                                    is_semantic_duplicate = True
            except Exception as semantic_err:
                self._increment_metric("semantic_filter_failures")
                self._increment_metric("semantic_filter_degraded_path_taken")
                logger.warning(
                    "Semantic filter degraded for user_id={} proposal_title={} error_class={} error_message={}",
                    self.user_id,
                    getattr(p, "title", ""),
                    type(semantic_err).__name__,
                    str(semantic_err),
                )
                
            if not is_semantic_duplicate:
                filtered.append(p)
                
        return filtered

    def _extract_indexed_status(self, search_result: Dict[str, Any]) -> Optional[str]:
        """Extract indexed status from txtai result metadata if available."""
        status = search_result.get("status")
        if status:
            return str(status).lower()

        obj = search_result.get("object")
        if isinstance(obj, dict):
            obj_status = obj.get("status")
            return str(obj_status).lower() if obj_status else None

        return None
