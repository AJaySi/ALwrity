/**
 * Schemas for rendering JSON fields as user-friendly forms
 */

export interface JsonFieldSchema {
  type: 'object' | 'array';
  fields?: Record<string, FieldDefinition>; // For object type
  itemType?: 'string' | 'object'; // For array type
  itemFields?: Record<string, FieldDefinition>; // For array of objects
  itemLabel?: string; // Label for array items
}

export interface FieldDefinition {
  type: 'text' | 'multiline' | 'select' | 'multiselect' | 'number';
  label: string;
  placeholder?: string;
  options?: string[]; // For select/multiselect
  required?: boolean;
  helperText?: string;
}

export const JSON_FIELD_SCHEMAS: Record<string, JsonFieldSchema> = {
  content_preferences: {
    type: 'object',
    fields: {
      preferred_formats: {
        type: 'multiselect',
        label: 'Preferred Content Formats',
        options: ['Blog Posts', 'Articles', 'Videos', 'Infographics', 'Webinars', 'Podcasts', 'Case Studies', 'Whitepapers', 'Social Media Posts', 'Email Newsletters'],
        required: true,
        helperText: 'Select the content formats your audience prefers'
      },
      content_topics: {
        type: 'multiselect',
        label: 'Content Topics',
        options: ['Industry insights', 'Best practices', 'Case studies', 'How-to guides', 'Product updates', 'Company news', 'Thought leadership', 'Educational content'],
        helperText: 'Select topics your audience is interested in'
      },
      content_style: {
        type: 'multiselect',
        label: 'Content Style',
        options: ['Professional', 'Educational', 'Conversational', 'Technical', 'Inspirational', 'Humorous', 'Authoritative'],
        helperText: 'Select the tone and style for your content'
      },
      content_length: {
        type: 'select',
        label: 'Preferred Content Length',
        options: ['Short (300-500 words)', 'Medium (1000-2000 words)', 'Long (2000+ words)', 'Variable'],
        helperText: 'Select the typical length for your content'
      },
      visual_preferences: {
        type: 'multiselect',
        label: 'Visual Preferences',
        options: ['Infographics', 'Charts', 'Diagrams', 'Images', 'Videos', 'Animations', 'Interactive elements'],
        helperText: 'Select visual elements to include in content'
      }
    }
  },

  consumption_patterns: {
    type: 'object',
    fields: {
      primary_channels: {
        type: 'multiselect',
        label: 'Primary Content Channels',
        options: ['Website', 'Email', 'Social Media', 'Mobile App', 'Newsletter', 'Blog', 'YouTube', 'Podcast'],
        helperText: 'Where does your audience consume content?'
      },
      preferred_times: {
        type: 'multiselect',
        label: 'Preferred Consumption Times',
        options: ['Morning (6-9 AM)', 'Mid-morning (9-11 AM)', 'Lunch (12-2 PM)', 'Afternoon (2-4 PM)', 'Evening (5-7 PM)', 'Night (7-10 PM)'],
        helperText: 'When does your audience typically consume content?'
      },
      device_preference: {
        type: 'multiselect',
        label: 'Device Preference',
        options: ['Desktop', 'Mobile', 'Tablet', 'Smart TV', 'Smart Speaker'],
        helperText: 'What devices does your audience use?'
      },
      content_length_preference: {
        type: 'select',
        label: 'Preferred Content Length',
        options: ['Short (1-3 min read)', 'Medium (5-10 min read)', 'Long (10+ min read)', 'Variable'],
        helperText: 'How long does your audience prefer to consume content?'
      },
      engagement_pattern: {
        type: 'text',
        label: 'Engagement Pattern',
        placeholder: 'e.g., High engagement on educational content',
        helperText: 'Describe how your audience typically engages with content'
      }
    }
  },

  audience_pain_points: {
    type: 'array',
    itemType: 'string',
    itemLabel: 'Pain Point'
  },

  buying_journey: {
    type: 'object',
    fields: {
      awareness: {
        type: 'multiline',
        label: 'Awareness Stage',
        placeholder: 'How do customers first discover your solution?',
        helperText: 'Describe how customers become aware of your product/service'
      },
      consideration: {
        type: 'multiline',
        label: 'Consideration Stage',
        placeholder: 'What factors do customers consider?',
        helperText: 'Describe what customers evaluate during consideration'
      },
      decision: {
        type: 'multiline',
        label: 'Decision Stage',
        placeholder: 'What influences the final purchase decision?',
        helperText: 'Describe what drives the purchase decision'
      },
      retention: {
        type: 'multiline',
        label: 'Retention Stage',
        placeholder: 'How do you keep customers engaged?',
        helperText: 'Describe ongoing engagement and retention strategies'
      }
    }
  },

  seasonal_trends: {
    type: 'array',
    itemType: 'string',
    itemLabel: 'Seasonal Trend'
  },

  business_objectives: {
    type: 'array',
    itemType: 'string',
    itemLabel: 'Business Objective'
  },

  target_metrics: {
    type: 'object',
    fields: {
      primary_metric: {
        type: 'text',
        label: 'Primary Metric',
        placeholder: 'e.g., Website traffic',
        required: true
      },
      target_value: {
        type: 'number',
        label: 'Target Value',
        placeholder: 'e.g., 10000',
        helperText: 'Your target number for the primary metric'
      },
      secondary_metrics: {
        type: 'multiselect',
        label: 'Secondary Metrics',
        options: ['Lead generation', 'Conversion rate', 'Engagement rate', 'Brand awareness', 'Customer retention', 'Revenue', 'ROI'],
        helperText: 'Additional metrics you want to track'
      }
    }
  },

  performance_metrics: {
    type: 'object',
    fields: {
      traffic: {
        type: 'number',
        label: 'Monthly Traffic',
        placeholder: 'e.g., 10000',
        helperText: 'Current monthly website traffic'
      },
      conversion_rate: {
        type: 'number',
        label: 'Conversion Rate (%)',
        placeholder: 'e.g., 2.5',
        helperText: 'Current conversion rate percentage'
      },
      bounce_rate: {
        type: 'number',
        label: 'Bounce Rate (%)',
        placeholder: 'e.g., 50',
        helperText: 'Current bounce rate percentage'
      },
      avg_session_duration: {
        type: 'number',
        label: 'Avg Session Duration (seconds)',
        placeholder: 'e.g., 150',
        helperText: 'Average time users spend on site'
      }
    }
  },

  engagement_metrics: {
    type: 'object',
    fields: {
      likes: {
        type: 'number',
        label: 'Average Likes',
        placeholder: 'e.g., 500',
        helperText: 'Average number of likes per post'
      },
      shares: {
        type: 'number',
        label: 'Average Shares',
        placeholder: 'e.g., 50',
        helperText: 'Average number of shares per post'
      },
      comments: {
        type: 'number',
        label: 'Average Comments',
        placeholder: 'e.g., 30',
        helperText: 'Average number of comments per post'
      },
      click_through_rate: {
        type: 'number',
        label: 'Click-Through Rate (%)',
        placeholder: 'e.g., 3.5',
        helperText: 'Average click-through rate percentage'
      },
      time_on_page: {
        type: 'number',
        label: 'Average Time on Page (seconds)',
        placeholder: 'e.g., 180',
        helperText: 'Average time users spend on a page'
      },
      engagement_rate: {
        type: 'number',
        label: 'Engagement Rate (%)',
        placeholder: 'e.g., 5.2',
        helperText: 'Overall engagement rate percentage'
      }
    }
  },

  top_competitors: {
    type: 'array',
    itemType: 'object',
    itemLabel: 'Competitor',
    itemFields: {
      name: {
        type: 'text',
        label: 'Competitor Name',
        placeholder: 'e.g., Company ABC',
        required: true,
        helperText: 'Name of the competitor'
      },
      website: {
        type: 'text',
        label: 'Website URL',
        placeholder: 'e.g., https://example.com',
        helperText: 'Competitor website URL'
      },
      strength: {
        type: 'multiline',
        label: 'Key Strengths',
        placeholder: 'What are their main strengths?',
        helperText: 'Describe what makes this competitor strong'
      },
      weakness: {
        type: 'multiline',
        label: 'Key Weaknesses',
        placeholder: 'What are their main weaknesses?',
        helperText: 'Describe areas where this competitor is weaker'
      }
    }
  },

  competitor_content_strategies: {
    type: 'object',
    fields: {
      content_types: {
        type: 'multiselect',
        label: 'Content Types They Use',
        options: ['Blog Posts', 'Videos', 'Webinars', 'Case Studies', 'Whitepapers', 'Infographics', 'Podcasts', 'Social Media', 'Email Campaigns'],
        helperText: 'What content types do competitors focus on?'
      },
      publishing_frequency: {
        type: 'select',
        label: 'Publishing Frequency',
        options: ['Daily', 'Multiple times per week', 'Weekly', 'Bi-weekly', 'Monthly', 'Irregular'],
        helperText: 'How often do competitors publish content?'
      },
      content_themes: {
        type: 'multiselect',
        label: 'Content Themes',
        options: ['Product features', 'Industry insights', 'Customer success', 'Thought leadership', 'Educational', 'Entertainment', 'News and updates'],
        helperText: 'What themes do competitors focus on?'
      },
      distribution_channels: {
        type: 'multiselect',
        label: 'Distribution Channels',
        options: ['Website/Blog', 'LinkedIn', 'Twitter', 'Facebook', 'YouTube', 'Email', 'Newsletter', 'Podcast platforms'],
        helperText: 'Where do competitors distribute their content?'
      },
      engagement_approach: {
        type: 'multiline',
        label: 'Engagement Approach',
        placeholder: 'How do competitors engage with their audience?',
        helperText: 'Describe how competitors interact with their audience'
      }
    }
  },

  market_gaps: {
    type: 'array',
    itemType: 'object',
    itemLabel: 'Market Gap',
    itemFields: {
      gap_description: {
        type: 'multiline',
        label: 'Gap Description',
        placeholder: 'Describe the content gap in the market',
        required: true,
        helperText: 'What content need is not being met?'
      },
      opportunity: {
        type: 'multiline',
        label: 'Opportunity',
        placeholder: 'How can we fill this gap?',
        helperText: 'How can your brand capitalize on this gap?'
      },
      target_audience: {
        type: 'text',
        label: 'Target Audience',
        placeholder: 'e.g., Small business owners',
        helperText: 'Who would benefit from content addressing this gap?'
      },
      priority: {
        type: 'select',
        label: 'Priority',
        options: ['High', 'Medium', 'Low'],
        helperText: 'How important is it to address this gap?'
      }
    }
  },

  industry_trends: {
    type: 'array',
    itemType: 'object',
    itemLabel: 'Industry Trend',
    itemFields: {
      trend_name: {
        type: 'text',
        label: 'Trend Name',
        placeholder: 'e.g., AI-powered content creation',
        required: true,
        helperText: 'Name of the industry trend'
      },
      description: {
        type: 'multiline',
        label: 'Description',
        placeholder: 'Describe the trend and its impact',
        helperText: 'What is this trend and why does it matter?'
      },
      impact: {
        type: 'select',
        label: 'Impact Level',
        options: ['High', 'Medium', 'Low'],
        helperText: 'How significant is this trend?'
      },
      relevance: {
        type: 'multiline',
        label: 'Relevance to Your Brand',
        placeholder: 'How does this trend relate to your content strategy?',
        helperText: 'How can you leverage this trend?'
      }
    }
  },

  emerging_trends: {
    type: 'array',
    itemType: 'object',
    itemLabel: 'Emerging Trend',
    itemFields: {
      trend_name: {
        type: 'text',
        label: 'Trend Name',
        placeholder: 'e.g., Voice search optimization',
        required: true,
        helperText: 'Name of the emerging trend'
      },
      description: {
        type: 'multiline',
        label: 'Description',
        placeholder: 'Describe the emerging trend',
        helperText: 'What is this new trend?'
      },
      growth_potential: {
        type: 'select',
        label: 'Growth Potential',
        options: ['Very High', 'High', 'Medium', 'Low', 'Unknown'],
        helperText: 'How likely is this trend to grow?'
      },
      early_adoption_benefit: {
        type: 'multiline',
        label: 'Early Adoption Benefit',
        placeholder: 'What are the benefits of adopting this trend early?',
        helperText: 'Why should you consider this trend now?'
      }
    }
  },

  content_mix: {
    type: 'object',
    fields: {
      blog_posts: {
        type: 'number',
        label: 'Blog Posts (%)',
        placeholder: 'e.g., 40',
        helperText: 'Percentage of content mix for blog posts'
      },
      videos: {
        type: 'number',
        label: 'Videos (%)',
        placeholder: 'e.g., 25',
        helperText: 'Percentage of content mix for videos'
      },
      social_media: {
        type: 'number',
        label: 'Social Media (%)',
        placeholder: 'e.g., 20',
        helperText: 'Percentage of content mix for social media'
      },
      email: {
        type: 'number',
        label: 'Email (%)',
        placeholder: 'e.g., 10',
        helperText: 'Percentage of content mix for email'
      },
      other_formats: {
        type: 'number',
        label: 'Other Formats (%)',
        placeholder: 'e.g., 5',
        helperText: 'Percentage of content mix for other formats'
      },
      distribution_strategy: {
        type: 'multiline',
        label: 'Distribution Strategy',
        placeholder: 'Describe how you plan to distribute content across these formats',
        helperText: 'Explain your content distribution approach'
      }
    }
  },

  optimal_timing: {
    type: 'object',
    fields: {
      blog_posts: {
        type: 'multiselect',
        label: 'Best Times for Blog Posts',
        options: ['Monday Morning', 'Tuesday Morning', 'Wednesday Morning', 'Thursday Morning', 'Friday Morning', 'Monday Afternoon', 'Tuesday Afternoon', 'Wednesday Afternoon', 'Thursday Afternoon', 'Friday Afternoon', 'Weekend'],
        helperText: 'Select optimal days/times for publishing blog posts'
      },
      social_media: {
        type: 'multiselect',
        label: 'Best Times for Social Media',
        options: ['Early Morning (6-9 AM)', 'Mid-Morning (9-11 AM)', 'Lunch (12-2 PM)', 'Afternoon (2-5 PM)', 'Evening (5-8 PM)', 'Night (8-10 PM)'],
        helperText: 'Select optimal times for social media posts'
      },
      email: {
        type: 'multiselect',
        label: 'Best Times for Email',
        options: ['Monday Morning', 'Tuesday Morning', 'Wednesday Morning', 'Thursday Morning', 'Friday Morning', 'Weekend'],
        helperText: 'Select optimal days/times for sending emails'
      },
      videos: {
        type: 'multiselect',
        label: 'Best Times for Videos',
        options: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'Weekday Evenings', 'Weekend Mornings'],
        helperText: 'Select optimal days/times for publishing videos'
      },
      timezone: {
        type: 'text',
        label: 'Target Timezone',
        placeholder: 'e.g., EST, PST, GMT',
        helperText: 'Primary timezone for your audience'
      },
      notes: {
        type: 'multiline',
        label: 'Timing Notes',
        placeholder: 'Any additional notes about optimal timing',
        helperText: 'Additional considerations for content timing'
      }
    }
  },

  quality_metrics: {
    type: 'object',
    fields: {
      readability_score: {
        type: 'number',
        label: 'Target Readability Score',
        placeholder: 'e.g., 60',
        helperText: 'Target Flesch Reading Ease score (0-100)'
      },
      word_count_range: {
        type: 'text',
        label: 'Word Count Range',
        placeholder: 'e.g., 1000-2000',
        helperText: 'Target word count range for content'
      },
      seo_score: {
        type: 'number',
        label: 'Target SEO Score',
        placeholder: 'e.g., 80',
        helperText: 'Target SEO optimization score (0-100)'
      },
      engagement_threshold: {
        type: 'number',
        label: 'Engagement Threshold (%)',
        placeholder: 'e.g., 3',
        helperText: 'Minimum expected engagement rate'
      },
      quality_checklist: {
        type: 'multiselect',
        label: 'Quality Checklist Items',
        options: ['Grammar check', 'Fact verification', 'SEO optimization', 'Visual elements', 'Internal linking', 'External linking', 'CTA placement', 'Mobile optimization', 'Accessibility', 'Brand voice consistency'],
        helperText: 'Quality standards to check before publishing'
      },
      review_process: {
        type: 'multiline',
        label: 'Review Process',
        placeholder: 'Describe your content review and approval process',
        helperText: 'How is content reviewed before publication?'
      }
    }
  },

  editorial_guidelines: {
    type: 'object',
    fields: {
      tone: {
        type: 'multiselect',
        label: 'Tone Guidelines',
        options: ['Professional', 'Conversational', 'Friendly', 'Authoritative', 'Educational', 'Inspirational', 'Humorous', 'Technical'],
        helperText: 'Select the tone(s) to use in content'
      },
      style_guide: {
        type: 'text',
        label: 'Style Guide Reference',
        placeholder: 'e.g., AP Style, Chicago Manual, Custom',
        helperText: 'Which style guide to follow?'
      },
      formatting_rules: {
        type: 'multiline',
        label: 'Formatting Rules',
        placeholder: 'e.g., Use H2 for main sections, bullet points for lists, etc.',
        helperText: 'Specific formatting requirements'
      },
      citation_requirements: {
        type: 'multiline',
        label: 'Citation Requirements',
        placeholder: 'Describe how to cite sources and references',
        helperText: 'How should sources be cited?'
      },
      image_guidelines: {
        type: 'multiline',
        label: 'Image Guidelines',
        placeholder: 'Describe image requirements, alt text, sizing, etc.',
        helperText: 'Guidelines for using images in content'
      },
      language_preferences: {
        type: 'multiselect',
        label: 'Language Preferences',
        options: ['US English', 'UK English', 'Canadian English', 'Australian English', 'Other'],
        helperText: 'Which variant of English to use?'
      },
      prohibited_content: {
        type: 'multiline',
        label: 'Prohibited Content',
        placeholder: 'List content types or topics to avoid',
        helperText: 'What content should be avoided?'
      }
    }
  },

  brand_voice: {
    type: 'object',
    fields: {
      personality_traits: {
        type: 'multiselect',
        label: 'Brand Personality Traits',
        options: ['Trustworthy', 'Innovative', 'Friendly', 'Professional', 'Playful', 'Serious', 'Approachable', 'Expert', 'Bold', 'Humble', 'Confident', 'Empathetic'],
        helperText: 'Select traits that define your brand voice'
      },
      communication_style: {
        type: 'multiline',
        label: 'Communication Style',
        placeholder: 'Describe how your brand communicates (formal, casual, etc.)',
        helperText: 'How does your brand communicate?'
      },
      key_messages: {
        type: 'multiline',
        label: 'Key Messages',
        placeholder: 'List the core messages your brand always conveys',
        helperText: 'What are your brand\'s core messages?'
      },
      do_s: {
        type: 'multiline',
        label: 'Do\'s',
        placeholder: 'What your brand voice should do',
        helperText: 'Guidelines for what your brand voice should do'
      },
      dont_s: {
        type: 'multiline',
        label: 'Don\'ts',
        placeholder: 'What your brand voice should avoid',
        helperText: 'Guidelines for what your brand voice should avoid'
      },
      examples: {
        type: 'multiline',
        label: 'Voice Examples',
        placeholder: 'Provide examples of content that represents your brand voice well',
        helperText: 'Examples of content that matches your brand voice'
      }
    }
  },

  conversion_rates: {
    type: 'object',
    fields: {
      email_signup: {
        type: 'number',
        label: 'Email Signup Rate (%)',
        placeholder: 'e.g., 2.5',
        helperText: 'Target email signup conversion rate'
      },
      lead_generation: {
        type: 'number',
        label: 'Lead Generation Rate (%)',
        placeholder: 'e.g., 1.8',
        helperText: 'Target lead generation conversion rate'
      },
      content_download: {
        type: 'number',
        label: 'Content Download Rate (%)',
        placeholder: 'e.g., 5.0',
        helperText: 'Target content download conversion rate'
      },
      purchase: {
        type: 'number',
        label: 'Purchase Rate (%)',
        placeholder: 'e.g., 0.5',
        helperText: 'Target purchase conversion rate'
      },
      newsletter_subscription: {
        type: 'number',
        label: 'Newsletter Subscription Rate (%)',
        placeholder: 'e.g., 3.0',
        helperText: 'Target newsletter subscription rate'
      },
      current_performance: {
        type: 'multiline',
        label: 'Current Performance',
        placeholder: 'Describe current conversion rate performance',
        helperText: 'What are your current conversion rates?'
      },
      improvement_goals: {
        type: 'multiline',
        label: 'Improvement Goals',
        placeholder: 'Describe goals for improving conversion rates',
        helperText: 'What improvements are you targeting?'
      }
    }
  },

  content_roi_targets: {
    type: 'object',
    fields: {
      traffic_roi: {
        type: 'number',
        label: 'Traffic ROI Target (%)',
        placeholder: 'e.g., 150',
        helperText: 'Target ROI for traffic generation (percentage)'
      },
      lead_roi: {
        type: 'number',
        label: 'Lead ROI Target (%)',
        placeholder: 'e.g., 200',
        helperText: 'Target ROI for lead generation (percentage)'
      },
      revenue_roi: {
        type: 'number',
        label: 'Revenue ROI Target (%)',
        placeholder: 'e.g., 300',
        helperText: 'Target ROI for revenue generation (percentage)'
      },
      engagement_roi: {
        type: 'number',
        label: 'Engagement ROI Target (%)',
        placeholder: 'e.g., 120',
        helperText: 'Target ROI for engagement (percentage)'
      },
      measurement_period: {
        type: 'select',
        label: 'Measurement Period',
        options: ['Monthly', 'Quarterly', 'Semi-annually', 'Annually'],
        helperText: 'How often will ROI be measured?'
      },
      calculation_method: {
        type: 'multiline',
        label: 'ROI Calculation Method',
        placeholder: 'Describe how ROI is calculated',
        helperText: 'How do you calculate content ROI?'
      },
      benchmarks: {
        type: 'multiline',
        label: 'Industry Benchmarks',
        placeholder: 'List relevant industry ROI benchmarks',
        helperText: 'What are the industry benchmarks for comparison?'
      }
    }
  }
};
