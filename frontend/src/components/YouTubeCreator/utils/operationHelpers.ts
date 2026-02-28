/**
 * YouTube Creator Operation Helpers
 * 
 * Provides utility functions to build operation objects for OperationButton
 * with YouTube-specific operation types and token estimates.
 * 
 * This module maintains separation of concerns by keeping YouTube-specific
 * logic isolated from the shared OperationButton component.
 */

import { PreflightOperation } from '../../../services/billingService';
import { DurationType, DURATION_TYPES } from '../constants';

/**
 * Validates and normalizes duration type.
 * 
 * @param durationType - Duration type to validate
 * @returns Valid DurationType or 'medium' as fallback
 */
function validateDurationType(durationType?: DurationType | string | null): DurationType {
  if (!durationType) return 'medium';
  if (DURATION_TYPES.includes(durationType as DurationType)) {
    return durationType as DurationType;
  }
  // Log warning in development
  if (process.env.NODE_ENV === 'development') {
    console.warn(`[YouTube Creator] Invalid duration type: ${durationType}, defaulting to 'medium'`);
  }
  return 'medium';
}

/**
 * Validates token count is non-negative.
 * 
 * @param tokens - Token count to validate
 * @returns Validated token count (0 if negative)
 */
function validateTokenCount(tokens: number): number {
  return Math.max(0, Math.round(tokens));
}

/**
 * Estimate token count for YouTube operations based on duration type.
 * 
 * Estimates are based on backend analysis:
 * - Video planning: ~6000-9000 tokens (varies by duration)
 * - Scene building: ~6500-10000 tokens (varies by duration and enhancements)
 * 
 * @param operationType - Type of operation
 * @param durationType - Video duration type (validated and normalized)
 * @returns Estimated token count (non-negative integer)
 */
function estimateYouTubeTokens(
  operationType: 'video_planning' | 'scene_building',
  durationType?: DurationType | string | null
): number {
  const normalizedDuration = validateDurationType(durationType);

  const baseEstimates = {
    video_planning: {
      shorts: 7000,
      medium: 5000,
      long: 8000,
    },
    scene_building: {
      shorts: 0,
      medium: 5000,
      long: 9000,
    },
  };

  const tokens = baseEstimates[operationType][normalizedDuration];
  return validateTokenCount(tokens);
}

/**
 * Maps provider string to backend enum value.
 * 
 * @param provider - Provider name (e.g., 'gemini', 'huggingface')
 * @returns Backend enum value ('gemini' or 'mistral')
 */
function mapProviderToEnum(provider: string): 'gemini' | 'mistral' {
  const normalized = provider.toLowerCase().trim();
  if (normalized === 'huggingface' || normalized === 'mistral') {
    return 'mistral';
  }
  return 'gemini'; // Default to gemini
}

/**
 * Gets actual provider name for display/logging.
 * 
 * @param provider - Provider name
 * @returns Actual provider name string
 */
function getActualProviderName(provider: string): string {
  const normalized = provider.toLowerCase().trim();
  if (normalized === 'huggingface' || normalized === 'mistral') {
    return 'huggingface';
  }
  return 'gemini';
}

/**
 * Build operation object for video planning.
 * 
 * @param durationType - Video duration type (affects token estimate, validated)
 * @param providerOverride - Optional provider override (defaults to 'gemini')
 * @returns PreflightOperation object for OperationButton
 */
export function buildVideoPlanningOperation(
  durationType?: DurationType | string | null,
  providerOverride?: string
): PreflightOperation {
  const provider = providerOverride || 'huggingface';
  const normalizedDuration = validateDurationType(durationType);
  
  return {
    provider: mapProviderToEnum(provider),
    model: 'gemini-2.5-flash',
    operation_type: 'video_planning',
    tokens_requested: estimateYouTubeTokens('video_planning', normalizedDuration),
    actual_provider_name: getActualProviderName(provider),
  };
}

/**
 * Build operation object for scene building.
 * 
 * @param durationType - Video duration type (affects token estimate, validated)
 * @param hasPlan - Whether plan already exists (affects if scenes are included in planning)
 * @param providerOverride - Optional provider override (defaults to 'gemini')
 * @returns PreflightOperation object for OperationButton
 */
export function buildSceneBuildingOperation(
  durationType?: DurationType | string | null,
  hasPlan: boolean = true,
  providerOverride?: string
): PreflightOperation {
  const normalizedDuration = validateDurationType(durationType);
  const provider = providerOverride || 'huggingface';
  
  // For shorts, scenes are included in planning, so no separate operation needed
  if (normalizedDuration === 'shorts' && hasPlan) {
    // Return minimal operation (scenes already generated)
    return {
      provider: mapProviderToEnum(provider),
      model: 'gemini-2.5-flash',
      operation_type: 'scene_building',
      tokens_requested: 0, // Already included in planning
      actual_provider_name: getActualProviderName(provider),
    };
  }

  return {
    provider: mapProviderToEnum(provider),
    model: 'gemini-2.5-flash',
    operation_type: 'scene_building',
    tokens_requested: estimateYouTubeTokens('scene_building', normalizedDuration),
    actual_provider_name: getActualProviderName(provider),
  };
}

/**
 * Build operation object for image editing (Make Presentable).
 * 
 * @returns PreflightOperation object for OperationButton
 */
export function buildImageEditingOperation(): PreflightOperation {
  return {
    provider: 'image_edit',
    model: 'default',
    operation_type: 'image_editing',
    tokens_requested: 0, // Image operations are not token-based
    actual_provider_name: 'image_edit',
  };
}

/**
 * Build operation object for image generation (Avatar/Scene images).
 * 
 * @param providerOverride - Optional provider override (defaults to 'stability')
 * @returns PreflightOperation object for OperationButton
 */
export function buildImageGenerationOperation(
  providerOverride?: string
): PreflightOperation {
  // Default to stability (common image provider)
  // Valid providers: 'stability', 'openai', 'anthropic', etc.
  const provider = (providerOverride || 'stability').toLowerCase().trim();
  
  return {
    provider,
    operation_type: 'image_generation',
    tokens_requested: 0, // Image operations are not token-based
    actual_provider_name: provider,
  };
}


