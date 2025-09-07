import { 
  TodayTask, 
  DailyWorkflow, 
  NavigationState, 
  WorkflowError
} from '../types/workflow';

interface NavigationConfig {
  autoNavigate: boolean;
  delayBeforeNavigation: number; // milliseconds
  showNavigationConfirmation: boolean;
  enableBackNavigation: boolean;
  persistNavigationState: boolean;
}

interface NavigationEvent {
  type: 'task_started' | 'task_completed' | 'task_skipped' | 'navigation_requested';
  taskId: string;
  workflowId: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

class TaskNavigationService {
  private config: NavigationConfig;
  private navigationHistory: NavigationEvent[] = [];
  private currentNavigationState: NavigationState | null = null;
  private navigationListeners: Array<(event: NavigationEvent) => void> = [];

  constructor(config: NavigationConfig = {
    autoNavigate: true,
    delayBeforeNavigation: 2000,
    showNavigationConfirmation: false,
    enableBackNavigation: true,
    persistNavigationState: true
  }) {
    this.config = config;
    this.loadNavigationHistory();
  }

  /**
   * Navigate to a specific task
   */
  async navigateToTask(
    task: TodayTask, 
    workflow: DailyWorkflow,
    options: {
      skipConfirmation?: boolean;
      trackNavigation?: boolean;
    } = {}
  ): Promise<boolean> {
    try {
      // Validate task and workflow
      if (!this.validateTaskForNavigation(task, workflow)) {
        throw new WorkflowError({
          code: 'INVALID_NAVIGATION_TARGET',
          message: `Cannot navigate to task ${task.id}`,
          timestamp: new Date(),
          recoverable: true,
          suggestedAction: 'Check task dependencies and status'
        });
      }

      // Show confirmation if required
      if (this.config.showNavigationConfirmation && !options.skipConfirmation) {
        const confirmed = await this.showNavigationConfirmation(task);
        if (!confirmed) {
          return false;
        }
      }

      // Execute navigation based on action type
      const navigationSuccess = await this.executeNavigation(task);
      
      if (navigationSuccess) {
        // Update navigation state
        this.updateNavigationState(task, workflow);
        
        // Track navigation event
        if (options.trackNavigation !== false) {
          this.trackNavigationEvent({
            type: 'navigation_requested',
            taskId: task.id,
            workflowId: workflow.id,
            timestamp: new Date(),
            metadata: { actionType: task.actionType, actionUrl: task.actionUrl }
          });
        }

        // Auto-navigate to next task if enabled
        if (this.config.autoNavigate && task.status === 'completed') {
          setTimeout(() => {
            this.autoNavigateToNextTask(workflow);
          }, this.config.delayBeforeNavigation);
        }
      }

      return navigationSuccess;
    } catch (error) {
      console.error('Navigation failed:', error);
      throw error;
    }
  }

  /**
   * Auto-navigate to the next available task
   */
  async autoNavigateToNextTask(workflow: DailyWorkflow): Promise<TodayTask | null> {
    try {
      const nextTask = this.getNextAvailableTask(workflow);
      
      if (nextTask) {
        await this.navigateToTask(nextTask, workflow, { 
          skipConfirmation: true,
          trackNavigation: true 
        });
        return nextTask;
      }

      return null;
    } catch (error) {
      console.error('Auto-navigation failed:', error);
      return null;
    }
  }

  /**
   * Navigate back to previous task
   */
  async navigateBack(workflow: DailyWorkflow): Promise<TodayTask | null> {
    if (!this.config.enableBackNavigation) {
      throw new WorkflowError({
        code: 'BACK_NAVIGATION_DISABLED',
        message: 'Back navigation is disabled',
        timestamp: new Date(),
        recoverable: false
      });
    }

    try {
      const previousTask = this.getPreviousTask(workflow);
      
      if (previousTask) {
        await this.navigateToTask(previousTask, workflow, { 
          skipConfirmation: true,
          trackNavigation: true 
        });
        return previousTask;
      }

      return null;
    } catch (error) {
      console.error('Back navigation failed:', error);
      throw error;
    }
  }

