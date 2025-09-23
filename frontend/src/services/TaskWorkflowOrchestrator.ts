import { 
  TodayTask, 
  DailyWorkflow, 
  WorkflowProgress, 
  TaskCompletionData,
  TaskGenerationContext,
  WorkflowOrchestratorConfig,
  NavigationState,
  WorkflowError
} from '../types/workflow';
import { taskNavigationService } from './TaskNavigationService';
import { taskDependencyManager } from './TaskDependencyManager';
import { taskCompletionVerifier } from './TaskCompletionVerifier';

class TaskWorkflowOrchestrator {
  private workflows: Map<string, DailyWorkflow> = new Map();
  private config: WorkflowOrchestratorConfig;

  constructor(config: WorkflowOrchestratorConfig = {
    autoNavigate: true,
    showProgress: true,
    enableNotifications: true,
    persistProgress: true,
    allowTaskSkipping: true
  }) {
    this.config = config;
    this.loadPersistedWorkflows();
  }

  /**
   * Generate a new daily workflow for a user
   */
  async generateDailyWorkflow(
    userId: string, 
    date: string = new Date().toISOString().split('T')[0],
    context?: TaskGenerationContext
  ): Promise<DailyWorkflow> {
    try {
      // Check if workflow already exists for this date
      const existingWorkflow = this.getWorkflow(userId, date);
      if (existingWorkflow) {
        return existingWorkflow;
      }

      // Generate tasks based on context or default configuration
      const tasks = await this.generateTasksForDate(userId, date, context);
      
      // Create new workflow
      const workflow: DailyWorkflow = {
        id: `${userId}-${date}`,
        date,
        userId,
        tasks,
        currentTaskIndex: 0,
        completedTasks: 0,
        totalTasks: tasks.length,
        workflowStatus: 'not_started',
        totalEstimatedTime: tasks.reduce((sum, task) => sum + task.estimatedTime, 0),
        actualTimeSpent: 0
      };

      // Save workflow
      this.workflows.set(workflow.id, workflow);
      this.persistWorkflow(workflow);

      return workflow;
    } catch (error) {
      throw new WorkflowError({
        code: 'WORKFLOW_GENERATION_FAILED',
        message: `Failed to generate workflow for user ${userId} on ${date}`,
        timestamp: new Date(),
        recoverable: true,
        suggestedAction: 'Retry workflow generation'
      });
    }
  }

  /**
   * Get workflow for a specific user and date
   */
  getWorkflow(userId: string, date: string): DailyWorkflow | null {
    const workflowId = `${userId}-${date}`;
    return this.workflows.get(workflowId) || null;
  }

