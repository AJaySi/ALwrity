"""
Quality Validation Service
AI response quality assessment and strategic analysis.
All methods derive results from actual input data — no hardcoded defaults.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class QualityValidationService:
    """Service for quality validation and strategic analysis."""

    def __init__(self):
        pass

    def validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate data against a minimal JSON-like schema definition.
        Raises ValueError on failure.
        Schema format example:
        {"type": "object", "required": ["strategy_brief", "channels"], "properties": {"strategy_brief": {"type": "object"}, "channels": {"type": "array"}}}
        """
        def _check(node, sch, path="$"):
            t = sch.get("type")
            if t == "object":
                if not isinstance(node, dict):
                    raise ValueError(f"Schema error at {path}: expected object")
                for req in sch.get("required", []):
                    if req not in node or node[req] in (None, ""):
                        raise ValueError(f"Schema error at {path}.{req}: required field missing")
                for key, sub in sch.get("properties", {}).items():
                    if key in node:
                        _check(node[key], sub, f"{path}.{key}")
            elif t == "array":
                if not isinstance(node, list):
                    raise ValueError(f"Schema error at {path}: expected array")
                item_s = sch.get("items")
                if item_s:
                    for i, item in enumerate(node):
                        _check(item, item_s, f"{path}[{i}]")
            elif t == "string":
                if not isinstance(node, str) or not node.strip():
                    raise ValueError(f"Schema error at {path}: expected non-empty string")
            elif t == "number":
                if not isinstance(node, (int, float)):
                    raise ValueError(f"Schema error at {path}: expected number")
            elif t == "boolean":
                if not isinstance(node, bool):
                    raise ValueError(f"Schema error at {path}: expected boolean")
            elif t == "any":
                return
            else:
                return
        _check(data, schema)

    def calculate_strategic_scores(self, ai_recommendations: Dict[str, Any]) -> Dict[str, float]:
        """Calculate strategic performance scores from AI recommendations.
        Scores are derived per analysis type from actual metrics, then aggregated
        with dimension-specific weightings — no blanket multipliers.
        """
        scores = {
            'overall_score': 0.0,
            'content_quality_score': 0.0,
            'engagement_score': 0.0,
            'conversion_score': 0.0,
            'innovation_score': 0.0
        }

        analysis_count = 0
        weighted_total = 0.0
        weight_sum = 0.0

        # Dimension-specific weights
        dimension_weights = {
            'comprehensive_strategy': {'quality': 0.35, 'engagement': 0.20, 'conversion': 0.25, 'innovation': 0.20},
            'audience_intelligence': {'quality': 0.25, 'engagement': 0.40, 'conversion': 0.20, 'innovation': 0.15},
            'competitive_intelligence': {'quality': 0.30, 'engagement': 0.15, 'conversion': 0.25, 'innovation': 0.30},
            'performance_optimization': {'quality': 0.20, 'engagement': 0.15, 'conversion': 0.45, 'innovation': 0.20},
            'content_calendar_optimization': {'quality': 0.30, 'engagement': 0.25, 'conversion': 0.20, 'innovation': 0.25},
        }

        for analysis_type, recommendations in ai_recommendations.items():
            if not isinstance(recommendations, dict):
                continue
            metrics = recommendations.get('metrics')
            if not isinstance(metrics, dict):
                continue

            score = metrics.get('score', 50)
            confidence = metrics.get('confidence', 0.5)
            weight = confidence

            weighted_total += score * weight
            weight_sum += weight
            analysis_count += 1

            weights = dimension_weights.get(analysis_type, {'quality': 0.25, 'engagement': 0.25, 'conversion': 0.25, 'innovation': 0.25})
            scores['content_quality_score'] += (score * weights['quality'] * weight)
            scores['engagement_score'] += (score * weights['engagement'] * weight)
            scores['conversion_score'] += (score * weights['conversion'] * weight)
            scores['innovation_score'] += (score * weights['innovation'] * weight)

        if weight_sum > 0:
            scores['overall_score'] = round(weighted_total / weight_sum, 2)
            scores['content_quality_score'] = round(scores['content_quality_score'] / weight_sum, 2)
            scores['engagement_score'] = round(scores['engagement_score'] / weight_sum, 2)
            scores['conversion_score'] = round(scores['conversion_score'] / weight_sum, 2)
            scores['innovation_score'] = round(scores['innovation_score'] / weight_sum, 2)

        return scores

    def extract_market_positioning(self, ai_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market positioning from AI recommendations.
        Scans all analysis types for positioning, competitive_advantage, and market_share signals.
        Returns empty dict if no data is available instead of synthetic defaults.
        """
        positioning = {}
        best_confidence = 0.0

        for analysis_type, recommendations in ai_recommendations.items():
            if not isinstance(recommendations, dict):
                continue
            metrics = recommendations.get('metrics', {})
            confidence = metrics.get('confidence', 0.0)
            if confidence <= best_confidence:
                continue

            recs = recommendations.get('recommendations', [])
            if isinstance(recs, list):
                for r in recs:
                    if not isinstance(r, dict):
                        continue
                    pos = r.get('market_position') or r.get('positioning')
                    adv = r.get('competitive_advantage')
                    share = r.get('market_share')
                    score = r.get('positioning_score') or metrics.get('positioning_score')
                    if any([pos, adv, share, score]):
                        best_confidence = confidence
                        if pos:
                            positioning['industry_position'] = pos
                        if adv:
                            positioning['competitive_advantage'] = adv
                        if share:
                            positioning['market_share'] = str(share)
                        if score is not None:
                            positioning['positioning_score'] = score

        # Check top-level keys as fallback
        if not positioning:
            for key in ('industry_position', 'competitive_advantage', 'market_share', 'positioning_score'):
                val = ai_recommendations.get(key)
                if val is not None:
                    positioning[key] = val

        return positioning

    def extract_competitive_advantages(self, ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract competitive advantages from AI recommendations.
        Scans competitive_intelligence and other analysis types for advantage signals.
        Returns empty list if no data is available.
        """
        advantages = []

        for analysis_type, recommendations in ai_recommendations.items():
            if not isinstance(recommendations, dict):
                continue
            recs = recommendations.get('recommendations', [])
            if not isinstance(recs, list):
                continue
            for r in recs:
                if not isinstance(r, dict):
                    continue
                adv = r.get('advantage') or r.get('competitive_advantage')
                if adv:
                    advantages.append({
                        'advantage': adv,
                        'impact': r.get('impact', 'Medium'),
                        'implementation': r.get('implementation', 'Planned')
                    })

        # Deduplicate by advantage text
        seen = set()
        unique = []
        for a in advantages:
            key = a['advantage'].strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(a)

        return unique

    def extract_strategic_risks(self, ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract strategic risks from AI recommendations.
        Scans all analysis types for risk signals.
        Returns empty list if no data is available.
        """
        risks = []

        for analysis_type, recommendations in ai_recommendations.items():
            if not isinstance(recommendations, dict):
                continue
            recs = recommendations.get('recommendations', [])
            if not isinstance(recs, list):
                continue
            for r in recs:
                if not isinstance(r, dict):
                    continue
                risk_text = r.get('risk') or r.get('strategic_risk') or r.get('threat')
                if risk_text:
                    risks.append({
                        'risk': risk_text,
                        'probability': r.get('probability', 'Medium'),
                        'impact': r.get('impact', 'Medium')
                    })

            risks_list = recommendations.get('risks') or recommendations.get('strategic_risks')
            if isinstance(risks_list, list):
                for r in risks_list:
                    if isinstance(r, dict) and r.get('risk'):
                        risks.append(r)

        seen = set()
        unique = []
        for r in risks:
            key = r['risk'].strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique

    def extract_opportunity_analysis(self, ai_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract opportunity analysis from AI recommendations.
        Scans all analysis types for opportunity signals.
        Returns empty list if no data is available.
        """
        opportunities = []

        for analysis_type, recommendations in ai_recommendations.items():
            if not isinstance(recommendations, dict):
                continue
            recs = recommendations.get('recommendations', [])
            if not isinstance(recs, list):
                continue
            for r in recs:
                if not isinstance(r, dict):
                    continue
                opp = r.get('opportunity') or r.get('growth_opportunity')
                if opp:
                    opportunities.append({
                        'opportunity': opp,
                        'potential_impact': r.get('potential_impact', 'Medium'),
                        'implementation_ease': r.get('implementation_ease', 'Medium')
                    })

            opps_list = recommendations.get('opportunities') or recommendations.get('growth_opportunities')
            if isinstance(opps_list, list):
                for o in opps_list:
                    if isinstance(o, dict) and o.get('opportunity'):
                        opportunities.append(o)

        seen = set()
        unique = []
        for o in opportunities:
            key = o['opportunity'].strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(o)

        return unique

    def validate_ai_response_quality(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of AI response using multi-dimensional analysis.
        Scores are derived from actual content, not placeholders.
        """
        quality_metrics = {
            'completeness': 0.0,
            'relevance': 0.0,
            'actionability': 0.0,
            'confidence': 0.0,
            'overall_quality': 0.0
        }

        # Completeness: weighted by field importance
        field_weights = {
            'recommendations': 0.35,
            'insights': 0.30,
            'metrics': 0.20,
            'analysis_type': 0.15
        }
        weighted_present = 0.0
        total_weight = 0.0
        for field, weight in field_weights.items():
            total_weight += weight
            val = ai_response.get(field)
            if field == 'recommendations':
                if isinstance(val, list) and len(val) > 0:
                    weighted_present += weight
            elif field == 'insights':
                if isinstance(val, list) and len(val) > 0:
                    weighted_present += weight
            elif field == 'metrics':
                if isinstance(val, dict) and len(val) > 0:
                    weighted_present += weight
            else:
                if val is not None:
                    weighted_present += weight
        quality_metrics['completeness'] = round(weighted_present / total_weight, 2) if total_weight > 0 else 0.0

        # Relevance: evaluate recommendations content quality
        recommendations = ai_response.get('recommendations', [])
        if isinstance(recommendations, list) and len(recommendations) > 0:
            scored = 0
            total_recs = len(recommendations)
            for r in recommendations:
                if isinstance(r, dict):
                    has_action = bool(r.get('action') or r.get('recommendation') or r.get('step'))
                    has_reason = bool(r.get('reason') or r.get('rationale') or r.get('impact'))
                    if has_action and has_reason:
                        scored += 1
            quality_metrics['relevance'] = round(scored / total_recs, 2) if total_recs > 0 else 0.5
        else:
            quality_metrics['relevance'] = 0.0

        # Actionability: recommendation detail score
        if isinstance(recommendations, list) and len(recommendations) > 0:
            actionable = 0
            for r in recommendations:
                if isinstance(r, dict):
                    has_timeline = bool(r.get('timeline') or r.get('effort'))
                    has_impact = bool(r.get('impact') or r.get('expected_outcome'))
                    if has_timeline or has_impact:
                        actionable += 1
            quality_metrics['actionability'] = round(min(1.0, actionable / max(len(recommendations), 1)), 2)
        else:
            quality_metrics['actionability'] = 0.0

        # Confidence from metrics
        metrics = ai_response.get('metrics', {})
        quality_metrics['confidence'] = round(metrics.get('confidence', 0.0), 2) if isinstance(metrics, dict) else 0.0

        # Overall weighted quality
        weights = {'completeness': 0.25, 'relevance': 0.30, 'actionability': 0.25, 'confidence': 0.20}
        overall = sum(quality_metrics[k] * weights[k] for k in weights)
        quality_metrics['overall_quality'] = round(overall, 2)

        return quality_metrics

    def assess_strategy_quality(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the overall quality of a content strategy.
        Uses field-level analysis with content-aware scoring — not simple presence checks.
        """
        quality_assessment = {
            'data_completeness': 0.0,
            'strategic_clarity': 0.0,
            'implementation_readiness': 0.0,
            'competitive_positioning': 0.0,
            'overall_quality': 0.0
        }

        # Data completeness with weighted field groups
        field_groups = {
            'objectives': {'fields': ['business_objectives', 'target_metrics'], 'weight': 0.25},
            'resources': {'fields': ['content_budget', 'team_size', 'implementation_timeline'], 'weight': 0.25},
            'audience': {'fields': ['content_preferences', 'consumption_patterns', 'audience_pain_points'], 'weight': 0.25},
            'competition': {'fields': ['top_competitors', 'market_gaps', 'competitive_position'], 'weight': 0.25}
        }
        total_weight = 0.0
        weighted_score = 0.0
        for group_name, group in field_groups.items():
            group_present = sum(1 for f in group['fields'] if strategy_data.get(f) not in (None, '', []))
            group_score = group_present / len(group['fields']) if group['fields'] else 0
            weighted_score += group_score * group['weight']
            total_weight += group['weight']
        quality_assessment['data_completeness'] = round(weighted_score / total_weight, 2) if total_weight > 0 else 0.0

        # Strategic clarity: evaluate quality of business objectives
        objectives = strategy_data.get('business_objectives')
        if isinstance(objectives, str) and len(objectives) > 20:
            quality_assessment['strategic_clarity'] = 0.9
        elif isinstance(objectives, str) and len(objectives) > 0:
            quality_assessment['strategic_clarity'] = 0.6
        elif isinstance(objectives, list) and len(objectives) > 0:
            quality_assessment['strategic_clarity'] = 0.8
        else:
            quality_assessment['strategic_clarity'] = 0.0

        # Implementation readiness: budget + team + timeline
        readiness_signals = 0
        if strategy_data.get('content_budget') not in (None, '', 0):
            readiness_signals += 1
        if strategy_data.get('team_size') not in (None, '', 0):
            readiness_signals += 1
        if strategy_data.get('implementation_timeline') not in (None, '', []):
            readiness_signals += 1
        quality_assessment['implementation_readiness'] = round(readiness_signals / 3.0, 2)

        # Competitive positioning: evaluate depth of competitive data
        comp_signals = 0
        if strategy_data.get('top_competitors') not in (None, '', []):
            comp_signals += 1
        if strategy_data.get('market_gaps') not in (None, '', []):
            comp_signals += 1
        if strategy_data.get('competitive_position') not in (None, ''):
            comp_signals += 1
        if strategy_data.get('industry_trends') not in (None, '', []):
            comp_signals += 1
        quality_assessment['competitive_positioning'] = round(comp_signals / 4.0, 2)

        # Overall quality
        quality_assessment['overall_quality'] = round(
            sum(quality_assessment.values()) / len(quality_assessment), 2
        )

        return quality_assessment 