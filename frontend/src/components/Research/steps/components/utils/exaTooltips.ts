/**
 * Detailed tooltips for Exa search options
 * These help educate end users about each Exa option
 */

export const exaOptionTooltips = {
  category: {
    title: "Content Category",
    description: "Filter results by content type. Choose a specific category to focus your search on particular content formats like research papers, news articles, or company profiles. Leave empty to search across all categories.",
    examples: {
      "research paper": "Best for academic papers, scientific publications, and scholarly content from sources like arXiv, Nature, IEEE.",
      "news": "Recent news articles and current events from news websites.",
      "company": "Company profiles, business information, and corporate websites.",
      "pdf": "PDF documents and downloadable files.",
      "github": "GitHub repositories, code, and technical documentation.",
      "tweet": "Twitter/X posts and social media content.",
      "personal site": "Personal blogs, portfolios, and individual websites.",
      "linkedin profile": "LinkedIn profiles and professional networking content.",
      "financial report": "Financial statements, earnings reports, and economic data.",
    }
  },
  
  searchType: {
    title: "Search Algorithm",
    description: "Choose how Exa searches the web. Each algorithm is optimized for different use cases and latency requirements. Exa uses embeddings-based 'next-link prediction' to understand semantic meaning, not just keyword matches.",
    types: {
      auto: {
        title: "Auto (Default) - Best of all worlds",
        description: "Intelligently combines multiple search methods (neural, keyword, and others) using a reranker model that adapts to your query type. Provides the best balance of quality and versatility without manual tuning.",
        whenToUse: "Recommended for most use cases. Use for general research, production workloads, or when query types vary significantly. Best when you want versatility without choosing a specific method.",
        latency: "Median latency: ~1000ms",
        quality: "High quality, versatile across query types",
      },
      fast: {
        title: "Fast - World's fastest search API",
        description: "Streamlined versions of neural and reranker models optimized for speed. Trades a small amount of performance for significant speed improvements. Best for applications where milliseconds matter.",
        whenToUse: "Use for real-time applications (voice agents, autocomplete), low-latency QA, or high-volume agent workflows where latency accumulates. Perfect when speed is critical.",
        latency: "Median latency: <500ms (excluding network)",
        quality: "Good factual accuracy, optimized for speed",
        note: "Best for single-step factual queries",
      },
      deep: {
        title: "Deep - Comprehensive research",
        description: "Comprehensive search with automatic query expansion or custom query variations. Runs parallel searches across multiple query formulations to find comprehensive results. Returns rich contextual summaries for each result.",
        whenToUse: "Use for agentic workflows, complex research tasks, multi-hop queries, or when comprehensive coverage matters more than speed. Ideal for research assistants and deep analysis.",
        latency: "Median latency: ~5000ms",
        quality: "Highest quality, comprehensive coverage",
        note: "Requires context=true for detailed summaries. Best for multi-step reasoning workflows.",
      },
      neural: {
        title: "Neural - Embeddings-based semantic search",
        description: "Uses AI embeddings and 'next-link prediction' to understand semantic meaning. Finds results that are conceptually similar even without exact keyword matches. Incorporated into Fast and Auto search types.",
        whenToUse: "Use for exploratory searches, finding semantically related content, or when you want to discover related concepts beyond exact keyword matches. Best for thematic and conceptual relationships.",
        latency: "Variable (incorporated into Fast/Auto)",
        quality: "Excellent semantic understanding",
        note: "Also available as part of Auto and Fast search types",
      },
      keyword: {
        title: "Keyword - Traditional search",
        description: "Traditional keyword-based search similar to Google. Uses exact keyword matching and ranking algorithms. Faster and more cost-effective than neural search.",
        whenToUse: "Use when you need precise keyword matching, want faster results, or are searching for specific terms, brands, or exact phrases.",
        limits: "Maximum 10 results with keyword search.",
        latency: "Fastest (traditional search)",
      },
    }
  },
  
  numResults: {
    title: "Number of Results",
    description: "How many search results to return. More results provide comprehensive coverage but take longer and cost more. Fewer results are faster and more focused.",
    recommendations: {
      "1-10": "Quick overview, fast results, lower cost. Good for simple queries or when you need just a few high-quality sources.",
      "11-25": "Balanced coverage. Recommended for most research tasks. Provides good depth without excessive cost.",
      "26-50": "Comprehensive research. Use for in-depth analysis, expert-level research, or when you need extensive source coverage.",
      "51-100": "Maximum coverage. Use for exhaustive research, literature reviews, or when you need to find every relevant source. Note: Only available with neural search.",
    },
    limits: "Keyword search: max 10 results. Neural search: max 100 results.",
  },
  
  highlights: {
    title: "Extract Highlights",
    description: "Enable AI-powered highlight extraction. Exa's AI identifies and extracts the most relevant text snippets from each result that match your query. These highlights are perfect for quick scanning and understanding key points.",
    benefits: [
      "Quick overview of each source without reading full content",
      "AI-identified most relevant passages",
      "Great for research summaries and citations",
      "Helps you quickly assess source relevance",
    ],
    whenToUse: "Enable for research, content creation, or when you want to quickly identify key information from sources. Recommended for most use cases.",
    cost: "Additional cost per page for highlight generation.",
  },
  
  context: {
    title: "Return Context String",
    description: "Combine all result contents into a single context string optimized for LLM processing. This is ideal for RAG (Retrieval-Augmented Generation) applications, AI analysis, or when you need to process all content together.",
    benefits: [
      "Single unified text string from all results",
      "Optimized for AI/LLM processing",
      "Better for RAG applications than highlights",
      "Recommended 10,000+ characters for best results",
    ],
    whenToUse: "Enable when you're using results with AI/LLM tools, need full content for analysis, or building RAG applications. Context strings often perform better than highlights for AI processing.",
    recommendation: "We recommend using 10,000+ characters for best performance, though no limit works best.",
  },
  
  includeDomains: {
    title: "Include Domains",
    description: "Restrict search results to specific domains only. If specified, results will ONLY come from these domains. Useful for searching within trusted sources, specific websites, or curated domain lists.",
    whenToUse: [
      "Searching within trusted sources (e.g., academic journals, reputable news sites)",
      "Focusing on specific websites or organizations",
      "Building curated research from known high-quality sources",
      "Ensuring all results come from verified domains",
    ],
    format: "Enter domains separated by commas. Example: arxiv.org, nature.com, ieee.org",
    example: "arxiv.org, paperswithcode.com, openai.com, deepmind.com",
    limit: "Maximum 1200 domains can be specified.",
  },
  
  excludeDomains: {
    title: "Exclude Domains",
    description: "Exclude specific domains from search results. If specified, no results will be returned from these domains. Useful for filtering out unwanted sources, spam sites, or low-quality content.",
    whenToUse: [
      "Filtering out spam or low-quality websites",
      "Excluding competitor sites from results",
      "Removing unwanted content sources",
      "Focusing on higher-quality domains",
    ],
    format: "Enter domains separated by commas. Example: spam.com, ads.com, low-quality-site.com",
    example: "spam.com, ads.com, clickbait-site.com",
    limit: "Maximum 1200 domains can be excluded.",
  },

  dateFilter: {
    title: "Start Published Date",
    description: "Filter results to only include content published after this date. This helps you find recent content or content from a specific time period onwards.",
    whenToUse: [
      "Finding recent content (e.g., last year, last month)",
      "Filtering by publication date",
      "Ensuring content freshness",
      "Time-sensitive research",
    ],
    format: "ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ (e.g., 2025-01-01T00:00:00.000Z)",
    example: "2025-01-01T00:00:00.000Z (content from January 1, 2025 onwards)",
    note: "Only links with a published date after this date will be returned.",
  },

  endPublishedDate: {
    title: "End Published Date",
    description: "Filter results to only include content published before this date. Use with Start Published Date to create a precise date range.",
    whenToUse: [
      "Creating a date range for published content",
      "Finding content from a specific time period",
      "Historical research within a timeframe",
      "Combining with Start Published Date for precise filtering",
    ],
    format: "ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ (e.g., 2025-12-31T23:59:59.999Z)",
    example: "2025-12-31T23:59:59.999Z (content up to December 31, 2025)",
    note: "Only links with a published date before this date will be returned. Use with Start Published Date to create a range.",
  },

  startCrawlDate: {
    title: "Start Crawl Date",
    description: "Filter results to only include links that Exa discovered (crawled) after this date. Crawl date refers to when Exa first found the link, not when it was published.",
    whenToUse: [
      "Finding recently discovered content",
      "Filtering by when Exa indexed the content",
      "Ensuring content is in Exa's index after a certain date",
      "Time-sensitive indexing requirements",
    ],
    format: "ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ (e.g., 2025-01-01T00:00:00.000Z)",
    example: "2025-01-01T00:00:00.000Z (links crawled after January 1, 2025)",
    note: "Crawl date is different from published date. This filters by when Exa discovered the link, not when it was originally published.",
  },

  endCrawlDate: {
    title: "End Crawl Date",
    description: "Filter results to only include links that Exa discovered (crawled) before this date. Use with Start Crawl Date to create a crawl date range.",
    whenToUse: [
      "Creating a crawl date range",
      "Finding content indexed within a specific period",
      "Historical indexing research",
      "Combining with Start Crawl Date for precise filtering",
    ],
    format: "ISO 8601 format: YYYY-MM-DDTHH:mm:ss.sssZ (e.g., 2025-12-31T23:59:59.999Z)",
    example: "2025-12-31T23:59:59.999Z (links crawled before December 31, 2025)",
    note: "Crawl date is different from published date. This filters by when Exa discovered the link. Use with Start Crawl Date to create a range.",
  },

  includeText: {
    title: "Include Text Filter",
    description: "Filter results to only include webpages that contain specific text. This helps narrow down results to pages mentioning specific terms or phrases.",
    whenToUse: [
      "Finding pages that mention specific terms",
      "Filtering by content keywords",
      "Ensuring results contain specific phrases",
      "Narrowing search to relevant content",
    ],
    format: "Enter up to 5 words. Example: 'large language model'",
    example: "large language model, artificial intelligence, machine learning",
    limit: "Currently only 1 string is supported, of up to 5 words. Checks webpage text.",
    note: "This filters results based on text content, not just metadata.",
  },

  excludeText: {
    title: "Exclude Text Filter",
    description: "Filter results to exclude webpages that contain specific text. This helps filter out unwanted content or pages mentioning terms you want to avoid.",
    whenToUse: [
      "Excluding pages with specific terms",
      "Filtering out unwanted content",
      "Avoiding certain topics or phrases",
      "Removing irrelevant results",
    ],
    format: "Enter up to 5 words. Example: 'course tutorial'",
    example: "course, tutorial, advertisement",
    limit: "Currently only 1 string is supported, of up to 5 words. Checks the first 1000 words of webpage text.",
    note: "This filters results based on text content, helping avoid unwanted pages.",
  },

  highlightsNumSentences: {
    title: "Highlights: Sentences Per Snippet",
    description: "Number of sentences to return for each highlight snippet. More sentences provide more context but increase response size.",
    whenToUse: [
      "Need more context in highlights (use 2-3 sentences)",
      "Want concise highlights (use 1 sentence)",
      "Balancing detail vs response size",
    ],
    format: "Integer, minimum 1",
    example: "2 sentences per highlight (default)",
    recommendation: "Use 1-2 sentences for concise highlights, 3+ for more context.",
  },

  highlightsPerUrl: {
    title: "Highlights: Snippets Per URL",
    description: "Number of highlight snippets to return for each search result. More highlights provide better coverage of the content but increase response size.",
    whenToUse: [
      "Need comprehensive coverage (use 3-5 highlights)",
      "Want quick overview (use 1-2 highlights)",
      "Balancing coverage vs response size",
    ],
    format: "Integer, minimum 1",
    example: "3 highlights per URL (default)",
    recommendation: "Use 3-5 highlights for comprehensive research, 1-2 for quick overviews.",
  },

  contextMaxCharacters: {
    title: "Context: Max Characters",
    description: "Maximum character limit for the context string. When context is enabled, all result contents are combined into one string. Higher limits provide more content but increase response size.",
    whenToUse: [
      "RAG applications (use 10,000+ characters)",
      "Comprehensive analysis (use 10,000+ characters)",
      "Limited response size (use 5,000-10,000 characters)",
      "Quick summaries (use 1,000-5,000 characters)",
    ],
    format: "Integer, recommended 10,000+ for best results",
    example: "10,000 characters (recommended for RAG)",
    recommendation: "We recommend using 10,000+ characters for best results, though no limit works best. Context strings often perform better than highlights for RAG applications.",
    note: "If you have 5 results and set 1000 characters, each result gets about 200 characters.",
  },

  textMaxCharacters: {
    title: "Text: Max Characters",
    description: "Maximum character limit for the full page text. This controls how much text content is retrieved from each webpage. Useful for controlling response size and API costs.",
    whenToUse: [
      "Controlling response size",
      "Limiting API costs",
      "Quick content preview (use 500-1000 characters)",
      "Full content analysis (use 5000+ characters)",
    ],
    format: "Integer, no strict limit",
    example: "1000 characters (default)",
    recommendation: "Use 1000-2000 for quick previews, 5000+ for comprehensive content analysis.",
  },

  summaryQuery: {
    title: "Summary: Custom Query",
    description: "Custom query to direct the LLM's generation of summaries. This helps get summaries focused on specific aspects of the content.",
    whenToUse: [
      "Need summaries focused on specific topics",
      "Customizing summary content",
      "Directing LLM attention to key aspects",
      "Getting targeted insights",
    ],
    format: "String query, e.g., 'Key advancements' or 'Main developments'",
    example: "Key insights about artificial intelligence",
    recommendation: "Use specific queries to get summaries focused on what you need. Leave empty for general summaries.",
  },
};
