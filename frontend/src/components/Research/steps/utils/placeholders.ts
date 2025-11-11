/**
 * Industry-specific placeholder examples for personalized experience
 */
export const getIndustryPlaceholders = (industry: string): string[] => {
  const industryExamples: Record<string, string[]> = {
    Healthcare: [
      "Research: AI-powered diagnostic tools in clinical practice\n\n💡 What you'll get:\n• FDA-approved AI medical devices\n• Clinical accuracy and patient outcomes\n• Implementation costs and ROI",
      "Analyze: Telemedicine adoption trends and patient satisfaction\n\n💡 Research includes:\n• Post-pandemic telehealth growth\n• Remote patient monitoring technologies\n• Insurance coverage and reimbursement",
      "Investigate: Personalized medicine and genomic testing advances\n\n💡 You'll discover:\n• Latest genomic sequencing technologies\n• Precision therapy success rates\n• Ethical considerations and regulations"
    ],
    Technology: [
      "Investigate: Latest developments in edge computing and IoT\n\n💡 What you'll get:\n• Edge AI deployment strategies\n• 5G integration and performance\n• Industry use cases and benchmarks",
      "Compare: Cloud providers for enterprise SaaS applications\n\n💡 Research includes:\n• AWS vs Azure vs GCP feature comparison\n• Cost optimization strategies\n• Security and compliance certifications",
      "Analyze: Quantum computing breakthroughs and commercial applications\n\n💡 You'll discover:\n• Latest quantum hardware developments\n• Real-world problem solving examples\n• Investment landscape and timeline"
    ],
    Finance: [
      "Research: DeFi regulatory landscape and compliance challenges\n\n💡 What you'll get:\n• Global regulatory frameworks\n• Compliance best practices\n• Risk management strategies",
      "Analyze: Digital banking customer retention strategies\n\n💡 Research includes:\n• Neobank growth and market share\n• Customer acquisition costs and LTV\n• Personalization and UX innovations",
      "Investigate: ESG investing trends and impact measurement\n\n💡 You'll discover:\n• ESG rating methodologies\n• Fund performance and returns\n• Regulatory requirements and reporting"
    ],
    Marketing: [
      "Research: AI-powered marketing automation and personalization\n\n💡 What you'll get:\n• Top marketing AI platforms and features\n• ROI and conversion rate improvements\n• Implementation case studies",
      "Analyze: Influencer marketing ROI and authenticity trends\n\n💡 Research includes:\n• Micro vs macro influencer effectiveness\n• Platform-specific engagement rates\n• Brand partnership best practices",
      "Investigate: Privacy-first marketing in a cookieless world\n\n💡 You'll discover:\n• First-party data strategies\n• Contextual targeting innovations\n• Compliance with privacy regulations"
    ],
    Business: [
      "Research: Remote work policies and hybrid workplace models\n\n💡 What you'll get:\n• Productivity metrics and employee satisfaction\n• Technology infrastructure requirements\n• Cultural impact and change management",
      "Analyze: Supply chain resilience and diversification strategies\n\n💡 Research includes:\n• Nearshoring and reshoring trends\n• Technology solutions for visibility\n• Risk mitigation frameworks",
      "Investigate: Sustainability initiatives and corporate ESG programs\n\n💡 You'll discover:\n• Industry-specific sustainability benchmarks\n• Cost-benefit analysis of green initiatives\n• Stakeholder communication strategies"
    ],
    Education: [
      "Research: EdTech tools for personalized learning experiences\n\n💡 What you'll get:\n• Adaptive learning platform comparisons\n• Student engagement and outcomes data\n• Implementation costs and training needs",
      "Analyze: Microlearning and skill-based education trends\n\n💡 Research includes:\n• Corporate training effectiveness\n• Platform and content recommendations\n• ROI and completion rates",
      "Investigate: AI tutoring systems and student support tools\n\n💡 You'll discover:\n• Natural language processing advances\n• Student performance improvements\n• Accessibility and inclusion features"
    ],
    'Real Estate': [
      "Research: PropTech innovations transforming property management\n\n💡 What you'll get:\n• Smart building technologies and IoT\n• Tenant experience platforms\n• Operational efficiency gains",
      "Analyze: Virtual staging and 3D property tours adoption\n\n💡 Research includes:\n• Technology provider comparisons\n• Impact on sales velocity and pricing\n• Cost vs traditional staging",
      "Investigate: Real estate tokenization and fractional ownership\n\n💡 You'll discover:\n• Blockchain platforms and regulations\n• Investor demographics and demand\n• Liquidity and exit strategies"
    ],
    Travel: [
      "Research: Sustainable tourism trends and eco-travel preferences\n\n💡 What you'll get:\n• Green certification programs\n• Traveler willingness to pay premium\n• Destination best practices",
      "Analyze: AI-powered travel personalization and recommendations\n\n💡 Research includes:\n• Recommendation engine technologies\n• Booking conversion rate improvements\n• Customer lifetime value impact",
      "Investigate: Bleisure travel and workation destination trends\n\n💡 You'll discover:\n• Remote work-friendly destinations\n• Co-working and accommodation options\n• Digital nomad demographics"
    ]
  };

  return industryExamples[industry] || [
    "Research: Latest AI advancements in your industry\n\n💡 What you'll get:\n• Recent breakthroughs and innovations\n• Key companies and technologies\n• Expert insights and market trends",
    
    "Write a blog on: Emerging trends shaping your industry in 2025\n\n💡 This will research:\n• Technology disruptions and innovations\n• Regulatory changes and compliance\n• Consumer behavior shifts",
    
    "Analyze: Best practices and success stories in your field\n\n💡 Research includes:\n• Industry leader strategies\n• Implementation case studies\n• ROI and performance metrics",
    
    "https://example.com/article\n\n💡 URL detected! Research will:\n• Extract key insights from the article\n• Find related sources and updates\n• Provide comprehensive context"
  ];
};

