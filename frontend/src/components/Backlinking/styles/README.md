# Backlinking Styles - AI Design System

## Overview

This directory contains the complete AI-themed styling system for the backlinking feature. All styles are feature-contained and use a futuristic AI design system with neural glows, quantum effects, and enterprise-grade animations.

## Architecture

### Feature Containment
- **Theme Isolation**: `BacklinkingThemeProvider` prevents style leakage
- **CSS Scoping**: Unique class names and CSS custom properties
- **No Global Impact**: Styles only affect backlinking components

### File Structure
```
styles/
├── index.ts                 # Main exports
├── theme.ts                 # Material-UI theme overrides
├── backlinkingStyles.ts     # CSS-in-JS style objects
├── components.ts            # Styled Material-UI components
├── hooks.ts                 # Theme utilities
├── ai-animations.css        # Keyframe animations
├── BacklinkingThemeProvider.tsx # Theme provider
└── README.md               # This file
```

## Usage

### Basic Component Styling
```typescript
import { BacklinkingStyles } from '../styles';
import { CampaignCard, GradientButton } from '../styles/components';

// Use predefined styles
<Box sx={BacklinkingStyles.container}>
  <CampaignCard elevation={3}>
    <Typography sx={BacklinkingStyles.cardTitle}>
      AI Campaign
    </Typography>
  </CampaignCard>

  <GradientButton variant="contained">
    Start AI Research
  </GradientButton>
</Box>
```

### Theme Access
```typescript
import { useTheme } from '@mui/material/styles';

const MyComponent = () => {
  const theme = useTheme();

  return (
    <Box sx={{
      backgroundColor: theme.palette.background.default,
      border: `1px solid ${theme.palette.primary.main}`,
    }}>
      Themed Content
    </Box>
  );
};
```

### Animation Classes
```typescript
// Apply CSS animation classes
<Box className="neural-pulse">
  Pulsing Element
</Box>

<Box className="quantum-glow">
  Glowing Effect
</Box>
```

## Design System

### Color Palette
```typescript
theme.palette = {
  primary: { main: '#60A5FA' },    // Electric Blue
  secondary: { main: '#A855F7' },  // Neural Purple
  accent: '#06B6D4',               // Quantum Cyan
  background: {
    default: '#0F172A',            // Dark AI background
    paper: '#1E293B',              // Card backgrounds
  }
}
```

### CSS Custom Properties
```css
:root {
  --primary: 217 91% 60%;
  --secondary: 260 85% 55%;
  --accent: 180 100% 50%;

  --gradient-neural: linear-gradient(45deg, hsl(var(--primary)), hsl(var(--accent)), hsl(var(--secondary)));
  --gradient-quantum: linear-gradient(90deg, hsl(var(--accent)), hsl(var(--primary)), hsl(var(--secondary)));

  --pulse-primary: 0 0 30px hsl(var(--primary) / 0.6);
  --pulse-secondary: 0 0 30px hsl(var(--secondary) / 0.6);
}
```

## Available Components

### Layout Components
- `BacklinkingStyles.container` - Main dashboard container
- `BacklinkingStyles.header` - AI-themed header
- `BacklinkingStyles.cardGrid` - Responsive card grid

### UI Components
- `CampaignCard` - Neural glow campaign cards
- `GradientButton` - Quantum gradient buttons
- `BacklinkingTextField` - AI-themed input fields
- `StatusChip` - Dynamic status indicators
- `AnimatedIconButton` - Floating action buttons

### Utility Classes
- `.neural-glow` - Primary glow effect
- `.quantum-glow` - Multi-layer quantum shadows
- `.enterprise-card` - Glass morphism cards
- `.ai-gradient` - Neural gradient background
- `.neural-pulse` - Pulsing animation
- `.quantum-pulse` - Quantum glow animation

## Animations

### Available Keyframes
```css
@keyframes neural-pulse    /* Scale + opacity pulsing */
@keyframes quantum-pulse   /* Multi-stage quantum effects */
@keyframes glow-pulse      /* Enterprise glow cycling */
@keyframes data-flow       /* Streaming data effect */
@keyframes ai-float        /* Floating elements */
@keyframes matrix-rain     /* Matrix-style falling */
@keyframes enterprise-glow /* Advanced enterprise pulsing */
```

### Performance Tips
- Use `transform` and `opacity` for smooth animations
- Apply animations via CSS classes, not inline styles
- Respect `prefers-reduced-motion` user preference

## Adding New Styles

### 1. Component Styles
Add to `backlinkingStyles.ts`:
```typescript
export const BacklinkingStyles = {
  // ... existing styles
  newComponent: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
  },
};
```

### 2. Styled Components
Add to `components.ts`:
```typescript
export const NewStyledComponent = styled(MaterialComponent)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  // ... styles
}));
```

### 3. Theme Extensions
Modify `theme.ts` for theme-level changes:
```typescript
export const BacklinkingTheme: ThemeOptions = {
  // ... existing theme
  components: {
    MuiNewComponent: {
      styleOverrides: {
        root: {
          // Custom component overrides
        },
      },
    },
  },
};
```

## Best Practices

### Style Organization
- **Centralize**: Use `backlinkingStyles.ts` for reusable styles
- **Component-specific**: Use `sx` prop for unique component styles
- **Theme variables**: Always use `theme.palette.*` instead of hard-coded colors
- **Consistent naming**: Follow existing naming patterns

### Performance
- **Stable references**: Ensure style objects don't cause re-renders
- **CSS-in-JS**: Leverage Material-UI's optimized style injection
- **Bundle optimization**: Unused styles are automatically tree-shaken

### Accessibility
- **Color contrast**: All combinations meet WCAG AA standards
- **Animation preferences**: Respect user motion preferences
- **Focus indicators**: Clear keyboard navigation support

## Integration

### Theme Provider
```typescript
import { BacklinkingThemeProvider } from './styles';

const BacklinkingFeature = () => (
  <BacklinkingThemeProvider>
    <BacklinkingDashboard />
  </BacklinkingThemeProvider>
);
```

### Style Imports
```typescript
// Import everything needed
import {
  BacklinkingStyles,
  CampaignCard,
  GradientButton,
  useBacklinkingTheme,
} from '../styles';
```

## Maintenance

### Regular Updates
- Review color contrast annually
- Update animations based on user feedback
- Add new styled components as needed
- Maintain CSS custom property consistency

### Breaking Changes
- Document any theme or style API changes
- Provide migration guides for component updates
- Test all components after style system changes

## Troubleshooting

### Common Issues
- **Styles not applying**: Check theme provider wrapping
- **Animations not working**: Verify CSS class application
- **Color inconsistencies**: Use theme.palette instead of hard-coded values
- **Performance issues**: Check for style object recreation

### Debug Tools
- Use browser dev tools to inspect computed styles
- Check Material-UI theme in React dev tools
- Verify CSS custom properties in computed styles panel