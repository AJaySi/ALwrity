import { ResearchConfig, DateRange } from "../../../services/blogWriterApi";
import { CreateProjectPayload, Knobs } from "../types";

export const DEFAULT_KNOBS: Knobs = {
  voice_emotion: "neutral",
  voice_speed: 1,
  resolution: "720p",
  scene_length_target: 45,
  sample_rate: 24000,
  bitrate: "standard",
};

export const allowedDateRanges: DateRange[] = [
  "last_week",
  "last_month",
  "last_3_months",
  "last_6_months",
  "last_year",
  "all_time",
];

export const sanitizeExaConfig = (
  exa?: CreateProjectPayload["knobs"] & any & { exa_suggested_config?: any } | any
): ResearchConfig | undefined => {
  if (!exa) return undefined;
  const cfg = exa as {
    exa_search_type?: "auto" | "keyword" | "neural";
    exa_category?: string;
    exa_include_domains?: string[];
    exa_exclude_domains?: string[];
    max_sources?: number;
    include_statistics?: boolean;
    date_range?: string;
  };

  const searchType: ResearchConfig["exa_search_type"] =
    cfg.exa_search_type && ["auto", "keyword", "neural"].includes(cfg.exa_search_type)
      ? cfg.exa_search_type
      : undefined;

  const dateRange: DateRange | undefined = cfg.date_range && allowedDateRanges.includes(cfg.date_range as DateRange)
    ? (cfg.date_range as DateRange)
    : undefined;

  return {
    provider: "exa",
    exa_search_type: searchType,
    exa_category: cfg.exa_category,
    exa_include_domains: cfg.exa_include_domains,
    exa_exclude_domains: cfg.exa_exclude_domains,
    max_sources: cfg.max_sources,
    include_statistics: cfg.include_statistics,
    date_range: dateRange,
  };
};

export const announceError = (setAnnouncement: (msg: string) => void, error: unknown) => {
  const message = error instanceof Error ? error.message : "Unexpected error";
  setAnnouncement(message);
};

export const getStepLabel = (step: string | null): string => {
  switch (step) {
    case "analysis":
      return "Analysis";
    case "research":
      return "Research";
    case "script":
      return "Script Editing";
    case "render":
      return "Rendering";
    default:
      return "Unknown";
  }
};

