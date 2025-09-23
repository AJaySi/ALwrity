# BlogWriterLanding Component

A beautiful, animated landing page for the ALwrity Blog Writer that utilizes the custom background image with artistic button placement and subtle animations.

## Features

### 🎨 **Visual Design**
- **Full-screen background image** (`/blog-writer-bg.png`) with horizontal stretching (56% width) and left alignment
- **Gradient overlays** for subtle depth
- **Clean, minimal design** without decorative elements
- **Glassmorphism effects** on secondary buttons

### ✨ **Interactions**
- **Button hover effects** with smooth transitions
- **Modal interactions** with clean transitions
- **Responsive hover states** for all interactive elements

### 🚀 **Interactive Elements**
- **Primary CTA Button**: "Chat/Write with ALwrity Copilot" with gradient background
- **Secondary CTA Button**: "ALwrity Blog Writer SuperPowers" opens feature modal
- **SuperPowers Modal**: Showcases 6 key features with hover effects
- **Responsive design** that works on all screen sizes

### 🎯 **User Experience**
- **Clear messaging** about the blog writing capabilities
- **Feature showcase** in an engaging modal format
- **Clean, focused messaging** without distracting text
- **Clean transitions** between states

## Usage

```tsx
import BlogWriterLanding from './BlogWriterLanding';

<BlogWriterLanding 
  onStartWriting={() => {
    // Handle start writing action
    // This can trigger copilot interaction
  }}
/>
```

## Props

- `onStartWriting: () => void` - Callback function called when user clicks "Chat/Write with ALwrity Copilot"

## Integration

The component integrates with:
- **useCopilotTrigger hook** for copilot interaction
- **BlogWriter main component** as the initial state
- **Responsive design** that adapts to different screen sizes

## Styling

All styles are inline with CSS-in-JS approach for:
- **Better performance** (no external CSS files)
- **Component isolation** (styles don't leak)
- **Dynamic theming** (easy to modify colors/effects)
- **Animation control** (precise timing and effects)

## Accessibility

- **Semantic HTML** structure
- **Keyboard navigation** support
- **Screen reader** friendly
- **High contrast** text and buttons
- **Focus indicators** for interactive elements
