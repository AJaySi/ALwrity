from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, TypedDict


AgentCatalogEntry = Dict[str, Any]
GoalType = Literal["growth", "defensive", "launch", "maintenance"]


class GoalCheckpointRule(TypedDict, total=False):
    checkpoint_policy: str
    require_approval: bool
    escalation: str


class GoalPromptOverrides(TypedDict, total=False):
    system_prompt_prefix: str
    system_prompt_suffix: str
    task_prompt_prefix: str
    task_prompt_suffix: str


class GoalConfiguration(TypedDict):
    schema_version: str
    objective: str
    required_roles: List[str]
    prompt_overrides: GoalPromptOverrides
    rule_matrix: Dict[str, GoalCheckpointRule]


AGENT_TEAM_CATALOG: List[AgentCatalogEntry] = [
    {
        "agent_key": "strategy_orchestrator",
        "agent_type": "StrategyOrchestrator",
        "role": "Team Lead",
        "responsibilities": [
            "Coordinate all marketing agents and delegate work",
            "Synthesize a unified daily strategy across channels",
            "Prioritize actions based on impact and urgency",
            "Maintain safety constraints and request approval when needed",
        ],
        "tools": [
            "market_signal_detector",
            "google_trends_fetcher",
            "agent_coordinator",
            "performance_analyzer",
            "strategy_synthesizer",
            "task_delegator",
        ],
        "defaults": {
            "display_name_template": "{website_name} Marketing Team Lead",
            "enabled": True,
            "schedule": {"mode": "on_demand"},
            "system_prompt_template": (
                "You are the Marketing Strategy Orchestrator for {website_name}.\n\n"
                "Mission: coordinate the AI marketing team to help {website_name} win in digital marketing.\n\n"
                "Non-negotiables:\n"
                "- Delegate tasks to specialists using the available team tools.\n"
                "- Keep outputs practical for non-technical users.\n"
                "- Maintain safety constraints and request approval for high-risk actions.\n\n"
                "Context you may receive:\n"
                "- website_url, brand_voice, target_audience, competitors, content pillars\n\n"
                "Output style:\n"
                "- Provide a concise plan with priorities, expected outcomes, and next steps."
            ),
            "task_prompt_template": (
                "Task: Create a unified marketing plan for today.\n"
                "Use the provided context and delegate specialized work when needed.\n\n"
                "Return JSON with:\n"
                "{\n"
                "  \"summary\": string,\n"
                "  \"priorities\": [string],\n"
                "  \"delegations\": [{\"agent\": string, \"task\": string}],\n"
                "  \"next_actions\": [{\"title\": string, \"why\": string, \"expected_outcome\": string, \"risk_level\": \"low\"|\"medium\"|\"high\"}]\n"
                "}\n"
            ),
        },
    },
    {
        "agent_key": "content_strategist",
        "agent_type": "content_strategist",
        "role": "Content Strategist",
        "responsibilities": [
            "Analyze content performance and engagement signals",
            "Identify content gaps using semantic and sitemap analysis",
            "Optimize content for clarity, SEO, and conversions",
            "Track performance over time and recommend next actions",
        ],
        "tools": [
            "content_analyzer",
            "semantic_gap_detector",
            "content_optimizer",
            "performance_tracker",
            "sitemap_analyzer",
        ],
        "defaults": {
            "display_name_template": "{website_name} Content Strategist",
            "enabled": True,
            "schedule": {"mode": "weekly", "days": ["mon"], "time": "09:00"},
            "system_prompt_template": (
                "You are the Content Strategy Agent for {website_name}.\n\n"
                "Mission: help {website_name} publish content that matches the brand voice and grows traffic.\n\n"
                "Operating principles:\n"
                "- Be specific, actionable, and non-technical.\n"
                "- Prefer high-impact, low-effort recommendations first.\n"
                "- Maintain brand consistency.\n\n"
                "When you respond, include:\n"
                "- What to do, why it matters, and what success looks like."
            ),
            "task_prompt_template": (
                "Task: Propose the next 5 content actions for {website_name}.\n"
                "Inputs may include: website analysis, competitors, content pillars, recent results.\n\n"
                "Return JSON with:\n"
                "{\n"
                "  \"actions\": [{\"title\": string, \"why\": string, \"outline\": [string], \"cta\": string, \"risk_level\": \"low\"|\"medium\"|\"high\"}],\n"
                "  \"notes\": [string]\n"
                "}\n"
            ),
        },
    },
    {
        "agent_key": "competitor_analyst",
        "agent_type": "competitor_analyst",
        "role": "Competitor Analyst",
        "responsibilities": [
            "Monitor competitor strategy and positioning using SIF",
            "Assess threats and opportunities from competitor moves",
            "Generate counter-strategy recommendations",
            "Execute safe response actions (with approvals when needed)",
        ],
        "tools": [
            "competitor_monitor",
            "threat_analyzer",
            "response_generator",
            "strategy_executor",
        ],
        "defaults": {
            "display_name_template": "{website_name} Competitor Analyst",
            "enabled": True,
            "schedule": {"mode": "weekly", "days": ["wed"], "time": "10:00"},
            "system_prompt_template": (
                "You are the Competitor Response Agent for {website_name}.\n\n"
                "Mission: monitor competitor moves and translate them into clear actions for {website_name}.\n\n"
                "Rules:\n"
                "- Use semantic insights to avoid guesswork.\n"
                "- Avoid panic. Prioritize only meaningful threats.\n"
                "- Keep outputs concise and actionable."
            ),
            "task_prompt_template": (
                "Task: Summarize competitor moves and recommend responses.\n\n"
                "Return JSON with:\n"
                "{\n"
                "  \"threat_level\": \"low\"|\"medium\"|\"high\",\n"
                "  \"signals\": [string],\n"
                "  \"responses\": [{\"title\": string, \"why\": string, \"expected_outcome\": string, \"risk_level\": \"low\"|\"medium\"|\"high\"}]\n"
                "}\n"
            ),
        },
    },
    {
        "agent_key": "seo_specialist",
        "agent_type": "seo_specialist",
        "role": "SEO Specialist",
        "responsibilities": [
            "Audit technical SEO and prioritize fixes by impact",
            "Generate safe SEO fixes and improvements",
            "Adjust keyword strategy based on data and trends",
            "Validate changes against safety and quality constraints",
        ],
        "tools": [
            "seo_auditor",
            "issue_prioritizer",
            "auto_fix_executor",
            "strategy_generator",
            "query_seo_knowledge_base",
        ],
        "defaults": {
            "display_name_template": "{website_name} SEO Specialist",
            "enabled": True,
            "schedule": {"mode": "weekly", "days": ["fri"], "time": "11:00"},
            "system_prompt_template": (
                "You are the SEO Optimization Agent for {website_name}.\n\n"
                "Mission: continuously improve technical SEO and on-page basics while preserving user experience.\n\n"
                "Rules:\n"
                "- Prioritize high-impact, low-risk fixes.\n"
                "- Explain recommendations in simple language.\n"
                "- If an action is risky, require approval."
            ),
            "task_prompt_template": (
                "Task: Produce a weekly SEO fix list for {website_name}.\n\n"
                "Return JSON with:\n"
                "{\n"
                "  \"fixes\": [{\"title\": string, \"why\": string, \"steps\": [string], \"risk_level\": \"low\"|\"medium\"|\"high\"}],\n"
                "  \"metrics_to_watch\": [string]\n"
                "}\n"
            ),
        },
    },
    {
        "agent_key": "social_media_manager",
        "agent_type": "social_media_manager",
        "role": "Social Media Manager",
        "responsibilities": [
            "Monitor social trends and identify opportunities",
            "Adapt content for platform-specific distribution",
            "Optimize engagement signals (timing, hooks, hashtags)",
            "Coordinate distribution safely (with approvals when needed)",
        ],
        "tools": [
            "social_monitor",
            "content_adapter",
            "engagement_optimizer",
            "distribution_manager",
        ],
        "defaults": {
            "display_name_template": "{website_name} Social Media Manager",
            "enabled": True,
            "schedule": {"mode": "weekly", "days": ["tue"], "time": "09:30"},
            "system_prompt_template": (
                "You are the Social Media Manager for {website_name}.\n\n"
                "Mission: help {website_name} distribute content effectively without spam.\n\n"
                "Rules:\n"
                "- Adapt to platform norms.\n"
                "- Optimize for engagement ethically.\n"
                "- Keep messages aligned with brand voice."
            ),
            "task_prompt_template": (
                "Task: Suggest a weekly distribution plan for {website_name}.\n\n"
                "Return JSON with:\n"
                "{\n"
                "  \"posts\": [{\"platform\": string, \"post\": string, \"best_time\": string, \"hashtags\": [string]}],\n"
                "  \"notes\": [string]\n"
                "}\n"
            ),
        },
    },
]

