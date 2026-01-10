/**
 * Terminology Mapping Utility
 * 
 * Maps technical terms to simple, user-friendly language for non-technical users.
 * Used throughout Product Marketing and Campaign Creator components.
 */

export interface TerminologyMap {
  [key: string]: {
    simple: string;
    description?: string;
    examples?: string[];
  };
}

/**
 * Main terminology mapping dictionary.
 * Maps technical terms to simple language.
 */
export const TERMINOLOGY: TerminologyMap = {
  // Campaign Creator Terms
  'Campaign Blueprint': {
    simple: 'Marketing Campaign',
    description: 'Your complete marketing plan with all content pieces',
  },
  'campaign_blueprint': {
    simple: 'marketing campaign',
  },
  'Asset Nodes': {
    simple: 'Content Pieces',
    description: 'Individual images, videos, or text posts for your campaign',
  },
  'asset_nodes': {
    simple: 'content pieces',
  },
  'KPI': {
    simple: 'How will you measure success?',
    description: 'Key Performance Indicator - how you\'ll track if your campaign is working',
    examples: ['Sales increase', 'Website visits', 'Social media followers', 'Email signups'],
  },
  'kpi': {
    simple: 'success metric',
  },
  'Brand DNA': {
    simple: 'Your Brand Style',
    description: 'Your brand\'s unique personality, colors, and voice',
  },
  'brand_dna': {
    simple: 'brand style',
  },
  'Channel Pack': {
    simple: 'Platform Settings',
    description: 'Settings optimized for each social media platform',
  },
  'channel_pack': {
    simple: 'platform settings',
  },
  'Phase Management': {
    simple: 'Campaign Timeline',
    description: 'The schedule for when your campaign content will be published',
  },
  'phase_management': {
    simple: 'campaign timeline',
  },
  'Asset Proposals': {
    simple: 'Content Ideas',
    description: 'AI-generated suggestions for your campaign content',
  },
  'asset_proposals': {
    simple: 'content ideas',
  },
  'Orchestration': {
    simple: 'Campaign Planning',
    description: 'Automatically organizing and planning your campaign',
  },
  'orchestration': {
    simple: 'campaign planning',
  },
  
  // Product Marketing Terms
  'Product Photoshoot': {
    simple: 'Product Photos',
    description: 'Professional photos of your product',
  },
  'product_photoshoot': {
    simple: 'product photos',
  },
  'Environment': {
    simple: 'Photo Setting',
    description: 'Where the product photo will be taken',
    examples: ['Studio', 'Lifestyle', 'Outdoor', 'Minimalist'],
  },
  'environment': {
    simple: 'photo setting',
  },
  'Background Style': {
    simple: 'Background',
    description: 'What\'s behind your product in the photo',
    examples: ['White', 'Transparent', 'Lifestyle scene', 'Branded'],
  },
  'background_style': {
    simple: 'background',
  },
  'Lighting': {
    simple: 'Lighting Style',
    description: 'How the product is lit',
    examples: ['Natural', 'Studio', 'Dramatic', 'Soft'],
  },
  'lighting': {
    simple: 'lighting style',
  },
  'Resolution': {
    simple: 'Image Size',
    description: 'How large and detailed the image will be',
    examples: ['1024x1024', '2048x2048'],
  },
  'resolution': {
    simple: 'image size',
  },
  'Variations': {
    simple: 'Number of Photos',
    description: 'How many different photos to generate',
  },
  'variations': {
    simple: 'number of photos',
  },
  'Animation Type': {
    simple: 'Animation Style',
    description: 'How the product will move in the video',
    examples: ['Reveal', '360° Rotation', 'Demo', 'Lifestyle'],
  },
  'animation_type': {
    simple: 'animation style',
  },
  'Video Type': {
    simple: 'Video Style',
    description: 'What kind of video to create',
    examples: ['Demo', 'Storytelling', 'Feature Highlight', 'Launch'],
  },
  'video_type': {
    simple: 'video style',
  },
  'Explainer Type': {
    simple: 'Video Purpose',
    description: 'What the video will explain',
    examples: ['Product Overview', 'Feature Demo', 'Tutorial', 'Brand Message'],
  },
  'explainer_type': {
    simple: 'video purpose',
  },
  
  // General Terms
  'Asset': {
    simple: 'Content',
    description: 'Any image, video, or text created for marketing',
  },
  'asset': {
    simple: 'content',
  },
  'Channel': {
    simple: 'Platform',
    description: 'Where you\'ll share your content',
    examples: ['Instagram', 'Facebook', 'LinkedIn', 'TikTok'],
  },
  'channel': {
    simple: 'platform',
  },
  'Template': {
    simple: 'Style Preset',
    description: 'A pre-designed style you can use',
  },
  'template': {
    simple: 'style preset',
  },
  'Pre-flight Validation': {
    simple: 'Campaign Check',
    description: 'Making sure everything is ready before creating your campaign',
  },
  'preflight': {
    simple: 'campaign check',
  },
};

