import { create } from 'zustand';

import {
  BacklinkCampaignRecord,
  BacklinkCoverageResponse,
  BacklinkModuleRecord,
  createBacklinkCampaign,
  fetchBacklinkMigrationCoverage,
  fetchBacklinkModuleRegistry,
  listBacklinkCampaigns,
} from '../api/backlinkOutreachApi';

interface BacklinkOutreachStore {
  modules: BacklinkModuleRecord[];
  coverage: BacklinkCoverageResponse | null;
  campaigns: BacklinkCampaignRecord[];
  isLoading: boolean;
  error: string | null;
  refreshBacklinkRegistry: () => Promise<void>;
  fetchCampaigns: (userId: string, workspaceId: string) => Promise<void>;
  createCampaign: (userId: string, workspaceId: string, name: string) => Promise<string | null>;
}

export const useBacklinkOutreachStore = create<BacklinkOutreachStore>((set) => ({
  modules: [],
  coverage: null,
  campaigns: [],
  isLoading: false,
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
  fetchCampaigns: async (userId: string, workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await listBacklinkCampaigns(userId, workspaceId);
      set({ campaigns: response.campaigns, isLoading: false });
    } catch (error: any) {
      set({
        isLoading: false,
        error: error?.message ?? 'Failed to load campaigns',
      });
    }
  },
  createCampaign: async (userId: string, workspaceId: string, name: string) => {
    set({ isLoading: true, error: null });
    try {
      const result = await createBacklinkCampaign({ user_id: userId, workspace_id: workspaceId, name });
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
}));
