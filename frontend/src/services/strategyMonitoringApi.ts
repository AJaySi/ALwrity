import { apiClient, aiApiClient } from '../api/client';
import { useState } from 'react';

export interface MonitoringTask {
  component: string;
  title: string;
  description: string;
  assignee: 'ALwrity' | 'Human';
  frequency: string;
  metric: string;
  measurementMethod: string;
  successCriteria: string;
  alertThreshold: string;
  actionableInsights: string;
}

export interface MonitoringComponent {
  name: string;
  icon: string;
  tasks: MonitoringTask[];
}

export interface MonitoringPlan {
  totalTasks: number;
  alwrityTasks: number;
  humanTasks: number;
  metricsCount: number;
  monitoringTasks: MonitoringTask[];
  monitoringSchedule?: any;
  successMetrics?: any;
  metadata?: any;
}

export const strategyMonitoringApi = {
  /**
   * Generate monitoring plan for a strategy
   */
  async generateMonitoringPlan(strategyId: number): Promise<{ success: boolean; data: MonitoringPlan; message: string }> {
    try {
      const response = await apiClient.post(`/api/content-planning/strategy/${strategyId}/generate-monitoring-plan`);
      return response.data;
    } catch (error: any) {
      console.error('Error generating monitoring plan:', error);
      throw new Error(error.response?.data?.detail || 'Failed to generate monitoring plan');
    }
  },

  /**
   * Activate strategy with monitoring plan
   */
  async activateStrategyWithMonitoring(strategyId: number, monitoringPlan: MonitoringPlan): Promise<{ success: boolean; message: string; strategy_id: number }> {
    try {
      const response = await apiClient.post(`/api/content-planning/strategy/${strategyId}/activate-with-monitoring`, monitoringPlan);
      return response.data;
    } catch (error: any) {
      console.error('Error activating strategy with monitoring:', error);
      throw new Error(error.response?.data?.detail || 'Failed to activate strategy with monitoring');
    }
  },

  /**
   * Get monitoring plan for a strategy
   */
  async getMonitoringPlan(strategyId: number): Promise<{ success: boolean; data: any }> {
    try {
      const response = await apiClient.get(`/api/content-planning/strategy/${strategyId}/monitoring-plan`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting monitoring plan:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get monitoring plan');
    }
  },

  /**
   * Update monitoring plan
   */
  async updateMonitoringPlan(strategyId: number, monitoringPlan: Partial<MonitoringPlan>): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.put(`/api/content-planning/strategy/${strategyId}/monitoring-plan`, monitoringPlan);
      return response.data;
    } catch (error: any) {
      console.error('Error updating monitoring plan:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update monitoring plan');
    }
  },

  /**
   * Get performance history for a strategy
   */
  async getPerformanceHistory(strategyId: number, days: number = 30): Promise<{ success: boolean; data: any }> {
    try {
      const response = await apiClient.get(`/api/content-planning/strategy/${strategyId}/performance-history?days=${days}`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting performance history:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get performance history');
    }
  },

  /**
   * Deactivate a strategy
   */
  async deactivateStrategy(strategyId: number, userId: number = 1): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post(`/api/content-planning/strategy/${strategyId}/deactivate`, { user_id: userId });
      return response.data;
    } catch (error: any) {
      console.error('Error deactivating strategy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to deactivate strategy');
    }
  },

  /**
   * Pause a strategy
   */
  async pauseStrategy(strategyId: number, userId: number = 1): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post(`/api/content-planning/strategy/${strategyId}/pause`, { user_id: userId });
      return response.data;
    } catch (error: any) {
      console.error('Error pausing strategy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to pause strategy');
    }
  },

  /**
   * Resume a strategy
   */
  async resumeStrategy(strategyId: number, userId: number = 1): Promise<{ success: boolean; message: string }> {
    try {
      const response = await apiClient.post(`/api/content-planning/strategy/${strategyId}/resume`, { user_id: userId });
      return response.data;
    } catch (error: any) {
      console.error('Error resuming strategy:', error);
      throw new Error(error.response?.data?.detail || 'Failed to resume strategy');
    }
  },

  /**
   * Get performance metrics for a strategy
   */
  async getPerformanceMetrics(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/strategy/${strategyId}/performance-metrics`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting performance metrics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get performance metrics');
    }
  },

  /**
   * Get trend data for a strategy
   */
  async getTrendData(strategyId: number, timeRange: string = '30d'): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await aiApiClient.get(`/api/content-planning/strategy/${strategyId}/trend-data?time_range=${timeRange}`);
      return response.data;
    } catch (error: any) {
      console.error('Error getting trend data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get trend data');
    }
  },

  // New API calls for transparency data
  async getTransparencyData(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/strategy/${strategyId}/transparency-data`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching transparency data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch transparency data');
    }
  },

  async getMonitoringTasks(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/strategy/${strategyId}/monitoring-tasks`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching monitoring tasks:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch monitoring tasks');
    }
  },

  async getDataFreshness(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/strategy/${strategyId}/data-freshness`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching data freshness:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch data freshness');
    }
  },

  // Quality Analysis API methods
  async getQualityAnalysis(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await aiApiClient.post(`/api/content-planning/quality-analysis/${strategyId}/analyze`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching quality analysis:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch quality analysis');
    }
  },

  async getQualityMetrics(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/quality-analysis/${strategyId}/metrics`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching quality metrics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch quality metrics');
    }
  },

  async getQualityRecommendations(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/quality-analysis/${strategyId}/recommendations`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching quality recommendations:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch quality recommendations');
    }
  },

  async getQualityDashboard(strategyId: number): Promise<{ success: boolean; data: any; message: string }> {
    try {
      const response = await apiClient.get(`/api/content-planning/quality-analysis/${strategyId}/dashboard`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching quality dashboard:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch quality dashboard');
    }
  }
};

// Hook for monitoring plan generation
export const useMonitoringPlanGeneration = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generatePlan = async (strategyId: number): Promise<MonitoringPlan> => {
    setIsGenerating(true);
    setError(null);
    
    try {
      const response = await strategyMonitoringApi.generateMonitoringPlan(strategyId);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  return { generatePlan, isGenerating, error };
};
