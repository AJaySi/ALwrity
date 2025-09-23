import { 
  TodayTask
} from '../types/workflow';

interface VerificationResult {
  isCompleted: boolean;
  confidence: number; // 0-1 scale
  evidence: string[];
  warnings: string[];
  suggestions: string[];
}

interface VerificationRule {
  id: string;
  name: string;
  description: string;
  pillarId: string;
  actionType: string;
  verifier: (task: TodayTask, context?: any) => Promise<VerificationResult>;
  weight: number; // Importance weight for confidence calculation
}

interface VerificationContext {
  userId: string;
  timestamp: Date;
  platformData?: Record<string, any>;
  userActivity?: Record<string, any>;
}

class TaskCompletionVerifier {
  private verificationRules: Map<string, VerificationRule> = new Map();
  private verificationHistory: Map<string, VerificationResult[]> = new Map();

  constructor() {
    this.initializeDefaultRules();
  }

  /**
   * Verify if a task has been completed
   */
  async verifyTaskCompletion(
    task: TodayTask, 
    context?: VerificationContext
  ): Promise<VerificationResult> {
    try {
      const rule = this.verificationRules.get(`${task.pillarId}-${task.actionType}`);
      
      if (!rule) {
        // Fallback to basic verification
        return this.basicVerification(task, context);
      }

      const result = await rule.verifier(task, context);
      
      // Store verification history
      this.storeVerificationResult(task.id, result);
      
      return result;
    } catch (error) {
      console.error(`Verification failed for task ${task.id}:`, error);
      
      return {
        isCompleted: false,
        confidence: 0,
        evidence: [],
        warnings: [`Verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        suggestions: ['Try completing the task again or contact support']
      };
    }
  }

  /**
   * Verify multiple tasks at once
   */
  async verifyMultipleTasks(
    tasks: TodayTask[], 
    context?: VerificationContext
  ): Promise<Map<string, VerificationResult>> {
    const results = new Map<string, VerificationResult>();
    
    // Verify tasks in parallel for better performance
    const verificationPromises = tasks.map(async (task) => {
      const result = await this.verifyTaskCompletion(task, context);
      results.set(task.id, result);
    });

    await Promise.all(verificationPromises);
    return results;
  }

  /**
   * Get verification history for a task
   */
  getVerificationHistory(taskId: string): VerificationResult[] {
    return this.verificationHistory.get(taskId) || [];
  }

  /**
   * Add custom verification rule
   */
  addVerificationRule(rule: VerificationRule): void {
    const key = `${rule.pillarId}-${rule.actionType}`;
    this.verificationRules.set(key, rule);
  }

  /**
   * Remove verification rule
   */
  removeVerificationRule(pillarId: string, actionType: string): void {
    const key = `${pillarId}-${actionType}`;
    this.verificationRules.delete(key);
  }

  /**
   * Get all verification rules
   */
  getVerificationRules(): VerificationRule[] {
    return Array.from(this.verificationRules.values());
  }

  /**
   * Initialize default verification rules
   */
  private initializeDefaultRules(): void {
    // Plan pillar rules
    this.addVerificationRule({
      id: 'plan-navigate',
      name: 'Content Planning Navigation',
      description: 'Verify user navigated to content planning dashboard',
      pillarId: 'plan',
      actionType: 'navigate',
      weight: 0.8,
      verifier: async (task, context) => {
        return this.verifyNavigation(task, context);
      }
    });

    // Generate pillar rules
    this.addVerificationRule({
      id: 'generate-navigate',
      name: 'Content Generation Navigation',
      description: 'Verify user navigated to content generation tools',
      pillarId: 'generate',
      actionType: 'navigate',
      weight: 0.8,
      verifier: async (task, context) => {
        return this.verifyNavigation(task, context);
      }
    });

    // Publish pillar rules
    this.addVerificationRule({
      id: 'publish-navigate',
      name: 'Content Publishing Navigation',
      description: 'Verify user navigated to publishing tools',
      pillarId: 'publish',
      actionType: 'navigate',
      weight: 0.8,
      verifier: async (task, context) => {
        return this.verifyNavigation(task, context);
      }
    });

    // Analyze pillar rules
    this.addVerificationRule({
      id: 'analyze-navigate',
      name: 'Analytics Navigation',
      description: 'Verify user navigated to analytics dashboard',
      pillarId: 'analyze',
      actionType: 'navigate',
      weight: 0.8,
      verifier: async (task, context) => {
        return this.verifyNavigation(task, context);
      }
    });

    // Engage pillar rules
    this.addVerificationRule({
      id: 'engage-navigate',
      name: 'Engagement Navigation',
      description: 'Verify user navigated to engagement tools',
      pillarId: 'engage',
      actionType: 'navigate',
      weight: 0.8,
      verifier: async (task, context) => {
        return this.verifyNavigation(task, context);
      }
    });

    // Remarket pillar rules
    this.addVerificationRule({
      id: 'remarket-navigate',
      name: 'Remarketing Navigation',
      description: 'Verify user navigated to remarketing tools',
      pillarId: 'remarket',
      actionType: 'navigate',
      weight: 0.8,
      verifier: async (task, context) => {
        return this.verifyNavigation(task, context);
      }
    });
  }

  /**
   * Verify navigation-based tasks
   */
  private async verifyNavigation(
    task: TodayTask, 
    context?: VerificationContext
  ): Promise<VerificationResult> {
    const evidence: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];
    let confidence = 0;

    try {
      // Check if user is currently on the target page
      if (typeof window !== 'undefined' && task.actionUrl) {
        const currentPath = window.location.pathname;
        const targetPath = task.actionUrl;
        
        if (currentPath === targetPath) {
          evidence.push(`User is currently on target page: ${targetPath}`);
          confidence += 0.4;
        } else {
          warnings.push(`User is not on target page. Current: ${currentPath}, Expected: ${targetPath}`);
          suggestions.push('Navigate to the correct page to complete this task');
        }
      }

      // Check user activity (if available)
      if (context?.userActivity) {
        const activity = context.userActivity;
        const taskStartTime = task.startedAt?.getTime() || 0;
        const recentActivity = Object.entries(activity)
          .filter(([_, timestamp]) => typeof timestamp === 'number' && timestamp > taskStartTime);

        if (recentActivity.length > 0) {
          evidence.push(`User activity detected after task start: ${recentActivity.length} actions`);
          confidence += 0.3;
        } else {
          warnings.push('No user activity detected after task start');
        }
      }

      // Check platform data (if available)
      if (context?.platformData) {
        const platformData = context.platformData;
        if (platformData.lastActivity && platformData.lastActivity > (task.startedAt?.getTime() || 0)) {
          evidence.push('Platform activity detected after task start');
          confidence += 0.3;
        }
      }

      // Time-based verification
      if (task.startedAt && task.completedAt) {
        const timeSpent = task.completedAt.getTime() - task.startedAt.getTime();
        const estimatedTime = task.estimatedTime * 60 * 1000; // Convert to milliseconds
        
        if (timeSpent >= estimatedTime * 0.5) { // At least 50% of estimated time
          evidence.push(`Task took ${Math.round(timeSpent / 60000)} minutes (estimated: ${task.estimatedTime} minutes)`);
          confidence += 0.2;
        } else {
          warnings.push(`Task completed too quickly (${Math.round(timeSpent / 60000)} minutes vs ${task.estimatedTime} estimated)`);
        }
      }

      // Cap confidence at 1.0
      confidence = Math.min(confidence, 1.0);

      return {
        isCompleted: confidence >= 0.6, // Threshold for completion
        confidence,
        evidence,
        warnings,
        suggestions
      };

    } catch (error) {
      return {
        isCompleted: false,
        confidence: 0,
        evidence: [],
        warnings: [`Navigation verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`],
        suggestions: ['Try navigating to the target page again']
      };
    }
  }

  /**
   * Basic verification fallback
   */
  private async basicVerification(
    task: TodayTask, 
    context?: VerificationContext
  ): Promise<VerificationResult> {
    const evidence: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];
    let confidence = 0;

    // Check if task has completion timestamp
    if (task.completedAt) {
      evidence.push('Task has completion timestamp');
      confidence += 0.5;
    } else {
      warnings.push('No completion timestamp found');
    }

    // Check if task was started
    if (task.startedAt) {
      evidence.push('Task was started');
      confidence += 0.3;
    } else {
      warnings.push('No start timestamp found');
    }

    // Check time spent
    if (task.startedAt && task.completedAt) {
      const timeSpent = task.completedAt.getTime() - task.startedAt.getTime();
      if (timeSpent > 0) {
        evidence.push(`Task took ${Math.round(timeSpent / 60000)} minutes`);
        confidence += 0.2;
      }
    }

    return {
      isCompleted: confidence >= 0.5,
      confidence,
      evidence,
      warnings,
      suggestions: suggestions.length > 0 ? suggestions : ['Complete the task to verify completion']
    };
  }

  /**
   * Store verification result in history
   */
  private storeVerificationResult(taskId: string, result: VerificationResult): void {
    const history = this.verificationHistory.get(taskId) || [];
    history.push(result);
    
    // Keep only last 10 verification results
    if (history.length > 10) {
      history.shift();
    }
    
    this.verificationHistory.set(taskId, history);
  }

  /**
   * Get verification statistics
   */
  getVerificationStats(): {
    totalVerifications: number;
    averageConfidence: number;
    completionRate: number;
    mostCommonWarnings: string[];
  } {
    const allResults = Array.from(this.verificationHistory.values()).flat();
    
    if (allResults.length === 0) {
      return {
        totalVerifications: 0,
        averageConfidence: 0,
        completionRate: 0,
        mostCommonWarnings: []
      };
    }

    const totalVerifications = allResults.length;
    const averageConfidence = allResults.reduce((sum, result) => sum + result.confidence, 0) / totalVerifications;
    const completionRate = allResults.filter(result => result.isCompleted).length / totalVerifications;
    
    // Count warning frequency
    const warningCounts = new Map<string, number>();
    allResults.forEach(result => {
      result.warnings.forEach(warning => {
        warningCounts.set(warning, (warningCounts.get(warning) || 0) + 1);
      });
    });
    
    const mostCommonWarnings = Array.from(warningCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([warning]) => warning);

    return {
      totalVerifications,
      averageConfidence,
      completionRate,
      mostCommonWarnings
    };
  }

  /**
   * Clear verification history
   */
  clearVerificationHistory(): void {
    this.verificationHistory.clear();
  }

  /**
   * Export verification data
   */
  exportVerificationData(): {
    rules: VerificationRule[];
    history: Record<string, VerificationResult[]>;
    stats: {
      totalVerifications: number;
      averageConfidence: number;
      completionRate: number;
      mostCommonWarnings: string[];
    };
  } {
    return {
      rules: this.getVerificationRules(),
      history: Object.fromEntries(this.verificationHistory),
      stats: this.getVerificationStats()
    };
  }
}

// Export singleton instance
export const taskCompletionVerifier = new TaskCompletionVerifier();
export default TaskCompletionVerifier;
