import React from 'react';
import { Grid } from '@mui/material';
import { SelectFieldWithTooltip } from './SelectFieldWithTooltip';
import { SectionProps } from './types';
import {
  WRITING_STYLES,
  STORY_TONES,
  NARRATIVE_POVS,
  AUDIENCE_AGE_GROUPS,
  CONTENT_RATINGS,
  ENDING_PREFERENCES,
  STORY_LENGTHS,
} from './constants';

interface StoryConfigurationSectionProps extends SectionProps {
  normalizedAudienceAgeGroup: string;
}

export const StoryConfigurationSection: React.FC<StoryConfigurationSectionProps> = ({
  state,
  customValues,
  textFieldStyles,
  normalizedAudienceAgeGroup,
}) => {
  return (
    <>
      {/* Writing Style */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Writing Style"
          value={state.writingStyle}
          onChange={(e) => state.setWritingStyle(e.target.value)}
          helperText="Choose the narrative style and prose approach"
          options={WRITING_STYLES}
          customValues={customValues.customWritingStyles}
          sx={textFieldStyles}
          tooltip={{
            title: 'Writing Style',
            description: 'Select the narrative style that best fits your story. This affects sentence structure, vocabulary, and overall prose approach.',
            examples: [
              { label: 'Formal', description: 'Structured, academic, precise language' },
              { label: 'Casual', description: 'Conversational, relaxed, everyday language' },
              { label: 'Poetic', description: 'Lyrical, metaphorical, rich imagery' },
              { label: 'Humorous', description: 'Witty, playful, comedic tone' },
              { label: 'Narrative', description: 'Traditional storytelling style' },
            ],
          }}
        />
      </Grid>

      {/* Story Tone */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Story Tone"
          value={state.storyTone}
          onChange={(e) => state.setStoryTone(e.target.value)}
          helperText="Set the emotional atmosphere and mood of your story"
          options={STORY_TONES}
          customValues={customValues.customStoryTones}
          sx={textFieldStyles}
          tooltip={{
            title: 'Story Tone',
            description: 'The tone determines the emotional atmosphere and overall mood of your story. It affects how readers feel while reading.',
            examples: [
              { label: 'Dark', description: 'Serious, grim, somber atmosphere' },
              { label: 'Uplifting', description: 'Positive, hopeful, inspiring' },
              { label: 'Suspenseful', description: 'Tense, thrilling, edge-of-seat' },
              { label: 'Whimsical', description: 'Playful, fanciful, lighthearted' },
              { label: 'Mysterious', description: 'Enigmatic, puzzling, intriguing' },
            ],
          }}
        />
      </Grid>

      {/* Narrative POV */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Narrative Point of View"
          value={state.narrativePOV}
          onChange={(e) => state.setNarrativePOV(e.target.value)}
          helperText="Choose the perspective from which the story is told"
          options={NARRATIVE_POVS}
          customValues={customValues.customNarrativePOVs}
          sx={textFieldStyles}
          tooltip={{
            title: 'Narrative Point of View',
            description: "Select the perspective from which your story is narrated. This determines how much readers know about characters and events.",
            examples: [
              { label: 'First Person', description: '"I" perspective, limited to one character\'s thoughts' },
              { label: 'Third Person Limited', description: '"He/She" perspective, follows one character closely' },
              { label: 'Third Person Omniscient', description: '"He/She" perspective, knows all characters\' thoughts' },
            ],
          }}
        />
      </Grid>

      {/* Audience Age Group */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Audience Age Group"
          value={normalizedAudienceAgeGroup}
          onChange={(e) => state.setAudienceAgeGroup(e.target.value)}
          helperText="Target age group for your story"
          options={AUDIENCE_AGE_GROUPS}
          customValues={customValues.customAudienceAgeGroups}
          sx={textFieldStyles}
          tooltip={{
            title: 'Audience Age Group',
            description: 'Select the primary target age group. This affects language complexity, themes, and content appropriateness.',
            examples: [
              { label: 'Children (5-12)', description: 'Simple language, clear themes, age-appropriate content' },
              { label: 'Young Adults (13-17)', description: 'Moderate complexity, coming-of-age themes' },
              { label: 'Adults (18+)', description: 'Complex themes, mature content allowed' },
              { label: 'All Ages', description: 'Universal appeal, family-friendly' },
            ],
          }}
        />
      </Grid>

      {/* Content Rating */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Content Rating"
          value={state.contentRating}
          onChange={(e) => state.setContentRating(e.target.value)}
          helperText="Set the content rating based on themes and material"
          options={CONTENT_RATINGS}
          customValues={customValues.customContentRatings}
          sx={textFieldStyles}
          tooltip={{
            title: 'Content Rating',
            description: 'Select the appropriate content rating based on themes, language, violence, and mature content in your story.',
            examples: [
              { label: 'G', description: 'General audience, all ages appropriate' },
              { label: 'PG', description: 'Parental guidance suggested, mild themes' },
              { label: 'PG-13', description: 'Parents strongly cautioned, some mature content' },
              { label: 'R', description: 'Restricted, mature themes and content' },
            ],
          }}
        />
      </Grid>

      {/* Ending Preference */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Ending Preference"
          value={state.endingPreference}
          onChange={(e) => state.setEndingPreference(e.target.value)}
          helperText="Choose how you want your story to conclude"
          options={ENDING_PREFERENCES}
          customValues={customValues.customEndingPreferences}
          sx={textFieldStyles}
          tooltip={{
            title: 'Ending Preference',
            description: 'Select the type of ending you want for your story. This guides the resolution and final emotional impact.',
            examples: [
              { label: 'Happy', description: 'Positive resolution, characters succeed' },
              { label: 'Tragic', description: 'Sad or bittersweet conclusion' },
              { label: 'Cliffhanger', description: 'Open ending, sequel potential' },
              { label: 'Twist', description: 'Unexpected revelation or turn' },
              { label: 'Open-ended', description: 'Ambiguous, reader interpretation' },
              { label: 'Bittersweet', description: 'Mixed emotions, realistic outcome' },
            ],
          }}
        />
      </Grid>

      {/* Story Length */}
      <Grid item xs={12} md={6}>
        <SelectFieldWithTooltip
          label="Story Length"
          value={state.storyLength}
          onChange={(e) => state.setStoryLength(e.target.value)}
          helperText="Choose the target length for your story"
          options={STORY_LENGTHS}
          sx={textFieldStyles}
          tooltip={{
            title: 'Story Length',
            description: 'Select the target length for your story. This controls how detailed and extensive the generated story will be.',
            examples: [
              { label: 'Short (>1000 words)', description: 'Brief, concise story' },
              { label: 'Medium (>5000 words)', description: 'Standard length story with good detail' },
              { label: 'Long (>10000 words)', description: 'Extended, detailed story with rich development' },
            ],
          }}
        />
      </Grid>
    </>
  );
};

