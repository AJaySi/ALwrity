import { useState, useEffect, useCallback } from 'react';
import { getApiKeysForOnboarding, getStep1ApiKeysFromProgress, saveApiKey } from '../../../../api/onboarding';
import { getKeyStatus, formatErrorMessage } from '../../common/onboardingUtils';
import { Provider } from './ProviderCard';
import { apiClient } from '../../../../api/client';

export const useApiKeyStep = (onContinue: (stepData?: any) => void) => {
  const [geminiKey, setGeminiKey] = useState('');
  const [exaKey, setExaKey] = useState('');
  const [copilotkitKey, setCopilotkitKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [showExaKey, setShowExaKey] = useState(false);
  const [showCopilotkitKey, setShowCopilotkitKey] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [savedKeys, setSavedKeys] = useState<Record<string, string>>({});
  const [benefitsModalOpen, setBenefitsModalOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null);
  const [keysLoaded, setKeysLoaded] = useState(false);
  const [currentProviderIndex, setCurrentProviderIndex] = useState(0);
  const [showCompletionToast, setShowCompletionToast] = useState(false);

  const loadExistingKeys = useCallback(async () => {
    try {
      console.log('ApiKeyStep: Loading API keys...');
      // 1) Try .env/unmasked endpoint
      const envKeys = await getApiKeysForOnboarding();
      // 2) If missing, fallback to saved progress payload
      const progressKeys = await getStep1ApiKeysFromProgress();

      const merged = {
        gemini: envKeys.gemini ?? progressKeys.gemini ?? '',
        exa: envKeys.exa ?? progressKeys.exa ?? '',
        copilotkit: envKeys.copilotkit ?? progressKeys.copilotkit ?? '',
      } as Record<string, string>;

      setSavedKeys(merged);
      if (merged.gemini) setGeminiKey(merged.gemini);
      if (merged.exa) setExaKey(merged.exa);
      if (merged.copilotkit) setCopilotkitKey(merged.copilotkit);
      setKeysLoaded(true);
      console.log('ApiKeyStep: API keys loaded successfully', merged);
    } catch (error) {
      console.error('ApiKeyStep: Error loading API keys:', error);
      setKeysLoaded(true); // Set to true even on error to prevent infinite retries
    }
  }, []);

  const handleContinue = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    // Validate that all required API keys are provided
    console.log('ApiKeyStep: Validating API keys - Gemini:', !!geminiKey.trim(), 'Exa:', !!exaKey.trim(), 'CopilotKit:', !!copilotkitKey.trim());
    if (!geminiKey.trim() || !exaKey.trim() || !copilotkitKey.trim()) {
      const missingKeys = [];
      if (!geminiKey.trim()) missingKeys.push('Gemini');
      if (!exaKey.trim()) missingKeys.push('Exa');
      if (!copilotkitKey.trim()) missingKeys.push('CopilotKit');
      setError(`Please provide all required API keys. Missing: ${missingKeys.join(', ')}`);
      setLoading(false);
      return;
    }

    // Validate API key formats
    if (!geminiKey.trim().startsWith('AIza')) {
      setError('Gemini API key must start with "AIza"');
      setLoading(false);
      return;
    }

    // Exa API keys are UUIDs (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    const exaUuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!exaUuidRegex.test(exaKey.trim())) {
      setError('Exa API key must be a valid UUID (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)');
      setLoading(false);
      return;
    }

    if (!copilotkitKey.trim().startsWith('ck_pub_')) {
      setError('CopilotKit API key must start with "ck_pub_"');
      setLoading(false);
      return;
    }

    try {
      // First, save all API keys individually
      const promises = [];

      if (geminiKey.trim()) {
        promises.push(saveApiKey('gemini', geminiKey.trim()));
      }

      if (exaKey.trim()) {
        promises.push(saveApiKey('exa', exaKey.trim()));
      }

      if (copilotkitKey.trim()) {
        promises.push(saveApiKey('copilotkit', copilotkitKey.trim()));
        // Store CopilotKit key in localStorage for frontend use
        localStorage.setItem('copilotkit_api_key', copilotkitKey.trim());
        console.log('ApiKeyStep: CopilotKit key saved to localStorage for frontend CopilotKit provider');
        
        // Also save to frontend .env file (for development)
        try {
          await apiClient.post('/api/frontend-env/update', {
            key: 'REACT_APP_COPILOTKIT_API_KEY',
            value: copilotkitKey.trim(),
            description: 'CopilotKit API key for AI assistant functionality'
          });
          console.log('ApiKeyStep: CopilotKit key saved to frontend .env file');
        } catch (envError) {
          console.warn('ApiKeyStep: Failed to save CopilotKit key to frontend .env file:', envError);
          // Don't fail the entire process if .env update fails
        }
      }

      try {
        await Promise.all(promises);
      } catch (saveError: any) {
        console.error('Error saving API keys:', saveError);
        setError('Failed to save API keys. Please try again.');
        setLoading(false);
        return;
      }

      // Trigger CopilotKit reinitialization
      if (copilotkitKey.trim()) {
        window.dispatchEvent(new CustomEvent('copilotkit-key-updated', { 
          detail: { apiKey: copilotkitKey.trim() } 
        }));
      }

      // Then complete the step with the API keys data
      const stepData = {
        api_keys: {
          gemini: geminiKey.trim(),
          exa: exaKey.trim(),
          copilotkit: copilotkitKey.trim()
        }
      };

      // Complete step 1 with the API keys data
      console.log('ApiKeyStep: Attempting to complete step 1 with data:', stepData);
      try {
        const response = await apiClient.post('/api/onboarding/step/1/complete', { data: stepData });
        console.log('ApiKeyStep: Step completion response:', response.data);
      } catch (fetchError: any) {
        console.error('Error completing step:', fetchError);
        let errorMessage = 'Failed to complete step. Please try again.';
        
        if (fetchError.response) {
          // Server responded with an error
          console.log('ApiKeyStep: Error response data:', fetchError.response.data);
          errorMessage = fetchError.response.data?.detail || errorMessage;
        } else if (fetchError.request) {
          // Request made but no response
          errorMessage = 'Network error. Please check your connection and try again.';
        }
        
        console.log('ApiKeyStep: Setting error message:', errorMessage);
        setError(errorMessage);
        setLoading(false);
        return; // Don't continue if step completion fails
      }

      setSuccess('API keys saved successfully!');
      await loadExistingKeys();

      // Auto-continue after a short delay with step data
      setTimeout(() => {
        onContinue(stepData);
      }, 1500);
    } catch (err) {
      setError(formatErrorMessage(err));
      console.error('Error saving API keys:', err);
    } finally {
      setLoading(false);
    }
  };

  const providers: Provider[] = [
    {
      name: 'Google Gemini',
      description: "Google's latest AI model for content creation",
      benefits: ['Multimodal capabilities', 'Real-time information', "Google's latest technology"],
      key: geminiKey,
      setKey: setGeminiKey,
      showKey: showGeminiKey,
      setShowKey: setShowGeminiKey,
      placeholder: 'AIza...',
      status: getKeyStatus(geminiKey, 'gemini'),
      link: 'https://makersuite.google.com/app/apikey',
      free: true,
      recommended: true,
    },
    {
      name: 'Exa AI',
      description: 'Advanced web search and research capabilities',
      benefits: ['Real-time web search', 'Content discovery', 'Research automation'],
      key: exaKey,
      setKey: setExaKey,
      showKey: showExaKey,
      setShowKey: setShowExaKey,
      placeholder: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
      status: getKeyStatus(exaKey, 'exa'),
      link: 'https://dashboard.exa.ai/login',
      free: true,
      recommended: true,
    },
    {
      name: 'CopilotKit',
      description: 'In-app AI assistant for enhanced user experience',
      benefits: ['Interactive AI chat', 'Context-aware assistance', 'Seamless integration'],
      key: copilotkitKey,
      setKey: setCopilotkitKey,
      showKey: showCopilotkitKey,
      setShowKey: setShowCopilotkitKey,
      placeholder: 'ck_pub_...',
      status: getKeyStatus(copilotkitKey, 'copilotkit'),
      link: 'https://copilotkit.ai',
      free: true,
      recommended: true,
    },
  ];

  // All three keys are required
  const isValid = !!(geminiKey.trim() && exaKey.trim() && copilotkitKey.trim());
  
  // Debug logging
  useEffect(() => {
    console.log('useApiKeyStep: Validation check:', {
      gemini: geminiKey.trim(),
      exa: exaKey.trim(),
      copilotkit: copilotkitKey.trim(),
      isValid
    });
  }, [geminiKey, exaKey, copilotkitKey, isValid]);
  
  // When keys change and all are valid, auto-save them
  useEffect(() => {
    if (isValid && (geminiKey || exaKey || copilotkitKey)) {
      console.log('useApiKeyStep: All keys valid, auto-saving...');
      // Save keys immediately when all are provided
      const saveKeys = async () => {
        try {
          const promises = [];
          
          if (geminiKey.trim()) {
            promises.push(saveApiKey('gemini', geminiKey.trim()));
          }
          if (exaKey.trim()) {
            promises.push(saveApiKey('exa', exaKey.trim()));
          }
          if (copilotkitKey.trim()) {
            promises.push(saveApiKey('copilotkit', copilotkitKey.trim()));
            // Store CopilotKit key in localStorage for frontend use
            localStorage.setItem('copilotkit_api_key', copilotkitKey.trim());
          }
          
          await Promise.all(promises);
          console.log('useApiKeyStep: All API keys auto-saved successfully (backend handles .env files)');
        } catch (error) {
          console.error('useApiKeyStep: Auto-save failed:', error);
        }
      };
      
      saveKeys();
    }
  }, [geminiKey, exaKey, copilotkitKey, isValid]);

  // Auto-scroll to next provider when current one is valid
  useEffect(() => {
    if (currentProviderIndex < 2) {
      const currentKey = currentProviderIndex === 0 ? geminiKey : 
                       currentProviderIndex === 1 ? exaKey : copilotkitKey;
      
      if (currentKey.trim() && getKeyStatus(currentKey, currentProviderIndex === 0 ? 'gemini' : 
                                          currentProviderIndex === 1 ? 'exa' : 'copilotkit') === 'valid') {
        // Auto-scroll to next provider after a short delay
        setTimeout(() => {
          setCurrentProviderIndex(prev => prev + 1);
        }, 1000);
      }
    }
  }, [geminiKey, exaKey, copilotkitKey, currentProviderIndex]);

  // Show completion toast when all keys are valid
  useEffect(() => {
    if (isValid && keysLoaded) {
      setShowCompletionToast(true);
      // Auto-hide toast after 5 seconds
      setTimeout(() => setShowCompletionToast(false), 5000);
    }
  }, [isValid, keysLoaded]);

  const handleBenefitsClick = (provider: Provider) => {
    setSelectedProvider(provider);
    setBenefitsModalOpen(true);
  };

  const handleCloseBenefitsModal = () => {
    setBenefitsModalOpen(false);
    setSelectedProvider(null);
  };

  useEffect(() => {
    loadExistingKeys();
  }, [loadExistingKeys]);

  return {
    // State
    geminiKey,
    exaKey,
    copilotkitKey,
    loading,
    error,
    success,
    showGeminiKey,
    showExaKey,
    showCopilotkitKey,
    showHelp,
    savedKeys,
    benefitsModalOpen,
    selectedProvider,
    keysLoaded,
    providers,
    isValid,
    currentProviderIndex,
    setCurrentProviderIndex,
    showCompletionToast,
    setShowCompletionToast,

    // Actions
    setShowHelp,
    handleContinue,
    handleBenefitsClick,
    handleCloseBenefitsModal,
    loadExistingKeys,
  };
};
