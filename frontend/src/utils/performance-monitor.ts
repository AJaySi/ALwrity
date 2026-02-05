/**
 * Performance Monitoring Utility
 * Tracks component render times and memory usage
 */

interface PerformanceMetric {
  componentName: string;
  renderTime: number;
  timestamp: number;
  memoryUsage?: number;
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
    
    // Monitor page load performance
    if ('performance' in window) {
      window.addEventListener('load', () => {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
          const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
          console.log(`📊 Page load time: ${loadTime.toFixed(2)}ms`);
          this.recordMetric('page-load', loadTime);
        }
      });
    }
  }

  // Stop monitoring
  stopMonitoring() {
    this.isMonitoring = false;
    this.cleanupObservers();
    console.log('🛑 Performance monitoring stopped');
    this.generateReport();
  }

  // Record a performance metric
  recordMetric(componentName: string, renderTime: number, memoryUsage?: number) {
    const metric: PerformanceMetric = {
      componentName,
      renderTime,
      timestamp: Date.now(),
      memoryUsage
    };
    
    this.metrics.push(metric);
    
    // Keep only last 100 metrics to prevent memory leaks
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }
    
    // Log slow renders
    if (renderTime > 100) { // 100ms threshold
      console.warn(`🐌 Slow render detected: ${componentName} took ${renderTime.toFixed(2)}ms`);
    }
  }

  // Measure component render time
  measureRender(componentName: string, renderFunction: () => void) {
    if (!this.isMonitoring) return renderFunction;
    
    const startTime = performance.now();
    renderFunction();
    const endTime = performance.now();
    
    const renderTime = endTime - startTime;
    this.recordMetric(componentName, renderTime);
    
    return renderTime;
  }

  // Setup mutation observers for DOM changes
  private setupObservers() {
    if (typeof MutationObserver !== 'undefined') {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach(() => {
          this.recordMetric('dom-mutation', 0);
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true
      });

      this.observers.push(observer);
    }
  }

  // Clean up observers
  private cleanupObservers() {
    this.observers.forEach(observer => {
      observer.disconnect();
    });
    this.observers = [];
  }

  // Generate performance report
  private generateReport() {
    if (this.metrics.length === 0) {
      console.log('📊 No performance metrics collected');
      return;
    }

    console.log('\n📊 Performance Report:');
    console.log('=====================');

    // Calculate statistics
    const renderTimes = this.metrics.map(m => m.renderTime);
    const avgRenderTime = renderTimes.reduce((sum, time) => sum + time, 0) / renderTimes.length;
    const maxRenderTime = Math.max(...renderTimes);
    const slowRenders = renderTimes.filter(time => time > 100).length;

    console.log(`Total measurements: ${this.metrics.length}`);
    console.log(`Average render time: ${avgRenderTime.toFixed(2)}ms`);
    console.log(`Max render time: ${maxRenderTime.toFixed(2)}ms`);
    console.log(`Slow renders (>100ms): ${slowRenders}`);

    // Component breakdown
    const componentStats = this.metrics.reduce((stats, metric) => {
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

  // Get current metrics
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  // Clear metrics
  clearMetrics() {
    this.metrics = [];
    console.log('🗑️ Performance metrics cleared');
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// HOC for measuring component performance
export const withPerformanceTracking = <P extends object>(
  componentName: string,
  Component: React.ComponentType<P>
) => {
  const WrappedComponent = React.memo(Component);
  
  return (props: P) => {
    const measureRender = () => {
      return React.createElement(WrappedComponent, props);
    };
    
    performanceMonitor.measureRender(componentName, measureRender);
  };
};

export default PerformanceMonitor;
