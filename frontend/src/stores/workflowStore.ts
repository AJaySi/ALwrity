import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  TodayTask, 
  DailyWorkflow, 
  WorkflowProgress, 
  UserWorkflowPreferences,
  NavigationState,
  WorkflowError
} from '../types/workflow';
import { taskWorkflowOrchestrator } from '../services/TaskWorkflowOrchestrator';

interface WorkflowState {
  // Current workflow state
  currentWorkflow: DailyWorkflow | null;
  workflowProgress: WorkflowProgress | null;
  navigationState: NavigationState | null;
  
  // User preferences
  userPreferences: UserWorkflowPreferences | null;
  
  // UI state
  isWorkflowModalOpen: boolean;
  isLoading: boolean;
  error: WorkflowError | null;
  
  // Actions
  generateDailyWorkflow: (userId: string, date?: string) => Promise<void>;
  startWorkflow: (workflowId: string) => Promise<void>;
  pauseWorkflow: (workflowId: string) => Promise<void>;
  stopWorkflow: (workflowId: string) => Promise<void>;
  completeTask: (taskId: string, completionData?: any) => Promise<void>;
  skipTask: (taskId: string) => Promise<void>;
  moveToNextTask: () => Promise<void>;
  moveToPreviousTask: () => Promise<void>;
  
  // UI actions
  openWorkflowModal: () => void;
  closeWorkflowModal: () => void;
  setError: (error: WorkflowError | null) => void;
  clearError: () => void;
  
  // Preferences
  updateUserPreferences: (preferences: Partial<UserWorkflowPreferences>) => void;
  
  // Utility actions
  refreshWorkflowProgress: () => void;
  getCurrentTask: () => TodayTask | null;
  getNextTask: () => TodayTask | null;
  isWorkflowComplete: () => boolean;
  getCompletionPercentage: () => number;
}

