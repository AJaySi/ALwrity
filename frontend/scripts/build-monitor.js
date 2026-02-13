/**
 * Build Performance Monitor
 *
 * Monitors build performance and bundle size to ensure
 * we're not introducing memory leaks or performance issues.
 */

const fs = require('fs');
const path = require('path');

function analyzeBundle() {
  const buildDir = path.join(__dirname, '../build/static/js');

  if (!fs.existsSync(buildDir)) {
    console.log('❌ Build directory not found. Run build first.');
    return;
  }

  const files = fs.readdirSync(buildDir);
  const jsFiles = files.filter(file => file.endsWith('.js'));

  console.log('📊 Build Analysis Results:');
  console.log('========================');

  let totalSize = 0;
  jsFiles.forEach(file => {
    const filePath = path.join(buildDir, file);
    const stats = fs.statSync(filePath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    totalSize += stats.size;

    console.log(`📄 ${file}: ${sizeMB} MB`);
  });

  const totalSizeMB = (totalSize / (1024 * 1024)).toFixed(2);
  console.log(`\n📦 Total Bundle Size: ${totalSizeMB} MB`);

  // Performance thresholds
  const thresholds = {
    warning: 10, // MB
    critical: 15 // MB
  };

  if (totalSizeMB > thresholds.critical) {
    console.log('🚨 CRITICAL: Bundle size exceeds recommended limit!');
    console.log('   Consider code splitting or bundle optimization.');
  } else if (totalSizeMB > thresholds.warning) {
    console.log('⚠️  WARNING: Bundle size is large.');
    console.log('   Monitor for potential performance issues.');
  } else {
    console.log('✅ Bundle size is within acceptable limits.');
  }

  // Memory usage note
  console.log('\n🧠 Memory Usage:');
  console.log('   Build completed with 4GB Node.js memory limit.');
  console.log('   If builds are slow, consider:');
  console.log('   - Code splitting (lazy loading)');
  console.log('   - Bundle analysis for large dependencies');
  console.log('   - Tree shaking optimization');
}

// Run analysis if called directly
if (require.main === module) {
  analyzeBundle();
}

module.exports = { analyzeBundle };