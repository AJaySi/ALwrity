import { apiClient, aiApiClient } from "./client";

export type AgentTeamCatalogEntry = {
  agent_key: string;
  agent_type?: string;
  role?: string;
  responsibilities: string[];
  tools: string[];
  defaults?: {
    display_name_template?: string;
    enabled?: boolean;
    schedule?: any;
  };
  profile?: {
    display_name?: string | null;
    enabled?: boolean;
    schedule?: any;
    notification_prefs?: any;
    tone?: any;
    system_prompt?: string | null;
    task_prompt_template?: string | null;
    reporting_prefs?: any;
    updated_at?: string | null;
  };
};

export async function getAgentTeam(): Promise<AgentTeamCatalogEntry[]> {
  const res = await apiClient.get("/api/agents/team");
  return res.data?.data?.agents || [];
}

export async function saveAgentProfile(agentKey: string, payload: Record<string, any>) {
  const res = await apiClient.post(`/api/agents/team/${encodeURIComponent(agentKey)}`, payload);
  return res.data?.data?.profile;
}

export async function aiOptimizeAgentProfile(
  agentKey: string,
  scope: "agent" | "system_prompt" | "task_prompt_template",
  contextCard: Record<string, any>
) {
  const res = await aiApiClient.post(`/api/agents/team/${encodeURIComponent(agentKey)}/ai-optimize`, {
    scope,
    context_card: contextCard,
  });
  return res.data?.data?.suggestion;
}

export async function previewAgentProfile(agentKey: string, contextCard: Record<string, any>) {
  const res = await aiApiClient.post(`/api/agents/team/${encodeURIComponent(agentKey)}/preview`, {
    context_card: contextCard,
  });
  return res.data?.data?.preview;
}

