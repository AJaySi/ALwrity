#!/usr/bin/env node

/**
 * Performance Comparison Script
 * Compares performance between original and lazy loading versions
 */

const { execSync } = require('child_process');
const fs = require('fs');

function runBuildWithFlags(flags, buildName) {
  console.log(`\n🔨 Building ${buildName}...`);
  console.log('================================');
  
  const startTime = Date.now();
  
  try {
    // Set environment variables for feature flags
    const envVars = Object.entries(flags)
      .map(([key, value]) => `REACT_APP_${key.toUpperCase()}=${value}`)
      .join(' ');
    
    const command = `cross-env ${envVars} npm run build:fast`;
    console.log(`Running: ${command}`);
    
    execSync(command, { stdio: 'inherit', cwd: process.cwd() });
    
    const endTime = Date.now();
    const buildTime = endTime - startTime;
    
    console.log(`✅ ${buildName} build completed in ${buildTime}ms`);
    
    // Analyze bundle size
    analyzeBundleSize(buildName);
    
    return { buildTime, success: true };
    
  } catch (error) {
    console.error(`❌ ${buildName} build failed:`, error.message);
    return { buildTime: 0, success: false };
  }
}

function analyzeBundleSize(buildName) {
  try {
    const buildDir = './build/static/js';
    if (!fs.existsSync(buildDir)) {
      console.log(`⚠️  Build directory not found for ${buildName}`);
      return;
    }
    
    const files = fs.readdirSync(buildDir);
    const jsFiles = files.filter(file => file.endsWith('.js'));
    
    let totalSize = 0;
    console.log(`\n📊 ${buildName} Bundle Analysis:`);
    
    jsFiles.forEach(file => {
      const filePath = `${buildDir}/${file}`;
      const stats = fs.statSync(filePath);
      const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
      totalSize += stats.size;
      console.log(`  ${file}: ${sizeMB} MB`);
    });
    
    const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
    console.log(`\n📦 Total Bundle Size: ${totalSizeMB} MB`);
    
    return { totalSize, fileCount: jsFiles.length };
    
  } catch (error) {
    console.error(`❌ Failed to analyze ${buildName} bundle:`, error.message);
    return null;
  }
}

function main() {
  console.log('🚀 Performance Comparison Test');
  console.log('============================');
  
  const results = {};
  
  // Test 1: Original App (no optimizations)
  results.original = runBuildWithFlags({
    LAZY_LOADING: 'false',
    PERFORMANCE_MONITORING: 'false',
    BUNDLE_OPTIMIZATION: 'false'
  }, 'Original App');
  
  // Test 2: Lazy Loading Only
  results.lazyOnly = runBuildWithFlags({
    LAZY_LOADING: 'true',
    PERFORMANCE_MONITORING: 'false',
    BUNDLE_OPTIMIZATION: 'false'
  }, 'Lazy Loading Only');
  
  // Test 3: Full Optimization
  results.fullOptimization = runBuildWithFlags({
    LAZY_LOADING: 'true',
    PERFORMANCE_MONITORING: 'true',
    BUNDLE_OPTIMIZATION: 'true'
  }, 'Full Optimization');
  
  // Generate comparison report
  console.log('\n📈 Performance Comparison Report');
  console.log('===============================');
  
  Object.entries(results).forEach(([name, result]) => {
    if (result.success) {
      console.log(`\n${name}:`);
      console.log(`  Build Time: ${result.buildTime}ms`);
      console.log(`  Status: ✅ Success`);
    } else {
      console.log(`\n${name}:`);
      console.log(`  Status: ❌ Failed`);
    }
  });
  
  // Calculate improvements
  if (results.original.success && results.lazyOnly.success) {
    const lazyImprovement = ((results.original.buildTime - results.lazyOnly.buildTime) / results.original.buildTime * 100).toFixed(1);
    console.log(`\n🎯 Lazy Loading Improvement: ${lazyImprovement}% faster build time`);
  }
  
  if (results.lazyOnly.success && results.fullOptimization.success) {
    const fullOptimizationImprovement = ((results.lazyOnly.buildTime - results.fullOptimization.buildTime) / results.lazyOnly.buildTime * 100).toFixed(1);
    console.log(`🎯 Full Optimization Improvement: ${fullOptimizationImprovement}% faster build time`);
  }
  
  console.log('\n✅ Performance comparison complete');
  console.log('\n💡 Recommendations:');
  console.log('- Use lazy loading for better initial load performance');
  console.log('- Enable performance monitoring for production insights');
  console.log('- Bundle optimization reduces overall bundle size');
}

if (require.main === module) {
  main();
}

module.exports = { runBuildWithFlags, analyzeBundleSize };
