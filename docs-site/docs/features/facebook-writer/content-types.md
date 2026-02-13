# Facebook Writer Content Types

Comprehensive guide to all Facebook content types supported by ALwrity Facebook Writer, including detailed specifications, use cases, and optimization strategies.

## Overview

Facebook Writer supports a comprehensive ecosystem of content types, from traditional posts to advanced multimedia formats. Each content type is optimized for Facebook's algorithm and audience behavior patterns.

## Core Content Types

### Facebook Posts

#### Standard Posts
Traditional Facebook posts with text, images, and links optimized for maximum engagement.

**Specifications:**
- **Character Limit**: 63,206 characters
- **Optimal Length**: 100-150 words for engagement
- **Image Formats**: JPG, PNG, GIF (up to 4MB)
- **Video Support**: Up to 240 minutes, various formats

**Content Structure:**
```json
{
  "hook": "Attention-grabbing opening (first 20 words)",
  "body": "Main content with value proposition",
  "call_to_action": "Clear next step for readers",
  "hashtags": "2-3 relevant hashtags",
  "visual_element": "Image or video that supports the message"
}
```

**Optimization Strategies:**
- **Hook Strength**: First 20 words determine 80% of engagement
- **Value First**: Provide immediate value before asking for engagement
- **Question Integration**: Include questions to boost comments by 40%
- **Timing**: Post when audience is most active (typically weekdays 2-4 PM)

#### Link Posts
Posts that drive traffic to external content with compelling link previews.

**Best Practices:**
- **Compelling Hook**: Make the link preview irresistible
- **Value Proposition**: Clearly state what readers will gain
- **Trust Signals**: Include credibility indicators
- **Mobile Optimization**: Ensure link works perfectly on mobile

### Facebook Stories

#### Ephemeral Content
15-second temporary content designed for immediate engagement and community building.

**Story Types:**

##### Interactive Stories
```json
{
  "type": "interactive",
  "elements": [
    {
      "type": "question",
      "question": "What's your biggest remote work challenge?",
      "sticker_style": "modern_minimal"
    },
    {
      "type": "poll",
      "question": "Coffee first or straight to work?",
      "options": ["Coffee ☕", "Work 💼"],
      "colors": ["#8B4513", "#4A90E2"]
    }
  ],
  "background": "gradient_sunset",
  "music": "upbeat_motivational"
}
```

##### Countdown Stories
Build anticipation for upcoming events, launches, or deadlines.

**Use Cases:**
- Product launches
- Event promotions
- Limited-time offers
- Seasonal campaigns

##### Q&A Stories
Live interaction features for community engagement.

**Implementation:**
- **Question Submission**: Allow audience to submit questions
- **Live Responses**: Answer questions in real-time
- **Follow-up Content**: Create posts from popular questions

### Facebook Reels

#### Short-Form Video Content
15-60 second videos optimized for Facebook's algorithm and mobile viewing.

**Technical Specifications:**
- **Duration**: 15 seconds to 10 minutes (Reels optimized for 15-60 seconds)
- **Aspect Ratio**: 9:16 (vertical) recommended
- **Resolution**: 720p minimum, 1080p optimal
- **Format**: MP4 preferred
- **File Size**: Up to 4GB

#### Reel Content Strategy

##### Hook-Driven Structure
```
Seconds 0-3: Hook (80% of view decisions made here)
Seconds 3-8: Build interest and value
Seconds 8-12: Call to action or key takeaway
Seconds 12+: End screen with engagement prompt
```

##### Content Categories

**Educational Reels:**
- How-to tutorials
- Industry insights
- Skill-building content
- Problem-solution format

**Entertainment Reels:**
- Behind-the-scenes content
- Fun challenges
- Brand personality showcases
- User-generated content highlights

**Promotional Reels:**
- Product demonstrations
- Feature spotlights
- Customer testimonials
- Limited-time offers

#### Reel Optimization

**Algorithm Factors:**
- **Watch Time**: Complete views heavily weighted
- **Engagement**: Likes, comments, shares, saves
- **Re-shareability**: Content that viewers want to share
- **Audio Quality**: Clear audio with trending sounds
- **Thumbnail Appeal**: Compelling first frame