export const useWorkflowStore = create<WorkflowState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentWorkflow: null,
      workflowProgress: null,
      navigationState: null,
      userPreferences: null,
      isWorkflowModalOpen: false,
      isLoading: false,
      error: null,

      // Generate daily workflow
      generateDailyWorkflow: async (userId: string, date?: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const workflow = await taskWorkflowOrchestrator.generateDailyWorkflow(userId, date);
          const progress = taskWorkflowOrchestrator.getWorkflowProgress(workflow.id);
          const navigation = taskWorkflowOrchestrator.getNavigationState(workflow.id);
          
          set({
            currentWorkflow: workflow,
            workflowProgress: progress,
            navigationState: navigation,
            isLoading: false
          });
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Start workflow
      startWorkflow: async (workflowId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const workflow = await taskWorkflowOrchestrator.startWorkflow(workflowId);
          const progress = taskWorkflowOrchestrator.getWorkflowProgress(workflow.id);
          const navigation = taskWorkflowOrchestrator.getNavigationState(workflow.id);
          
          set({
            currentWorkflow: workflow,
            workflowProgress: progress,
            navigationState: navigation,
            isLoading: false
          });
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Pause workflow
      pauseWorkflow: async (workflowId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // For now, we'll just update the workflow status to paused
          // In a real implementation, this would call the orchestrator
          const currentWorkflow = get().currentWorkflow;
          if (currentWorkflow && currentWorkflow.id === workflowId) {
            const pausedWorkflow = {
              ...currentWorkflow,
              workflowStatus: 'paused' as const,
              pausedAt: new Date()
            };
            
            set({
              currentWorkflow: pausedWorkflow,
              isLoading: false
            });
          }
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Stop workflow
      stopWorkflow: async (workflowId: string) => {
        set({ isLoading: true, error: null });
        
        try {
          // For now, we'll just update the workflow status to stopped
          // In a real implementation, this would call the orchestrator
          const currentWorkflow = get().currentWorkflow;
          if (currentWorkflow && currentWorkflow.id === workflowId) {
            const stoppedWorkflow = {
              ...currentWorkflow,
              workflowStatus: 'stopped' as const,
              completedAt: new Date()
            };
            
            set({
              currentWorkflow: stoppedWorkflow,
              isLoading: false
            });
          }
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Complete task
      completeTask: async (taskId: string, completionData?: any) => {
        const { currentWorkflow } = get();
        if (!currentWorkflow) return;

        set({ isLoading: true, error: null });
        
        try {
          const progress = await taskWorkflowOrchestrator.completeTask(
            currentWorkflow.id, 
            taskId, 
            completionData
          );
          const navigation = taskWorkflowOrchestrator.getNavigationState(currentWorkflow.id);
          
          // Update current workflow
          const updatedWorkflow = taskWorkflowOrchestrator.getWorkflow(
            currentWorkflow.userId, 
            currentWorkflow.date
          );
          
          set({
            currentWorkflow: updatedWorkflow,
            workflowProgress: progress,
            navigationState: navigation,
            isLoading: false
          });
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Skip task
      skipTask: async (taskId: string) => {
        const { currentWorkflow } = get();
        if (!currentWorkflow) return;

        set({ isLoading: true, error: null });
        
        try {
          const progress = await taskWorkflowOrchestrator.skipTask(
            currentWorkflow.id, 
            taskId
          );
          const navigation = taskWorkflowOrchestrator.getNavigationState(currentWorkflow.id);
          
          // Update current workflow
          const updatedWorkflow = taskWorkflowOrchestrator.getWorkflow(
            currentWorkflow.userId, 
            currentWorkflow.date
          );
          
          set({
            currentWorkflow: updatedWorkflow,
            workflowProgress: progress,
            navigationState: navigation,
            isLoading: false
          });
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Move to next task
      moveToNextTask: async () => {
        const { currentWorkflow } = get();
        if (!currentWorkflow) return;

        set({ isLoading: true, error: null });
        
        try {
          await taskWorkflowOrchestrator.moveToNextTask(currentWorkflow.id);
          const progress = taskWorkflowOrchestrator.getWorkflowProgress(currentWorkflow.id);
          const navigation = taskWorkflowOrchestrator.getNavigationState(currentWorkflow.id);
          
          // Update current workflow
          const updatedWorkflow = taskWorkflowOrchestrator.getWorkflow(
            currentWorkflow.userId, 
            currentWorkflow.date
          );
          
          set({
            currentWorkflow: updatedWorkflow,
            workflowProgress: progress,
            navigationState: navigation,
            isLoading: false
          });
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // Move to previous task
      moveToPreviousTask: async () => {
        const { currentWorkflow } = get();
        if (!currentWorkflow) return;

        set({ isLoading: true, error: null });
        
        try {
          // This would need to be implemented in the orchestrator
          // For now, we'll just refresh the navigation state
          const navigation = taskWorkflowOrchestrator.getNavigationState(currentWorkflow.id);
          
          set({
            navigationState: navigation,
            isLoading: false
          });
        } catch (error) {
          const workflowError = error as WorkflowError;
          set({ 
            error: workflowError, 
            isLoading: false 
          });
        }
      },

      // UI actions
      openWorkflowModal: () => set({ isWorkflowModalOpen: true }),
      closeWorkflowModal: () => set({ isWorkflowModalOpen: false }),
      setError: (error: WorkflowError | null) => set({ error }),
      clearError: () => set({ error: null }),

      // Update user preferences
      updateUserPreferences: (preferences: Partial<UserWorkflowPreferences>) => {
        const { userPreferences } = get();
        set({
          userPreferences: {
            ...userPreferences,
            ...preferences
          } as UserWorkflowPreferences
        });
      },

      // Utility actions
      refreshWorkflowProgress: () => {
        const { currentWorkflow } = get();
        if (!currentWorkflow) return;

        try {
          const progress = taskWorkflowOrchestrator.getWorkflowProgress(currentWorkflow.id);
          const navigation = taskWorkflowOrchestrator.getNavigationState(currentWorkflow.id);
          
          set({
            workflowProgress: progress,
            navigationState: navigation
          });
        } catch (error) {
          console.warn('Failed to refresh workflow progress:', error);
        }
      },

      getCurrentTask: () => {
        const { navigationState } = get();
        return navigationState?.currentTask || null;
      },

      getNextTask: () => {
        const { navigationState } = get();
        return navigationState?.nextTask || null;
      },

      isWorkflowComplete: () => {
        const { workflowProgress } = get();
        return workflowProgress ? workflowProgress.completedTasks === workflowProgress.totalTasks : false;
      },

      getCompletionPercentage: () => {
        const { workflowProgress } = get();
        return workflowProgress?.completionPercentage || 0;
      }
    }),
    {
      name: 'workflow-store',
      partialize: (state) => ({
        userPreferences: state.userPreferences,
        currentWorkflow: state.currentWorkflow
      })
    }
  )
);

export default useWorkflowStore;
