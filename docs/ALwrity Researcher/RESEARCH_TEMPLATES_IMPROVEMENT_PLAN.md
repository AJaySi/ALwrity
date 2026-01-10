# Research Templates Improvement Plan

**Date**: 2025-01-29  
**Status**: Planning & Implementation Guide

---

## 📊 Current State: Research Presets

### What We Have
- **AI-Generated Presets**: Generated from research persona based on user's onboarding data
- **Rule-Based Presets**: Fallback presets when persona doesn't exist
- **Quick Start Presets**: Displayed in ResearchTest page sidebar
- **Preset Structure**: Includes name, keywords, industry, target audience, research mode, config, icon, gradient

### Current Limitations
1. **No User-Created Templates**: Users can't save their own research configurations
2. **No Template Management**: No way to edit, delete, or organize templates
3. **No Template Sharing**: Can't share templates with team members
4. **No Template Categories**: All presets shown together, no organization
5. **No Template Analytics**: Can't see which templates are used most
6. **Limited Customization**: Presets are static, can't be modified after creation
7. **No Template Library**: No community or pre-built templates

---

## 🎯 Proposed Improvements: Research Templates System

### Phase 1: User-Created Templates (High Priority)

#### 1.1 Save Research as Template
**Feature**: Allow users to save any research configuration as a reusable template

**Implementation**:
```typescript
interface ResearchTemplate {
  id: string;
  name: string;
  description?: string;
  keywords: string;
  industry: string;
  target_audience: string;
  research_mode: ResearchMode;
  config: ResearchConfig;
  icon?: string;
  gradient?: string;
  category?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
  usage_count: number;
  is_favorite: boolean;
  is_public: boolean; // For future sharing
}
```

**UI Components**:
- "Save as Template" button in IntentConfirmationPanel (after research completes)
- Template name input dialog
- Template description (optional)
- Category/tag selection

**Backend**:
- New endpoint: `POST /api/research/templates/save`
- Store templates in database (new `research_templates` table)
- Associate with user_id

#### 1.2 Template Library UI
**Feature**: Display user's saved templates alongside AI-generated presets

**UI Components**:
- Template cards with name, description, usage count
- "Use Template" button
- "Edit Template" button
- "Delete Template" button
- "Favorite" toggle
- Search/filter templates

**Layout**:
```
┌─────────────────────────────────────┐
│ Quick Start Templates               │
├─────────────────────────────────────┤
│ [AI Preset 1] [AI Preset 2] ...    │
│                                     │
│ My Templates (5)                    │
│ [Template 1] [Template 2] ...      │
│                                     │
│ + Create New Template               │
└─────────────────────────────────────┘
```

#### 1.3 Template Management
**Feature**: Edit, delete, duplicate, and organize templates

**Actions**:
- **Edit**: Modify template name, keywords, config
- **Delete**: Remove template with confirmation
- **Duplicate**: Create copy of template
- **Favorite**: Mark frequently used templates
- **Category**: Organize into categories (e.g., "Marketing", "Technical", "Competitive Analysis")

---

### Phase 2: Enhanced Template Features (Medium Priority)

#### 2.1 Template Categories & Tags
**Feature**: Organize templates with categories and tags

**Categories**:
- Content Marketing
- Competitive Analysis
- Industry Trends
- Technical Research
- Product Research
- Custom categories

**Tags**:
- Multiple tags per template
- Filter by tags
- Tag suggestions based on keywords

#### 2.2 Template Analytics
**Feature**: Track template usage and effectiveness

**Metrics**:
- Usage count (how many times used)
- Last used date
- Success rate (research completion)
- Average research time
- Most popular templates

**UI**:
- Show usage stats on template cards
- "Most Used" section
- "Recently Used" section

#### 2.3 Smart Template Suggestions
**Feature**: AI suggests templates based on user behavior

**Logic**:
- Suggest templates based on:
  - Similar keywords used before
  - Same industry/audience
  - Time of day/week patterns
  - Recent research topics

**UI**:
- "Suggested for You" section
- "Based on your recent research" badge

---

### Phase 3: Advanced Template Features (Low Priority)

#### 3.1 Template Sharing
**Feature**: Share templates with team members or community

**Implementation**:
- Public/private toggle
- Share link generation
- Team workspace templates
- Template marketplace (future)

#### 3.2 Template Variables
**Feature**: Templates with placeholders that users can fill

**Example**:
```typescript
{
  name: "Competitive Analysis: {company}",
  keywords: "Research {company} marketing strategies and product positioning",
  // User fills in {company} when using template
}
```

**UI**:
- Variable input dialog when using template
- Pre-fill common variables from user data

#### 3.3 Template Workflows
**Feature**: Chain multiple templates together

**Use Case**:
1. Run "Industry Trends" template
2. Then run "Competitive Analysis" template
3. Then run "Content Ideas" template

**UI**:
- "Create Workflow" button
- Drag-and-drop template ordering
- Save workflow as single template

---

## 🏗️ Implementation Plan

### Step 1: Database Schema
```sql
CREATE TABLE research_templates (
  id VARCHAR(100) PRIMARY KEY,
  user_id VARCHAR(100) NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  keywords TEXT NOT NULL,
  industry VARCHAR(100),
  target_audience VARCHAR(200),
  research_mode VARCHAR(20),
  config JSON NOT NULL,
  icon VARCHAR(10),
  gradient VARCHAR(200),
  category VARCHAR(100),
  tags JSON,
  usage_count INT DEFAULT 0,
  is_favorite BOOLEAN DEFAULT FALSE,
  is_public BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_used_at DATETIME,
  INDEX idx_user_id (user_id),
  INDEX idx_category (category),
  INDEX idx_created_at (created_at)
);
```

