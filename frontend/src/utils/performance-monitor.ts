/**
 * Performance Monitoring Utility
 * Tracks component render times and memory usage
 */

import React from 'react';

interface PerformanceMetric {
  componentName: string;
  renderTime: number;
  timestamp: number;
  memoryUsage?: number;
}

interface ComponentStats {
  count: number;
  totalTime: number;
  avgTime: number;
}

interface ComponentStatsMap {
  [key: string]: ComponentStats;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observers: MutationObserver[] = [];
  private isMonitoring = false;

  constructor() {
    this.setupObservers();
  }

  // Start monitoring performance
  startMonitoring() {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    console.log('🔍 Performance monitoring started');
  }

  // Stop monitoring
  stopMonitoring() {
    this.isMonitoring = false;
    this.observers.forEach(observer => observer.disconnect());
    console.log('🛑 Performance monitoring stopped');
  }

  // Record a performance metric
  recordMetric(componentName: string, renderTime: number) {
    const memoryUsage = this.getMemoryUsage();
    
    this.metrics.push({
      componentName,
      renderTime,
      timestamp: Date.now(),
      memoryUsage
    });

    // Keep only last 100 metrics
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }
  }

  // Measure component render time
  measureRender(componentName: string, renderFn: () => void) {
    const startTime = performance.now();
    renderFn();
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    this.recordMetric(componentName, renderTime);
  }

  // Get current memory usage
  private getMemoryUsage(): number | undefined {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize;
    }
    return undefined;
  }

  // Setup mutation observers
  private setupObservers() {
    if (typeof MutationObserver !== 'undefined') {
      const observer = new MutationObserver(() => {
        if (this.isMonitoring) {
          // Track DOM changes
        }
      });
      
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
      
      this.observers.push(observer);
    }
  }

  // Get performance summary
  getSummary() {
    if (this.metrics.length === 0) {
      console.log('📊 No performance data available');
      return;
    }

    const totalMetrics = this.metrics.length;
    const avgRenderTime = this.metrics.reduce((sum, m) => sum + m.renderTime, 0) / totalMetrics;
    const maxRenderTime = Math.max(...this.metrics.map(m => m.renderTime));
    const slowRenders = this.metrics.filter(m => m.renderTime > 100).length;

    console.log('\n📊 Performance Summary:');
    console.log(`Total renders: ${totalMetrics}`);
    console.log(`Average render time: ${avgRenderTime.toFixed(2)}ms`);
    console.log(`Max render time: ${maxRenderTime.toFixed(2)}ms`);
    console.log(`Slow renders (>100ms): ${slowRenders}`);

    // Component breakdown
    const componentStats = this.metrics.reduce((stats: ComponentStatsMap, metric) => {
      if (!stats[metric.componentName]) {
        stats[metric.componentName] = {
          count: 0,
          totalTime: 0,
          avgTime: 0
        };
      }
      
      stats[metric.componentName].count++;
      stats[metric.componentName].totalTime += metric.renderTime;
      stats[metric.componentName].avgTime = stats[metric.componentName].totalTime / stats[metric.componentName].count;
      
      return stats;
    }, {});

    // Show slowest components
    const slowComponents = Object.entries(componentStats)
      .filter(([_, stats]) => stats.avgTime > 50)
      .sort(([_, a], [__, b]) => b.avgTime - a.avgTime)
      .slice(0, 5);

    if (slowComponents.length > 0) {
      console.log('\n🐌 Slowest components:');
      slowComponents.forEach(([name, stats]) => {
        console.log(`  ${name}: ${stats.avgTime.toFixed(2)}ms avg (${stats.count} renders)`);
      });
    }

    // Memory usage analysis
    const memoryMetrics = this.metrics.filter(m => m.memoryUsage);
    if (memoryMetrics.length > 0) {
      const avgMemory = memoryMetrics.reduce((sum, m) => sum + (m.memoryUsage || 0), 0) / memoryMetrics.length;
      console.log(`\n🧠 Average memory usage: ${(avgMemory / 1024 / 1024).toFixed(2)}MB`);
    }

    // Recommendations
    console.log('\n💡 Performance Recommendations:');
    if (avgRenderTime > 50) {
      console.log('- Consider React.memo() for expensive components');
    }
    if (slowRenders > this.metrics.length * 0.1) {
      console.log('- Implement virtual scrolling for large lists');
    }
    if (maxRenderTime > 200) {
      console.log('- Consider code splitting for heavy components');
    }
  }

  // Clear all metrics
  clearMetrics() {
    this.metrics = [];
    console.log('🗑️ Performance metrics cleared');
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

// HOC for performance tracking
export const withPerformanceTracking = <P extends object>(
  componentName: string,
  Component: React.ComponentType<P>
): React.ComponentType<P> => {
  const WrappedComponent = React.memo(Component);
  
  return function TrackedComponent(props: P) {
    const startTime = performance.now();
    const result = React.createElement(WrappedComponent, props as any);
    const endTime = performance.now();
    
    performanceMonitor.recordMetric(componentName, endTime - startTime);
    return result;
  };
};

export default performanceMonitor;