  /**
   * Start a workflow
   */
  async startWorkflow(workflowId: string): Promise<DailyWorkflow> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new WorkflowError({
        code: 'WORKFLOW_NOT_FOUND',
        message: `Workflow ${workflowId} not found`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    workflow.workflowStatus = 'in_progress';
    workflow.startedAt = new Date();
    
    // Mark first task as in progress
    if (workflow.tasks.length > 0) {
      workflow.tasks[0].status = 'in_progress';
      workflow.tasks[0].startedAt = new Date();
    }

    this.persistWorkflow(workflow);
    return workflow;
  }

  /**
   * Complete a specific task
   */
  async completeTask(
    workflowId: string, 
    taskId: string, 
    completionData?: Partial<TaskCompletionData>
  ): Promise<WorkflowProgress> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new WorkflowError({
        code: 'WORKFLOW_NOT_FOUND',
        message: `Workflow ${workflowId} not found`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    const task = workflow.tasks.find(t => t.id === taskId);
    if (!task) {
      throw new WorkflowError({
        code: 'TASK_NOT_FOUND',
        message: `Task ${taskId} not found in workflow ${workflowId}`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    // Verify task completion
    await taskCompletionVerifier.verifyTaskCompletion(task, {
      userId: workflow.userId,
      timestamp: new Date()
    });

    // Mark task as completed
    task.status = 'completed';
    task.completedAt = new Date();
    
    // Calculate time spent
    if (task.startedAt) {
      const timeSpent = Math.round((task.completedAt.getTime() - task.startedAt.getTime()) / (1000 * 60));
      workflow.actualTimeSpent += timeSpent;
    }

    // Update dependency manager
    taskDependencyManager.updateTaskStatus(taskId, 'completed');

    // Update workflow progress
    workflow.completedTasks++;
    
    // Check if workflow is complete
    if (workflow.completedTasks === workflow.totalTasks) {
      workflow.workflowStatus = 'completed';
      workflow.completedAt = new Date();
    }

    // Auto-navigate to next task if enabled
    if (this.config.autoNavigate) {
      const nextTask = taskDependencyManager.getReadyTasks(workflow)[0];
      if (nextTask) {
        setTimeout(async () => {
          try {
            await taskNavigationService.navigateToTask(nextTask, workflow);
          } catch (error) {
            console.warn('Auto-navigation failed:', error);
          }
        }, 2000); // 2 second delay
      }
    }

    this.persistWorkflow(workflow);
    return this.getWorkflowProgress(workflowId);
  }

  /**
   * Skip a task
   */
  async skipTask(workflowId: string, taskId: string): Promise<WorkflowProgress> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new WorkflowError({
        code: 'WORKFLOW_NOT_FOUND',
        message: `Workflow ${workflowId} not found`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    const task = workflow.tasks.find(t => t.id === taskId);
    if (!task) {
      throw new WorkflowError({
        code: 'TASK_NOT_FOUND',
        message: `Task ${taskId} not found in workflow ${workflowId}`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    task.status = 'skipped';
    workflow.completedTasks++;
    
    this.persistWorkflow(workflow);
    return this.getWorkflowProgress(workflowId);
  }

  /**
   * Get current workflow progress
   */
  getWorkflowProgress(workflowId: string): WorkflowProgress {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new WorkflowError({
        code: 'WORKFLOW_NOT_FOUND',
        message: `Workflow ${workflowId} not found`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    const currentTask = workflow.tasks[workflow.currentTaskIndex];
    const nextTask = workflow.tasks[workflow.currentTaskIndex + 1];
    const remainingTasks = workflow.tasks.slice(workflow.currentTaskIndex + 1);
    const estimatedTimeRemaining = remainingTasks.reduce((sum, task) => sum + task.estimatedTime, 0);

    return {
      completedTasks: workflow.completedTasks,
      totalTasks: workflow.totalTasks,
      completionPercentage: Math.round((workflow.completedTasks / workflow.totalTasks) * 100),
      currentTask,
      nextTask,
      estimatedTimeRemaining,
      actualTimeSpent: workflow.actualTimeSpent
    };
  }

  /**
   * Get navigation state for current workflow
   */
  getNavigationState(workflowId: string): NavigationState {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new WorkflowError({
        code: 'WORKFLOW_NOT_FOUND',
        message: `Workflow ${workflowId} not found`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    const currentTask = workflow.tasks[workflow.currentTaskIndex];
    const previousTask = workflow.currentTaskIndex > 0 ? workflow.tasks[workflow.currentTaskIndex - 1] : null;
    const nextTask = workflow.currentTaskIndex < workflow.tasks.length - 1 ? workflow.tasks[workflow.currentTaskIndex + 1] : null;

    return {
      currentTask,
      previousTask,
      nextTask,
      canGoBack: workflow.currentTaskIndex > 0,
      canGoForward: workflow.currentTaskIndex < workflow.tasks.length - 1
    };
  }

  /**
   * Move to next task in workflow
   */
  async moveToNextTask(workflowId: string): Promise<TodayTask | null> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new WorkflowError({
        code: 'WORKFLOW_NOT_FOUND',
        message: `Workflow ${workflowId} not found`,
        timestamp: new Date(),
        recoverable: false
      });
    }

    if (workflow.currentTaskIndex < workflow.tasks.length - 1) {
      workflow.currentTaskIndex++;
      const nextTask = workflow.tasks[workflow.currentTaskIndex];
      
      // Mark next task as in progress
      if (nextTask.status === 'pending') {
        nextTask.status = 'in_progress';
        nextTask.startedAt = new Date();
      }

      this.persistWorkflow(workflow);
      return nextTask;
    }

    return null;
  }

  /**
   * Generate tasks for a specific date (enhanced with dependency management)
   */
  private async generateTasksForDate(
    userId: string, 
    date: string, 
    context?: TaskGenerationContext
  ): Promise<TodayTask[]> {
    // This is a placeholder implementation
    // In Phase 3, this will be replaced with AI-powered task generation
    
    const defaultTasks: TodayTask[] = [
      {
        id: `${userId}-${date}-plan-1`,
        pillarId: 'plan',
        title: 'Review content strategy',
        description: 'Check and update your content strategy for the week',
        status: 'pending',
        priority: 'high',
        estimatedTime: 15,
        actionType: 'navigate',
        actionUrl: '/content-planning-dashboard',
        enabled: true,
        icon: 'Business',
        color: '#4CAF50'
      },
      {
        id: `${userId}-${date}-plan-2`,
        pillarId: 'plan',
        title: 'Update content calendar',
        description: 'Review and update your content calendar',
        status: 'pending',
        priority: 'medium',
        estimatedTime: 10,
        dependencies: [`${userId}-${date}-plan-1`],
        actionType: 'navigate',
        actionUrl: '/content-planning-dashboard',
        enabled: true,
        icon: 'CalendarMonth',
        color: '#4CAF50'
      },
      {
        id: `${userId}-${date}-generate-1`,
        pillarId: 'generate',
        title: 'Create social media content',
        description: 'Generate content for your social media platforms',
        status: 'pending',
        priority: 'high',
        estimatedTime: 30,
        dependencies: [`${userId}-${date}-plan-1`, `${userId}-${date}-plan-2`],
        actionType: 'navigate',
        actionUrl: '/facebook-writer',
        enabled: true,
        icon: 'AutoAwesome',
        color: '#2196F3'
      },
      {
        id: `${userId}-${date}-generate-2`,
        pillarId: 'generate',
        title: 'Create blog content',
        description: 'Write blog posts for your website',
        status: 'pending',
        priority: 'medium',
        estimatedTime: 45,
        dependencies: [`${userId}-${date}-plan-1`],
        actionType: 'navigate',
        actionUrl: '/blog-writer',
        enabled: true,
        icon: 'Article',
        color: '#2196F3'
      },
      {
        id: `${userId}-${date}-publish-1`,
        pillarId: 'publish',
        title: 'Publish social media content',
        description: 'Publish your created content to social media',
        status: 'pending',
        priority: 'medium',
        estimatedTime: 10,
        dependencies: [`${userId}-${date}-generate-1`],
        actionType: 'navigate',
        actionUrl: '/facebook-writer',
        enabled: true,
        icon: 'Publish',
        color: '#FF9800'
      },
      {
        id: `${userId}-${date}-publish-2`,
        pillarId: 'publish',
        title: 'Publish blog content',
        description: 'Publish blog posts to your website',
        status: 'pending',
        priority: 'medium',
        estimatedTime: 15,
        dependencies: [`${userId}-${date}-generate-2`],
        actionType: 'navigate',
        actionUrl: '/blog-writer',
        enabled: true,
        icon: 'Publish',
        color: '#FF9800'
      },
      {
        id: `${userId}-${date}-analyze-1`,
        pillarId: 'analyze',
        title: 'Review content performance',
        description: 'Analyze performance of published content',
        status: 'pending',
        priority: 'low',
        estimatedTime: 20,
        dependencies: [`${userId}-${date}-publish-1`, `${userId}-${date}-publish-2`],
        actionType: 'navigate',
        actionUrl: '/analytics-dashboard',
        enabled: true,
        icon: 'Analytics',
        color: '#9C27B0'
      },
      {
        id: `${userId}-${date}-engage-1`,
        pillarId: 'engage',
        title: 'Respond to comments',
        description: 'Engage with comments on your content',
        status: 'pending',
        priority: 'low',
        estimatedTime: 15,
        dependencies: [`${userId}-${date}-publish-1`],
        actionType: 'navigate',
        actionUrl: '/engagement-dashboard',
        enabled: true,
        icon: 'ChatBubbleOutline',
        color: '#E91E63'
      },
      // Engage pillar tasks
      {
        id: `${userId}-${date}-engage-1`,
        pillarId: 'engage',
        title: 'Reply to blog comment',
        description: 'Respond to comments on your latest blog post',
        status: 'pending',
        priority: 'high',
        estimatedTime: 10,
        dependencies: [`${userId}-${date}-analyze-1`],
        actionType: 'navigate',
        actionUrl: '/engagement-dashboard',
        enabled: true,
        icon: 'Comment',
        color: '#E91E63'
      },
      {
        id: `${userId}-${date}-engage-2`,
        pillarId: 'engage',
        title: 'Respond to Twitter mention',
        description: 'Reply to Twitter mentions and engage with followers',
        status: 'pending',
        priority: 'medium',
        estimatedTime: 5,
        dependencies: [`${userId}-${date}-engage-1`],
        actionType: 'navigate',
        actionUrl: '/engagement-dashboard',
        enabled: true,
        icon: 'Twitter',
        color: '#1DA1F2'
      },
      // Remarket pillar tasks
      {
        id: `${userId}-${date}-remarket-1`,
        pillarId: 'remarket',
        title: 'Launch Retargeting Campaign',
        description: 'Create and launch targeted remarketing campaigns',
        status: 'pending',
        priority: 'high',
        estimatedTime: 35,
        dependencies: [`${userId}-${date}-engage-2`],
        actionType: 'navigate',
        actionUrl: '/remarketing-dashboard',
        enabled: true,
        icon: 'Psychology',
        color: '#00695C'
      },
      {
        id: `${userId}-${date}-remarket-2`,
        pillarId: 'remarket',
        title: 'Lead Nurturing Sequence',
        description: 'Set up automated lead nurturing workflows',
        status: 'pending',
        priority: 'medium',
        estimatedTime: 30,
        dependencies: [`${userId}-${date}-remarket-1`],
        actionType: 'navigate',
        actionUrl: '/lead-nurturing',
        enabled: true,
        icon: 'Refresh',
        color: '#4CAF50'
      }
    ];

    // Validate dependencies and get optimal execution order
    const tempWorkflow: DailyWorkflow = {
      id: `${userId}-${date}`,
      date,
      userId,
      tasks: defaultTasks,
      currentTaskIndex: 0,
      completedTasks: 0,
      totalTasks: defaultTasks.length,
      workflowStatus: 'not_started',
      totalEstimatedTime: defaultTasks.reduce((sum, task) => sum + task.estimatedTime, 0),
      actualTimeSpent: 0
    };

    // Validate dependency graph
    const validation = taskDependencyManager.validateDependencyGraph(tempWorkflow);
    if (!validation.isValid) {
      console.warn('Dependency validation failed:', validation.errors);
      // Return tasks without dependencies if validation fails
      return defaultTasks.map(task => ({ ...task, dependencies: [] }));
    }

    // Get optimal execution order
    const orderedTasks = taskDependencyManager.getOptimalExecutionOrder(tempWorkflow);
    
    return orderedTasks;
  }

  /**
   * Persist workflow to localStorage
   */
  private persistWorkflow(workflow: DailyWorkflow): void {
    if (this.config.persistProgress) {
      try {
        localStorage.setItem(`workflow-${workflow.id}`, JSON.stringify(workflow));
      } catch (error) {
        console.warn('Failed to persist workflow:', error);
      }
    }
  }

  /**
   * Load persisted workflows from localStorage
   */
  private loadPersistedWorkflows(): void {
    if (this.config.persistProgress) {
      try {
        const keys = Object.keys(localStorage).filter(key => key.startsWith('workflow-'));
        keys.forEach(key => {
          const workflowData = localStorage.getItem(key);
          if (workflowData) {
            try {
              const workflow = JSON.parse(workflowData) as DailyWorkflow;
              
              // Ensure workflow has required properties
              if (!workflow.id || !workflow.date || !workflow.userId) {
                console.warn(`Invalid workflow data for key ${key}, skipping`);
                return;
              }
              
              // Ensure tasks array exists and is valid
              if (!workflow.tasks || !Array.isArray(workflow.tasks)) {
                console.warn(`Invalid tasks array for workflow ${workflow.id}, initializing empty array`);
                workflow.tasks = [];
              }
              
              // Convert date strings back to Date objects
              if (workflow.startedAt) workflow.startedAt = new Date(workflow.startedAt);
              if (workflow.completedAt) workflow.completedAt = new Date(workflow.completedAt);
              
              // Process tasks with null checks
              workflow.tasks.forEach(task => {
                if (task && typeof task === 'object') {
                  if (task.startedAt) task.startedAt = new Date(task.startedAt);
                  if (task.completedAt) task.completedAt = new Date(task.completedAt);
                }
              });
              
              this.workflows.set(workflow.id, workflow);
            } catch (parseError) {
              console.warn(`Failed to parse workflow data for key ${key}:`, parseError);
              // Remove corrupted data
              localStorage.removeItem(key);
            }
          }
        });
      } catch (error) {
        console.warn('Failed to load persisted workflows:', error);
      }
    }
  }

  /**
   * Clear completed workflows (cleanup)
   */
  clearCompletedWorkflows(): void {
    const completedWorkflows = Array.from(this.workflows.values())
      .filter(workflow => workflow.workflowStatus === 'completed');
    
    completedWorkflows.forEach(workflow => {
      this.workflows.delete(workflow.id);
      if (this.config.persistProgress) {
        localStorage.removeItem(`workflow-${workflow.id}`);
      }
    });
  }
}

// Export singleton instance
export const taskWorkflowOrchestrator = new TaskWorkflowOrchestrator();
export default TaskWorkflowOrchestrator;
