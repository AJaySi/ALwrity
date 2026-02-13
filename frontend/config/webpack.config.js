const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  // Override webpack config for better optimization
  webpack: function(config, { env }) {
    return {
      ...config,
      optimization: {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            // Critical paths - loaded immediately
            critical: {
              name: 'critical',
              test: /[\\/]node_modules[\\/](react|react-dom|@clerk|react-router-dom)[\\/]/,
              priority: 20,
              chunks: 'all',
            },
            // Feature modules - split by feature
            features: {
              name: 'features',
              test: /[\\/]src[\\/](components|pages)[\\/](VideoStudio|ImageStudio|ProductMarketing)[\\/]/,
              priority: 15,
              chunks: 'all',
            },
            // Dashboard components - split by dashboard type
            dashboards: {
              name: 'dashboards',
              test: /[\\/]src[\\/](components|pages)[\\/](MainDashboard|SEODashboard|ContentPlanningDashboard|FacebookWriter|LinkedInWriter|BlogWriter|StoryWriter)[\\/]/,
              priority: 10,
              chunks: 'all',
            },
            // Heavy libraries - vendor chunks
            vendors: {
              test: /[\\/]node_modules[\\/]/,
              priority: -10,
              name: 'vendors',
              chunks: 'all',
            },
          },
        },
        // Tree shaking optimization
        usedExports: true,
        sideEffects: false,
        // Minimization
        minimize: env === 'production',
      },
      resolve: {
        ...config.resolve,
        alias: {
          // Help webpack find modules faster
          '@': path.resolve(__dirname, 'src'),
        },
      },
      plugins: [
        ...config.plugins,
        // Bundle analyzer for development
        env === 'development' && new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: '../bundle-report.html',
        }),
      ],
    };
  },
  // Performance monitoring
  performance: {
    maxAssetSize: 250000, // 250KB max per file
    maxEntrypointSize: 500000, // 500KB max per entry
    hints: 'warning', // show performance warnings
  },
};
