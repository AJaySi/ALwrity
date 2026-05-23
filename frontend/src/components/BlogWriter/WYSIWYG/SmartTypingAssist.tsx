import React, { useState, useRef, useEffect } from 'react';
import { debug } from '../../../utils/debug';
import { assistiveWritingApi } from '../../../services/blogWriterApi';

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
  const [showContinueWritingPrompt, setShowContinueWritingPrompt] = useState(false);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastGeneratedAtRef = useRef<number>(0);
  const hasShownFirstRef = useRef(false);
  const isGeneratingRef = useRef(false);
  const smartSuggestionRef = useRef<typeof smartSuggestion>(null);
  const initialContentLengthRef = useRef<number | null>(null);
  const mountedRef = useRef(true);
  
  // Quality improvement tracking
  const [suggestionStats, setSuggestionStats] = useState({
    totalShown: 0,
    totalAccepted: 0,
    totalRejected: 0,
    totalCycled: 0
  });

  // Smart typing assist functionality
  const generateSmartSuggestion = async (currentText: string, cursorPosition?: number) => {
    debug.log('[SmartTypingAssist] generateSmartSuggestion called', { textLength: currentText.length, cursorPosition });
    
    if (currentText.length < 20) {
      debug.log('[SmartTypingAssist] Text too short for suggestion');
      return; // Only suggest after some meaningful content
    }
    
    debug.log('[SmartTypingAssist] Starting suggestion generation...');
    setIsGeneratingSuggestion(true);
    isGeneratingRef.current = true;

    try {
      if (!mountedRef.current) return;
      
      debug.log('[SmartTypingAssist] Calling assistive writing API...');
      const response = await assistiveWritingApi.getSuggestion(currentText, cursorPosition);
      
      if (!mountedRef.current) return;
      
      if (!response.success || !response.suggestions.length) {
        debug.log('[SmartTypingAssist] No suggestions from API', { message: response.message });
        return;
      }

      debug.log('[SmartTypingAssist] Received suggestions from API', { count: response.suggestions.length });
      
      // Store all suggestions
      setAllSuggestions(response.suggestions);
      setSuggestionIndex(0);
      
      // Show first suggestion
      const firstSuggestion = response.suggestions[0];
      debug.log('[SmartTypingAssist] Showing first suggestion', { preview: firstSuggestion.text.substring(0, 50) + '...' });
      
      // Track suggestion shown
      setSuggestionStats(prev => ({
        ...prev,
        totalShown: prev.totalShown + 1
      }));
      
      // Get viewport-safe position for suggestion placement
      if (contentRef.current) {
        const element = contentRef.current;
        const rect = element.getBoundingClientRect();
        const maxWidth = 420;
        const maxHeight = 350;
        
        let x = Math.max(20, Math.min(rect.left + 20, window.innerWidth - (maxWidth + 20)));
        let y = rect.bottom + 10;
        
        if (y + maxHeight > window.innerHeight - 20) {
          y = rect.top - maxHeight - 10;
          if (y < 20) {
            y = Math.max(20, (window.innerHeight - maxHeight) / 2);
            x = Math.max(20, (window.innerWidth - maxWidth) / 2);
          }
        }
        
        y = Math.max(20, Math.min(y, window.innerHeight - maxHeight - 20));
        x = Math.max(20, Math.min(x, window.innerWidth - maxWidth - 20));
        
        setSmartSuggestion({
          text: firstSuggestion.text,
          position: { x, y },
          confidence: firstSuggestion.confidence,
          sources: firstSuggestion.sources
        });
      }
    } catch (error) {
      debug.error('[SmartTypingAssist] Failed to generate smart suggestion', error);
    } finally {
      setIsGeneratingSuggestion(false);
      isGeneratingRef.current = false;
    }
  };

  const handleTypingChange = (newText: string, cursorPosition?: number) => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Track initial content baseline on first user keystroke
    // This prevents triggering suggestions on pre-filled content
    if (initialContentLengthRef.current === null) {
      initialContentLengthRef.current = newText.length;
      debug.log('[SmartTypingAssist] Set initial content baseline', { length: newText.length });
    }

    // Store cursor position for use after debounce
    const cursorPos = cursorPosition;

    typingTimeoutRef.current = setTimeout(() => {
      const cooldownMs = 15000;
      const now = Date.now();
      const sinceLast = now - lastGeneratedAtRef.current;
      const baseline = initialContentLengthRef.current ?? 0;
      const userAddedChars = newText.length - baseline;

      if (!hasShownFirstRef.current && newText.length >= 50 && userAddedChars >= 30 && !isGeneratingRef.current) {
        debug.log('[SmartTypingAssist] Generating first suggestion');
        generateSmartSuggestion(newText, cursorPos);
        setHasShownFirstSuggestion(true);
        lastGeneratedAtRef.current = now;
      } else if (hasShownFirstRef.current && newText.length > 100 && userAddedChars >= 30 && sinceLast >= cooldownMs && !isGeneratingRef.current && !smartSuggestionRef.current) {
        debug.log('[SmartTypingAssist] Showing "Continue writing" prompt');
        setShowContinueWritingPrompt(true);
      }
    }, 3000);
  };

  const handleAcceptSuggestion = () => {
    if (smartSuggestion && onTextReplace && contentRef.current) {
      const element = contentRef.current as HTMLTextAreaElement;
      const currentContent = element.value || '';
      
      // Get cursor position
      const cursorPosition = element.selectionStart || currentContent.length;
      debug.log('[SmartTypingAssist] Cursor position', { cursorPosition, contentLength: currentContent.length });
      
      // Insert suggestion at cursor position
      const beforeCursor = currentContent.substring(0, cursorPosition);
      const afterCursor = currentContent.substring(cursorPosition);
      const suggestionWithSpace = ' ' + smartSuggestion.text + ' ';
      const newContent = beforeCursor + suggestionWithSpace + afterCursor;
      
      // Calculate where cursor should be after insertion (right after the suggestion)
      const newCursorPosition = cursorPosition + suggestionWithSpace.length;
      
      // Track suggestion accepted
      setSuggestionStats(prev => ({
        ...prev,
        totalAccepted: prev.totalAccepted + 1
      }));
      
      debug.log('[SmartTypingAssist] Suggestion accepted', { cursorPosition, newContentLength: newContent.length, newCursorPosition });
      
      // Use the text replacement callback
      onTextReplace(currentContent, newContent, 'smart-suggestion');
      
      // Set cursor position after the inserted text
      setTimeout(() => {
        if (contentRef.current) {
          const el = contentRef.current as HTMLTextAreaElement;
          el.focus();
          el.setSelectionRange(newCursorPosition, newCursorPosition);
          debug.log('[SmartTypingAssist] Cursor positioned', { position: newCursorPosition });
        }
      }, 50);
      
      setSmartSuggestion(null);
    }
  };

  const handleRejectSuggestion = () => {
    // Track suggestion rejected
    setSuggestionStats(prev => ({
      ...prev,
      totalRejected: prev.totalRejected + 1
    }));
    
    debug.log('[SmartTypingAssist] Suggestion rejected', { stats: { ...suggestionStats, totalRejected: suggestionStats.totalRejected + 1 } });
    
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
      
      debug.log('[SmartTypingAssist] Showing next suggestion', { index: nextIndex + 1, total: allSuggestions.length });
      debug.log('[SmartTypingAssist] Suggestion cycled', { stats: { ...suggestionStats, totalCycled: suggestionStats.totalCycled + 1 } });
      
      setSuggestionIndex(nextIndex);
      setSmartSuggestion(prev => prev ? {
        ...prev,
        text: nextSuggestion.text,
        confidence: nextSuggestion.confidence,
        sources: nextSuggestion.sources
      } : null);
    }
  };

  // Handle "Continue writing" button click
  const handleRequestSuggestion = async () => {
    if (!contentRef.current) return;
    
    const element = contentRef.current as HTMLTextAreaElement;
    const currentContent = element.value || '';
    const cursorPos = element.selectionStart;
    
    setShowContinueWritingPrompt(false);
    
    const baseline = initialContentLengthRef.current ?? 0;
    const userAddedChars = currentContent.length - baseline;
    if (currentContent.length > 20 && userAddedChars >= 10) {
      await generateSmartSuggestion(currentContent, cursorPos);
    }
  };

  // Handle dismissing the "Continue writing" prompt
  const handleDismissPrompt = () => {
    setShowContinueWritingPrompt(false);
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

  // Sync refs with state so timeout callbacks always read latest values
  useEffect(() => { hasShownFirstRef.current = hasShownFirstSuggestion; }, [hasShownFirstSuggestion]);
  useEffect(() => { isGeneratingRef.current = isGeneratingSuggestion; }, [isGeneratingSuggestion]);
  useEffect(() => { smartSuggestionRef.current = smartSuggestion; }, [smartSuggestion]);

  // Mount guard and cleanup
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
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
    showContinueWritingPrompt,
    handleTypingChange,
    handleAcceptSuggestion,
    handleRejectSuggestion,
    handleNextSuggestion,
    handleRequestSuggestion,
    handleDismissPrompt,
    getSuggestionStats,
    generateSmartSuggestion
  };
};

export default useSmartTypingAssist;
export type { SmartTypingAssistProps, Suggestion };
