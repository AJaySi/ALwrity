import { create } from 'zustand';

import {
  BacklinkCoverageResponse,
  BacklinkModuleRecord,
  fetchBacklinkMigrationCoverage,
  fetchBacklinkModuleRegistry,
} from '../api/backlinkOutreachApi';

interface BacklinkOutreachStore {
  modules: BacklinkModuleRecord[];
  coverage: BacklinkCoverageResponse | null;
  isLoading: boolean;
  error: string | null;
  refreshBacklinkRegistry: () => Promise<void>;
}

export const useBacklinkOutreachStore = create<BacklinkOutreachStore>((set) => ({
  modules: [],
  coverage: null,
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
}));