  /**
   * Get the next available task in the workflow
   */
  getNextAvailableTask(workflow: DailyWorkflow): TodayTask | null {
    const currentIndex = workflow.currentTaskIndex;
    const remainingTasks = workflow.tasks.slice(currentIndex + 1);
    
    // Find next task that's not completed and has dependencies satisfied
    for (const task of remainingTasks) {
      if (task.status === 'pending' && this.areDependenciesSatisfied(task, workflow)) {
        return task;
      }
    }

    return null;
  }

  /**
   * Get the previous task in the workflow
   */
  getPreviousTask(workflow: DailyWorkflow): TodayTask | null {
    const currentIndex = workflow.currentTaskIndex;
    
    if (currentIndex > 0) {
      return workflow.tasks[currentIndex - 1];
    }

    return null;
  }

  /**
   * Check if task dependencies are satisfied
   */
  areDependenciesSatisfied(task: TodayTask, workflow: DailyWorkflow): boolean {
    if (!task.dependencies || task.dependencies.length === 0) {
      return true;
    }

    return task.dependencies.every(depId => {
      const depTask = workflow.tasks.find(t => t.id === depId);
      return depTask && depTask.status === 'completed';
    });
  }

  /**
   * Execute the actual navigation based on task action type
   */
  private async executeNavigation(task: TodayTask): Promise<boolean> {
    try {
      switch (task.actionType) {
        case 'navigate':
          return await this.navigateToInternalPage(task);
        case 'modal':
          return await this.openModal(task);
        case 'external':
          return await this.navigateToExternalUrl(task);
        default:
          throw new WorkflowError({
            code: 'UNKNOWN_ACTION_TYPE',
            message: `Unknown action type: ${task.actionType}`,
            timestamp: new Date(),
            recoverable: true,
            suggestedAction: 'Check task configuration'
          });
      }
    } catch (error) {
      console.error(`Navigation execution failed for task ${task.id}:`, error);
      return false;
    }
  }