/**
 * Get simple term for a technical term.
 * 
 * @param technicalTerm - The technical term to translate
 * @returns Simple, user-friendly term
 */
export function getSimpleTerm(technicalTerm: string): string {
  const normalized = technicalTerm.trim();
  
  // Try exact match first
  if (TERMINOLOGY[normalized]) {
    return TERMINOLOGY[normalized].simple;
  }
  
  // Try case-insensitive match
  const lowerKey = Object.keys(TERMINOLOGY).find(
    key => key.toLowerCase() === normalized.toLowerCase()
  );
  if (lowerKey) {
    return TERMINOLOGY[lowerKey].simple;
  }
  
  // Return original if no match found
  return technicalTerm;
}

/**
 * Get description for a technical term.
 * 
 * @param technicalTerm - The technical term
 * @returns Description or undefined
 */
export function getTermDescription(technicalTerm: string): string | undefined {
  const normalized = technicalTerm.trim();
  
  if (TERMINOLOGY[normalized]?.description) {
    return TERMINOLOGY[normalized].description;
  }
  
  const lowerKey = Object.keys(TERMINOLOGY).find(
    key => key.toLowerCase() === normalized.toLowerCase()
  );
  if (lowerKey && TERMINOLOGY[lowerKey].description) {
    return TERMINOLOGY[lowerKey].description;
  }
  
  return undefined;
}

/**
 * Get examples for a technical term.
 * 
 * @param technicalTerm - The technical term
 * @returns Array of examples or undefined
 */
export function getTermExamples(technicalTerm: string): string[] | undefined {
  const normalized = technicalTerm.trim();
  
  if (TERMINOLOGY[normalized]?.examples) {
    return TERMINOLOGY[normalized].examples;
  }
  
  const lowerKey = Object.keys(TERMINOLOGY).find(
    key => key.toLowerCase() === normalized.toLowerCase()
  );
  if (lowerKey && TERMINOLOGY[lowerKey].examples) {
    return TERMINOLOGY[lowerKey].examples;
  }
  
  return undefined;
}

/**
 * Replace technical terms in text with simple terms.
 * 
 * @param text - Text containing technical terms
 * @returns Text with simple terms
 */
export function simplifyText(text: string): string {
  let simplified = text;
  
  // Replace all known technical terms
  Object.keys(TERMINOLOGY).forEach(technicalTerm => {
    const simpleTerm = TERMINOLOGY[technicalTerm].simple;
    // Case-insensitive replacement
    const regex = new RegExp(technicalTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    simplified = simplified.replace(regex, simpleTerm);
  });
  
  return simplified;
}

/**
 * Helper function to get tooltip text for a field.
 * Combines description and examples if available.
 * 
 * @param technicalTerm - The technical term
 * @returns Tooltip text
 */
export function getTooltipText(technicalTerm: string): string {
  const description = getTermDescription(technicalTerm);
  const examples = getTermExamples(technicalTerm);
  
  let tooltip = '';
  
  if (description) {
    tooltip = description;
  }
  
  if (examples && examples.length > 0) {
    if (tooltip) {
      tooltip += '\n\nExamples: ';
    } else {
      tooltip = 'Examples: ';
    }
    tooltip += examples.join(', ');
  }
  
  return tooltip || getSimpleTerm(technicalTerm);
}
