# Dashboard Media Optimization

This directory contains optimized components for images and videos used in the Image Studio Dashboard previews.

## Components

### OptimizedImage
A lazy-loading image component with the following features:
- **Intersection Observer**: Images only load when they're about to enter the viewport (50px margin)
- **Loading States**: Skeleton placeholders while images load
- **Error Handling**: Graceful fallback UI for failed image loads
- **Smooth Transitions**: Fade-in effect when images load
- **Responsive Sizing**: Supports `sizes` attribute for responsive image loading
- **Native Lazy Loading**: Falls back to native `loading="lazy"` attribute

### OptimizedVideo
A lazy-loading video component with the following features:
- **Intersection Observer**: Videos only load when they're about to be visible (100px margin)
- **Preload Control**: Default `preload="none"` to prevent unnecessary bandwidth usage
- **Poster Images**: Shows poster image while video loads
- **Loading States**: Skeleton placeholders during video load
- **Hover-to-Load**: Videos can be set to load on hover for better UX
- **Error Handling**: Graceful fallback UI for failed video loads

## Performance Benefits

1. **Reduced Initial Load**: Images and videos only load when needed
2. **Bandwidth Savings**: Videos don't preload, saving data for users
3. **Better UX**: Loading states provide visual feedback
4. **SEO Friendly**: Proper alt text and semantic HTML
5. **Accessibility**: Error states and fallbacks for better accessibility

## Usage

```tsx
import { OptimizedImage, OptimizedVideo } from '../utils';

// Image with lazy loading
<OptimizedImage
  src="/path/to/image.jpg"
  alt="Description"
  loading="lazy"
  sizes="(max-width: 600px) 100vw, 50vw"
  sx={{ width: '100%', height: '100%' }}
/>

// Video with lazy loading
<OptimizedVideo
  src="/path/to/video.mp4"
  poster="/path/to/poster.jpg"
  alt="Video description"
  controls
  preload="none"
  sx={{ width: '100%' }}
/>
```

## Best Practices

1. Always provide meaningful `alt` text for images
2. Use appropriate `sizes` attribute for responsive images
3. Set `preload="none"` for videos that aren't immediately visible
4. Provide poster images for videos to improve perceived performance
5. Use `loading="eager"` only for above-the-fold critical images

