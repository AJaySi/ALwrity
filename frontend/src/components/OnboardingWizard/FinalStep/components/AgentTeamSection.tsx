import React from "react";
import {
  Box,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Typography,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Stack,
  Divider,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import GroupIcon from "@mui/icons-material/Group";
import LockIcon from "@mui/icons-material/Lock";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import SaveIcon from "@mui/icons-material/Save";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import VisibilityIcon from "@mui/icons-material/Visibility";

import {
  aiOptimizeAgentProfile,
  previewAgentProfile,
  saveAgentProfile,
  type AgentTeamCatalogEntry,
} from "../../../../api/agentsTeam";

type Props = {
  websiteName: string;
  agents: AgentTeamCatalogEntry[];
  contextCard: Record<string, any>;
};

function resolveDisplayName(agent: AgentTeamCatalogEntry, websiteName: string) {
  const profileName = agent.profile?.display_name;
  if (profileName && profileName.trim()) return profileName.trim();
  const template = agent.defaults?.display_name_template || agent.role || agent.agent_key;
  return String(template).replace("{website_name}", websiteName || "Your");
}

function formatSchedule(schedule: any): string {
  if (!schedule) return "Not set";
  if (typeof schedule === "string") return schedule;
  const mode = schedule?.mode;
  if (!mode) return "Not set";
  if (mode === "on_demand") return "On-demand";
  if (mode === "weekly") {
    const days = Array.isArray(schedule?.days) ? schedule.days.join(", ") : "—";
    const time = schedule?.time || "—";
    return `Weekly • ${days} • ${time}`;
  }
  if (mode === "daily") {
    const time = schedule?.time || "—";
    return `Daily • ${time}`;
  }
  return String(mode);
}

type Draft = {
  display_name: string;
  enabled: boolean;
  schedule: any;
  system_prompt: string;
  task_prompt_template: string;
};

function getDefaultSystemPrompt(agent: AgentTeamCatalogEntry): string {
  return (agent.defaults as any)?.system_prompt_template || "";
}

function getDefaultTaskPrompt(agent: AgentTeamCatalogEntry): string {
  return (agent.defaults as any)?.task_prompt_template || "";
}

function lintDraft(agent: AgentTeamCatalogEntry, draft: Draft) {
  const warnings: string[] = [];

  const sys = (draft.system_prompt || "").trim();
  const task = (draft.task_prompt_template || "").trim();

  if (sys.length < 80) warnings.push("System prompt is very short. It may produce generic results.");
  if (task.length < 80) warnings.push("Task prompt template is very short. It may produce generic results.");
  if (sys.length > 15000) warnings.push("System prompt is very long. Consider shortening for reliability.");
  if (task.length > 15000) warnings.push("Task prompt template is very long. Consider shortening for reliability.");

  const combined = `${sys}\n${task}`.toLowerCase();
  if (combined.includes("api key") || combined.includes("apikey")) {
    warnings.push("Avoid asking for API keys inside prompts. ALwrity handles authentication separately.");
  }
  if (combined.includes("ignore previous") || combined.includes("ignore instructions")) {
    warnings.push("Avoid instructions that bypass safety or policy. They can cause unpredictable behavior.");
  }

  const tools = new Set((agent.tools || []).map((t) => String(t)));
  const toolRefRegex = /tool\s*:\s*([a-zA-Z0-9_]+)/g;
  const unknownTools = new Set<string>();
  for (const match of combined.matchAll(toolRefRegex)) {
    const name = match[1];
    if (name && !tools.has(name)) unknownTools.add(name);
  }
  if (unknownTools.size > 0) {
    warnings.push(`Prompt references unknown tools: ${Array.from(unknownTools).join(", ")}`);
  }

  const mode = draft.schedule?.mode;
  if (mode && !["on_demand", "weekly", "daily"].includes(String(mode))) {
    warnings.push("Schedule mode is not recognized. Use on_demand, weekly, or daily.");
  }

  return warnings;
}

const AgentTeamSection: React.FC<Props> = ({ websiteName, agents, contextCard }) => {
  const [drafts, setDrafts] = React.useState<Record<string, Draft>>({});
  const [savingKey, setSavingKey] = React.useState<string | null>(null);
  const [aiBusyKey, setAiBusyKey] = React.useState<string | null>(null);
  const [previewBusyKey, setPreviewBusyKey] = React.useState<string | null>(null);
  const [previewOpen, setPreviewOpen] = React.useState(false);
  const [previewTitle, setPreviewTitle] = React.useState("");
  const [previewData, setPreviewData] = React.useState<any>(null);
  const [aiSuggestionOpen, setAiSuggestionOpen] = React.useState(false);
  const [aiSuggestionTitle, setAiSuggestionTitle] = React.useState("");
  const [aiSuggestionData, setAiSuggestionData] = React.useState<any>(null);

  React.useEffect(() => {
    const next: Record<string, Draft> = {};
    for (const agent of agents) {
      const key = agent.agent_key;
      const displayName = resolveDisplayName(agent, websiteName);
      const enabled = agent.profile?.enabled ?? agent.defaults?.enabled ?? true;
      const schedule = agent.profile?.schedule ?? agent.defaults?.schedule ?? { mode: "on_demand" };
      const systemPrompt = agent.profile?.system_prompt ?? getDefaultSystemPrompt(agent);
      const taskPrompt = agent.profile?.task_prompt_template ?? getDefaultTaskPrompt(agent);
      next[key] = {
        display_name: displayName,
        enabled: Boolean(enabled),
        schedule,
        system_prompt: String(systemPrompt || ""),
        task_prompt_template: String(taskPrompt || ""),
      };
    }
    setDrafts(next);
  }, [agents, websiteName]);

  const setDraftField = (agentKey: string, patch: Partial<Draft>) => {
    setDrafts((prev) => ({ ...prev, [agentKey]: { ...(prev[agentKey] || ({} as Draft)), ...patch } }));
  };

  const handleSave = async (agent: AgentTeamCatalogEntry) => {
    const key = agent.agent_key;
    const draft = drafts[key];
    if (!draft) return;

    setSavingKey(key);
    try {
      await saveAgentProfile(key, {
        display_name: draft.display_name,
        enabled: draft.enabled,
        schedule: draft.schedule,
        system_prompt: draft.system_prompt,
        task_prompt_template: draft.task_prompt_template,
      });
    } finally {
      setSavingKey(null);
    }
  };

  const handleReset = async (agent: AgentTeamCatalogEntry) => {
    const key = agent.agent_key;
    const defaults: any = agent.defaults || {};
    const displayName = String(defaults.display_name_template || agent.role || key).replace("{website_name}", websiteName || "Your");
    setDraftField(key, {
      display_name: displayName,
      enabled: Boolean(defaults.enabled ?? true),
      schedule: defaults.schedule ?? { mode: "on_demand" },
      system_prompt: String(defaults.system_prompt_template || ""),
      task_prompt_template: String(defaults.task_prompt_template || ""),
    });

    setSavingKey(key);
    try {
      await saveAgentProfile(key, {
        display_name: null,
        schedule: null,
        system_prompt: null,
        task_prompt_template: null,
        enabled: Boolean(defaults.enabled ?? true),
      });
    } finally {
      setSavingKey(null);
    }
  };

  const handleAiOptimize = async (agent: AgentTeamCatalogEntry) => {
    const key = agent.agent_key;
    setAiBusyKey(key);
    try {
      const suggestion = await aiOptimizeAgentProfile(key, "agent", contextCard);
      setAiSuggestionTitle(resolveDisplayName(agent, websiteName));
      setAiSuggestionData(suggestion);
      setAiSuggestionOpen(true);

      const parsed = typeof suggestion === "string" ? safeJsonParse(suggestion) : suggestion;
      if (parsed && typeof parsed === "object") {
        const patch: Partial<Draft> = {};
        if (typeof parsed.display_name === "string") patch.display_name = parsed.display_name;
        if (typeof parsed.enabled === "boolean") patch.enabled = parsed.enabled;
        if (parsed.schedule && typeof parsed.schedule === "object") patch.schedule = parsed.schedule;
        if (typeof parsed.system_prompt === "string") patch.system_prompt = parsed.system_prompt;
        if (typeof parsed.task_prompt_template === "string") patch.task_prompt_template = parsed.task_prompt_template;
        if (Object.keys(patch).length > 0) setDraftField(key, patch);
      }
    } finally {
      setAiBusyKey(null);
    }
  };

  const handlePreview = async (agent: AgentTeamCatalogEntry) => {
    const key = agent.agent_key;
    setPreviewBusyKey(key);
    try {
      const preview = await previewAgentProfile(key, contextCard);
      setPreviewTitle(resolveDisplayName(agent, websiteName));
      setPreviewData(preview);
      setPreviewOpen(true);
    } finally {
      setPreviewBusyKey(null);
    }
  };

  return (
    <Paper sx={{ mt: 3, p: 3, borderRadius: 3 }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
        <GroupIcon />
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          Meet {websiteName || "Your"} AI Marketing Team
        </Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        These agents work together to help you plan, execute, and improve your digital marketing. Tools and responsibilities are locked for safety and reliability.
      </Typography>

      <Stack spacing={1.5}>
        {agents.map((agent) => {
          const displayName = resolveDisplayName(agent, websiteName);
          const scheduleText = formatSchedule(agent.profile?.schedule ?? agent.defaults?.schedule);
          const draft = drafts[agent.agent_key];
          const warnings = draft ? lintDraft(agent, draft) : [];

          return (
            <Accordion key={agent.agent_key} disableGutters elevation={0} sx={{ borderRadius: 2, border: "1px solid rgba(0,0,0,0.08)" }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%", gap: 2 }}>
                  <Box sx={{ minWidth: 0 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.2 }} noWrap>
                      {displayName}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {agent.role || agent.agent_key} • {scheduleText}
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1} sx={{ flexShrink: 0 }}>
                    <Chip size="small" icon={<LockIcon />} label="Tools locked" variant="outlined" />
                    <Chip size="small" icon={<LockIcon />} label="Responsibilities locked" variant="outlined" />
                  </Stack>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<AutoFixHighIcon />}
                      disabled={aiBusyKey === agent.agent_key}
                      onClick={() => handleAiOptimize(agent)}
                      sx={{ textTransform: "none" }}
                    >
                      AI Optimize
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<VisibilityIcon />}
                      disabled={previewBusyKey === agent.agent_key}
                      onClick={() => handlePreview(agent)}
                      sx={{ textTransform: "none" }}
                    >
                      Preview
                    </Button>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<SaveIcon />}
                      disabled={!draft || savingKey === agent.agent_key}
                      onClick={() => handleSave(agent)}
                      sx={{ textTransform: "none" }}
                    >
                      Save
                    </Button>
                    <Button
                      size="small"
                      variant="text"
                      startIcon={<RestartAltIcon />}
                      disabled={savingKey === agent.agent_key}
                      onClick={() => handleReset(agent)}
                      sx={{ textTransform: "none" }}
                    >
                      Reset
                    </Button>
                  </Box>

                  {warnings.length > 0 && (
                    <Alert severity="warning" sx={{ borderRadius: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
                        Suggestions to improve reliability
                      </Typography>
                      <Box component="ul" sx={{ pl: 2, m: 0 }}>
                        {warnings.map((w, idx) => (
                          <li key={idx}>
                            <Typography variant="body2">{w}</Typography>
                          </li>
                        ))}
                      </Box>
                    </Alert>
                  )}

                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                      Responsibilities
                    </Typography>
                    <Stack spacing={0.5}>
                      {(agent.responsibilities || []).map((r, idx) => (
                        <Typography key={idx} variant="body2">
                          • {r}
                        </Typography>
                      ))}
                    </Stack>
                  </Box>

                  <Divider />

                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                      Tools
                    </Typography>
                    <Stack direction="row" flexWrap="wrap" gap={1}>
                      {(agent.tools || []).map((t) => (
                        <Chip key={t} size="small" label={t} />
                      ))}
                    </Stack>
                  </Box>

                  <Divider />

                  {draft && (
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                        Editable settings
                      </Typography>
                      <Stack spacing={2}>
                        <TextField
                          label="Display name"
                          value={draft.display_name}
                          onChange={(e) => setDraftField(agent.agent_key, { display_name: e.target.value })}
                          fullWidth
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={draft.enabled}
                              onChange={(e) => setDraftField(agent.agent_key, { enabled: e.target.checked })}
                            />
                          }
                          label="Enabled"
                        />

                        <FormControl fullWidth>
                          <InputLabel>Schedule</InputLabel>
                          <Select
                            label="Schedule"
                            value={draft.schedule?.mode || "on_demand"}
                            onChange={(e) => setDraftField(agent.agent_key, { schedule: { ...(draft.schedule || {}), mode: e.target.value } })}
                          >
                            <MenuItem value="on_demand">On-demand</MenuItem>
                            <MenuItem value="weekly">Weekly</MenuItem>
                            <MenuItem value="daily">Daily</MenuItem>
                          </Select>
                        </FormControl>

                        {draft.schedule?.mode === "weekly" && (
                          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                            <TextField
                              label="Days (comma separated)"
                              value={Array.isArray(draft.schedule?.days) ? draft.schedule.days.join(", ") : ""}
                              onChange={(e) =>
                                setDraftField(agent.agent_key, {
                                  schedule: {
                                    ...(draft.schedule || {}),
                                    days: e.target.value
                                      .split(",")
                                      .map((d) => d.trim())
                                      .filter(Boolean),
                                  },
                                })
                              }
                              fullWidth
                            />
                            <TextField
                              label="Time (HH:MM)"
                              value={draft.schedule?.time || ""}
                              onChange={(e) => setDraftField(agent.agent_key, { schedule: { ...(draft.schedule || {}), time: e.target.value } })}
                              fullWidth
                            />
                          </Stack>
                        )}

                        {draft.schedule?.mode === "daily" && (
                          <TextField
                            label="Time (HH:MM)"
                            value={draft.schedule?.time || ""}
                            onChange={(e) => setDraftField(agent.agent_key, { schedule: { ...(draft.schedule || {}), time: e.target.value } })}
                            fullWidth
                          />
                        )}

                        <TextField
                          label="System prompt"
                          value={draft.system_prompt}
                          onChange={(e) => setDraftField(agent.agent_key, { system_prompt: e.target.value })}
                          multiline
                          minRows={6}
                          fullWidth
                        />
                        <TextField
                          label="Task prompt template"
                          value={draft.task_prompt_template}
                          onChange={(e) => setDraftField(agent.agent_key, { task_prompt_template: e.target.value })}
                          multiline
                          minRows={6}
                          fullWidth
                        />
                      </Stack>
                    </Box>
                  )}
                </Stack>
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Stack>

      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Preview: {previewTitle}</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
            {typeof previewData === "string" ? previewData : JSON.stringify(previewData, null, 2)}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)} sx={{ textTransform: "none" }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={aiSuggestionOpen} onClose={() => setAiSuggestionOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>AI Optimize suggestion: {aiSuggestionTitle}</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
            {typeof aiSuggestionData === "string" ? aiSuggestionData : JSON.stringify(aiSuggestionData, null, 2)}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiSuggestionOpen(false)} sx={{ textTransform: "none" }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default AgentTeamSection;

function safeJsonParse(raw: string): any {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}