GOAL_CONFIG_SCHEMA_VERSION = "1.0"

GOAL_REQUIRED_ROLES: Dict[GoalType, List[str]] = {
    "growth": ["Team Lead", "Content Strategist", "SEO Specialist", "Social Media Manager"],
    "defensive": ["Team Lead", "Competitor Analyst", "SEO Specialist"],
    "launch": ["Team Lead", "Content Strategist", "Social Media Manager", "Competitor Analyst"],
    "maintenance": ["Team Lead", "Content Strategist", "SEO Specialist"],
}

GOAL_CONFIGURATION_DEFAULTS: Dict[str, Any] = {
    "schema_version": GOAL_CONFIG_SCHEMA_VERSION,
    "objective": "",
    "required_roles": [],
    "prompt_overrides": {
        "system_prompt_prefix": "",
        "system_prompt_suffix": "",
        "task_prompt_prefix": "",
        "task_prompt_suffix": "",
    },
    "rule_matrix": {
        "pre_execution": {
            "checkpoint_policy": "standard",
            "require_approval": False,
            "escalation": "none",
        },
        "post_execution": {
            "checkpoint_policy": "standard",
            "require_approval": False,
            "escalation": "none",
        },
    },
}

GOAL_CONFIGURATION_CATALOG: Dict[GoalType, GoalConfiguration] = {
    "growth": {
        "schema_version": GOAL_CONFIG_SCHEMA_VERSION,
        "objective": "Accelerate audience and traffic growth with prioritized execution.",
        "required_roles": GOAL_REQUIRED_ROLES["growth"],
        "prompt_overrides": {
            "system_prompt_prefix": "Favor high-impact opportunities with measurable upside.",
            "task_prompt_prefix": "Prioritize experiments with fast learning loops.",
        },
        "rule_matrix": {
            "pre_execution": {"checkpoint_policy": "strict", "require_approval": False, "escalation": "team_lead"},
            "post_execution": {"checkpoint_policy": "strict", "require_approval": False, "escalation": "team_lead"},
        },
    },
    "defensive": {
        "schema_version": GOAL_CONFIG_SCHEMA_VERSION,
        "objective": "Protect rankings and market position against emerging threats.",
        "required_roles": GOAL_REQUIRED_ROLES["defensive"],
        "prompt_overrides": {
            "system_prompt_prefix": "Favor risk reduction and brand protection.",
            "task_prompt_suffix": "Highlight downside risk if actions are delayed.",
        },
        "rule_matrix": {
            "pre_execution": {"checkpoint_policy": "strict", "require_approval": True, "escalation": "security_review"},
            "post_execution": {"checkpoint_policy": "strict", "require_approval": True, "escalation": "security_review"},
        },
    },
    "launch": {
        "schema_version": GOAL_CONFIG_SCHEMA_VERSION,
        "objective": "Coordinate go-to-market execution with rapid cross-channel alignment.",
        "required_roles": GOAL_REQUIRED_ROLES["launch"],
        "prompt_overrides": {
            "system_prompt_prefix": "Coordinate launch-critical actions first.",
            "task_prompt_prefix": "Sequence actions by launch dependencies.",
        },
        "rule_matrix": {
            "pre_execution": {"checkpoint_policy": "strict", "require_approval": True, "escalation": "team_lead"},
            "post_execution": {"checkpoint_policy": "standard", "require_approval": False, "escalation": "none"},
        },
    },
    "maintenance": {
        "schema_version": GOAL_CONFIG_SCHEMA_VERSION,
        "objective": "Sustain baseline performance with reliable weekly optimization.",
        "required_roles": GOAL_REQUIRED_ROLES["maintenance"],
        "prompt_overrides": {},
        "rule_matrix": {
            "pre_execution": {"checkpoint_policy": "standard", "require_approval": False, "escalation": "none"},
            "post_execution": {"checkpoint_policy": "standard", "require_approval": False, "escalation": "none"},
        },
    },
}


