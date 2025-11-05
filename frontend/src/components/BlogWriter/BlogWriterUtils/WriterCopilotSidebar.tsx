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
    <>
      <style>{`
        /* Enterprise CopilotKit Suggestion Styling */
        
        /* All suggestion chips - base styling */
        .copilotkit-suggestions button,
        .copilot-suggestions button,
        [class*="suggestion"] button,
        [class*="Suggestion"] button {
          position: relative;
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          border-radius: 12px;
          border: 1px solid rgba(99, 102, 241, 0.2);
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          overflow: hidden;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(249, 250, 251, 0.98) 100%);
          color: #4b5563;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.5) inset;
          letter-spacing: 0.01em;
        }
        
        /* Shine effect on hover */
        .copilotkit-suggestions button::before,
        .copilot-suggestions button::before,
        [class*="suggestion"] button::before,
        [class*="Suggestion"] button::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
          transition: left 0.6s ease;
        }
        
        .copilotkit-suggestions button:hover::before,
        .copilot-suggestions button:hover::before,
        [class*="suggestion"] button:hover::before,
        [class*="Suggestion"] button:hover::before {
          left: 100%;
        }
        
        /* Regular suggestions - hover effects */
        .copilotkit-suggestions button:hover,
        .copilot-suggestions button:hover,
        [class*="suggestion"] button:hover:not([class*="next-suggestion"]),
        [class*="Suggestion"] button:hover:not([class*="next-suggestion"]) {
          transform: translateY(-2px) scale(1.02);
          box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2), 0 0 0 1px rgba(255, 255, 255, 0.6) inset;
          border-color: rgba(99, 102, 241, 0.3);
          background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(249, 250, 251, 1) 100%);
        }
        
        /* "Next:" Suggestions - Premium Enterprise Style */
        .copilotkit-suggestions button[data-is-next="true"],
        .copilot-suggestions button[data-is-next="true"],
        .copilotkit-suggestions button.next-suggestion,
        .copilot-suggestions button.next-suggestion,
        .copilotkit-suggestions button[aria-label*="Next:"],
        .copilot-suggestions button[aria-label*="Next:"] {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
          color: white !important;
          border: 1px solid rgba(255, 255, 255, 0.3) !important;
          box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4),
                      0 0 0 1px rgba(255, 255, 255, 0.2) inset,
                      0 2px 4px rgba(0, 0, 0, 0.1) inset,
                      0 0 20px rgba(102, 126, 234, 0.3) !important;
          font-weight: 700 !important;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          position: relative;
          animation: nextSuggestionPulse 3s ease-in-out infinite;
        }
        
        /* Pulse animation for Next suggestions */
        @keyframes nextSuggestionPulse {
          0%, 100% {
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4),
                        0 0 0 1px rgba(255, 255, 255, 0.2) inset,
                        0 2px 4px rgba(0, 0, 0, 0.1) inset,
                        0 0 20px rgba(102, 126, 234, 0.3);
          }
          50% {
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.5),
                        0 0 0 1px rgba(255, 255, 255, 0.25) inset,
                        0 2px 4px rgba(0, 0, 0, 0.1) inset,
                        0 0 30px rgba(102, 126, 234, 0.5);
          }
        }
        
        /* Next suggestion hover - enhanced */
        .copilotkit-suggestions button[data-is-next="true"]:hover,
        .copilot-suggestions button[data-is-next="true"]:hover,
        .copilotkit-suggestions button.next-suggestion:hover,
        .copilot-suggestions button.next-suggestion:hover,
        .copilotkit-suggestions button[aria-label*="Next:"]:hover,
        .copilot-suggestions button[aria-label*="Next:"]:hover {
          transform: translateY(-3px) scale(1.05) !important;
          box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6),
                      0 0 0 1px rgba(255, 255, 255, 0.3) inset,
                      0 3px 6px rgba(0, 0, 0, 0.15) inset,
                      0 0 40px rgba(102, 126, 234, 0.6) !important;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 40%, #f093fb 60%, #4facfe 100%) !important;
          animation: none;
        }
        
        /* Next suggestion active */
        .copilotkit-suggestions button[data-is-next="true"]:active,
        .copilot-suggestions button[data-is-next="true"]:active,
        .copilotkit-suggestions button.next-suggestion:active,
        .copilot-suggestions button.next-suggestion:active,
        .copilotkit-suggestions button[aria-label*="Next:"]:active,
        .copilot-suggestions button[aria-label*="Next:"]:active {
          transform: translateY(-1px) scale(1.02) !important;
          box-shadow: 0 3px 12px rgba(102, 126, 234, 0.5),
                      0 0 0 1px rgba(255, 255, 255, 0.25) inset,
                      0 1px 3px rgba(0, 0, 0, 0.1) inset !important;
        }
        
        /* Next suggestion focus */
        .copilotkit-suggestions button[data-is-next="true"]:focus-visible,
        .copilot-suggestions button[data-is-next="true"]:focus-visible,
        .copilotkit-suggestions button.next-suggestion:focus-visible,
        .copilot-suggestions button.next-suggestion:focus-visible,
        .copilotkit-suggestions button[aria-label*="Next:"]:focus-visible,
        .copilot-suggestions button[aria-label*="Next:"]:focus-visible {
          outline: none !important;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.4),
                      0 4px 16px rgba(102, 126, 234, 0.4),
                      0 0 0 1px rgba(255, 255, 255, 0.2) inset,
                      0 0 30px rgba(102, 126, 234, 0.5) !important;
        }
        
        /* Match buttons by text content using data attributes or class */
        /* We'll inject a data attribute via JS to identify Next suggestions */
        
        /* Regular suggestion active state */
        .copilotkit-suggestions button:active:not([data-is-next="true"]):not(.next-suggestion),
        .copilot-suggestions button:active:not([data-is-next="true"]):not(.next-suggestion) {
          transform: translateY(0) scale(0.98);
          box-shadow: 0 2px 6px rgba(99, 102, 241, 0.15);
        }
        
        /* Focus states for regular suggestions */
        .copilotkit-suggestions button:focus-visible:not([data-is-next="true"]):not(.next-suggestion),
        .copilot-suggestions button:focus-visible:not([data-is-next="true"]):not(.next-suggestion) {
          outline: none;
          box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3), 0 4px 12px rgba(99, 102, 241, 0.2);
        }
        
        /* Enhanced suggestion container */
        .copilotkit-suggestions,
        .copilot-suggestions {
          display: grid;
          grid-template-columns: 1fr;
          gap: 10px;
          margin: 16px 0;
          padding: 12px;
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(249, 250, 251, 0.6) 100%);
          border-radius: 12px;
          backdrop-filter: blur(8px);
        }
        
        @media (min-width: 420px) {
          .copilotkit-suggestions,
          .copilot-suggestions {
            grid-template-columns: 1fr 1fr;
            gap: 12px;
          }
        }
        
        /* Smooth transitions */
        * {
          transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
        }
      `}</style>
      
      {/* Inject data attributes to identify Next suggestions */}
      <script
        dangerouslySetInnerHTML={{
          __html: `
            (function() {
              const observer = new MutationObserver(() => {
                const suggestionButtons = document.querySelectorAll(
                  '.copilotkit-suggestions button, .copilot-suggestions button, [class*="suggestion"] button'
                );
                suggestionButtons.forEach(btn => {
                  const text = btn.textContent || btn.innerText || '';
                  if (text.includes('Next:')) {
                    btn.setAttribute('data-is-next', 'true');
                    btn.classList.add('next-suggestion');
                  } else {
                    btn.removeAttribute('data-is-next');
                    btn.classList.remove('next-suggestion');
                  }
                });
              });
              
              observer.observe(document.body, {
                childList: true,
                subtree: true
              });
              
              // Initial run
              setTimeout(() => {
                const suggestionButtons = document.querySelectorAll(
                  '.copilotkit-suggestions button, .copilot-suggestions button, [class*="suggestion"] button'
                );
                suggestionButtons.forEach(btn => {
                  const text = btn.textContent || btn.innerText || '';
                  if (text.includes('Next:')) {
                    btn.setAttribute('data-is-next', 'true');
                    btn.classList.add('next-suggestion');
                  }
                });
              }, 100);
            })();
          `
        }}
      />
      
      <CopilotSidebar
        labels={{
          title: 'ALwrity Co-Pilot',
          initial: !research
            ? 'Hi! I can help you research, outline, and draft your blog. Just tell me what topic you want to write about and I\'ll get started!'
            : 'Great! I can see you have research data. Let me help you create an outline and generate content for your blog.',
        }}
        suggestions={suggestions}
      makeSystemMessage={(context: string, additional?: string) => {
        const hasResearch = research !== null && research !== undefined;
        const hasOutline = outline && outline.length > 0;
        const isOutlineConfirmed = outlineConfirmed;
        const researchInfo = hasResearch && research
          ? {
              sources: research?.sources?.length || 0,
              queries: research?.search_queries?.length || 0,
              angles: research?.suggested_angles?.length || 0,
              primaryKeywords: research?.keyword_analysis?.primary || [],
              searchIntent: research?.keyword_analysis?.search_intent || 'informational',
            }
          : null;

        const outlineContext = hasOutline && outline
          ? `
OUTLINE DETAILS:
- Total sections: ${outline.length}
- Section headings: ${(outline || []).map((s: any) => s?.heading || 'Untitled').join(', ')}
- Total target words: ${(outline || []).reduce((sum: number, s: any) => sum + (s?.target_words || 0), 0)}
- Section breakdown: ${(outline || [])
              .map(
                (s: any) => `${s?.heading || 'Untitled'} (${s?.target_words || 0} words, ${s?.subheadings?.length || 0} subheadings, ${s?.key_points?.length || 0} key points)`
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

${hasOutline && outline ? `✅ OUTLINE GENERATED: ${outline.length} sections created${isOutlineConfirmed ? ' (CONFIRMED)' : ' (PENDING CONFIRMATION)'}` : '❌ No outline generated yet'}
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
    </>
  );
};

export default WriterCopilotSidebar;


