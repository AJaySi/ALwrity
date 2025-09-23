import { 
  TodayTask, 
  DailyWorkflow, 
  WorkflowError 
} from '../types/workflow';

interface DependencyGraph {
  [taskId: string]: {
    dependencies: string[];
    dependents: string[];
    status: 'ready' | 'blocked' | 'completed' | 'skipped';
  };
}

interface DependencyValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  readyTasks: string[];
  blockedTasks: string[];
}

class TaskDependencyManager {
  private dependencyGraph: DependencyGraph = {};

  /**
   * Build dependency graph from workflow tasks
   */
  buildDependencyGraph(workflow: DailyWorkflow): DependencyGraph {
    this.dependencyGraph = {};

    // Initialize all tasks in the graph
    workflow.tasks.forEach(task => {
      this.dependencyGraph[task.id] = {
        dependencies: task.dependencies || [],
        dependents: [],
        status: this.getTaskStatus(task, workflow)
      };
    });

    // Build dependent relationships
    Object.keys(this.dependencyGraph).forEach(taskId => {
      const task = this.dependencyGraph[taskId];
      task.dependencies.forEach(depId => {
        if (this.dependencyGraph[depId]) {
          this.dependencyGraph[depId].dependents.push(taskId);
        }
      });
    });

    return this.dependencyGraph;
  }

  /**
   * Validate dependency graph for issues
   */
  validateDependencyGraph(workflow: DailyWorkflow): DependencyValidationResult {
    const result: DependencyValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      readyTasks: [],
      blockedTasks: []
    };

    this.buildDependencyGraph(workflow);

    // Check for circular dependencies
    const circularDeps = this.detectCircularDependencies();
    if (circularDeps.length > 0) {
      result.isValid = false;
      result.errors.push(`Circular dependencies detected: ${circularDeps.join(', ')}`);
    }

    // Check for missing dependencies
    const missingDeps = this.detectMissingDependencies(workflow);
    if (missingDeps.length > 0) {
      result.isValid = false;
      result.errors.push(`Missing dependencies: ${missingDeps.join(', ')}`);
    }

    // Check for orphaned tasks (tasks with no dependencies or dependents)
    const orphanedTasks = this.detectOrphanedTasks();
    if (orphanedTasks.length > 0) {
      result.warnings.push(`Orphaned tasks detected: ${orphanedTasks.join(', ')}`);
    }

    // Categorize tasks by readiness
    Object.keys(this.dependencyGraph).forEach(taskId => {
      const task = this.dependencyGraph[taskId];
      if (task.status === 'ready') {
        result.readyTasks.push(taskId);
      } else if (task.status === 'blocked') {
        result.blockedTasks.push(taskId);
      }
    });