def _deep_merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def validate_goal_override_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    override_payload = payload or {}
    if not isinstance(override_payload, dict):
        raise ValueError("Goal override payload must be a dictionary.")

    allowed_root_keys = {"schema_version", "objective", "required_roles", "prompt_overrides", "rule_matrix"}
    unknown_root_keys = set(override_payload.keys()) - allowed_root_keys
    if unknown_root_keys:
        raise ValueError(f"Unsupported goal override fields: {sorted(unknown_root_keys)}")

    if "schema_version" in override_payload and not isinstance(override_payload["schema_version"], str):
        raise ValueError("schema_version must be a string.")
    if "objective" in override_payload and not isinstance(override_payload["objective"], str):
        raise ValueError("objective must be a string.")
    if "required_roles" in override_payload:
        roles = override_payload["required_roles"]
        if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
            raise ValueError("required_roles must be a list of strings.")
    if "prompt_overrides" in override_payload and not isinstance(override_payload["prompt_overrides"], dict):
        raise ValueError("prompt_overrides must be a dictionary.")
    if "rule_matrix" in override_payload and not isinstance(override_payload["rule_matrix"], dict):
        raise ValueError("rule_matrix must be a dictionary.")

    return override_payload


def get_goal_configuration(goal_type: str, override_payload: Optional[Dict[str, Any]] = None) -> GoalConfiguration:
    goal_key = (goal_type or "").strip().lower()
    base = GOAL_CONFIGURATION_CATALOG.get(goal_key) or GOAL_CONFIGURATION_CATALOG["maintenance"]
    validated_override = validate_goal_override_payload(override_payload)
    merged = _deep_merge_dict(_deep_merge_dict(GOAL_CONFIGURATION_DEFAULTS, base), validated_override)
    return merged


def get_agent_catalog_entry(agent_key: str) -> Optional[AgentCatalogEntry]:
    agent_key_value = (agent_key or "").strip()
    for entry in AGENT_TEAM_CATALOG:
        if entry.get("agent_key") == agent_key_value:
            return entry
    return None
