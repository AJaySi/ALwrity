# Image Studio Masking Feature Analysis

## Summary

This document identifies which Image Studio operations require or would benefit from masking capabilities.

---

## Operations Requiring Masking

### ✅ **Currently Implemented**

#### 1. **Inpaint & Fix** (`inpaint`)
- **Status**: ✅ Mask Required
- **Backend Support**: Yes (`mask_bytes` parameter in `StabilityAIService.inpaint()`)
- **Frontend**: ✅ Mask editor integrated via `ImageMaskEditor`
- **Use Case**: Edit specific regions of an image with precise control
- **Mask Type**: Required (but can work without mask using prompt-only mode)

---

## Operations That Could Benefit from Optional Masking

### 🔄 **Recommended for Enhancement**

#### 2. **General Edit** (`general_edit`)
- **Status**: ✅ Optional mask now enabled
- **Backend Support**: ✅ HuggingFace image-to-image with mask support
- **Frontend**: ✅ Mask editor automatically shown
- **Use Case**: Selective editing of specific regions in prompt-based edits
- **Implementation**: Mask passed to HuggingFace `image_to_image` method (model-dependent support)

#### 3. **Search & Replace** (`search_replace`)
- **Status**: ✅ Optional mask now enabled
- **Backend Support**: ✅ Stability AI search-and-replace with mask parameter
- **Frontend**: ✅ Mask editor automatically shown
- **Use Case**: More precise object replacement when search prompt is ambiguous
- **Implementation**: Mask passed to Stability `search_and_replace` API endpoint

#### 4. **Search & Recolor** (`search_recolor`)
- **Status**: ✅ Optional mask now enabled
- **Backend Support**: ✅ Stability AI search-and-recolor with mask parameter
- **Frontend**: ✅ Mask editor automatically shown
- **Use Case**: Precise color changes when select prompt matches multiple objects
- **Implementation**: Mask passed to Stability `search_and_recolor` API endpoint

---

## Operations Not Requiring Masking

### ❌ **No Masking Needed**

#### 5. **Remove Background** (`remove_background`)
- **Reason**: Automatic subject detection, no manual masking required

#### 6. **Outpaint** (`outpaint`)
- **Reason**: Expands canvas boundaries, no selective editing needed

#### 7. **Replace Background & Relight** (`relight`)
- **Reason**: Uses reference images for background/lighting, no masking needed

#### 8. **Create Studio** (Image Generation)
- **Reason**: Generates images from scratch, no input image to mask

#### 9. **Upscale Studio** (Image Upscaling)
- **Reason**: Upscales entire image uniformly, no selective processing

---

## Current Implementation Status

### Frontend (`EditStudio.tsx`)
- ✅ Mask editor dialog integrated
- ✅ Shows "Create Mask" button when `fields.mask === true`
- ✅ Currently only enabled for `inpaint` operation

### Backend (`edit_service.py`)
- ✅ `mask_base64` parameter accepted in `EditStudioRequest`
- ✅ Mask passed to `StabilityAIService.inpaint()` for inpainting
- ⚠️ Mask not utilized for `general_edit` (HuggingFace) even though supported

---

## Recommendations

### High Priority
1. **Enable optional masking for `general_edit`**
   - Update `SUPPORTED_OPERATIONS["general_edit"]["fields"]["mask"]` to `True` (optional)
   - Ensure HuggingFace provider receives mask when provided
   - Update frontend to show mask editor for this operation

### Medium Priority
2. **Add optional masking for `search_replace`**
   - Allow mask to override or refine `search_prompt` detection
   - Update backend to use mask when provided alongside search_prompt
   - Update frontend UI to show mask option

3. **Add optional masking for `search_recolor`**
   - Allow mask to override or refine `select_prompt` selection
   - Update backend to use mask when provided alongside select_prompt
   - Update frontend UI to show mask option

### Low Priority
4. **Consider mask preview/validation**
   - Show mask overlay on base image before submission
   - Validate mask dimensions match base image
   - Provide mask editing hints/tips

---

## Technical Notes

### Mask Format
- **Format**: Grayscale image (PNG recommended)
- **Encoding**: Base64 data URL (`data:image/png;base64,...`)
- **Convention**: 
  - White pixels = region to edit/modify
  - Black pixels = region to preserve
  - Gray pixels = partial influence (for soft masks)

### Backend Mask Handling
```python
# Current pattern in edit_service.py
mask_bytes = self._decode_base64_image(request.mask_base64)
if mask_bytes:
    # Use mask in operation
    result = await stability_service.inpaint(
        image=image_bytes,
        prompt=request.prompt,
        mask=mask_bytes,  # Optional but recommended
        ...
    )
```

### Frontend Mask Editor Integration
```tsx
// Current pattern in EditStudio.tsx
<EditImageUploader
  requiresMask={fields.mask}  // Shows mask controls when true
  onOpenMaskEditor={() => setShowMaskEditor(true)}
/>

<ImageMaskEditor
  baseImage={baseImage}
  maskImage={maskImage}
  onMaskChange={(mask) => setMaskImage(mask)}
  onClose={() => setShowMaskEditor(false)}
/>
```

---

## Testing Checklist

- [x] Mask editor opens for `inpaint` operation
- [x] Mask can be drawn/erased on canvas
- [x] Mask exports as base64 grayscale image
- [x] Mask is sent to backend for inpainting
- [x] Optional mask works for `general_edit` (backend implemented)
- [x] Optional mask works for `search_replace` (backend implemented)
- [x] Optional mask works for `search_recolor` (backend implemented)
- [x] Mask editor automatically shows for all mask-enabled operations
- [ ] Mask validation (dimensions, format) - Future enhancement
- [ ] Mask preview overlay before submission - Future enhancement

---

## Related Files

- **Frontend Components**:
  - `frontend/src/components/ImageStudio/ImageMaskEditor.tsx` - Mask editor component
  - `frontend/src/components/ImageStudio/EditStudio.tsx` - Edit Studio main component
  - `frontend/src/components/ImageStudio/EditImageUploader.tsx` - Image uploader with mask support

- **Backend Services**:
  - `backend/services/image_studio/edit_service.py` - Edit operation orchestration
  - `backend/services/stability_service.py` - Stability AI integration (inpaint, erase)
  - `backend/routers/image_studio.py` - API endpoints

- **Documentation**:
  - `.cursor/rules/image-studio.mdc` - Development rules including masking guidelines

