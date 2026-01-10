"""
Query deduplication logic for unified research analyzer.

Removes redundant queries that would return similar results
and ensures queries are linked to intent fields.
"""

from typing import List
from loguru import logger

from models.research_intent_models import ResearchIntent, ResearchQuery


def deduplicate_queries(
    queries: List[ResearchQuery], 
    intent: ResearchIntent
) -> List[ResearchQuery]:
    """
    Remove redundant queries that would return similar results.
    
    Rules:
    1. If two queries are semantically very similar (same keywords, same purpose), merge them
    2. If a query can answer multiple secondary questions, combine them
    3. If focus areas overlap significantly, don't create separate queries
    4. Maximum 8 queries - prioritize by importance
    5. Always keep the primary query (addresses_primary_question=True)
    """
    if len(queries) <= 8:
        # Still check for exact duplicates
        seen_queries = set()
        deduplicated = []
        for query in queries:
            query_key = (query.query.lower().strip(), query.provider)
            if query_key not in seen_queries:
                seen_queries.add(query_key)
                deduplicated.append(query)
        return deduplicated
    
    # Sort by priority (highest first)
    queries.sort(key=lambda q: q.priority, reverse=True)
    
    # Always keep primary query
    primary_queries = [q for q in queries if q.addresses_primary_question]
    other_queries = [q for q in queries if not q.addresses_primary_question]
    
    deduplicated = []
    seen_keywords = set()
    
    # Add primary queries first (should be only one, but handle multiple)
    for query in primary_queries:
        query_key = (query.query.lower().strip(), query.provider)
        if query_key not in seen_keywords:
            seen_keywords.add(query_key)
            deduplicated.append(query)
    
    # Process other queries with similarity checking
    for query in other_queries:
        query_key = (query.query.lower().strip(), query.provider)
        
        # Check for exact duplicate
        if query_key in seen_keywords:
            continue
        
        # Check for semantic similarity with existing queries
        query_words = set(query.query.lower().split())
        is_duplicate = False
        
        for existing in deduplicated:
            existing_words = set(existing.query.lower().split())
            
            # Calculate Jaccard similarity (intersection over union)
            intersection = query_words & existing_words
            union = query_words | existing_words
            similarity = len(intersection) / len(union) if union else 0
            
            # CRITICAL: Don't merge queries that target different focus areas or also_answering topics
            # These should remain separate even if they're similar
            query_focus_areas = set(query.targets_focus_areas)
            existing_focus_areas = set(existing.targets_focus_areas)
            query_also_answering = set(query.covers_also_answering)
            existing_also_answering = set(existing.covers_also_answering)
            
            # If queries target different focus areas, keep them separate
            if query_focus_areas and existing_focus_areas and query_focus_areas != existing_focus_areas:
                continue  # Keep separate - different focus areas
            
            # If queries cover different also_answering topics, keep them separate
            if query_also_answering and existing_also_answering and query_also_answering != existing_also_answering:
                continue  # Keep separate - different also_answering topics
            
            # Only consider duplicate if >90% similarity (increased from 80%) AND same purpose/provider AND same focus/also_answering
            # This is more strict to avoid over-deduplication
            if similarity > 0.9 and query.purpose == existing.purpose and query.provider == existing.provider:
                # Only merge if they truly target the same things
                if query_focus_areas == existing_focus_areas and query_also_answering == existing_also_answering:
                    is_duplicate = True
                    # Merge: update existing query's linking arrays
                    existing.addresses_secondary_questions = list(set(
                        existing.addresses_secondary_questions + query.addresses_secondary_questions
                    ))
                    existing.targets_focus_areas = list(set(
                        existing.targets_focus_areas + query.targets_focus_areas
                    ))
                    existing.covers_also_answering = list(set(
                        existing.covers_also_answering + query.covers_also_answering
                    ))
                    # Update expected_results to reflect merged coverage
                    if query.expected_results and query.expected_results not in existing.expected_results:
                        existing.expected_results += f" Also covers: {query.expected_results}"
                    break
        
        if not is_duplicate:
            deduplicated.append(query)
            seen_keywords.add(query_key)
        
        # Limit to 8 queries total
        if len(deduplicated) >= 8:
            break
    
    logger.info(f"Deduplicated queries: {len(queries)} -> {len(deduplicated)}")
    return deduplicated
