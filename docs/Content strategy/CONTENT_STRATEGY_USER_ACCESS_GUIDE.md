# Content Strategy - User Access Guide

## 🎯 **Overview**

This document outlines all the different ways end users can access the Content Strategy feature in ALwrity. The Content Strategy feature is accessible through multiple entry points, providing flexibility for different user workflows.

**Last Updated**: January 2025

---

## 📍 **Primary Access Methods**

### **1. Direct URL Navigation** ✅

**Route**: `/content-planning`

**How to Access**:
- Type `/content-planning` in the browser address bar
- Content Strategy is the **first tab** (index 0) in the Content Planning Dashboard
- Tab label: **"CONTENT STRATEGY"** with Psychology icon (🧠)

**User Flow**:
```
User → Types /content-planning → Content Planning Dashboard → Content Strategy Tab (Active by default)
```

**Code Reference**:
```478:478:frontend/src/App.tsx
<Route path="/content-planning" element={<ProtectedRoute><ContentPlanningDashboard /></ProtectedRoute>} />
```

---

### **2. Main Dashboard Navigation** ✅

**Entry Points from Main Dashboard**:

#### **A. Analyze Pillar Tasks**
- **Location**: Main Dashboard → Analyze Pillar → Task Chips
- **Tasks that link to Content Strategy**:
  1. **"Review content performance"**
     - Description: "Analyze last week's content engagement metrics"
     - Action: Navigates to `/content-planning-dashboard`
     - Priority: High
     - Estimated Time: 20 minutes
  
  2. **"Check strategy alignment"**
     - Description: "Review content strategy against performance data"
     - Action: Navigates to `/content-planning-dashboard`
     - Priority: High
     - Estimated Time: 15 minutes

**Code Reference**:
```38:58:frontend/src/components/MainDashboard/components/AnalyzePillarChips.tsx
actionUrl: '/content-planning-dashboard',
action: () => navigate('/content-planning-dashboard')
```

#### **B. Plan Pillar Tasks**
- **Location**: Main Dashboard → Plan Pillar → Task Chips
- **Tasks that link to Content Strategy**:
  1. **"Create Weekly Content Calendar"**
     - Description: "Plan and schedule content for the upcoming week"
     - Action: Navigates to `/content-planning-dashboard`
     - Priority: High
     - Estimated Time: 20 minutes

**Code Reference**:
```116:116:frontend/src/components/MainDashboard/components/PillarData.tsx
actionUrl: '/content-planning-dashboard',
```

#### **C. Engage Pillar Tasks**
- **Location**: Main Dashboard → Engage Pillar → Task Chips
- **Tasks that link to Content Strategy**:
  - Various engagement tasks that navigate to `/content-planning-dashboard`

**Note**: The route `/content-planning-dashboard` appears to be an alias or redirect to `/content-planning`

---

### **3. Content Planning Dashboard Tabs** ✅

**Location**: Content Planning Dashboard → Tabs Navigation

**Tab Structure**:
1. **CONTENT STRATEGY** (Tab 0) - **This is the Content Strategy feature**
   - Icon: Psychology (🧠)
   - Component: `ContentStrategyTab`
   - Default active tab when dashboard loads

2. Calendar (Tab 1)
3. Analytics (Tab 2)
4. Gap Analysis (Tab 3)
5. Create (Tab 4)

**Code Reference**:
```162:168:frontend/src/components/ContentPlanningDashboard/ContentPlanningDashboard.tsx
const tabs = [
  { label: 'CONTENT STRATEGY', icon: <StrategyIcon />, component: <ContentStrategyTab /> },
  { label: 'CALENDAR', icon: <CalendarIcon />, component: <CalendarTab /> },
  { label: 'ANALYTICS', icon: <AnalyticsIcon />, component: <AnalyticsTab /> },
  { label: 'GAP ANALYSIS', icon: <SearchIcon />, component: <GapAnalysisTab /> },
  { label: 'CREATE', icon: <CreateIcon />, component: <CreateTab /> }
];
```

**How to Access**:
- Navigate to `/content-planning`
- Click on the **"CONTENT STRATEGY"** tab (first tab)
- Or use programmatic navigation with `activeTab: 0` in route state

---

### **4. Programmatic Navigation with State** ✅

**Method**: Navigation with route state to set active tab

**Example Navigation**:
```typescript
navigate('/content-planning', { 
  state: { 
    activeTab: 0, // 0 = Content Strategy tab
    fromStrategyBuilder: true 
  }
});
```

