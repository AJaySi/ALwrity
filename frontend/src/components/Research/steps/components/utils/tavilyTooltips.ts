/**
 * Detailed tooltips for Tavily search options
 * These help educate end users about each Tavily option
 */

export const tavilyOptionTooltips = {
  topic: {
    title: "Search Topic",
    description: "Choose the category of content you want to search. This helps Tavily optimize its search algorithm for your specific use case.",
    options: {
      general: {
        title: "General - Broad searches",
        description: "Best for general web searches, informational queries, and diverse content types. Use when you need a wide range of sources and perspectives.",
        whenToUse: "Use for general research, educational content, or when you're not sure which topic category fits best.",
      },
      news: {
        title: "News - Real-time updates",
        description: "Optimized for recent news articles, current events, and time-sensitive information. Provides access to the latest developments and breaking news.",
        whenToUse: "Use for current events, recent developments, breaking news, or when you need the most up-to-date information.",
      },
      finance: {
        title: "Finance - Financial data",
        description: "Focused on financial markets, economic data, company financials, stock information, and investment-related content.",
        whenToUse: "Use for financial research, market analysis, company financials, economic trends, or investment information.",
      },
    }
  },

  searchDepth: {
    title: "Search Depth",
    description: "Controls the depth and quality of search results. Higher depth means better relevance but longer latency and higher cost.",
    options: {
      basic: {
        title: "Basic - Balanced (1 credit)",
        description: "Provides one NLP summary per URL. Good balance between relevance, speed, and cost. Recommended for most use cases.",
        whenToUse: "Use for general research, quick searches, or when you need a good balance of quality and speed.",
        latency: "Fast",
        quality: "Good relevance",
        cost: "1 credit per search",
      },
      advanced: {
        title: "Advanced - Highest quality (2 credits)",
        description: "Provides multiple semantic snippets per URL for the highest relevance. Best for comprehensive research and expert-level analysis.",
        whenToUse: "Use for comprehensive research, expert analysis, or when you need the highest quality results. Enables chunks_per_source parameter.",
        latency: "Slower",
        quality: "Highest relevance",
        cost: "2 credits per search",
        note: "Allows chunks_per_source up to 3 for more detailed content per source",
      },
      fast: {
        title: "Fast - Good quality, lower latency (1 credit)",
        description: "Provides multiple semantic snippets per URL with optimized latency. Good quality with faster response times than advanced.",
        whenToUse: "Use when you need good relevance with lower latency than advanced mode. Enables chunks_per_source parameter.",
        latency: "Faster than advanced",
        quality: "Good relevance",
        cost: "1 credit per search",
        note: "Allows chunks_per_source up to 3",
      },
      "ultra-fast": {
        title: "Ultra-Fast - Minimal latency (1 credit)",
        description: "Minimizes latency while providing one NLP summary per URL. Best for time-critical queries where speed is essential.",
        whenToUse: "Use for time-critical queries, real-time applications, or when minimal latency is more important than maximum relevance.",
        latency: "Minimal",
        quality: "Good relevance",
        cost: "1 credit per search",
      },
    }
  },

  includeAnswer: {
    title: "AI Answer",
    description: "Get an AI-generated answer summarizing the search results. This provides a quick overview of the findings without reading all sources.",
    options: {
      false: {
        title: "Disabled",
        description: "No AI-generated answer. You'll only get the raw search results.",
        whenToUse: "Use when you want to analyze results yourself or when you don't need a summary.",
      },
      true: {
        title: "Basic Answer",
        description: "Quick AI-generated summary of the search results. Provides a concise overview.",
        whenToUse: "Use for quick summaries or when you need a brief overview of findings.",
      },
      basic: {
        title: "Basic Answer",
        description: "Quick AI-generated summary of the search results. Provides a concise overview.",
        whenToUse: "Use for quick summaries or when you need a brief overview of findings.",
      },
      advanced: {
        title: "Advanced Answer",
        description: "Detailed AI-generated answer with comprehensive insights from all search results. Best for in-depth analysis.",
        whenToUse: "Use for comprehensive research, detailed analysis, or when you need thorough insights from all sources.",
      },
    }
  },

  timeRange: {
    title: "Time Range",
    description: "Filter results by recency. Use this to find recent content within a specific time period. Shorthand options (d, w, m, y) are supported.",
    options: {
      day: {
        title: "Past Day",
        description: "Results from the last 24 hours. Best for breaking news and very recent developments.",
        whenToUse: "Use for breaking news, real-time updates, or very recent events.",
      },
      week: {
        title: "Past Week",
        description: "Results from the last 7 days. Good for recent news and current events.",
        whenToUse: "Use for recent news, current events, or weekly updates.",
      },
      month: {
        title: "Past Month",
        description: "Results from the last 30 days. Good for recent trends and monthly updates.",
        whenToUse: "Use for recent trends, monthly updates, or when you need relatively fresh content.",
      },
      year: {
        title: "Past Year",
        description: "Results from the last 12 months. Good for annual trends and yearly analysis.",
        whenToUse: "Use for annual trends, yearly analysis, or when you need content from the past year.",
      },
    },
    note: "For more precise date ranges, use Start Date and End Date fields instead.",
  },

  includeRawContent: {
    title: "Raw Content Format",
    description: "Include the raw HTML content from web pages. This provides full text content but may increase latency and response size.",
    options: {
      false: {
        title: "Disabled",
        description: "No raw content. You'll only get summaries and metadata.",
        whenToUse: "Use when you only need summaries and don't need full page content.",
      },
      true: {
        title: "Markdown Format",
        description: "Full page content formatted as Markdown. Preserves structure and formatting.",
        whenToUse: "Use when you need full page content with formatting preserved.",
      },
      markdown: {
        title: "Markdown Format",
        description: "Full page content formatted as Markdown. Preserves structure and formatting.",
        whenToUse: "Use when you need full page content with formatting preserved.",
      },
      text: {
        title: "Plain Text",
        description: "Full page content as plain text. No formatting, just raw text content.",
        whenToUse: "Use when you need full page content but don't need formatting.",
      },
    },
    note: "Including raw content may increase latency and response size. Use only when necessary.",
  },

  includeDomains: {
    title: "Include Domains",
    description: "Restrict search results to specific domains. Only results from these domains will be returned. Useful for trusted sources or specific websites.",
    examples: [
      "nature.com - For scientific articles from Nature",
      "arxiv.org - For academic papers from arXiv",
      "github.com - For code repositories and technical content",
      "news.ycombinator.com - For Hacker News discussions",
    ],
    whenToUse: "Use when you want to search only specific trusted sources or websites. Maximum 300 domains.",
    note: "Separate multiple domains with commas. Maximum 300 domains allowed.",
  },

  excludeDomains: {
    title: "Exclude Domains",
    description: "Exclude specific domains from search results. Results from these domains will be filtered out. Useful for avoiding spam or unwanted sources.",
    examples: [
      "spam.com - Exclude spam websites",
      "ads.com - Exclude ad-heavy sites",
      "example.com - Exclude specific unwanted sources",
    ],
    whenToUse: "Use when you want to filter out specific domains or avoid unwanted sources. Maximum 150 domains.",
    note: "Separate multiple domains with commas. Maximum 150 domains allowed.",
  },

  country: {
    title: "Country Code",
    description: "Boost results from a specific country. This helps prioritize content from a particular geographic region. Use lowercase full country name.",
    examples: [
      "united states - For US-focused results",
      "united kingdom - For UK-focused results",
      "india - For India-focused results",
      "canada - For Canada-focused results",
    ],
    whenToUse: "Use when you need region-specific content or want to prioritize results from a particular country.",
    note: "Use lowercase full country name (e.g., 'united states' not 'US'). Works best with 'general' topic.",
  },

  startDate: {
    title: "Start Date",
    description: "Return only results published after this date. Provides precise date filtering for more accurate time-based searches.",
    whenToUse: "Use when you need results from a specific date onwards. More precise than time_range.",
    note: "Format: YYYY-MM-DD. Use with End Date to create a date range.",
  },

  endDate: {
    title: "End Date",
    description: "Return only results published before this date. Use with Start Date to create a precise date range.",
    whenToUse: "Use when you need results up to a specific date. More precise than time_range.",
    note: "Format: YYYY-MM-DD. Use with Start Date to create a date range.",
  },

  chunksPerSource: {
    title: "Chunks Per Source",
    description: "Number of content chunks to return per source. Higher values provide more detailed content from each source but may increase response size.",
    whenToUse: "Use with 'advanced' or 'fast' search_depth to get more detailed content per source. Maximum is 3.",
    note: "Only available with 'advanced' or 'fast' search_depth. Maximum is 3 chunks per source.",
    range: "1-3 chunks per source",
  },

  includeImages: {
    title: "Include Images",
    description: "Include query-related images in the search results. Images are selected based on relevance to your search query.",
    whenToUse: "Use when you need visual content related to your search query, such as charts, diagrams, or illustrations.",
    note: "Enabling this may increase response size. Use include_image_descriptions for AI-generated image descriptions.",
  },

  includeImageDescriptions: {
    title: "Include Image Descriptions",
    description: "Include AI-generated descriptions of images. Provides context about what each image contains. Requires include_images to be enabled.",
    whenToUse: "Use when you need to understand image content without viewing the images directly.",
    note: "Requires 'Include Images' to be enabled. Provides AI-generated descriptions of image content.",
  },

  includeFavicon: {
    title: "Include Favicon URLs",
    description: "Include the favicon (website icon) URL for each search result. Useful for visual identification of sources.",
    whenToUse: "Use when you want to display source icons or visually identify different sources in your UI.",
    note: "Provides the favicon URL for each result, useful for UI display purposes.",
  },

  autoParameters: {
    title: "Auto-Configure Parameters",
    description: "Let Tavily automatically optimize search parameters based on your query. Uses AI to select the best settings for your specific search.",
    whenToUse: "Use when you're unsure about optimal settings or want Tavily to automatically optimize for your query.",
    note: "Costs 2 credits per search. Use sparingly as it's more expensive than manual configuration.",
  },
};

