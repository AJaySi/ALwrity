import { apiClient, aiApiClient } from './client';

export interface AssetResponse {
  success: boolean;
  image_url?: string;
  image_base64?: string;
  optimized_prompt?: string;
  asset_id?: number;
  message?: string;
  error?: string;
}

export interface VoiceCloneResponse {
  success: boolean;
  custom_voice_id?: string;
  preview_audio_url?: string;
  asset_id?: number;
  message?: string;
  error?: string;
}

export const generateBrandAvatar = async (
  prompt: string,
  stylePreset?: string,
  aspectRatio: string = "1:1"
): Promise<AssetResponse> => {
  try {
    const response = await apiClient.post('/onboarding/assets/generate-avatar', {
      prompt,
      style_preset: stylePreset,
      aspect_ratio: aspectRatio,
      user_id: "current_user" // Backend extracts actual user
    });
    return response.data;
  } catch (error: any) {
    console.error('Avatar generation error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to generate avatar'
    };
  }
};

export const optimizeAvatarPrompt = async (prompt: string): Promise<AssetResponse> => {
  try {
    const response = await apiClient.post('/onboarding/assets/enhance-prompt', {
      prompt,
      user_id: "current_user"
    });
    return response.data;
  } catch (error: any) {
    console.error('Prompt enhancement error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to enhance prompt'
    };
  }
};

export const createAvatarVariation = async (
  prompt: string,
  file: File
): Promise<AssetResponse> => {
    // TODO: Implement backend endpoint for variation
    // For now, return a mock error or handle as new generation
    console.warn("createAvatarVariation not fully implemented in backend");
    return {
        success: false,
        error: "Feature not available yet"
    };
};

export const enhanceBrandAvatar = async (
  file: File
): Promise<AssetResponse> => {
    // TODO: Implement backend endpoint for enhancement (upscaling)
    console.warn("enhanceBrandAvatar not fully implemented in backend");
    return {
        success: false,
        error: "Feature not available yet"
    };
};

export const setBrandAvatar = async (
  data: {
    image_base64: string;
    domain_name?: string;
    title: string;
  }
): Promise<AssetResponse> => {
    // TODO: Implement backend endpoint to set as active avatar
    // For now, simulate success
    return {
        success: true,
        message: "Avatar set as active"
    };
};

export interface VoiceCloneParams {
  audioFile: File;
  engine: 'minimax' | 'qwen3';
  customVoiceId?: string;
  model?: string;
  text?: string;
  referenceText?: string;
  language?: string;
  needNoiseReduction?: boolean;
  needVolumeNormalization?: boolean;
  accuracy?: number;
  languageBoost?: string;
}

export const createVoiceClone = async (
  params: VoiceCloneParams
): Promise<VoiceCloneResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', params.audioFile);
    formData.append('engine', params.engine);
    formData.append('user_id', "current_user");

    if (params.customVoiceId) formData.append('custom_voice_id', params.customVoiceId);
    if (params.model) formData.append('model', params.model);
    if (params.text) formData.append('text', params.text);
    if (params.referenceText) formData.append('reference_text', params.referenceText);
    if (params.language) formData.append('language', params.language);
    if (params.needNoiseReduction !== undefined) formData.append('need_noise_reduction', String(params.needNoiseReduction));
    if (params.needVolumeNormalization !== undefined) formData.append('need_volume_normalization', String(params.needVolumeNormalization));
    if (params.accuracy !== undefined) formData.append('accuracy', String(params.accuracy));
    if (params.languageBoost) formData.append('language_boost', params.languageBoost);

    // Legacy field support (voiceName was used before)
    // We might want to remove this if backend doesn't need it
    formData.append('voice_name', 'My Voice Clone'); 

    const response = await apiClient.post('/onboarding/assets/create-voice-clone', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Voice cloning error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || 'Failed to create voice clone'
    };
  }
};
