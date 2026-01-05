# Image Studio Editing - UI Requirements for Model Selection

**Date**: Current Session  
**Status**: 📋 **Requirements Document**  
**Purpose**: Define UI requirements for model selection, education, and auto-routing

---

## 🎯 Core Requirements

### **1. Model Selection UI**

#### **1.1 Model Selector Component**
- **Location**: Edit Studio sidebar or main panel
- **Type**: Dropdown/Select with search capability
- **Display**: 
  - Model name
  - Cost per edit
  - Quality tier badge (Budget/Mid/Premium)
  - Quick info icon (tooltip)

#### **1.2 Model Information Panel**
- **Trigger**: Click on info icon or "Learn More" button
- **Content**:
  - Model description
  - Use cases
  - Cost details
  - Max resolution
  - Special features (multi-image, typography, etc.)
  - Comparison with other models

#### **1.3 Model Comparison View**
- **Trigger**: "Compare Models" button
- **Display**: Side-by-side comparison table
- **Columns**: Model name, Cost, Max Res, Features, Best For
- **Filter**: By tier (Budget/Mid/Premium), by use case

---

## 🔄 Auto-Detection & Routing

### **2.1 Default Behavior (No Model Selected)**
- **Auto-select**: Best model based on:
  1. **Operation type**: Match model capabilities to operation
  2. **Image resolution**: Select model that supports input resolution
  3. **User tier**: Prefer budget models for free users, premium for pro users
  4. **Cost optimization**: Default to lowest cost model that meets requirements

### **2.2 Smart Recommendations**
- **Display**: "Recommended for you" badge on auto-selected model
- **Reason**: Show why this model was selected (e.g., "Best quality for 4K images")

### **2.3 Fallback Logic**
- **If no model matches**: Use first available model
- **If model unavailable**: Show error with alternative suggestions
- **If user has insufficient credits**: Suggest budget alternative

---

## 📚 User Education

### **3.1 Model Information Cards**

Each model should display:

```
┌─────────────────────────────────────┐
│ [Model Name] [Tier Badge]          │
│                                     │
│ 💰 Cost: $0.02 per edit            │
│ 📐 Max Resolution: 1536×1536        │
│ ⭐ Best For:                        │
│   • Quick edits                     │
│   • Budget-conscious projects       │
│   • Multi-image editing             │
│                                     │
│ ✨ Features:                        │
│   • ControlNet support             │
│   • Bilingual (CN/EN)              │
│   • Up to 3 reference images        │
│                                     │
│ [Learn More] [Select]               │
└─────────────────────────────────────┘
```

### **3.2 Use Case Examples**

For each model, show:
- **Example prompts**: "Change background to beach", "Add text overlay"
- **Before/After examples**: Visual examples (if available)
- **When to use**: Clear guidance on when this model is best

### **3.3 Cost Transparency**

- **Show estimated cost**: Before processing
- **Cost breakdown**: Per operation
- **Subscription impact**: How many edits user can make with current credits
- **Cost comparison**: "This costs 2x more but provides 4K quality"

---

## 🎨 UI Components Needed

### **4.1 ModelSelector Component**
```typescript
interface ModelSelectorProps {
  operation: string;
  imageResolution?: { width: number; height: number };
  userTier?: 'free' | 'pro' | 'enterprise';
  onModelSelect: (modelId: string) => void;
  selectedModel?: string;
}
```

**Features**:
- Search/filter models
- Group by tier
- Show recommendations
- Display cost and features

### **4.2 ModelInfoCard Component**
```typescript
interface ModelInfoCardProps {
  model: EditingModel;
  isSelected: boolean;
  isRecommended: boolean;
  onSelect: () => void;
  onLearnMore: () => void;
}
```

**Features**:
- Model details
- Cost display
- Feature badges
- Comparison button

### **4.3 ModelComparisonDialog Component**
```typescript
interface ModelComparisonDialogProps {
  models: EditingModel[];
  open: boolean;
  onClose: () => void;
  onSelect: (modelId: string) => void;
}
```

**Features**:
- Side-by-side comparison
- Filterable table
- Sortable columns
- Quick select

### **4.4 ModelRecommendationBadge Component**
```typescript
interface ModelRecommendationBadgeProps {
  reason: string;
  model: EditingModel;
}
```

**Features**:
- Show recommendation reason
- Link to model info
- Dismissible

