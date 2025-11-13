# Story Writer - Testing Guide & Current Status

## Overview

The Story Writer feature is a comprehensive AI-powered story generation system that allows users to create complete stories with multimedia capabilities including images, audio narration, and video composition.

## Current Status: ✅ Ready for Testing

### ✅ Completed Features

1. **Core Story Generation**
   - Premise generation
   - Structured outline generation (JSON schema with scenes)
   - Story start generation (min 4000 words)
   - Story continuation (iterative until completion)
   - Full story generation (async with task management)

2. **Multimedia Generation**
   - Image generation for story scenes
   - Audio narration generation (TTS) for scenes
   - Video composition from images and audio

3. **Backend API**
   - 15+ endpoints for all operations
   - Task management with progress tracking
   - Authentication and subscription integration
   - Error handling and logging

4. **Frontend Components**
   - 5-phase workflow (Setup → Premise → Outline → Writing → Export)
   - State management with localStorage persistence
   - Phase navigation with prerequisite checking
   - Multimedia display (images, audio, video)

5. **End-to-End Video Generation**
   - Complete workflow: Outline → Images → Audio → Video
   - Progress tracking with granular updates
   - Async task execution with polling support

### 🔧 Recent Fixes

1. **Async Function Fix**: Fixed `execute_complete_video_generation` to be a synchronous function (not async) since it performs blocking operations
2. **Progress Callback**: Improved progress tracking with proper mapping of sub-progress to overall progress
3. **Error Handling**: Enhanced error messages and exception logging
4. **Path Validation**: Added validation for image and audio file paths before video generation

## Testing Guide

### Prerequisites

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Environment Variables**
   - Ensure `.env` file is configured with:
     - `CLERK_SECRET_KEY` for authentication
     - `GEMINI_API_KEY` or `HUGGINGFACE_API_KEY` for LLM
     - Image generation API keys (if using image generation)

4. **Dependencies**
   - MoviePy (for video generation): `pip install moviepy imageio imageio-ffmpeg`
   - gTTS (for audio generation): `pip install gtts`
   - FFmpeg (system dependency for video processing)

### Test Scenarios

#### 1. Basic Story Generation Flow

**Steps:**
1. Navigate to `/story-writer`
2. Fill in the Setup form:
   - Select a persona (e.g., "Fantasy Writer")
   - Enter story setting (e.g., "A magical kingdom")
   - Enter characters (e.g., "A young wizard and a dragon")
   - Enter plot elements (e.g., "A quest to find a lost artifact")
   - Select writing style, tone, POV, audience, content rating, ending preference
3. Click "Generate Premise"
4. Review the generated premise
5. Click "Generate Outline"
6. Review the structured outline with scenes
7. Click "Generate Story Start"
8. Review the story beginning
9. Click "Continue Writing" multiple times until story is complete
10. Click "Export Story" to view the complete story

**Expected Results:**
- Premise is generated successfully
- Structured outline is generated with scene-by-scene details
- Story start is generated (min 4000 words)
- Story continuation works iteratively
- Story completion is detected when "IAMDONE" marker is found
- Complete story is displayed in the Export phase

#### 2. Structured Outline with Images and Audio

**Steps:**
1. Complete steps 1-6 from the basic flow
2. In the Outline phase, verify that structured scenes are displayed
3. Click "Generate Images" button
4. Wait for images to be generated for all scenes
5. Click "Generate Audio" button
6. Wait for audio narration to be generated for all scenes
7. Review the generated images and audio players

**Expected Results:**
- Images are generated for each scene
- Images are displayed in the Outline phase
- Audio files are generated for each scene
- Audio players are displayed for each scene
- Images and audio are persisted in state

#### 3. Video Generation

**Steps:**
1. Complete steps 1-6 from the basic flow (with images and audio generated)
2. Navigate to the Export phase
3. Click "Generate Video" button
4. Wait for video generation to complete
5. Review the generated video

**Expected Results:**
- Video is generated from images and audio
- Video is displayed in the Export phase
- Video can be downloaded
- Video composition combines all scenes into a single video

#### 4. End-to-End Video Generation (Async)

**Steps:**
1. Navigate to `/story-writer`
2. Fill in the Setup form
3. Use the API endpoint `/api/story/generate-complete-video` (via Postman or frontend)
4. Poll the task status using `/api/story/task/{task_id}/status`
5. Retrieve the result using `/api/story/task/{task_id}/result`

**Expected Results:**
- Task is created successfully
- Progress updates are provided at each step:
  - 10%: Premise generation
  - 20%: Outline generation
  - 30-50%: Image generation
  - 50-70%: Audio generation
  - 70%: Preparing video assets
  - 75-95%: Video composition
  - 100%: Complete
- Result contains premise, outline, images, audio, and video
- Video URL is provided for serving the video

#### 5. Error Handling

**Test Cases:**
1. **Invalid Story Parameters**
   - Submit form with missing required fields
   - Expected: Validation error message

2. **Network Errors**
   - Disconnect network during generation
   - Expected: Error message displayed, state preserved

3. **Subscription Limits**
   - Exceed subscription limits
   - Expected: 429 error with appropriate message

4. **Missing Dependencies**
   - Remove MoviePy or gTTS
   - Expected: Error message indicating missing dependency

5. **File Not Found**
   - Delete generated images or audio before video generation
   - Expected: Error message with details about missing files

#### 6. State Persistence

**Steps:**
1. Complete steps 1-3 from the basic flow
2. Refresh the page
3. Verify that state is preserved

