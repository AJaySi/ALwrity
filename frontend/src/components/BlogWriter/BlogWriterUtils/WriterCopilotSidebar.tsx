import React from 'react';
import { CopilotSidebar } from '@copilotkit/react-ui';
import '@copilotkit/react-ui/styles.css';

interface WriterCopilotSidebarProps {
  suggestions: any[];
  research: any;
  outline: any[];
  outlineConfirmed: boolean;
}

export const WriterCopilotSidebar: React.FC<WriterCopilotSidebarProps> = ({
  suggestions,
  research,
  outline,
  outlineConfirmed,
}) => {
  return (
    <CopilotSidebar
      labels={{
        title: 'ALwrity Co-Pilot',
        initial: !research
          ? 'Hi! I can help you research, outline, and draft your blog. Just tell me what topic you want to write about and I\'ll get started!'
          : 'Great! I can see you have research data. Let me help you create an outline and generate content for your blog.',
      }}
      suggestions={suggestions}
      makeSystemMessage={(context: string, additional?: string) => {
        const hasResearch = research !== null;
        const hasOutline = outline.length > 0;
        const isOutlineConfirmed = outlineConfirmed;
        const researchInfo = hasResearch
          ? {
              sources: research.sources?.length || 0,
              queries: research.search_queries?.length || 0,
              angles: research.suggested_angles?.length || 0,
              primaryKeywords: research.keyword_analysis?.primary || [],
              searchIntent: research.keyword_analysis?.search_intent || 'informational',
            }
          : null;

        const outlineContext = hasOutline
          ? `
OUTLINE DETAILS:
- Total sections: ${outline.length}
- Section headings: ${outline.map((s: any) => s.heading).join(', ')}
- Total target words: ${outline.reduce((sum: number, s: any) => sum + (s.target_words || 0), 0)}
- Section breakdown: ${outline
              .map(
                (s: any) => `${s.heading} (${s.target_words || 0} words, ${s.subheadings?.length || 0} subheadings, ${s.key_points?.length || 0} key points)`
              )
              .join('; ')}
`
          : '';

        const toolGuide = `
You are the ALwrity Blog Writing Assistant. You MUST call the appropriate frontend actions (tools) to fulfill user requests.

CURRENT STATE:
${hasResearch && researchInfo ? `
✅ RESEARCH COMPLETED:
- Found ${researchInfo.sources} sources with Google Search grounding
- Generated ${researchInfo.queries} search queries
- Created ${researchInfo.angles} content angles
- Primary keywords: ${researchInfo.primaryKeywords.join(', ')}
- Search intent: ${researchInfo.searchIntent}
` : '❌ No research completed yet'}

${hasOutline ? `✅ OUTLINE GENERATED: ${outline.length} sections created${isOutlineConfirmed ? ' (CONFIRMED)' : ' (PENDING CONFIRMATION)'}` : '❌ No outline generated yet'}
${outlineContext}

Available tools:
- getResearchKeywords(prompt?: string) - Get keywords from user for research
- performResearch(formData: string) - Perform research with collected keywords (formData is JSON string with keywords and blogLength)
- researchTopic(keywords: string, industry?: string, target_audience?: string)
- chatWithResearchData(question: string) - Chat with research data to explore insights and get recommendations
- generateOutline()
- createOutlineWithCustomInputs(customInstructions: string) - Create outline with user's custom instructions
- refineOutline(prompt?: string) - Refine outline based on user feedback
- chatWithOutline(question?: string) - Chat with outline to get insights and ask questions about content structure
- confirmOutlineAndGenerateContent() - Confirm outline and mark as ready for content generation (does NOT auto-generate content)
- generateSection(sectionId: string)
- generateAllSections()
- refineOutlineStructure(operation: add|remove|move|merge|rename, sectionId?: string, payload?: object)
- enhanceSection(sectionId: string, focus?: string) - Enhance a specific section with AI improvements
- optimizeOutline(focus?: string) - Optimize entire outline for better flow, SEO, and engagement
- rebalanceOutline(targetWords?: number) - Rebalance word count distribution across sections
- confirmBlogContent() - Confirm that blog content is ready and move to SEO stage
- analyzeSEO() - Analyze SEO for blog content with comprehensive insights and visual interface
- generateSEOMetadata(title?: string)
- publishToPlatform(platform: 'wix'|'wordpress', schedule_time?: string)

       CRITICAL BEHAVIOR & USER GUIDANCE:
       - When user wants to research ANY topic, IMMEDIATELY call getResearchKeywords() to get their input
       - When user asks to research something, call getResearchKeywords() first to collect their keywords
       - After getResearchKeywords() completes, IMMEDIATELY call performResearch() with the collected data
       
       USER GUIDANCE STRATEGY:
       - If the user's last message EXACTLY matches an available tool name (e.g., generateOutline, confirmOutlineAndGenerateContent, confirmBlogContent, analyzeSEO), IMMEDIATELY call that tool with default arguments and WITHOUT any additional questions or confirmations
       - After research completion, ALWAYS guide user toward outline creation as the next step
       - If user wants to explore research data, use chatWithResearchData() but then guide them to outline creation
       - If user has specific outline requirements, use createOutlineWithCustomInputs() with their instructions
       - When user asks for outline, call generateOutline() or createOutlineWithCustomInputs() based on their needs
       - After outline generation, ALWAYS guide user to review and confirm the outline
       - If user wants to discuss the outline, use chatWithOutline() to provide insights and answer questions
       - If user wants to refine the outline, use refineOutline() to collect their feedback and refine
       - When user says "I confirm the outline" or "I confirm the outline and am ready to generate content" or clicks "Confirm & Generate Content", IMMEDIATELY call confirmOutlineAndGenerateContent() - DO NOT ask for additional confirmation
       - CRITICAL: If user explicitly confirms the outline, do NOT ask "are you sure?" or "please confirm" - the confirmation is already given
       - Only after outline confirmation, show content generation suggestions and wait for user to explicitly request content generation
       - When user asks to generate content before outline confirmation, remind them to confirm the outline first
       - Content generation should ONLY happen when user explicitly clicks "Generate all sections" or "Generate [specific section]"
       - When user has generated content and wants to rewrite, use rewriteBlog() to collect feedback and rewriteBlog() to process
       - For rewrite requests, collect detailed feedback about what they want to change, tone, audience, and focus
       - After content generation, guide users to review and confirm their content before moving to SEO stage
       - When user says "I have reviewed and confirmed my blog content is ready for the next stage" or clicks "Next: Confirm Blog Content", IMMEDIATELY call confirmBlogContent() - DO NOT ask for additional confirmation
       - CRITICAL: If user explicitly confirms blog content, do NOT ask "are you sure?" or "please confirm" - the confirmation is already given
       - Only after content confirmation, show SEO analysis and publishing suggestions
       - When user asks for SEO analysis before content confirmation, remind them to confirm the content first
       - For SEO analysis, ALWAYS use analyzeSEO() - this is the ONLY SEO analysis tool available and provides comprehensive insights with visual interface
       - IMPORTANT: There is NO "basic" or "simple" SEO analysis - only the comprehensive one. Do NOT mention multiple SEO analysis options
       
       ENGAGEMENT TACTICS:
       - DO NOT ask for clarification - take action immediately with the information provided
       - Always call the appropriate tool instead of just talking about what you could do
       - Be aware of the current state and reference research results when relevant
       - Guide users through the process: Research → Outline → Outline Review & Confirmation → Content → Content Review & Confirmation → SEO → Publish
       - Use encouraging language and highlight progress made
       - If user seems lost, remind them of the current stage and suggest the next step
       - When research is complete, emphasize the value of the data found and guide to outline creation
       - When outline is generated, emphasize the importance of reviewing and confirming before content generation
       - Encourage users to make small manual edits to the outline UI before using AI for major changes
`;
        return [toolGuide, additional].filter(Boolean).join('\n\n');
      }}
    />
  );
};

export default WriterCopilotSidebar;