/**
 * Get tooltip content for a specific Tavily option
 */
export const getTavilyTooltipContent = (optionKey: keyof typeof tavilyOptionTooltips, value?: string): string => {
  const tooltip = tavilyOptionTooltips[optionKey];
  
  if (!tooltip) {
    return `Information about ${optionKey}`;
  }

  // Handle options with nested value-specific tooltips
  if ('options' in tooltip && value) {
    const valueTooltip = (tooltip.options as any)[value];
    if (valueTooltip) {
      let content = `**${valueTooltip.title}**\n\n${valueTooltip.description}\n\n`;
      if (valueTooltip.whenToUse) {
        content += `**When to use:** ${valueTooltip.whenToUse}\n\n`;
      }
      if (valueTooltip.latency) {
        content += `**Latency:** ${valueTooltip.latency}\n\n`;
      }
      if (valueTooltip.quality) {
        content += `**Quality:** ${valueTooltip.quality}\n\n`;
      }
      if (valueTooltip.cost) {
        content += `**Cost:** ${valueTooltip.cost}\n\n`;
      }
      if (valueTooltip.note) {
        content += `**Note:** ${valueTooltip.note}`;
      }
      return content;
    }
  }

  // Handle tooltips with examples
  if ('examples' in tooltip && Array.isArray(tooltip.examples)) {
    let content = `**${tooltip.title}**\n\n${tooltip.description}\n\n`;
    if (tooltip.whenToUse) {
      content += `**When to use:** ${tooltip.whenToUse}\n\n`;
    }
    content += `**Examples:**\n${tooltip.examples.map(ex => `• ${ex}`).join('\n')}\n\n`;
    if (tooltip.note) {
      content += `**Note:** ${tooltip.note}`;
    }
    return content;
  }

  // Default tooltip format
  let content = `**${tooltip.title}**\n\n${tooltip.description}\n\n`;
  if ('whenToUse' in tooltip && tooltip.whenToUse) {
    content += `**When to use:** ${tooltip.whenToUse}\n\n`;
  }
  if ('note' in tooltip && tooltip.note) {
    content += `**Note:** ${tooltip.note}`;
  }
  if ('range' in tooltip && tooltip.range) {
    content += `**Range:** ${tooltip.range}`;
  }

  return content;
};
