# Build Optimization Guide

This guide explains how to optimize the production build for better performance.

## Current Issues

1. **Minify JavaScript**: 504 KiB savings possible
2. **Reduce unused JavaScript**: 980 KiB savings possible
3. **Minify CSS**: 24 KiB savings possible
4. **Reduce unused CSS**: 25 KiB savings possible
5. **Cache Headers**: 1,702 KiB not cached (requires server configuration)

## React Scripts Build Configuration

React Scripts already minifies JavaScript and CSS in production builds. However, you can optimize further:

### 1. Environment Variables

Create `.env.production` (already created) with:

```env
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
```

### 2. Build Command

Run production build:
```bash
npm run build
```

This will:
- Minify JavaScript (already enabled)
- Minify CSS (already enabled)
- Tree-shake unused code (already enabled)
- Generate source maps (disabled via env var)

## Reducing Unused JavaScript

### Analyze Bundle Size

Install webpack-bundle-analyzer:
```bash
npm install --save-dev webpack-bundle-analyzer
```

Add to `package.json` scripts:
```json
"analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js"
```

Run:
```bash
npm run analyze
```

### Common Issues and Solutions

1. **Large Dependencies**:
   - `framer-motion`: 246 KiB - Consider lazy loading animations
   - `@mui/material`: Multiple chunks - Already code-split
   - `recharts`: Only load when needed

2. **Unused Imports**:
   - Use ESLint rule: `"no-unused-vars": "error"`
   - Run: `npx eslint --ext .ts,.tsx src/ --fix`

3. **Dynamic Imports**:
   - Already implemented for routes
   - Consider lazy loading heavy components like charts

## Server-Side Cache Headers

### For Express.js (if using)

```javascript
// Add to your Express server
app.use(express.static('build', {
  maxAge: '1y',
  immutable: true,
  etag: true,
  lastModified: true
}));
```

### For Nginx

```nginx
location /static {
    alias /path/to/build/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

### For Apache

```apache
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/webp "access plus 1 year"
</IfModule>
```

## Image Optimization

### Convert AskAlwrity-min.ico to WebP

1. Install sharp or use online tool:
```bash
npm install --save-dev sharp
```

2. Create script `scripts/optimize-images.js`:
```javascript
const sharp = require('sharp');
const path = require('path');

sharp('public/AskAlwrity-min.ico')
  .resize(60, 60)
  .webp({ quality: 80 })
  .toFile('public/AskAlwrity-min.webp')
  .then(() => console.log('Image optimized!'));
```

3. Update `index.html`:
```html
<link rel="icon" href="%PUBLIC_URL%/AskAlwrity-min.webp" />
```

## Performance Budget

Set performance budgets in `package.json`:

```json
{
  "performance": {
    "budgets": [
      {
        "type": "initial",
        "maximumWarning": "500kb",
        "maximumError": "1mb"
      },
      {
        "type": "anyComponentStyle",
        "maximumWarning": "50kb",
        "maximumError": "100kb"
      }
    ]
  }
}
```

## Monitoring

### Lighthouse CI

Add to CI/CD pipeline:
```bash
npm install -g @lhci/cli
lhci autorun
```

### Web Vitals

Monitor in production:
```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to your analytics service
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## Expected Improvements

After implementing all optimizations:

- **Performance Score**: 28 → 70-80+
- **Bundle Size**: Reduced by ~1.5MB (unused code + minification)
- **Cache Hit Rate**: 0% → 90%+ (with proper headers)
- **CLS**: 0.167 → <0.1 (with layout fixes)
- **LCP**: Improved by additional 200-300ms

