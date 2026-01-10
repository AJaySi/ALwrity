export const industries = [
  'General',
  'Technology',
  'Business',
  'Marketing',
  'Finance',
  'Healthcare',
  'Education',
  'Real Estate',
  'Entertainment',
  'Food & Beverage',
  'Travel',
  'Fashion',
  'Sports',
  'Science',
  'Law',
  'Other',
];

export const researchModes = [
  { value: 'basic', label: 'Basic - Quick insights' },
  { value: 'comprehensive', label: 'Comprehensive - In-depth analysis' },
  { value: 'targeted', label: 'Targeted - Specific focus' },
];

export const providers = [
  { value: 'google', label: '🔍 Google Search' },
  { value: 'exa', label: '🧠 Exa Neural Search' },
  { value: 'tavily', label: '🤖 Tavily AI Search' },
];

export const exaCategories = [
  { value: '', label: 'All Categories' },
  { value: 'company', label: 'Company Profiles' },
  { value: 'research paper', label: 'Research Papers' },
  { value: 'news', label: 'News Articles' },
  { value: 'pdf', label: 'PDF Documents' },
  { value: 'github', label: 'GitHub Repos' },
  { value: 'tweet', label: 'Tweets' },
  { value: 'personal site', label: 'Personal Sites' },
  { value: 'linkedin profile', label: 'LinkedIn Profiles' },
  { value: 'financial report', label: 'Financial Reports' },
];

export const exaSearchTypes = [
  { value: 'auto', label: 'Auto (Default) - Best of all worlds' },
  { value: 'fast', label: 'Fast - <500ms, speed-critical' },
  { value: 'deep', label: 'Deep - ~5000ms, comprehensive research' },
  { value: 'neural', label: 'Neural - Embeddings-based semantic' },
  { value: 'keyword', label: 'Keyword - Traditional search' },
];

export const tavilyTopics = [
  { value: 'general', label: 'General' },
  { value: 'news', label: 'News' },
  { value: 'finance', label: 'Finance' },
];

export const tavilySearchDepths = [
  { value: 'basic', label: 'Basic (1 credit) - Fast search' },
  { value: 'advanced', label: 'Advanced (2 credits) - Deep analysis' },
];

export const tavilyTimeRanges = [
  { value: '', label: 'No time filter' },
  { value: 'day', label: 'Last 24 hours' },
  { value: 'week', label: 'Last week' },
  { value: 'month', label: 'Last month' },
  { value: 'year', label: 'Last year' },
];

export const tavilyAnswerOptions = [
  { value: 'false', label: 'No answer' },
  { value: 'basic', label: 'Basic answer' },
  { value: 'advanced', label: 'Advanced answer' },
];

export const tavilyRawContentOptions = [
  { value: 'false', label: 'No raw content' },
  { value: 'markdown', label: 'Markdown format' },
  { value: 'text', label: 'Plain text' },
];