  /**
   * Navigate to internal ALwrity page
   */
  private async navigateToInternalPage(task: TodayTask): Promise<boolean> {
    if (!task.actionUrl) {
      throw new WorkflowError({
        code: 'MISSING_ACTION_URL',
        message: `Task ${task.id} is missing action URL`,
        timestamp: new Date(),
        recoverable: true,
        suggestedAction: 'Configure action URL for the task'
      });
    }

    try {
      // Use React Router navigation
      if (typeof window !== 'undefined' && window.history) {
        window.history.pushState(null, '', task.actionUrl);
        
        // Dispatch custom event for React Router to handle
        window.dispatchEvent(new PopStateEvent('popstate'));
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Internal navigation failed:', error);
      return false;
    }
  }

  /**
   * Open modal for task
   */
  private async openModal(task: TodayTask): Promise<boolean> {
    try {
      // Dispatch custom event to open modal
      const modalEvent = new CustomEvent('openTaskModal', {
        detail: { task }
      });
      
      if (typeof window !== 'undefined') {
        window.dispatchEvent(modalEvent);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Modal opening failed:', error);
      return false;
    }
  }

  /**
   * Navigate to external URL
   */
  private async navigateToExternalUrl(task: TodayTask): Promise<boolean> {
    if (!task.actionUrl) {
      throw new WorkflowError({
        code: 'MISSING_ACTION_URL',
        message: `Task ${task.id} is missing external URL`,
        timestamp: new Date(),
        recoverable: true,
        suggestedAction: 'Configure external URL for the task'
      });
    }

    try {
      if (typeof window !== 'undefined') {
        window.open(task.actionUrl, '_blank', 'noopener,noreferrer');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('External navigation failed:', error);
      return false;
    }
  }

  /**
   * Validate if task can be navigated to
   */
  private validateTaskForNavigation(task: TodayTask, workflow: DailyWorkflow): boolean {
    // Check if task exists in workflow
    const workflowTask = workflow.tasks.find(t => t.id === task.id);
    if (!workflowTask) {
      return false;
    }

    // Check if task is enabled
    if (!task.enabled) {
      return false;
    }

    // Check dependencies
    if (!this.areDependenciesSatisfied(task, workflow)) {
      return false;
    }

    return true;
  }

  /**
   * Show navigation confirmation dialog
   */
  private async showNavigationConfirmation(task: TodayTask): Promise<boolean> {
    return new Promise((resolve) => {
      // In a real implementation, this would show a confirmation dialog
      // For now, we'll use a simple confirm dialog
      const confirmed = window.confirm(
        `Navigate to: ${task.title}\n\n${task.description}\n\nContinue?`
      );
      resolve(confirmed);
    });
  }

  /**
   * Update navigation state
   */
  private updateNavigationState(task: TodayTask, workflow: DailyWorkflow): void {
    const currentIndex = workflow.tasks.findIndex(t => t.id === task.id);
    const previousTask = currentIndex > 0 ? workflow.tasks[currentIndex - 1] : null;
    const nextTask = currentIndex < workflow.tasks.length - 1 ? workflow.tasks[currentIndex + 1] : null;

    this.currentNavigationState = {
      currentTask: task,
      previousTask,
      nextTask,
      canGoBack: currentIndex > 0,
      canGoForward: currentIndex < workflow.tasks.length - 1
    };
  }

  /**
   * Track navigation event
   */
  private trackNavigationEvent(event: NavigationEvent): void {
    this.navigationHistory.push(event);
    
    // Notify listeners
    this.navigationListeners.forEach(listener => {
      try {
        listener(event);
      } catch (error) {
        console.error('Navigation listener error:', error);
      }
    });

    // Persist navigation history
    if (this.config.persistNavigationState) {
      this.persistNavigationHistory();
    }
  }

  /**
   * Add navigation event listener
   */
  addNavigationListener(listener: (event: NavigationEvent) => void): void {
    this.navigationListeners.push(listener);
  }

  /**
   * Remove navigation event listener
   */
  removeNavigationListener(listener: (event: NavigationEvent) => void): void {
    const index = this.navigationListeners.indexOf(listener);
    if (index > -1) {
      this.navigationListeners.splice(index, 1);
    }
  }

  /**
   * Get current navigation state
   */
  getCurrentNavigationState(): NavigationState | null {
    return this.currentNavigationState;
  }

  /**
   * Get navigation history
   */
  getNavigationHistory(): NavigationEvent[] {
    return [...this.navigationHistory];
  }

  /**
   * Clear navigation history
   */
  clearNavigationHistory(): void {
    this.navigationHistory = [];
    this.persistNavigationHistory();
  }

  /**
   * Persist navigation history to localStorage
   */
  private persistNavigationHistory(): void {
    try {
      localStorage.setItem('task-navigation-history', JSON.stringify(this.navigationHistory));
    } catch (error) {
      console.warn('Failed to persist navigation history:', error);
    }
  }

  /**
   * Load navigation history from localStorage
   */
  private loadNavigationHistory(): void {
    try {
      const stored = localStorage.getItem('task-navigation-history');
      if (stored) {
        this.navigationHistory = JSON.parse(stored).map((event: any) => ({
          ...event,
          timestamp: new Date(event.timestamp)
        }));
      }
    } catch (error) {
      console.warn('Failed to load navigation history:', error);
    }
  }

  /**
   * Update navigation configuration
   */
  updateConfig(newConfig: Partial<NavigationConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Get current configuration
   */
  getConfig(): NavigationConfig {
    return { ...this.config };
  }
}

// Export singleton instance
export const taskNavigationService = new TaskNavigationService();
export default TaskNavigationService;