**Use Cases**:
1. **From Strategy Builder**: After creating a strategy, navigate to review it
2. **From Calendar Wizard**: After calendar generation, navigate back to strategy
3. **From Other Features**: Any feature can navigate directly to Content Strategy tab

**Code Reference**:
```126:130:frontend/src/components/ContentPlanningDashboard/ContentPlanningDashboard.tsx
// Handle navigation state for active tab
useEffect(() => {
  if (location.state?.activeTab !== undefined) {
    setActiveTab(location.state.activeTab);
  }
}, [location.state]);
```

---

### **5. Strategy Builder Integration** ✅

**Location**: Content Planning Dashboard → Content Strategy Tab → Strategy Builder

**Access Flow**:
1. Navigate to `/content-planning`
2. Content Strategy tab is active by default
3. If no strategy exists, user sees:
   - **"Create Strategy"** button
   - **Strategy Onboarding Dialog**
   - Option to build a new strategy

4. If strategy exists, user sees:
   - **Strategy Intelligence Tab** with strategy details
   - **Review and Activate** options
   - **Edit Strategy** button

**Code Reference**:
```22:100:frontend/src/components/ContentPlanningDashboard/tabs/ContentStrategyTab.tsx
const ContentStrategyTab: React.FC = () => {
  // ... strategy loading logic
  // Shows StrategyIntelligenceTab or StrategyOnboardingDialog
}
```

---

### **6. Strategy Activation Flow** ✅

**Location**: Content Strategy Tab → Strategy Activation

**Access Flow**:
1. User reviews strategy in Content Strategy tab
2. Clicks **"Activate Strategy"** button
3. Strategy activation modal appears
4. After activation, user can:
   - Navigate to Calendar Wizard (automatic)
   - Return to Content Strategy tab
   - View Analytics tab

**Code Reference**:
```211:240:frontend/src/services/navigationOrchestrator.ts
handleStrategyActivationSuccess(strategyId: string, strategyData: any): void {
  // Navigate to analytics page first to show monitoring setup
  navigate('/content-planning', { 
    state: { 
      activeTab: 2, // Analytics tab
      strategyContext,
      fromStrategyActivation: true,
      showMonitoringSetup: true
    }
  });
  
  // Also preserve context for calendar wizard navigation
  this.navigateToCalendarWizard(strategyId, strategyContext);
}
```

---

### **7. Calendar Wizard Integration** ✅

**Location**: Calendar Tab → Calendar Generation Wizard

**Access Flow**:
1. Navigate to `/content-planning`
2. Click **"CALENDAR"** tab
3. Click **"Generate Calendar"** or **"Create Calendar"**
4. Calendar Wizard opens
5. Wizard auto-populates from **Active Strategy**
6. User can navigate back to Content Strategy tab to review/update strategy

**Integration Points**:
- Calendar wizard uses active strategy data
- Strategy context is preserved during calendar generation
- User can navigate between Strategy and Calendar tabs seamlessly

---

### **8. Tool Categories / Feature Discovery** ⚠️

**Location**: Tool Categories Data (Potential future feature)

**Note**: There's a reference to "Strategy Dashboard" in tool categories:
```374:380:frontend/src/data/toolCategories.ts
{
  name: 'Strategy Dashboard',
  description: 'Content strategy planning and performance overview',
  icon: React.createElement(StrategyIcon),
  status: 'beta',
  path: '/strategy-dashboard',
  features: ['Content Planning', 'Performance Overview', 'Goal Tracking', 'ROI Analysis', 'Strategic Insights'],
  isHighlighted: true
}
```

**Status**: ⚠️ This route (`/strategy-dashboard`) is **not currently implemented** in App.tsx routes. It may be a planned feature or legacy reference.

**Current Implementation**: Use `/content-planning` instead.

---

## 🔄 **Navigation Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ACCESS POINTS                        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Direct URL    │   │ Main Dashboard│   │ Other Features│
│ /content-     │   │ Task Chips    │   │ (Programmatic)│
│ planning      │   │               │   │               │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Content Planning        │
              │ Dashboard               │
              └─────────────┬───────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ CONTENT STRATEGY Tab    │
              │ (Tab 0 - Default)       │
              └─────────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ No Strategy   │   │ Has Strategy  │   │ Strategy      │
