/**
 * Industry-specific domain suggestions and Exa category mappings
 */
export const getIndustryDomainSuggestions = (industry: string): string[] => {
  const domainMap: Record<string, string[]> = {
    'Healthcare': ['pubmed.gov', 'nejm.org', 'thelancet.com', 'nih.gov'],
    'Technology': ['techcrunch.com', 'wired.com', 'arstechnica.com', 'theverge.com'],
    'Finance': ['wsj.com', 'bloomberg.com', 'ft.com', 'reuters.com'],
    'Science': ['nature.com', 'sciencemag.org', 'cell.com', 'pnas.org'],
    'Business': ['hbr.org', 'forbes.com', 'businessinsider.com', 'mckinsey.com'],
    'Marketing': ['marketingland.com', 'adweek.com', 'hubspot.com', 'moz.com'],
    'Education': ['edutopia.org', 'chronicle.com', 'insidehighered.com'],
    'Real Estate': ['realtor.com', 'zillow.com', 'forbes.com'],
    'Entertainment': ['variety.com', 'hollywoodreporter.com', 'deadline.com'],
    'Travel': ['lonelyplanet.com', 'nationalgeographic.com', 'travelandleisure.com'],
    'Fashion': ['vogue.com', 'elle.com', 'wwd.com'],
    'Sports': ['espn.com', 'si.com', 'bleacherreport.com'],
    'Law': ['law.com', 'abajournal.com', 'scotusblog.com'],
  };
  
  return domainMap[industry] || [];
};

export const getIndustryExaCategory = (industry: string): string | undefined => {
  const categoryMap: Record<string, string> = {
    'Healthcare': 'research paper',
    'Science': 'research paper',
    'Finance': 'financial report',
    'Technology': 'company',
    'Business': 'company',
    'Marketing': 'company',
    'Education': 'research paper',
    'Law': 'pdf',
  };
  
  return categoryMap[industry];
};

