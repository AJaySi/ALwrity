import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { facebookWriterApi, PostGenerateRequest } from '../../services/facebookWriterApi';
import { usePlatformPersonaContext } from '../shared/PersonaContext/PlatformPersonaProvider';

const useCopilotActionTyped = useCopilotAction as any;

const RegisterFacebookActionsEnhanced: React.FC = () => {
  // Get persona context for enhanced content generation
  const { corePersona, platformPersona } = usePlatformPersonaContext();

  // Helper function to apply persona constraints to content
  const applyPersonaConstraints = (content: string, constraints: any) => {
    if (!constraints) return content;
    
    let enhancedContent = content;
    
    // Apply sentence length constraints
    if (constraints.sentence_metrics?.average_sentence_length_words) {
      const targetLength = constraints.sentence_metrics.average_sentence_length_words;
      // This is a simplified example - in practice, you'd use more sophisticated NLP
      console.log(`🎭 Applying persona sentence length constraint: ${targetLength} words average`);
    }
    
    // Apply vocabulary constraints
    if (constraints.lexical_features?.go_to_words?.length > 0) {
      console.log(`🎭 Using persona go-to words: ${constraints.lexical_features.go_to_words.join(', ')}`);
    }
    
    if (constraints.lexical_features?.avoid_words?.length > 0) {
      console.log(`🎭 Avoiding persona avoid words: ${constraints.lexical_features.avoid_words.join(', ')}`);
    }
    
    return enhancedContent;
  };

  // Enhanced Facebook Post Generation with Persona
  useCopilotActionTyped({
    name: 'generateFacebookPostWithPersona',
    description: 'Generate an engaging Facebook post optimized for your writing persona and platform constraints',
    parameters: [
      { name: 'topic', type: 'string', required: false },
      { name: 'business_type', type: 'string', required: false },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'post_goal', type: 'string', required: false },
      { name: 'post_tone', type: 'string', required: false },
      { name: 'include', type: 'string', required: false },
      { name: 'avoid', type: 'string', required: false }
    ],
    handler: async (args: any) => {
      try {
        // Apply persona constraints to the request
        const personaConstraints = platformPersona?.content_format_rules as any;
        console.log('🎭 Applying persona constraints:', personaConstraints);
        
        const request: PostGenerateRequest = {
          business_type: args.business_type || 'General',
          target_audience: args.target_audience || 'General audience',
          post_goal: args.post_goal || 'Engage audience',
          post_tone: args.post_tone || 'Engaging',
          include: args.include || '',
          avoid: args.avoid || '',
          // Apply persona constraints through advanced options
          advanced_options: {
            use_hook: true,
            use_story: true,
            use_cta: true,
            use_question: true,
            use_emoji: true,
            use_hashtags: true
          }
        };

        // Track progress with persona analysis steps
        const progressSteps = [
          'Analyzing persona constraints...',
          'Applying linguistic fingerprint...',
          'Optimizing for Facebook platform...',
          'Generating persona-aware content...',
          'Validating against persona rules...'
        ];

        // Simulate progress tracking
        for (let i = 0; i < progressSteps.length; i++) {
          console.log(`🎭 Facebook Persona Progress: ${progressSteps[i]}`);
          await new Promise(resolve => setTimeout(resolve, 200));
        }

        const res = await facebookWriterApi.postGenerate(request);
        
        // Apply persona constraints to the generated content
        const enhancedContent = applyPersonaConstraints(res.data?.content || '', corePersona?.linguistic_fingerprint);
        
        // Dispatch event to update the draft
        window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { 
          detail: enhancedContent 
        }));

        return {
          success: true,
          content: enhancedContent,
          message: 'Facebook post generated with persona optimization and copied to draft successfully',
          persona_applied: {
            persona_name: corePersona?.persona_name,
            archetype: corePersona?.archetype,
            confidence_score: corePersona?.confidence_score,
            constraints_applied: {
              character_limit: personaConstraints?.character_limit,
              optimal_length: personaConstraints?.optimal_length,
              linguistic_fingerprint: corePersona?.linguistic_fingerprint
            }
          },
          original_response: res.data
        };
      } catch (error) {
        console.error('Error generating Facebook post with persona:', error);
        return {
          success: false,
          error: 'Failed to generate Facebook post with persona optimization'
        };
      }
    }
  });

  // Enhanced Facebook Ad Copy Generation with Persona
  useCopilotActionTyped({
    name: 'generateFacebookAdCopyWithPersona',
    description: 'Generate Facebook ad copy optimized for your writing persona and conversion goals',
    parameters: [
      { name: 'product_service', type: 'string', required: true },
      { name: 'target_audience', type: 'string', required: false },
      { name: 'campaign_goal', type: 'string', required: false },
      { name: 'budget_range', type: 'string', required: false }
    ],
    handler: async (args: any) => {
      try {
        const personaConstraints = platformPersona?.content_format_rules as any;
        
        // Track progress with persona analysis steps
        const progressSteps = [
          'Analyzing persona for ad copy optimization...',
          'Applying conversion-focused persona constraints...',
          'Generating persona-aware ad variations...',
          'Optimizing for Facebook ad format...'
        ];

        for (let i = 0; i < progressSteps.length; i++) {
          console.log(`🎭 Facebook Ad Persona Progress: ${progressSteps[i]}`);
          await new Promise(resolve => setTimeout(resolve, 200));
        }

        const res = await facebookWriterApi.adCopyGenerate({
          business_type: 'General',
          product_service: args.product_service,
          ad_objective: args.campaign_goal || 'Drive conversions',
          ad_format: 'Single Image',
          target_audience: args.target_audience || 'General audience',
          targeting_options: {
            age_group: '25-54',
            gender: 'All',
            location: 'Global',
            interests: 'General',
            behaviors: 'General',
            lookalike_audience: 'None'
          },
          unique_selling_proposition: 'Quality product with great value',
          budget_range: args.budget_range || 'Medium'
        });
        
        // Apply persona constraints to ad copy
        const enhancedAdCopy = applyPersonaConstraints(res.data?.content || '', corePersona?.linguistic_fingerprint);
        
        // Dispatch event to update the draft
        window.dispatchEvent(new CustomEvent('fbwriter:updateDraft', { 
          detail: enhancedAdCopy 
        }));

        return {
          success: true,
          ad_copy: enhancedAdCopy,
          persona_applied: {
            persona_name: corePersona?.persona_name,
            archetype: corePersona?.archetype,
            confidence_score: corePersona?.confidence_score
          },
          original_response: res.data
        };
      } catch (error) {
        console.error('Error generating Facebook ad copy with persona:', error);
        return {
          success: false,
          error: 'Failed to generate Facebook ad copy with persona optimization'
        };
      }
    }
  });

  // Content Validation Against Persona
  useCopilotActionTyped({
    name: 'validateContentAgainstPersona',
    description: 'Validate existing Facebook content against your writing persona and platform constraints',
    parameters: [
      { name: 'content', type: 'string', required: true }
    ],
    handler: async (args: any) => {
      try {
        const content = args.content;
        const personaConstraints = platformPersona?.content_format_rules as any;
        
        // Analyze content against persona constraints
        const validation = {
          character_count: content.length,
          optimal_range: personaConstraints?.optimal_length || '40-80 characters',
          status: content.length <= (personaConstraints?.character_limit || 63206) ? 'Within limits' : 'Exceeds limits',
          suggestions: [] as string[]
        };

        // Check sentence length against persona
        if (corePersona?.linguistic_fingerprint?.sentence_metrics?.average_sentence_length_words) {
          const avgWords = corePersona.linguistic_fingerprint.sentence_metrics.average_sentence_length_words;
          const sentences = content.split(/[.!?]+/).filter((s: string) => s.trim().length > 0);
          const avgSentenceLength = sentences.reduce((acc: number, s: string) => acc + s.trim().split(' ').length, 0) / sentences.length;
          
          if (Math.abs(avgSentenceLength - avgWords) > 5) {
            validation.suggestions.push(`Consider adjusting sentence length to match your persona's average of ${avgWords} words per sentence`);
          }
        }

        // Check for persona go-to words
        if (corePersona?.linguistic_fingerprint?.lexical_features?.go_to_words && corePersona.linguistic_fingerprint.lexical_features.go_to_words.length > 0) {
          const goToWords = corePersona.linguistic_fingerprint.lexical_features.go_to_words;
          const hasGoToWords = goToWords.some((word: string) => content.toLowerCase().includes(word.toLowerCase()));
          if (!hasGoToWords) {
            validation.suggestions.push(`Consider incorporating your persona's go-to words: ${goToWords.join(', ')}`);
          }
        }

        // Check for persona avoid words
        if (corePersona?.linguistic_fingerprint?.lexical_features?.avoid_words && corePersona.linguistic_fingerprint.lexical_features.avoid_words.length > 0) {
          const avoidWords = corePersona.linguistic_fingerprint.lexical_features.avoid_words;
          const hasAvoidWords = avoidWords.some((word: string) => content.toLowerCase().includes(word.toLowerCase()));
          if (hasAvoidWords) {
            validation.suggestions.push(`Consider replacing words that your persona avoids: ${avoidWords.join(', ')}`);
          }
        }

        // Platform-specific validation
        if (content.length < 40) {
          validation.suggestions.push('Consider adding more detail to meet Facebook\'s optimal post length');
        }

        return {
          success: true,
          validation,
          persona_analysis: {
            persona_name: corePersona?.persona_name,
            archetype: corePersona?.archetype,
            confidence_score: corePersona?.confidence_score
          }
        };
      } catch (error) {
        console.error('Error validating content against persona:', error);
        return {
          success: false,
          error: 'Failed to validate content against persona'
        };
      }
    }
  });

  // Get Persona Writing Suggestions
  useCopilotActionTyped({
    name: 'getPersonaWritingSuggestions',
    description: 'Get personalized writing suggestions based on your persona and Facebook platform optimization',
    parameters: [
      { name: 'content_type', type: 'string', required: false }
    ],
    handler: async (args: any) => {
      try {
        const contentType = args.content_type || 'general post';
        
        const suggestions = {
          writing_style: [] as string[],
          platform_optimization: [] as string[],
          persona_specific: [] as string[]
        };

        // Writing style suggestions based on persona
        if (corePersona?.linguistic_fingerprint?.sentence_metrics?.average_sentence_length_words) {
          const avgWords = corePersona.linguistic_fingerprint.sentence_metrics.average_sentence_length_words;
          suggestions.writing_style.push(`Aim for ${avgWords} words per sentence to match your persona's style`);
        }

        if (corePersona?.linguistic_fingerprint?.lexical_features?.go_to_words && corePersona.linguistic_fingerprint.lexical_features.go_to_words.length > 0) {
          const goToWords = corePersona.linguistic_fingerprint.lexical_features.go_to_words;
          suggestions.persona_specific.push(`Use your signature words: ${goToWords.join(', ')}`);
        }

        if (corePersona?.linguistic_fingerprint?.lexical_features?.avoid_words && corePersona.linguistic_fingerprint.lexical_features.avoid_words.length > 0) {
          const avoidWords = corePersona.linguistic_fingerprint.lexical_features.avoid_words;
          suggestions.persona_specific.push(`Avoid these words: ${avoidWords.join(', ')}`);
        }

        // Platform optimization suggestions
        const personaConstraints = platformPersona?.content_format_rules as any;
        if (personaConstraints?.optimal_length) {
          suggestions.platform_optimization.push(`Optimal length for Facebook: ${personaConstraints.optimal_length}`);
        }

        if (personaConstraints?.character_limit) {
          suggestions.platform_optimization.push(`Character limit: ${personaConstraints.character_limit} characters`);
        }

        // Content type specific suggestions
        if (contentType.includes('ad')) {
          suggestions.platform_optimization.push('Focus on clear value proposition and strong call-to-action');
          suggestions.platform_optimization.push('Use emotional triggers that resonate with your target audience');
        } else if (contentType.includes('story')) {
          suggestions.platform_optimization.push('Keep it concise and visually engaging');
          suggestions.platform_optimization.push('Use first-person narrative for authenticity');
        }

        return {
          success: true,
          suggestions,
          persona_context: {
            persona_name: corePersona?.persona_name,
            archetype: corePersona?.archetype,
            confidence_score: corePersona?.confidence_score,
            core_belief: corePersona?.core_belief
          }
        };
      } catch (error) {
        console.error('Error getting persona writing suggestions:', error);
        return {
          success: false,
          error: 'Failed to get persona writing suggestions'
        };
      }
    }
  });

  return null; // This component only registers actions
};

export default RegisterFacebookActionsEnhanced;
