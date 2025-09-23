import { useCallback } from 'react';

/**
 * Hook to trigger copilot actions from UI components
 */
export const useCopilotTrigger = () => {
  const triggerResearch = useCallback((topic?: string) => {
    // This function can be used to programmatically trigger copilot actions
    // For now, it's a placeholder that can be extended to interact with the copilot
    console.log('Triggering research for topic:', topic);
    
    // In a real implementation, this could:
    // 1. Send a message to the copilot
    // 2. Trigger a specific copilot action
    // 3. Open the copilot sidebar with a pre-filled message
    
    // For now, we'll just log the action
    // The user can still interact with the copilot manually
  }, []);

  const triggerOutlineGeneration = useCallback(() => {
    console.log('Triggering outline generation');
    // Similar to triggerResearch, this could interact with the copilot
  }, []);

  return {
    triggerResearch,
    triggerOutlineGeneration
  };
};
