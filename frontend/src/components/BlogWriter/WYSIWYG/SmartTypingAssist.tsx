import React, { useState, useRef, useEffect } from 'react';

interface SmartTypingAssistProps {
  contentRef: React.RefObject<HTMLDivElement | HTMLTextAreaElement>;
  onTextReplace?: (originalText: string, newText: string, editType: string) => void;
}

interface Suggestion {
  text: string;
  confidence?: number;
  sources?: Array<{
    title: string;
    url: string;
    text?: string;
    author?: string;
    published_date?: string;
    score: number;
  }>;
}

const useSmartTypingAssist = (
  contentRef: React.RefObject<HTMLDivElement | HTMLTextAreaElement>,
  onTextReplace?: (originalText: string, newText: string, editType: string) => void
) => {
  // Smart typing assist states
  const [smartSuggestion, setSmartSuggestion] = useState<{
    text: string;
    position: { x: number; y: number };
    confidence?: number;
    sources?: Array<{
      title: string;
      url: string;
      text?: string;
      author?: string;
      published_date?: string;
      score: number;
    }>;
  } | null>(null);
  const [suggestionIndex, setSuggestionIndex] = useState(0);
  const [allSuggestions, setAllSuggestions] = useState<Suggestion[]>([]);
  const [isGeneratingSuggestion, setIsGeneratingSuggestion] = useState(false);
  const [hasShownFirstSuggestion, setHasShownFirstSuggestion] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Quality improvement tracking
  const [suggestionStats, setSuggestionStats] = useState({
    totalShown: 0,
    totalAccepted: 0,
    totalRejected: 0,
    totalCycled: 0
  });

  // Smart typing assist functionality
  const generateSmartSuggestion = async (currentText: string) => {
    console.log('🔍 [SmartTypingAssist] generateSmartSuggestion called with text length:', currentText.length);
    
    if (currentText.length < 20) {
      console.log('🔍 [SmartTypingAssist] Text too short for suggestion');
      return; // Only suggest after some meaningful content
    }
    
    console.log('🔍 [SmartTypingAssist] Starting suggestion generation...');
    setIsGeneratingSuggestion(true);
    
    try {
      // Import the assistive writing API
      const { assistiveWritingApi } = await import('../../../services/blogWriterApi');
      
      console.log('🔍 [SmartTypingAssist] Calling assistive writing API...');
      const response = await assistiveWritingApi.getSuggestion(currentText, 3); // Get 3 suggestions
      
      if (response.success && response.suggestions.length > 0) {
        console.log('🔍 [SmartTypingAssist] Received', response.suggestions.length, 'suggestions from API');
        
        // Store all suggestions
        setAllSuggestions(response.suggestions);
        setSuggestionIndex(0);
        
        // Show first suggestion
        const firstSuggestion = response.suggestions[0];
        console.log('🔍 [SmartTypingAssist] Showing first suggestion:', firstSuggestion.text.substring(0, 50) + '...');
        
        // Track suggestion shown
        setSuggestionStats(prev => ({
          ...prev,
          totalShown: prev.totalShown + 1
        }));
        
        // Get cursor position for suggestion placement
        if (contentRef.current) {
          const element = contentRef.current;
          const rect = element.getBoundingClientRect();
          const x = Math.max(20, Math.min(rect.left + 20, window.innerWidth - 420)); // Ensure it stays on screen
          const y = Math.max(20, rect.bottom + 10);
          
          setSmartSuggestion({
            text: firstSuggestion.text,
            position: { x, y },
            confidence: firstSuggestion.confidence,
            sources: firstSuggestion.sources
          });
        }
      } else {
        console.log('🔍 [SmartTypingAssist] No suggestions received from API');
        // Fallback to generic suggestions if API fails
        const fallbackSuggestions = [
          "This approach provides significant value to readers by offering actionable insights they can implement immediately.",
          "Research indicates that this strategy has proven effective across multiple industries and use cases.",
          "Furthermore, this method demonstrates measurable improvements in key performance indicators.",
          "Additionally, industry experts recommend this technique for sustainable long-term growth.",
          "Moreover, this framework addresses common challenges while providing practical solutions."
        ];
        
        const randomSuggestion = fallbackSuggestions[Math.floor(Math.random() * fallbackSuggestions.length)];
        
        if (contentRef.current) {
          const element = contentRef.current;
          const rect = element.getBoundingClientRect();
          const x = rect.left + 20;
          const y = rect.bottom + 5;
          
          setSmartSuggestion({
            text: randomSuggestion,
            position: { x, y }
          });
        }
      }
    } catch (error) {
      console.error('🔍 [SmartTypingAssist] Failed to generate smart suggestion:', error);
      
      // Fallback to generic suggestions on error
      const fallbackSuggestions = [
        "This approach provides significant value to readers by offering actionable insights they can implement immediately.",
        "Research indicates that this strategy has proven effective across multiple industries and use cases.",
        "Furthermore, this method demonstrates measurable improvements in key performance indicators.",
        "Additionally, industry experts recommend this technique for sustainable long-term growth.",
        "Moreover, this framework addresses common challenges while providing practical solutions."
      ];
      
      const randomSuggestion = fallbackSuggestions[Math.floor(Math.random() * fallbackSuggestions.length)];
      
      if (contentRef.current) {
        const element = contentRef.current;
        const rect = element.getBoundingClientRect();
        const x = rect.left + 20;
        const y = rect.bottom + 5;
        
        setSmartSuggestion({
          text: randomSuggestion,
          position: { x, y }
        });
      }
    } finally {
      setIsGeneratingSuggestion(false);
    }
  };

  const handleTypingChange = (newText: string) => {
    console.log('🔍 [SmartTypingAssist] handleTypingChange called with text length:', newText.length);
    
    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // Clear any existing suggestion when user types
    setSmartSuggestion(null);
    
    // Set new timeout for suggestion generation
    typingTimeoutRef.current = setTimeout(() => {
      console.log('🔍 [SmartTypingAssist] Typing timeout triggered, text length:', newText.length, 'hasShownFirstSuggestion:', hasShownFirstSuggestion);
      
      // First time suggestion appears automatically
      if (!hasShownFirstSuggestion && newText.length > 20) {
        console.log('🔍 [SmartTypingAssist] Generating first suggestion');
        generateSmartSuggestion(newText);
        setHasShownFirstSuggestion(true);
      } 
      // After first time, only suggest after longer pauses or more content
      else if (hasShownFirstSuggestion && newText.length > 50 && Math.random() > 0.7) {
        console.log('🔍 [SmartTypingAssist] Generating subsequent suggestion');
        generateSmartSuggestion(newText);
      } else {
        console.log('🔍 [SmartTypingAssist] No suggestion generated - conditions not met');
      }
    }, 3000); // 3 second pause before suggesting
  };

  const handleAcceptSuggestion = () => {
    if (smartSuggestion && onTextReplace && contentRef.current) {
      const element = contentRef.current;
      const currentContent = (element as HTMLTextAreaElement).value || (element as HTMLDivElement).textContent || '';
      const newContent = currentContent + ' ' + smartSuggestion.text;
      
      // Track suggestion accepted
      setSuggestionStats(prev => ({
        ...prev,
        totalAccepted: prev.totalAccepted + 1
      }));
      
      console.log('🔍 [SmartTypingAssist] Suggestion accepted! Stats:', {
        ...suggestionStats,
        totalAccepted: suggestionStats.totalAccepted + 1
      });
      
      // Use the text replacement callback
      onTextReplace(currentContent, newContent, 'smart-suggestion');
      
      setSmartSuggestion(null);
    }
  };

  const handleRejectSuggestion = () => {
    // Track suggestion rejected
    setSuggestionStats(prev => ({
      ...prev,
      totalRejected: prev.totalRejected + 1
    }));
    
    console.log('🔍 [SmartTypingAssist] Suggestion rejected! Stats:', {
      ...suggestionStats,
      totalRejected: suggestionStats.totalRejected + 1
    });
    
    setSmartSuggestion(null);
    setAllSuggestions([]);
    setSuggestionIndex(0);
  };

  const handleNextSuggestion = () => {
    if (allSuggestions.length > 0 && suggestionIndex < allSuggestions.length - 1) {
      const nextIndex = suggestionIndex + 1;
      const nextSuggestion = allSuggestions[nextIndex];
      
      // Track suggestion cycled
      setSuggestionStats(prev => ({
        ...prev,
        totalCycled: prev.totalCycled + 1
      }));
      
      console.log('🔍 [SmartTypingAssist] Showing next suggestion:', nextIndex + 1, 'of', allSuggestions.length);
      console.log('🔍 [SmartTypingAssist] Suggestion cycled! Stats:', {
        ...suggestionStats,
        totalCycled: suggestionStats.totalCycled + 1
      });
      
      setSuggestionIndex(nextIndex);
      setSmartSuggestion(prev => prev ? {
        ...prev,
        text: nextSuggestion.text,
        confidence: nextSuggestion.confidence,
        sources: nextSuggestion.sources
      } : null);
    }
  };

  // Get suggestion statistics for quality improvement
  const getSuggestionStats = () => {
    const acceptanceRate = suggestionStats.totalShown > 0 
      ? Math.round((suggestionStats.totalAccepted / suggestionStats.totalShown) * 100) 
      : 0;
    
    return {
      ...suggestionStats,
      acceptanceRate,
      engagementRate: suggestionStats.totalShown > 0 
        ? Math.round(((suggestionStats.totalAccepted + suggestionStats.totalCycled) / suggestionStats.totalShown) * 100)
        : 0
    };
  };

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return {
    smartSuggestion,
    isGeneratingSuggestion,
    allSuggestions,
    suggestionIndex,
    suggestionStats: getSuggestionStats(),
    handleTypingChange,
    handleAcceptSuggestion,
    handleRejectSuggestion,
    handleNextSuggestion,
    getSuggestionStats,
    generateSmartSuggestion
  };
};

export default useSmartTypingAssist;
export type { SmartTypingAssistProps, Suggestion };