│ → Create New  │   │ → Review/Edit │   │ Activation    │
└───────────────┘   └───────────────┘   └───────┬───────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────┐
                                    │ Calendar Wizard         │
                                    │ (Auto-populated from    │
                                    │  Active Strategy)       │
                                    └─────────────────────────┘
```

---

## 📋 **Summary of Access Methods**

| # | Access Method | Route/Path | User Action | Status |
|---|--------------|------------|-------------|--------|
| 1 | Direct URL | `/content-planning` | Type URL in browser | ✅ Active |
| 2 | Main Dashboard - Analyze Tasks | `/content-planning-dashboard` | Click task chip | ✅ Active |
| 3 | Main Dashboard - Plan Tasks | `/content-planning-dashboard` | Click task chip | ✅ Active |
| 4 | Main Dashboard - Engage Tasks | `/content-planning-dashboard` | Click task chip | ✅ Active |
| 5 | Content Planning Dashboard Tab | Tab 0 (Content Strategy) | Click tab | ✅ Active |
| 6 | Programmatic Navigation | `/content-planning?activeTab=0` | Code navigation | ✅ Active |
| 7 | Strategy Builder | Within Content Strategy Tab | Create/Edit strategy | ✅ Active |
| 8 | Strategy Activation | Within Content Strategy Tab | Activate strategy | ✅ Active |
| 9 | Calendar Integration | Calendar Tab → Strategy | Navigate between tabs | ✅ Active |
| 10 | Tool Categories | `/strategy-dashboard` | (Not implemented) | ⚠️ Not Active |

---

## 🎯 **Recommended User Flows**

### **Flow 1: First-Time User**
```
1. Complete Onboarding
2. Navigate to Main Dashboard
3. Click "Create Strategy" or task chip
4. → Content Planning Dashboard opens
5. → Content Strategy Tab is active
6. → Strategy Onboarding Dialog appears
7. → User creates first strategy
```

### **Flow 2: Returning User with Strategy**
```
1. Navigate to /content-planning
2. → Content Strategy Tab is active
3. → Strategy Intelligence Tab shows existing strategy
4. → User can review, edit, or activate strategy
```

### **Flow 3: Strategy to Calendar**
```
1. Navigate to Content Strategy Tab
2. Review/Activate strategy
3. Click "Generate Calendar" or navigate to Calendar Tab
4. → Calendar Wizard opens
5. → Auto-populated from Active Strategy
6. → Generate calendar
```

### **Flow 4: Task-Driven Access**
```
1. Main Dashboard shows task chips
2. User clicks "Review content performance" or similar task
3. → Navigates to Content Planning Dashboard
4. → Content Strategy Tab (or appropriate tab) is active
5. → User completes task
```

---

## 🔧 **Technical Details**

### **Route Configuration**
- **Primary Route**: `/content-planning`
- **Component**: `ContentPlanningDashboard`
- **Tab Index**: 0 (Content Strategy)
- **Protected Route**: Yes (requires authentication)

### **State Management**
- **Tab State**: Managed in `ContentPlanningDashboard` component
- **Strategy State**: Managed in `contentPlanningStore` (Zustand)
- **Navigation State**: Uses React Router `location.state`

### **Context Preservation**
- **Strategy Context**: Preserved via `StrategyCalendarContext`
- **Session Storage**: Used for cross-navigation state
- **Route State**: Used for tab activation

---

## 📝 **Notes for Developers**

1. **Route Aliases**: `/content-planning-dashboard` appears in some components but may redirect to `/content-planning`
2. **Tab Indexing**: Content Strategy is always tab index 0
3. **Default Tab**: Content Strategy tab is active by default when dashboard loads
4. **State Navigation**: Use `location.state.activeTab` to programmatically set active tab
5. **Strategy Context**: Strategy data is preserved across navigation via context and session storage

---

## 🚀 **Future Enhancements**

Potential improvements based on codebase analysis:

1. **Tool Categories Integration**: Implement `/strategy-dashboard` route if needed
2. **Sidebar Navigation**: Add Content Strategy to main navigation sidebar
3. **Quick Access Menu**: Add Content Strategy to quick access menu
4. **Keyboard Shortcuts**: Add keyboard shortcuts for quick navigation
5. **Breadcrumb Navigation**: Add breadcrumbs for better navigation context

---

**Last Updated**: January 2025  
**Document Status**: Active  
**Review Frequency**: Quarterly