**Performance Metrics:**
- **Average View Duration**: Target 80% of video length
- **Engagement Rate**: Comments + shares per 1000 views
- **Completion Rate**: Percentage who watch to end
- **Share Rate**: How often content is shared

### Carousel Posts

#### Multi-Image Storytelling
Up to 10 images in a single post that tell a progressive story or showcase multiple items.

**Carousel Structure:**
```json
{
  "cover_slide": {
    "image": "attention_grabbing_image.jpg",
    "text": "Hook and main value proposition",
    "cta": "Swipe to see more"
  },
  "content_slides": [
    {
      "image": "feature_1.jpg",
      "text": "Feature explanation",
      "position": 1
    },
    {
      "image": "benefit_2.jpg",
      "text": "Benefit demonstration",
      "position": 2
    }
  ],
  "end_slide": {
    "image": "cta_image.jpg",
    "text": "Final call to action",
    "link": "https://example.com/action"
  }
}
```

#### Storytelling Frameworks

##### Problem-Solution-Benefit (PSB)
1. **Problem**: Identify audience pain point
2. **Solution**: Present your offering
3. **Benefit**: Show transformation/results

##### Before-After-Results (BAR)
1. **Before**: Show current state/challenge
2. **After**: Demonstrate improvement
3. **Results**: Quantify the outcomes

##### Feature-Benefit-Proof (FBP)
1. **Feature**: Explain capability
2. **Benefit**: Show value to user
3. **Proof**: Provide evidence/validation

## Advanced Content Types

### Event Content

#### Event Promotion Posts
Comprehensive event marketing content that drives attendance and engagement.

**Event Content Components:**
```json
{
  "event_description": {
    "title": "Strategic Planning Workshop",
    "date_time": "2024-02-15 14:00-17:00 EST",
    "location": "Virtual + In-person options",
    "target_audience": "Senior executives and managers"
  },
  "promotional_copy": {
    "hook": "Transform your strategic planning process",
    "value_proposition": "Learn proven frameworks from industry leaders",
    "social_proof": "Join 500+ executives who've improved their planning",
    "scarcity": "Limited to 50 participants"
  },
  "engagement_elements": {
    "questions": ["What are your biggest strategic planning challenges?"],
    "polls": ["Virtual or in-person?"],
    "rsvp_cta": "Reserve your spot now"
  }
}
```

#### Event Series Content
Multi-part content leading up to and following events.

**Pre-Event Content:**
- Teaser announcements
- Speaker introductions
- Topic previews
- Registration drives

**During-Event Content:**
- Live updates
- Key takeaway highlights
- Audience interaction
- Photo/video shares

**Post-Event Content:**
- Session summaries
- Key insights
- Attendee testimonials
- Next event previews

### Group Content

#### Community Engagement Posts
Content specifically optimized for Facebook Groups and community building.

**Group Post Types:**

##### Discussion Starters
```json
{
  "post_type": "discussion_starter",
  "goal": "community_engagement",
  "structure": {
    "question": "What's your experience with [topic]?",
    "context": "Share your insights and learn from others",
    "engagement_prompt": "Reply below with your thoughts!"
  },
  "moderation_tips": {
    "encourage_responses": true,
    "highlight_valuable_answers": true,
    "create_follow_up_threads": true
  }
}
```

##### Resource Shares
Valuable content that provides immediate value to group members.

**Resource Categories:**
- Industry reports and research
- Tool recommendations
- Best practice guides
- Educational content
- Networking opportunities

##### Member Spotlights
Content that highlights community members and their achievements.

**Spotlight Structure:**
- Member introduction
- Achievement highlights
- Community contribution
- Call for congratulations

### Page Optimization Content

#### About Section Content
Professional page descriptions that establish credibility and attract followers.

**About Section Components:**
```json
{
  "company_overview": "Clear description of what you do",
  "unique_value_proposition": "What makes you different",
  "target_audience": "Who you serve",
  "key_achievements": "Credibility indicators",
  "call_to_action": "What you want visitors to do"
}
```

#### Bio Optimization
Concise, compelling bio content that converts visitors to followers.

**Bio Best Practices:**
- **Character Limit**: 101 characters for full display
- **Hook First**: Start with attention-grabber
- **Value Proposition**: Clear benefit or unique angle
- **Call to Action**: Encourage following or visiting

