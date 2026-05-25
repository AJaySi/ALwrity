import { create } from 'zustand';

import {
  BacklinkCampaignRecord,
  BacklinkCoverageResponse,
  BacklinkModuleRecord,
  CampaignDetailResponse,
  CampaignAnalyticsResponse,
  createBacklinkCampaign,
  discoverDeepBacklinkOpportunities,
  EnrichedOpportunity,
  fetchBacklinkMigrationCoverage,
  fetchBacklinkModuleRegistry,
  fetchCampaignDetail,
  fetchCampaignAnalytics,
  FollowUpScheduleRecord,
  LeadRecord,
  listBacklinkCampaigns,
  sendOutreach,
  SendOutreachRequest,
  SendOutreachResponse,
  OutreachAttemptRecord,
  fetchCampaignAttempts,
  OutreachReplyRecord,
  fetchCampaignReplies,
  fetchFollowUps as apiFetchFollowUps,
} from '../api/backlinkOutreachApi';

async function withRetry<T>(fn: () => Promise<T>, retries = 1, delayMs = 1000): Promise<T> {
  let lastErr: any;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (err: any) {
      lastErr = err;
      if (attempt < retries && (!err?.response || err.response.status >= 500)) {
        await new Promise(r => setTimeout(r, delayMs * (attempt + 1)));
        continue;
      }
      throw err;
    }
  }
  throw lastErr;
}

interface BacklinkOutreachStore {
  modules: BacklinkModuleRecord[];
  coverage: BacklinkCoverageResponse | null;
  campaigns: BacklinkCampaignRecord[];
  selectedCampaign: CampaignDetailResponse | null;
  discoveredOpportunities: EnrichedOpportunity[];
  leads: LeadRecord[];
  attempts: OutreachAttemptRecord[];
  replies: OutreachReplyRecord[];
  followups: FollowUpScheduleRecord[];
  analytics: CampaignAnalyticsResponse | null;
  isLoading: boolean;
  isDiscovering: boolean;
  isAttemptsLoading: boolean;
  isRepliesLoading: boolean;
  isAnalyticsLoading: boolean;
  error: string | null;
  refreshBacklinkRegistry: () => Promise<void>;
  fetchCampaigns: (workspaceId: string) => Promise<void>;
  createCampaign: (workspaceId: string, name: string) => Promise<string | null>;
  selectCampaign: (campaignId: string) => Promise<void>;
  deepDiscover: (keyword: string, maxResults?: number, campaignId?: string) => Promise<EnrichedOpportunity[]>;
  clearDiscoveries: () => void;
  sendOutreachEmail: (req: SendOutreachRequest) => Promise<SendOutreachResponse | null>;
  fetchAttempts: (campaignId: string) => Promise<void>;
  fetchReplies: (campaignId: string) => Promise<void>;
  fetchFollowUps: (campaignId: string) => Promise<void>;
  fetchAnalytics: (campaignId: string) => Promise<void>;
}

export const useBacklinkOutreachStore = create<BacklinkOutreachStore>((set) => ({
  modules: [],
  coverage: null,
  campaigns: [],
  selectedCampaign: null,
  discoveredOpportunities: [],
  leads: [],
  attempts: [],
  replies: [],
  followups: [],
  analytics: null,
  isLoading: false,
  isDiscovering: false,
  isAttemptsLoading: false,
  isRepliesLoading: false,
  isAnalyticsLoading: false,
  error: null,
  refreshBacklinkRegistry: async () => {
    set({ isLoading: true, error: null });
    try {
      const [registryPayload, coveragePayload] = await Promise.all([
        fetchBacklinkModuleRegistry(),
        fetchBacklinkMigrationCoverage(),
      ]);
      set({ modules: registryPayload.modules, coverage: coveragePayload, isLoading: false });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error?.message ?? 'Failed to load backlink module registry',
      });
    }
  },
  fetchCampaigns: async (workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await withRetry(() => listBacklinkCampaigns(workspaceId));
      set({ campaigns: response.campaigns, isLoading: false });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error?.message ?? 'Failed to load campaigns',
      });
    }
  },
  createCampaign: async (workspaceId: string, name: string) => {
    set({ isLoading: true, error: null });
    try {
      const result = await createBacklinkCampaign({ workspace_id: workspaceId, name });
      set((state) => ({
        campaigns: [...state.campaigns, { campaign_id: result.campaign_id, name: result.name, status: result.status }],
        isLoading: false,
      }));
      return result.campaign_id;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error?.message ?? 'Failed to create campaign',
      });
      return null;
    }
  },
  selectCampaign: async (campaignId: string) => {
    set({ isLoading: true, error: null });
    try {
      const detail = await withRetry(() => fetchCampaignDetail(campaignId));
      set({ selectedCampaign: detail, leads: detail.leads, isLoading: false });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error?.message ?? 'Failed to load campaign',
      });
    }
  },
  deepDiscover: async (keyword: string, maxResults?: number, campaignId?: string) => {
    set({ isDiscovering: true, error: null });
    try {
      const result = await discoverDeepBacklinkOpportunities({ keyword, max_results: maxResults, campaign_id: campaignId });
      set({ discoveredOpportunities: result.opportunities, isDiscovering: false });
      return result.opportunities;
    } catch (error: any) {
      set({
        isDiscovering: false,
        error: error?.message ?? 'Discovery failed',
      });
      return [];
    }
  },
  clearDiscoveries: () => set({ discoveredOpportunities: [] }),
  sendOutreachEmail: async (req: SendOutreachRequest) => {
    set({ isLoading: true, error: null });
    try {
      const result = await sendOutreach(req);
      set({ isLoading: false });
      return result;
    } catch (error: any) {
      set({
        isLoading: false,
        error: error?.message ?? 'Failed to send outreach',
      });
      return null;
    }
  },
  fetchAttempts: async (campaignId: string) => {
    set({ isAttemptsLoading: true, error: null });
    try {
      const result = await withRetry(() => fetchCampaignAttempts(campaignId));
      set({ attempts: result.attempts, isAttemptsLoading: false });
    } catch (error: any) {
      set({
        isAttemptsLoading: false,
        error: error?.message ?? 'Failed to load attempts',
      });
    }
  },
  fetchReplies: async (campaignId: string) => {
    set({ isRepliesLoading: true, error: null });
    try {
      const result = await withRetry(() => fetchCampaignReplies(campaignId));
      set({ replies: result.replies, isRepliesLoading: false });
    } catch (error: any) {
      set({
        isRepliesLoading: false,
        error: error?.message ?? 'Failed to load replies',
      });
    }
  },
  fetchFollowUps: async (campaignId: string) => {
    set({ error: null });
    try {
      const result = await withRetry(() => apiFetchFollowUps(campaignId));
      set({ followups: result.followups });
    } catch (error: any) {
      set({ error: error?.message ?? 'Failed to load follow-ups' });
    }
  },
  fetchAnalytics: async (campaignId: string) => {
    set({ isAnalyticsLoading: true, error: null });
    try {
      const result = await withRetry(() => fetchCampaignAnalytics(campaignId));
      set({ analytics: result, isAnalyticsLoading: false });
    } catch (error: any) {
      set({
        isAnalyticsLoading: false,
        error: error?.message ?? 'Failed to load analytics',
      });
    }
  },
}));