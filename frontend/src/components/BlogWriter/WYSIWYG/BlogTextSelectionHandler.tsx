import React, { useState, useRef, useEffect } from 'react';
import { hallucinationDetectorService, HallucinationDetectionResponse } from '../../../services/hallucinationDetectorService';
import TextSelectionMenu from './TextSelectionMenu';
import useSmartTypingAssist from './SmartTypingAssist';

interface BlogTextSelectionHandlerProps {
  contentRef: React.RefObject<HTMLDivElement | HTMLTextAreaElement>;
  onTextReplace?: (originalText: string, newText: string, editType: string) => void;
}

const useBlogTextSelectionHandler = (
  contentRef: React.RefObject<HTMLDivElement | HTMLTextAreaElement>,
  onTextReplace?: (originalText: string, newText: string, editType: string) => void
) => {
  const [selectionMenu, setSelectionMenu] = useState<{ x: number; y: number; text: string } | null>(null);
  const [factCheckResults, setFactCheckResults] = useState<HallucinationDetectionResponse | null>(null);
  const [isFactChecking, setIsFactChecking] = useState(false);
  const [factCheckProgress, setFactCheckProgress] = useState<{ step: string; progress: number } | null>(null);
  const selectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Use the extracted smart typing assist hook
  const smartTypingAssist = useSmartTypingAssist(contentRef, onTextReplace);

  // Fact-checking functionality
  const handleCheckFacts = async (text: string) => {
    console.log('🔍 [BlogTextSelectionHandler] handleCheckFacts called with text:', text);
    if (!text.trim()) {
      console.log('🔍 [BlogTextSelectionHandler] No text to check, returning');
      return;
    }
    
    console.log('🔍 [BlogTextSelectionHandler] Starting fact check for:', text.trim());
    setIsFactChecking(true);
    setSelectionMenu(null);
    
    // Progress tracking
    const progressSteps = [
      { step: "Extracting verifiable claims...", progress: 20 },
      { step: "Searching for evidence...", progress: 40 },
      { step: "Analyzing claims against sources...", progress: 70 },
      { step: "Generating final assessment...", progress: 90 },
      { step: "Completing fact-check...", progress: 100 }
    ];
    
    let currentStepIndex = 0;
    
    // Start progress updates
    const progressInterval = setInterval(() => {
      if (currentStepIndex < progressSteps.length) {
        setFactCheckProgress(progressSteps[currentStepIndex]);
        currentStepIndex++;
      }
    }, 2000); // Update every 2 seconds
    
    // Set a timeout for the fact check (30 seconds)
    const timeoutId = setTimeout(() => {
      console.log('🔍 [BlogTextSelectionHandler] Fact check timeout reached');
      clearInterval(progressInterval);
      setFactCheckProgress(null);
      setIsFactChecking(false);
      setFactCheckResults({
        success: false,
        claims: [],
        overall_confidence: 0,
        total_claims: 0,
        supported_claims: 0,
        refuted_claims: 0,
        insufficient_claims: 0,
        timestamp: new Date().toISOString(),
        error: 'Fact check timed out after 30 seconds. Please try again with shorter text.'
      });
    }, 30000); // 30 second timeout
    
    try {
      console.log('🔍 [BlogTextSelectionHandler] Calling hallucinationDetectorService.detectHallucinations...');
      const results = await hallucinationDetectorService.detectHallucinations({
        text: text.trim(),
        include_sources: true,
        max_claims: 10
      });
      
      console.log('🔍 [BlogTextSelectionHandler] Fact check results received:', results);
      setFactCheckResults(results);
    } catch (error) {
      console.error('🔍 [BlogTextSelectionHandler] Error checking facts:', error);
      setFactCheckResults({
        success: false,
        claims: [],
        overall_confidence: 0,
        total_claims: 0,
        supported_claims: 0,
        refuted_claims: 0,
        insufficient_claims: 0,
        timestamp: new Date().toISOString(),
        error: `Failed to check facts: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      console.log('🔍 [BlogTextSelectionHandler] Fact check completed, setting isFactChecking to false');
      clearInterval(progressInterval);
      clearTimeout(timeoutId);
      setFactCheckProgress(null);
      setIsFactChecking(false);
    }
  };

  const handleCloseFactCheckResults = () => {
    setFactCheckResults(null);
  };

  // Blog-specific quick edit functionality for selected text
  const handleQuickEdit = (editType: string, selectedText: string) => {
    console.log('🔍 [BlogTextSelectionHandler] handleQuickEdit called:', editType, selectedText);
    
    let editedText = selectedText;
    
    switch (editType) {
      case 'improve':
        // Enhance readability and engagement
        editedText = selectedText.replace(/\./g, '. ').replace(/\s+/g, ' ').trim();
        if (!editedText.endsWith('.') && !editedText.endsWith('!') && !editedText.endsWith('?')) {
          editedText += '.';
        }
        break;
      case 'add-transition':
        // Add transitional phrases
        const transitions = ['Furthermore,', 'Additionally,', 'Moreover,', 'In essence,', 'As a result,'];
        const randomTransition = transitions[Math.floor(Math.random() * transitions.length)];
        editedText = `${randomTransition} ${selectedText.toLowerCase()}`;
        break;
      case 'shorten':
        // Condense while maintaining meaning
        editedText = selectedText
          .replace(/\b(very|really|extremely|quite|rather|fairly)\s+/gi, '')
          .replace(/\b(that|which) (is|are|was|were)\s+/gi, '')
          .replace(/\bin order to\b/gi, 'to')
          .replace(/\bdue to the fact that\b/gi, 'because')
          .trim();
        break;
      case 'expand':
        // Add explanatory content
        editedText = selectedText + ' This approach provides significant value by offering concrete benefits and actionable insights that readers can immediately implement.';
        break;
      case 'professionalize':
        // Make more formal and professional
        editedText = selectedText
          .replace(/\bcan't\b/gi, 'cannot')
          .replace(/\bwon't\b/gi, 'will not')
          .replace(/\bdon't\b/gi, 'do not')
          .replace(/\bisn't\b/gi, 'is not')
          .replace(/\baren't\b/gi, 'are not')
          .replace(/\bI think\b/gi, 'It is evident that')
          .replace(/\bI believe\b/gi, 'Research indicates that');
        break;
      case 'add-data':
        // Add statistical backing
        editedText = selectedText + ' According to recent industry studies, this approach has shown measurable improvements in key performance metrics.';
        break;
      default:
        return;
    }
    
    // Call the callback with the edited text
    if (onTextReplace) {
      onTextReplace(selectedText, editedText, editType);
    }
    
    // Also dispatch custom event for broader compatibility
    window.dispatchEvent(new CustomEvent('blogwriter:replaceSelectedText', { 
      detail: { 
        originalText: selectedText,
        editedText: editedText,
        editType: editType
      } 
    }));
    
    // Close the selection menu
    setSelectionMenu(null);
  };


  // Cleanup progress and timeouts on unmount
  useEffect(() => {
    return () => {
      setFactCheckProgress(null);
      if (selectionTimeoutRef.current) {
        clearTimeout(selectionTimeoutRef.current);
      }
    };
  }, []);

  // Text selection handler with debouncing
  const handleTextSelection = () => {
    console.log('🔍 [BlogTextSelectionHandler] handleTextSelection called');
    
    // Clear any existing timeout
    if (selectionTimeoutRef.current) {
      clearTimeout(selectionTimeoutRef.current);
    }
    
    // Debounce the selection handling
    selectionTimeoutRef.current = setTimeout(() => {
      try {
        const sel = window.getSelection();
        console.log('🔍 [BlogTextSelectionHandler] Selection object (debounced):', sel);
        
        if (!sel || sel.rangeCount === 0) { 
          console.log('🔍 [BlogTextSelectionHandler] No selection or range count is 0');
          setSelectionMenu(null); 
          return; 
        }
        
        const text = (sel.toString() || '').trim();
        console.log('🔍 [BlogTextSelectionHandler] Selected text (debounced):', text, 'Length:', text.length);
        
        if (!text || text.length < 10) { 
          console.log('🔍 [BlogTextSelectionHandler] Text too short or empty, hiding menu');
          setSelectionMenu(null); 
          return; 
        }
        
        const range = sel.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        console.log('🔍 [BlogTextSelectionHandler] Range rect:', rect);
        
        // Check if rect has valid dimensions
        if (rect.width === 0 && rect.height === 0) {
          console.log('🔍 [BlogTextSelectionHandler] Invalid rect dimensions, trying alternative positioning');
          
          // Try to get position from the textarea element itself
          if (contentRef.current) {
            const textareaRect = contentRef.current.getBoundingClientRect();
            console.log('🔍 [BlogTextSelectionHandler] Textarea rect:', textareaRect);
            
            // Position menu near the textarea center
            const x = Math.max(8, Math.min(textareaRect.left + (textareaRect.width / 2), window.innerWidth - 280));
            const y = Math.max(8, textareaRect.top + window.scrollY - 60);
            
            const menuPosition = { x, y, text };
            console.log('🔍 [BlogTextSelectionHandler] Using textarea position:', menuPosition);
            setSelectionMenu(menuPosition);
            return;
          }
        }
        
        // Use viewport coordinates for absolute positioning
        const x = Math.max(8, Math.min(rect.left + (rect.width / 2), window.innerWidth - 280)); // Account for menu width
        const y = Math.max(8, rect.top + window.scrollY - 60); // Position above selection
        
        const menuPosition = { x, y, text };
        console.log('🔍 [BlogTextSelectionHandler] Setting selection menu at position (debounced):', menuPosition);
        setSelectionMenu(menuPosition);
        
      } catch (error) {
        console.error('🔍 [BlogTextSelectionHandler] Error handling text selection:', error);
        setSelectionMenu(null);
      }
    }, 150); // 150ms debounce
  };

  return {
    selectionMenu,
    setSelectionMenu,
    factCheckResults,
    isFactChecking,
    factCheckProgress,
    handleTextSelection,
    handleCheckFacts,
    handleCloseFactCheckResults,
    handleQuickEdit,
    // Smart typing assist functionality from extracted hook
    ...smartTypingAssist,
    // Render the selection menu and fact-check components
    renderSelectionMenu: () => (
      <TextSelectionMenu
        selectionMenu={selectionMenu}
        factCheckResults={factCheckResults}
        isFactChecking={isFactChecking}
        factCheckProgress={factCheckProgress}
        smartSuggestion={smartTypingAssist.smartSuggestion}
        isGeneratingSuggestion={smartTypingAssist.isGeneratingSuggestion}
        allSuggestions={smartTypingAssist.allSuggestions}
        suggestionIndex={smartTypingAssist.suggestionIndex}
        onCheckFacts={handleCheckFacts}
        onCloseFactCheckResults={handleCloseFactCheckResults}
        onQuickEdit={handleQuickEdit}
        onAcceptSuggestion={smartTypingAssist.handleAcceptSuggestion}
        onRejectSuggestion={smartTypingAssist.handleRejectSuggestion}
        onNextSuggestion={smartTypingAssist.handleNextSuggestion}
      />
    )
  };
};

export default useBlogTextSelectionHandler;
export type { BlogTextSelectionHandlerProps };