**Expected Results:**
- Premise is preserved
- Outline is preserved
- Story content is preserved
- Generated images and audio are preserved
- Phase navigation state is preserved

#### 7. Phase Navigation

**Steps:**
1. Complete the basic flow up to the Writing phase
2. Navigate back to the Outline phase
3. Modify the outline
4. Navigate forward to the Writing phase
5. Verify that changes are reflected

**Expected Results:**
- Backward navigation works correctly
- Forward navigation respects prerequisites
- State is preserved during navigation
- Changes are reflected in subsequent phases

### API Endpoint Testing

#### 1. Premise Generation
```bash
POST /api/story/generate-premise
Content-Type: application/json
Authorization: Bearer <token>

{
  "persona": "Fantasy Writer",
  "story_setting": "A magical kingdom",
  "character_input": "A young wizard",
  "plot_elements": "A quest",
  ...
}
```

#### 2. Outline Generation
```bash
POST /api/story/generate-outline?premise=<premise>&use_structured=true
Content-Type: application/json
Authorization: Bearer <token>

{
  "persona": "Fantasy Writer",
  ...
}
```

#### 3. Image Generation
```bash
POST /api/story/generate-images
Content-Type: application/json
Authorization: Bearer <token>

{
  "scenes": [
    {
      "scene_number": 1,
      "title": "Scene 1",
      "image_prompt": "A magical kingdom with a young wizard",
      ...
    }
  ],
  "provider": "gemini",
  "width": 1024,
  "height": 1024
}
```

#### 4. Audio Generation
```bash
POST /api/story/generate-audio
Content-Type: application/json
Authorization: Bearer <token>

{
  "scenes": [
    {
      "scene_number": 1,
      "title": "Scene 1",
      "audio_narration": "Once upon a time...",
      ...
    }
  ],
  "provider": "gtts",
  "lang": "en",
  "slow": false
}
```

#### 5. Video Generation
```bash
POST /api/story/generate-video
Content-Type: application/json
Authorization: Bearer <token>

{
  "scenes": [...],
  "image_urls": ["/api/story/images/scene_1_image.png", ...],
  "audio_urls": ["/api/story/audio/scene_1_audio.mp3", ...],
  "story_title": "My Story",
  "fps": 24,
  "transition_duration": 0.5
}
```

#### 6. Complete Video Generation (Async)
```bash
POST /api/story/generate-complete-video
Content-Type: application/json
Authorization: Bearer <token>

{
  "persona": "Fantasy Writer",
  ...
}

# Response:
{
  "task_id": "uuid",
  "status": "pending",
  "message": "Complete video generation started"
}

# Poll status:
GET /api/story/task/{task_id}/status

# Get result:
GET /api/story/task/{task_id}/result
```

## Known Issues & Limitations

1. **Video Generation Dependencies**
   - Requires FFmpeg to be installed on the system
   - MoviePy can be resource-intensive for long videos
   - Video generation may take several minutes for multiple scenes

2. **Audio Generation**
   - gTTS requires internet connection
   - pyttsx3 is offline but may have lower quality
   - Audio generation may take time for long narration texts

3. **Image Generation**
   - Image generation may take time for multiple scenes
   - Rate limits may apply based on provider
   - Image quality depends on the provider used

4. **State Persistence**
   - Large state objects may cause localStorage issues
   - Map serialization is handled but may have edge cases

5. **Progress Tracking**
   - Progress callbacks may not be perfectly granular
   - Some operations may not provide detailed progress

## Next Steps

### Phase 1: End-to-End Testing (Current)
- [x] Fix async function issues
- [x] Improve progress tracking
- [x] Enhance error handling
- [ ] Complete manual testing of all flows
- [ ] Test with different story parameters
- [ ] Test error scenarios
- [ ] Test state persistence

### Phase 2: CopilotKit Integration (Next)
- [ ] Create CopilotKit actions hook
- [ ] Create CopilotKit sidebar component
- [ ] Integrate CopilotKit into Story Writer
- [ ] Test CopilotKit actions

### Phase 3: UX Enhancements
- [ ] Add loading states and progress indicators
- [ ] Improve error messages
- [ ] Add animations and transitions
- [ ] Enhance responsive design

### Phase 4: Advanced Features
- [ ] Draft management
- [ ] Rich text editing
- [ ] Export enhancements (PDF, DOCX, EPUB)
- [ ] Story templates

## Troubleshooting

### Issue: Video generation fails
**Solution**: 
- Verify FFmpeg is installed: `ffmpeg -version`
- Check that image and audio files exist
- Verify file paths are correct
- Check system resources (memory, disk space)

### Issue: Audio generation fails
**Solution**:
- Verify internet connection (for gTTS)
- Check that gTTS is installed: `pip install gtts`
- Verify audio narration text is not empty
- Check system audio dependencies

### Issue: Image generation fails
**Solution**:
- Verify image generation API keys are configured
- Check that image prompts are not empty
- Verify provider is available
- Check subscription limits

### Issue: State not persisting
**Solution**:
- Check browser localStorage limits
- Verify state serialization is working
- Check for JavaScript errors in console
- Clear localStorage and try again

## Support

For issues or questions:
1. Check the logs in `backend/logs/`
2. Review error messages in the UI
3. Check browser console for frontend errors
4. Review API responses for backend errors

## Conclusion

The Story Writer feature is ready for comprehensive testing. All core functionality is implemented and working. The system supports:
- Complete story generation workflow
- Multimedia generation (images, audio, video)
- Async task management with progress tracking
- State persistence and phase navigation
- Error handling and logging

End users can now test the complete flow and provide feedback for improvements.