    return result;
  }

  /**
   * Get tasks that are ready to be executed
   */
  getReadyTasks(workflow: DailyWorkflow): TodayTask[] {
    this.buildDependencyGraph(workflow);
    
    return workflow.tasks.filter(task => {
      const graphTask = this.dependencyGraph[task.id];
      return graphTask && graphTask.status === 'ready' && task.status === 'pending';
    });
  }

  /**
   * Get tasks that are blocked by dependencies
   */
  getBlockedTasks(workflow: DailyWorkflow): TodayTask[] {
    this.buildDependencyGraph(workflow);
    
    return workflow.tasks.filter(task => {
      const graphTask = this.dependencyGraph[task.id];
      return graphTask && graphTask.status === 'blocked';
    });
  }

  /**
   * Get tasks that depend on a specific task
   */
  getDependentTasks(taskId: string): string[] {
    const task = this.dependencyGraph[taskId];
    return task ? [...task.dependents] : [];
  }

  /**
   * Get tasks that a specific task depends on
   */
  getDependencyTasks(taskId: string): string[] {
    const task = this.dependencyGraph[taskId];
    return task ? [...task.dependencies] : [];
  }

  /**
   * Check if a task can be executed (all dependencies satisfied)
   */
  canExecuteTask(taskId: string, workflow: DailyWorkflow): boolean {
    this.buildDependencyGraph(workflow);
    
    const task = this.dependencyGraph[taskId];
    if (!task) {
      return false;
    }

    return task.status === 'ready';
  }

  /**
   * Get the optimal execution order for tasks
   */
  getOptimalExecutionOrder(workflow: DailyWorkflow): TodayTask[] {
    this.buildDependencyGraph(workflow);
    
    const visited = new Set<string>();
    const visiting = new Set<string>();
    const executionOrder: TodayTask[] = [];

    const visit = (taskId: string) => {
      if (visiting.has(taskId)) {
        throw new WorkflowError({
          code: 'CIRCULAR_DEPENDENCY',
          message: `Circular dependency detected involving task ${taskId}`,
          timestamp: new Date(),
          recoverable: false
        });
      }

      if (visited.has(taskId)) {
        return;
      }

      visiting.add(taskId);
      
      const task = this.dependencyGraph[taskId];
      if (task) {
        // Visit dependencies first
        task.dependencies.forEach(depId => {
          visit(depId);
        });
      }

      visiting.delete(taskId);
      visited.add(taskId);

      // Add task to execution order
      const workflowTask = workflow.tasks.find(t => t.id === taskId);
      if (workflowTask) {
        executionOrder.push(workflowTask);
      }
    };

    // Visit all tasks
    workflow.tasks.forEach(task => {
      if (!visited.has(task.id)) {
        visit(task.id);
      }
    });

    return executionOrder;
  }

  /**
   * Update task status in dependency graph
   */
  updateTaskStatus(taskId: string, status: 'completed' | 'skipped' | 'in_progress'): void {
    if (this.dependencyGraph[taskId]) {
      // Update status of the task
      this.dependencyGraph[taskId].status = status === 'in_progress' ? 'ready' : status;
      
      // Update status of dependent tasks
      this.updateDependentTasksStatus(taskId);
    }
  }

  /**
   * Get dependency chain for a task (all tasks that must be completed first)
   */
  getDependencyChain(taskId: string): string[] {
    const chain: string[] = [];
    const visited = new Set<string>();

    const buildChain = (currentTaskId: string) => {
      if (visited.has(currentTaskId)) {
        return;
      }

      visited.add(currentTaskId);
      const task = this.dependencyGraph[currentTaskId];
      
      if (task) {
        task.dependencies.forEach(depId => {
          buildChain(depId);
          if (!chain.includes(depId)) {
            chain.push(depId);
          }
        });
      }
    };

    buildChain(taskId);
    return chain;
  }

  /**
   * Get impact of completing a task (what tasks become available)
   */
  getCompletionImpact(taskId: string): string[] {
    const impact: string[] = [];
    
    const task = this.dependencyGraph[taskId];
    if (task) {
      task.dependents.forEach(dependentId => {
        const dependent = this.dependencyGraph[dependentId];
        if (dependent && dependent.status === 'blocked') {
          // Check if all dependencies are now satisfied
          const allDepsSatisfied = dependent.dependencies.every(depId => {
            const depTask = this.dependencyGraph[depId];
            return depTask && (depTask.status === 'completed' || depTask.status === 'skipped');
          });
          
          if (allDepsSatisfied) {
            impact.push(dependentId);
          }
        }
      });
    }

    return impact;
  }

  /**
   * Detect circular dependencies in the graph
   */
  private detectCircularDependencies(): string[] {
    const visited = new Set<string>();
    const visiting = new Set<string>();
    const circular: string[] = [];

    const visit = (taskId: string, path: string[] = []) => {
      if (visiting.has(taskId)) {
        const cycleStart = path.indexOf(taskId);
        if (cycleStart !== -1) {
          circular.push(...path.slice(cycleStart), taskId);
        }
        return;
      }

      if (visited.has(taskId)) {
        return;
      }

      visiting.add(taskId);
      const task = this.dependencyGraph[taskId];
      
      if (task) {
        task.dependencies.forEach(depId => {
          visit(depId, [...path, taskId]);
        });
      }

      visiting.delete(taskId);
      visited.add(taskId);
    };

    Object.keys(this.dependencyGraph).forEach(taskId => {
      if (!visited.has(taskId)) {
        visit(taskId);
      }
    });

    return [...new Set(circular)];
  }

  /**
   * Detect missing dependencies
   */
  private detectMissingDependencies(workflow: DailyWorkflow): string[] {
    const missing: string[] = [];
    const taskIds = new Set(workflow.tasks.map(t => t.id));

    Object.keys(this.dependencyGraph).forEach(taskId => {
      const task = this.dependencyGraph[taskId];
      task.dependencies.forEach(depId => {
        if (!taskIds.has(depId)) {
          missing.push(`${taskId} -> ${depId}`);
        }
      });
    });

    return missing;
  }

  /**
   * Detect orphaned tasks
   */
  private detectOrphanedTasks(): string[] {
    const orphaned: string[] = [];

    Object.keys(this.dependencyGraph).forEach(taskId => {
      const task = this.dependencyGraph[taskId];
      if (task.dependencies.length === 0 && task.dependents.length === 0) {
        orphaned.push(taskId);
      }
    });

    return orphaned;
  }

  /**
   * Update dependent tasks status when a dependency is completed
   */
  private updateDependentTasksStatus(completedTaskId: string): void {
    const task = this.dependencyGraph[completedTaskId];
    if (!task) {
      return;
    }

    task.dependents.forEach(dependentId => {
      const dependent = this.dependencyGraph[dependentId];
      if (dependent && dependent.status === 'blocked') {
        // Check if all dependencies are now satisfied
        const allDepsSatisfied = dependent.dependencies.every(depId => {
          const depTask = this.dependencyGraph[depId];
          return depTask && (depTask.status === 'completed' || depTask.status === 'skipped');
        });

        if (allDepsSatisfied) {
          dependent.status = 'ready';
        }
      }
    });
  }

  /**
   * Get task status based on dependencies
   */
  private getTaskStatus(task: TodayTask, workflow: DailyWorkflow): 'ready' | 'blocked' | 'completed' | 'skipped' {
    if (task.status === 'completed' || task.status === 'skipped') {
      return task.status;
    }

    if (!task.dependencies || task.dependencies.length === 0) {
      return 'ready';
    }

    // Check if all dependencies are satisfied
    const allDepsSatisfied = task.dependencies.every(depId => {
      const depTask = workflow.tasks.find(t => t.id === depId);
      return depTask && (depTask.status === 'completed' || depTask.status === 'skipped');
    });

    return allDepsSatisfied ? 'ready' : 'blocked';
  }

  /**
   * Get dependency graph visualization data
   */
  getDependencyGraphData(): {
    nodes: Array<{ id: string; label: string; status: string }>;
    edges: Array<{ from: string; to: string; type: string }>;
  } {
    const nodes = Object.keys(this.dependencyGraph).map(taskId => ({
      id: taskId,
      label: taskId,
      status: this.dependencyGraph[taskId].status
    }));

    const edges: Array<{ from: string; to: string; type: string }> = [];
    Object.keys(this.dependencyGraph).forEach(taskId => {
      const task = this.dependencyGraph[taskId];
      task.dependencies.forEach(depId => {
        edges.push({
          from: depId,
          to: taskId,
          type: 'dependency'
        });
      });
    });

    return { nodes, edges };
  }
}

// Export singleton instance
export const taskDependencyManager = new TaskDependencyManager();
export default TaskDependencyManager;