### Advertising Content

#### Facebook Ad Copy
Compelling advertising copy optimized for Facebook's ad platform and algorithm.

**Ad Copy Frameworks:**

##### Awareness Ads
```json
{
  "objective": "brand_awareness",
  "structure": {
    "hook": "Did you know that...",
    "insight": "Industry statistic or trend",
    "question": "Have you experienced this?",
    "cta": "Learn more about our solution"
  },
  "creative_elements": {
    "image": "Problem/solution visual",
    "headline": "Attention-grabbing statement",
    "description": "Value proposition explanation"
  }
}
```

##### Consideration Ads
Focus on educating prospects about solutions and building interest.

**Content Strategy:**
- Problem identification
- Solution explanation
- Social proof inclusion
- Soft call-to-action

##### Conversion Ads
Direct response ads focused on driving immediate actions.

**Optimization Elements:**
- Clear value proposition
- Urgency or scarcity
- Strong call-to-action
- Trust indicators

## Multimedia Integration

### Image Optimization

#### Facebook Image Specifications
```json
{
  "feed_images": {
    "aspect_ratio": "1.91:1 to 4:5",
    "recommended": "1200 x 628 pixels",
    "minimum": "600 x 314 pixels"
  },
  "story_images": {
    "aspect_ratio": "9:16",
    "recommended": "1080 x 1920 pixels",
    "format": "JPG or PNG"
  },
  "carousel_images": {
    "aspect_ratio": "1:1",
    "recommended": "1080 x 1080 pixels",
    "multiple_images": "Up to 10 images"
  }
}
```

#### AI-Generated Image Optimization
- **Relevance**: Images must directly support content message
- **Quality**: High-resolution, professional appearance
- **Brand Consistency**: Colors, style, and tone alignment
- **Platform Optimization**: Formatted for Facebook's display requirements

### Video Content

#### Video Format Optimization
```json
{
  "reels": {
    "duration": "15-60 seconds optimal",
    "aspect_ratio": "9:16",
    "resolution": "1080p recommended",
    "frame_rate": "30 fps",
    "bitrate": "8-12 Mbps"
  },
  "feed_videos": {
    "duration": "1-15 minutes optimal",
    "aspect_ratio": "16:9 or 1:1",
    "resolution": "1080p recommended",
    "file_size": "Up to 4GB"
  }
}
```

#### Video Content Strategy
- **Hook First**: First 3 seconds determine 70% of completion
- **Value Delivery**: Provide immediate value or entertainment
- **Pacing**: Maintain viewer attention throughout
- **Call to Action**: Clear next steps at video end

## Performance Optimization

### Algorithm Understanding

#### Facebook Algorithm Factors
```json
{
  "primary_factors": {
    "engagement_rate": "Likes, comments, shares, saves",
    "watch_time": "How long people watch videos",
    "interaction_quality": "Meaningful vs. passive engagement",
    "relevance": "Content alignment with user interests",
    "recency": "How recently content was posted"
  },
  "secondary_factors": {
    "content_type": "Video performs better than text",
    "creator_history": "Consistent quality and posting",
    "community_interaction": "Group and page engagement",
    "external_signals": "Links and mentions from other platforms"
  }
}
```

### Content Performance Prediction

#### AI-Powered Analytics
```python
class ContentPerformancePredictor:
    async def predict_facebook_performance(
        self,
        content: str,
        content_type: str,
        audience_segment: str,
        posting_time: datetime
    ) -> PerformancePrediction:

        # Analyze content characteristics
        content_features = await self._extract_content_features(content)

        # Audience behavior analysis
        audience_insights = await self._analyze_audience_segment(audience_segment)

        # Platform algorithm factors
        algorithm_weights = await self._get_algorithm_weights(content_type)

        # Time optimization
        timing_score = await self._calculate_timing_optimization(posting_time)

        # Machine learning prediction
        prediction = await self.ml_model.predict({
            **content_features,
            **audience_insights,
            **algorithm_weights,
            "timing_score": timing_score
        })

        return PerformancePrediction(
            engagement_rate=prediction.engagement_rate,
            reach_potential=prediction.reach,
            viral_potential=prediction.virality,
            optimal_posting_time=prediction.best_time,
            content_improvements=prediction.suggestions
        )
```

