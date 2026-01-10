# Research Dashboard

## Overview

The Research Dashboard (formerly ResearchTest) is a refactored, modular implementation of the AI-Powered Research Lab. It provides enterprise-grade research intelligence with a clean, maintainable architecture.

## Folder Structure

```
ResearchDashboard/
├── components/          # UI components
│   ├── Header.tsx      # Dashboard header with title and user badge
│   ├── LeftPanel.tsx   # Container for left sidebar components
│   ├── PresetsCard.tsx # Quick start presets display
│   ├── DebugConsole.tsx # Debug panel for development
│   ├── FooterStats.tsx # Research statistics footer
│   └── PersonaDetailsModal.tsx # Persona details modal
├── hooks/              # Custom React hooks
│   ├── useProjectRestoration.ts  # Handles project restoration from localStorage
│   ├── usePersonaManagement.ts   # Manages research persona state
│   └── useCompetitorManagement.ts # Manages competitor analysis modal
├── utils/              # Utility functions
│   ├── presetUtils.ts  # Preset generation utilities
│   └── projectRestoration.ts # Project restoration utilities
├── types.ts            # TypeScript type definitions
├── constants.ts        # Constants (sample presets, etc.)
├── styles.ts           # Shared CSS styles
├── ResearchDashboard.tsx # Main component
├── index.ts            # Module exports
└── README.md           # This file
```

## Architecture

### Component Hierarchy

```
ResearchDashboard
├── Header
│   ├── Title & Description
│   ├── My Projects Button
│   └── UserBadge
├── LeftPanel
│   ├── PresetsCard
│   └── DebugConsole
├── ResearchWizard (from components/Research)
└── FooterStats (conditional)
```

### State Management

State is managed through custom hooks:

- **useProjectRestoration**: Handles restoration of saved research projects
- **usePersonaManagement**: Manages research persona loading, generation, and display
- **useCompetitorManagement**: Handles competitor analysis modal state

### Key Features

1. **Modular Components**: Each UI section is a separate, reusable component
2. **Custom Hooks**: Business logic separated into focused hooks
3. **Type Safety**: Comprehensive TypeScript types
4. **Maintainability**: Clear separation of concerns
5. **Extensibility**: Easy to add new features

## Usage

### Import

```typescript
import ResearchDashboard from './pages/ResearchDashboard';
// or
import { ResearchDashboard } from './pages/ResearchDashboard';
```

### Routes

The component is available at:
- `/research-test` (backward compatibility)
- `/research-dashboard` (primary route)
- `/alwrity-researcher` (alternative route)

## Migration Notes

The old `ResearchTest.tsx` file has been replaced with this modular structure. All functionality has been preserved:

- ✅ Project restoration from localStorage
- ✅ Research persona management
- ✅ Competitor analysis modal
- ✅ Preset management
- ✅ Debug console
- ✅ Footer statistics
- ✅ All modals and interactions

## Development Guidelines

### Adding New Features

1. **New UI Component**: Add to `components/` folder
2. **New Hook**: Add to `hooks/` folder
3. **New Utility**: Add to `utils/` folder
4. **New Type**: Add to `types.ts`
5. **New Constant**: Add to `constants.ts`

### Best Practices

- Keep components focused and single-purpose
- Extract business logic into hooks
- Use TypeScript types for all props and state
- Follow the existing naming conventions
- Add JSDoc comments for complex functions

## File Size Comparison

- **Before**: `ResearchTest.tsx` - 1,541 lines (monolithic)
- **After**: Modular structure with largest file ~200 lines

## Benefits

1. **Maintainability**: Easier to find and fix bugs
2. **Testability**: Components and hooks can be tested independently
3. **Reusability**: Components can be reused in other parts of the app
4. **Readability**: Smaller files are easier to understand
5. **Collaboration**: Multiple developers can work on different parts simultaneously