---

## 🔧 Backend API Requirements

### **5.1 Get Available Models Endpoint**
```
GET /api/image-studio/edit/models
Query params:
  - operation?: string (filter by operation type)
  - tier?: 'budget' | 'mid' | 'premium'
  - min_resolution?: number
  - max_cost?: number

Response:
{
  "models": [
    {
      "id": "qwen-edit-plus",
      "name": "Qwen Image Edit Plus",
      "cost": 0.02,
      "tier": "budget",
      "max_resolution": [1536, 1536],
      "capabilities": ["general_edit", "multi_image"],
      "description": "...",
      "use_cases": ["...", "..."],
      "features": ["ControlNet", "Bilingual"]
    }
  ],
  "recommended": {
    "model_id": "qwen-edit-plus",
    "reason": "Best quality for budget tier"
  }
}
```

### **5.2 Get Model Recommendations Endpoint**
```
POST /api/image-studio/edit/recommend
Body:
{
  "operation": "general_edit",
  "image_resolution": { "width": 1024, "height": 1024 },
  "user_tier": "free",
  "preferences": {
    "prioritize_cost": true,
    "prioritize_quality": false
  }
}

Response:
{
  "recommended_model": "qwen-edit",
  "reason": "Lowest cost option that supports your image resolution",
  "alternatives": [
    {
      "model_id": "qwen-edit-plus",
      "reason": "Better quality for $0.02 more"
    }
  ]
}
```

---

## 📊 Model Data Structure

### **6.1 EditingModel Interface**
```typescript
interface EditingModel {
  id: string;
  name: string;
  description: string;
  cost: number;
  cost_8k?: number; // For models with tiered pricing
  tier: 'budget' | 'mid' | 'premium';
  max_resolution: [number, number];
  capabilities: string[];
  use_cases: string[];
  features: string[];
  supports_multi_image: boolean;
  supports_controlnet: boolean;
  languages: string[];
  api_params: {
    uses_size: boolean;
    uses_aspect_ratio: boolean;
    uses_resolution: boolean;
    supports_guidance_scale: boolean;
    supports_seed: boolean;
  };
}
```

---

## 🎯 User Experience Flow

### **7.1 First-Time User**
1. User opens Edit Studio
2. System auto-selects recommended model
3. Shows "Recommended for you" badge with explanation
4. User can click "Why this model?" to learn more
5. User can change model if desired

### **7.2 Returning User**
1. User opens Edit Studio
2. System remembers last selected model (if applicable)
3. Shows last used model as default
4. User can change model anytime

### **7.3 Model Selection Flow**
1. User clicks model selector
2. Sees list of available models grouped by tier
3. Can filter by cost, resolution, features
4. Can click "Compare" to see side-by-side
5. Selects model
6. System shows estimated cost
7. User confirms and proceeds

---

## 📝 Implementation Checklist

### **Backend**
- [ ] Create `/api/image-studio/edit/models` endpoint
- [ ] Create `/api/image-studio/edit/recommend` endpoint
- [ ] Add model metadata to `WaveSpeedEditProvider.get_available_models()`
- [ ] Implement recommendation logic
- [ ] Add model selection to `EditStudioService`

### **Frontend**
- [ ] Create `ModelSelector` component
- [ ] Create `ModelInfoCard` component
- [ ] Create `ModelComparisonDialog` component
- [ ] Create `ModelRecommendationBadge` component
- [ ] Integrate into `EditStudio.tsx`
- [ ] Add model selection to request payload
- [ ] Display cost estimate before processing
- [ ] Show model info tooltips

### **Documentation**
- [ ] Create model comparison guide
- [ ] Add use case examples for each model
- [ ] Document recommendation algorithm
- [ ] Create user guide for model selection

---

## 🎨 Design Considerations

### **8.1 Visual Hierarchy**
- **Primary**: Selected model (highlighted)
- **Secondary**: Recommended model (badge)
- **Tertiary**: Other available models

### **8.2 Information Density**
- **Compact view**: Model name, cost, tier badge
- **Expanded view**: Full details, use cases, features
- **Comparison view**: Side-by-side table

### **8.3 Accessibility**
- Keyboard navigation
- Screen reader support
- Clear labels and descriptions
- Color contrast for badges

---

*Ready for implementation - Backend API and recommendation logic should be completed first*