### A/B Testing Framework

#### Content Optimization Testing
```json
{
  "test_configuration": {
    "test_name": "headline_optimization_test",
    "variants": [
      {
        "name": "variant_a",
        "headline": "5 Ways to Improve Your Productivity",
        "content_type": "listicle"
      },
      {
        "name": "variant_b",
        "headline": "The Productivity Secrets Nobody Talks About",
        "content_type": "mystery_teaser"
      }
    ],
    "audience_split": "50/50",
    "test_duration": "7_days",
    "success_metric": "engagement_rate",
    "minimum_sample_size": 1000
  }
}
```

## API Integration Examples

### Generate Optimized Facebook Post
```http
POST /api/facebook-writer/post/generate
```

```json
{
  "topic": "New Product Launch",
  "content_type": "announcement",
  "audience": "existing_customers",
  "platform_optimization": {
    "algorithm_focus": "engagement",
    "posting_strategy": "peak_times"
  },
  "multimedia": {
    "include_image": true,
    "image_style": "professional_modern"
  },
  "engagement_elements": {
    "include_question": true,
    "add_poll": false
  }
}
```

### Create Facebook Reel
```http
POST /api/facebook-writer/reel/generate
```

```json
{
  "topic": "Quick Social Media Tips",
  "duration": "30_seconds",
  "style": "educational_entertaining",
  "hook_type": "question",
  "target_audience": "small_business_owners",
  "music_preference": "upbeat_motivational"
}
```

### Generate Event Promotion Content
```http
POST /api/facebook-writer/event/generate
```

```json
{
  "event_details": {
    "name": "Digital Marketing Masterclass",
    "date": "2024-02-20T14:00:00Z",
    "type": "webinar",
    "price": 49
  },
  "content_strategy": "conversion_focused",
  "include_social_proof": true,
  "urgency_elements": "limited_seats"
}
```

## Best Practices by Content Type

### Posts
- **Hook First**: Start with compelling question or statement
- **Value Delivery**: Provide immediate benefit
- **Engagement Question**: Include question to boost comments
- **Visual Support**: Always include relevant image
- **Hashtag Strategy**: 2-3 relevant hashtags maximum

### Stories
- **Ephemeral Mindset**: Content for immediate consumption
- **Interactive Elements**: Include polls, questions, or quizzes
- **Series Approach**: Create story series for deeper engagement
- **Behind-the-Scenes**: Show authentic, unpolished content
- **Call to Action**: Clear next steps for viewers

### Reels
- **Hook Immediately**: First 3 seconds are critical
- **Value Fast**: Deliver benefit quickly
- **Trending Audio**: Use popular sounds when relevant
- **Text Overlays**: Include captions for accessibility
- **End Screen CTA**: Strong call-to-action at video end

### Carousels
- **Story Arc**: Logical progression across slides
- **Visual Consistency**: Maintain design consistency
- **One Idea Per Slide**: Avoid information overload
- **Progressive Disclosure**: Build toward conclusion
- **Clear CTA**: Obvious final call-to-action

## Success Metrics

### Content Performance Tracking
```json
{
  "content_metrics": {
    "engagement_rate": "(likes + comments + shares + saves) / reach × 100",
    "amplification_rate": "shares / impressions × 100",
    "click_through_rate": "link clicks / impressions × 100",
    "video_view_rate": "video views / impressions × 100",
    "completion_rate": "watches to end / video views × 100"
  },
  "audience_metrics": {
    "reach_growth": "New audience reached vs. previous period",
    "follower_quality": "Engagement rate of new followers",
    "demographic_match": "How well audience matches target",
    "interaction_depth": "Comments per post, responses to comments"
  }
}
```

### Optimization Goals
- **Engagement Rate**: Target 3-5% for organic content
- **Video Completion**: Target 70%+ completion rate for reels
- **Share Rate**: Target 0.5-1% share rate for highly shareable content
- **Click Rate**: Target 1-2% click-through rate for link posts

---

[:octicons-arrow-right-24: Back to Overview](overview.md)
[:octicons-arrow-right-24: Migration Guide](migration-guide.md)