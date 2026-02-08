import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  SemanticHealthMetric, 
  CompetitorSemanticSnapshot, 
  ContentSemanticInsight,
  SemanticDashboardData 
} from '../api/semanticDashboard';
import { semanticDashboardAPI } from '../api/semanticDashboard';

export interface SemanticDashboardStore {
  // State
  semanticHealth: SemanticHealthMetric | null;
  competitorSnapshots: CompetitorSemanticSnapshot[];
  contentInsights: ContentSemanticInsight[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  monitoringStatus: 'active' | 'inactive';

  // Actions
  setSemanticHealth: (health: SemanticHealthMetric | null) => void;
  setCompetitorSnapshots: (snapshots: CompetitorSemanticSnapshot[]) => void;
  setContentInsights: (insights: ContentSemanticInsight[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setLastUpdated: (timestamp: string | null) => void;
  setMonitoringStatus: (status: 'active' | 'inactive') => void;

  // Async actions
  fetchSemanticHealth: () => Promise<void>;
  fetchCompetitorSnapshots: () => Promise<void>;
  fetchContentInsights: () => Promise<void>;
  fetchAllSemanticData: () => Promise<void>;
  refreshSemanticAnalysis: () => Promise<void>;

  // Utility functions
  getHealthStatusColor: (status: string) => string;
  getInsightTypeColor: (type: string) => string;
  getConfidenceColor: (score: number) => string;
}

export const useSemanticDashboardStore = create<SemanticDashboardStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      semanticHealth: null,
      competitorSnapshots: [],
      contentInsights: [],
      loading: false,
      error: null,
      lastUpdated: null,
      monitoringStatus: 'inactive',

      // Actions
      setSemanticHealth: (health) => set({ semanticHealth: health }),
      setCompetitorSnapshots: (snapshots) => set({ competitorSnapshots: snapshots }),
      setContentInsights: (insights) => set({ contentInsights: insights }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      setLastUpdated: (timestamp) => set({ lastUpdated: timestamp }),
      setMonitoringStatus: (status) => set({ monitoringStatus: status }),

      // Fetch semantic health metrics
      fetchSemanticHealth: async () => {
        try {
          set({ loading: true, error: null });
          const health = await semanticDashboardAPI.getSemanticHealth();
          set({ 
            semanticHealth: health, 
            lastUpdated: new Date().toISOString(),
            monitoringStatus: 'active'
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch semantic health';
          set({ error: errorMessage });
          console.error('Error fetching semantic health:', error);
        } finally {
          set({ loading: false });
        }
      },

      // Fetch competitor snapshots
      fetchCompetitorSnapshots: async () => {
        try {
          set({ loading: true, error: null });
          const snapshots = await semanticDashboardAPI.getCompetitorSnapshots();
          set({ competitorSnapshots: snapshots, lastUpdated: new Date().toISOString() });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch competitor snapshots';
          set({ error: errorMessage });
          console.error('Error fetching competitor snapshots:', error);
        } finally {
          set({ loading: false });
        }
      },

      // Fetch content insights
      fetchContentInsights: async () => {
        try {
          set({ loading: true, error: null });
          const insights = await semanticDashboardAPI.getContentInsights();
          set({ contentInsights: insights, lastUpdated: new Date().toISOString() });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch content insights';
          set({ error: errorMessage });
          console.error('Error fetching content insights:', error);
        } finally {
          set({ loading: false });
        }
      },

      // Fetch all semantic data
      fetchAllSemanticData: async () => {
        try {
          set({ loading: true, error: null });
          
          // Fetch all data in parallel
          const [health, snapshots, insights] = await Promise.all([
            semanticDashboardAPI.getSemanticHealth(),
            semanticDashboardAPI.getCompetitorSnapshots(),
            semanticDashboardAPI.getContentInsights()
          ]);

          set({ 
            semanticHealth: health,
            competitorSnapshots: snapshots,
            contentInsights: insights,
            lastUpdated: new Date().toISOString(),
            monitoringStatus: 'active'
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to fetch semantic data';
          set({ error: errorMessage });
          console.error('Error fetching all semantic data:', error);
        } finally {
          set({ loading: false });
        }
      },

      // Refresh semantic analysis
      refreshSemanticAnalysis: async () => {
        try {
          set({ loading: true, error: null });
          await semanticDashboardAPI.refreshSemanticAnalysis();
          
          // Refetch all data after refresh
          await get().fetchAllSemanticData();
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to refresh semantic analysis';
          set({ error: errorMessage });
          console.error('Error refreshing semantic analysis:', error);
        } finally {
          set({ loading: false });
        }
      },

      // Utility functions
      getHealthStatusColor: (status: string) => {
        switch (status) {
          case 'healthy': return '#4CAF50';
          case 'warning': return '#FF9800';
          case 'critical': return '#F44336';
          default: return '#9E9E9E';
        }
      },

      getInsightTypeColor: (type: string) => {
        switch (type) {
          case 'opportunity': return '#4CAF50';
          case 'trend': return '#2196F3';
          case 'threat': return '#F44336';
          case 'gap': return '#FF9800';
          default: return '#9E9E9E';
        }
      },

      getConfidenceColor: (score: number) => {
        if (score >= 0.8) return '#4CAF50';
        if (score >= 0.6) return '#FF9800';
        return '#F44336';
      }
    }),
    {
      name: 'semantic-dashboard-store',
    }
  )
);