### Step 2: Backend API Endpoints
```python
# backend/api/research/router.py

@router.post("/templates/save")
async def save_research_template(
    request: SaveTemplateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Save current research configuration as template"""
    pass

@router.get("/templates")
async def get_user_templates(
    current_user: Dict = Depends(get_current_user),
    category: Optional[str] = None,
    favorite_only: bool = False
):
    """Get user's saved templates"""
    pass

@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    request: UpdateTemplateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Update existing template"""
    pass

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete template"""
    pass

@router.post("/templates/{template_id}/use")
async def use_template(
    template_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Use template and increment usage count"""
    pass
```

### Step 3: Frontend Components

#### 3.1 TemplateCard Component
```typescript
interface TemplateCardProps {
  template: ResearchTemplate;
  onUse: (template: ResearchTemplate) => void;
  onEdit: (template: ResearchTemplate) => void;
  onDelete: (templateId: string) => void;
  onToggleFavorite: (templateId: string) => void;
}
```

#### 3.2 TemplateLibrary Component
```typescript
interface TemplateLibraryProps {
  aiPresets: ResearchPreset[];
  userTemplates: ResearchTemplate[];
  onUseTemplate: (template: ResearchTemplate | ResearchPreset) => void;
  onCreateTemplate: () => void;
}
```

#### 3.3 SaveTemplateDialog Component
```typescript
interface SaveTemplateDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (template: Partial<ResearchTemplate>) => void;
  initialData: {
    keywords: string;
    industry: string;
    target_audience: string;
    research_mode: ResearchMode;
    config: ResearchConfig;
  };
}
```

### Step 4: Integration Points

#### 4.1 IntentConfirmationPanel
- Add "Save as Template" button after research configuration is confirmed
- Show template icon if current config matches a saved template

#### 4.2 ResearchTest Page
- Replace "Quick Start Presets" with "Template Library"
- Show AI presets + user templates
- Add "Create Template" button

#### 4.3 ResearchWizard
- Accept template as initial data
- Pre-fill all fields from template
- Track template usage

---

## 📋 Implementation Checklist

### Phase 1: Core Template System
- [ ] Create database schema for `research_templates`
- [ ] Create Pydantic models for templates
- [ ] Implement backend API endpoints (save, get, update, delete, use)
- [ ] Create frontend TypeScript interfaces
- [ ] Build TemplateCard component
- [ ] Build TemplateLibrary component
- [ ] Build SaveTemplateDialog component
- [ ] Integrate "Save as Template" in IntentConfirmationPanel
- [ ] Update ResearchTest page to show templates
- [ ] Add template usage tracking

### Phase 2: Enhanced Features
- [ ] Add category system
- [ ] Add tag system
- [ ] Implement template search/filter
- [ ] Add template analytics (usage count, last used)
- [ ] Add favorite functionality
- [ ] Add template sorting (most used, recently used, alphabetical)

### Phase 3: Advanced Features
- [ ] Template sharing (public/private)
- [ ] Template variables/placeholders
- [ ] Template workflows
- [ ] Template marketplace (future)

---

## 🎨 UI/UX Design Considerations

### Template Card Design
```
┌─────────────────────────────────┐
│ 📊 Competitive Analysis    ⭐   │
│                                 │
│ Research top competitors in... │
│                                 │
│ Marketing • B2B SaaS            │
│                                 │
│ Used 12 times • Last: 2d ago   │
│                                 │
│ [Use] [Edit] [Delete]           │
└─────────────────────────────────┘
```

### Template Library Layout
```
┌─────────────────────────────────────────┐
│ Template Library                        │
├─────────────────────────────────────────┤
│ [Search templates...]                   │
│                                         │
│ Categories: [All] [Marketing] [Tech]   │
│                                         │
│ ┌─ AI-Generated Presets ───────────┐  │
│ │ [Preset 1] [Preset 2] [Preset 3] │  │
│ └───────────────────────────────────┘  │
│                                         │
│ ┌─ My Templates (5) ────────────────┐  │
│ │ [Template 1] [Template 2] ...     │  │
│ └───────────────────────────────────┘  │
│                                         │
│ [+ Create New Template]                 │
└─────────────────────────────────────────┘
```

---

## 🔄 Migration from Presets to Templates

### Backward Compatibility
- Keep AI-generated presets as "read-only templates"
- Show presets in same UI as templates
- Allow users to "Save Preset as Template" to customize

### Data Migration
- No migration needed (presets are generated on-demand)
- Templates are new feature, doesn't affect existing presets

---

## 📊 Success Metrics

### Adoption Metrics
- % of users who create at least one template
- Average templates per user
- Template usage rate (templates used / total research operations)

### Engagement Metrics
- Most used templates
- Template reuse rate
- Time saved (estimated based on template usage)

### Quality Metrics
- Research completion rate with templates vs without
- User satisfaction with templates
- Template effectiveness (research quality)

---

## 🚀 Quick Win: Minimal Viable Template System

### MVP Features (Can implement in 2-3 days)
1. **Save Template**: Button in IntentConfirmationPanel
2. **Template List**: Show user templates in ResearchTest sidebar
3. **Use Template**: Click template to pre-fill research wizard
4. **Delete Template**: Remove template with confirmation

### MVP Database
- Simple table with: id, user_id, name, keywords, industry, target_audience, research_mode, config, created_at

### MVP UI
- Simple template cards in sidebar
- "Save as Template" button
- Basic template list

---

## ✅ Next Steps

1. **Review & Approve**: Get feedback on template system design
2. **Start with MVP**: Implement minimal viable template system
3. **Iterate**: Add features based on user feedback
4. **Scale**: Add advanced features (sharing, workflows, etc.)

---

**Status**: Ready for Implementation
