import React, { useState, useRef, useEffect } from 'react';
import { hallucinationDetectorService, HallucinationDetectionResponse } from '../../../services/hallucinationDetectorService';
import { chartApi, ChartGenerateResponse } from '../../../services/chartApi';
import CompactSelectionMenu from './CompactSelectionMenu';
import ChartGeneratorModal from '../../Chart/ChartGeneratorModal';
import LinkSearchModal from '../../Link/LinkSearchModal';
import useSmartTypingAssist from './SmartTypingAssist';

interface BlogTextSelectionHandlerProps {
  contentRef: React.RefObject<HTMLDivElement | HTMLTextAreaElement>;
  onTextReplace?: (originalText: string, newText: string, editType: string) => void;
  onFormatText?: (type: string, start?: number, end?: number) => void;
}

const useBlogTextSelectionHandler = (
  contentRef: React.RefObject<HTMLDivElement | HTMLTextAreaElement>,
  onTextReplace?: (originalText: string, newText: string, editType: string) => void,
  onFormatText?: (type: string, start?: number, end?: number) => void,
) => {
  const [selectionMenu, setSelectionMenu] = useState<{ x: number; y: number; text: string; start: number; end: number } | null>(null);
  const [factCheckResults, setFactCheckResults] = useState<HallucinationDetectionResponse | null>(null);
  const [isFactChecking, setIsFactChecking] = useState(false);
  const [factCheckProgress, setFactCheckProgress] = useState<{ step: string; progress: number } | null>(null);
  const [chartModalOpen, setChartModalOpen] = useState(false);
  const [chartModalText, setChartModalText] = useState('');
  const [chartResult, setChartResult] = useState<(ChartGenerateResponse & { sectionId?: string }) | null>(null);
  const [linkModalOpen, setLinkModalOpen] = useState(false);
  const [linkModalText, setLinkModalText] = useState('');
  const selectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const smartTypingAssist = useSmartTypingAssist(contentRef, onTextReplace);

  const handleCheckFacts = async (text: string) => {
    if (!text.trim()) return;
    setIsFactChecking(true);
    setSelectionMenu(null);
    
    const progressSteps = [
      { step: "Extracting verifiable claims...", progress: 20 },
      { step: "Searching for evidence...", progress: 40 },
      { step: "Analyzing claims against sources...", progress: 70 },
      { step: "Generating final assessment...", progress: 90 },
      { step: "Completing fact-check...", progress: 100 }
    ];
    
    let currentStepIndex = 0;
    const progressInterval = setInterval(() => {
      if (currentStepIndex < progressSteps.length) {
        setFactCheckProgress(progressSteps[currentStepIndex]);
        currentStepIndex++;
      }
    }, 2000);
    
    const timeoutId = setTimeout(() => {
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
        error: 'Fact check timed out after 120 seconds. Please try again with shorter text.'
      });
    }, 120000);
    
    try {
      const results = await hallucinationDetectorService.detectHallucinations({
        text: text.trim(),
        include_sources: true,
        max_claims: 10
      });
      setFactCheckResults(results);
    } catch (error) {
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
      clearInterval(progressInterval);
      clearTimeout(timeoutId);
      setFactCheckProgress(null);
      setIsFactChecking(false);
    }
  };

  const handleCloseFactCheckResults = () => {
    setFactCheckResults(null);
  };

  const handleGenerateChart = (text: string) => {
    setChartModalText(text);
    setChartModalOpen(true);
    setSelectionMenu(null);
  };

  const handleChartGenerated = (result: ChartGenerateResponse & { sectionId?: string }) => {
    setChartResult(result);
    setChartModalOpen(false);
  };

  const handleFindLinks = (text: string) => {
    setLinkModalText(text);
    setLinkModalOpen(true);
    setSelectionMenu(null);
  };

  const handleLinkRewordAccept = (rewordedText: string, sectionId?: string) => {
    if (onTextReplace && linkModalText) {
      onTextReplace(linkModalText, rewordedText, 'reword-with-links');
    }
    window.dispatchEvent(new CustomEvent('blogwriter:replaceSelectedText', {
      detail: {
        originalText: linkModalText,
        editedText: rewordedText,
        editType: 'reword-with-links'
      }
    }));
    setLinkModalOpen(false);
  };

  const handleQuickEdit = (editType: string, selectedText: string) => {
    let editedText = selectedText;
    
    switch (editType) {
      case 'improve':
        editedText = selectedText.replace(/\./g, '. ').replace(/\s+/g, ' ').trim();
        if (!editedText.endsWith('.') && !editedText.endsWith('!') && !editedText.endsWith('?')) {
          editedText += '.';
        }
        break;
      case 'add-transition':
        const transitions = ['Furthermore,', 'Additionally,', 'Moreover,', 'In essence,', 'As a result,'];
        const randomTransition = transitions[Math.floor(Math.random() * transitions.length)];
        editedText = `${randomTransition} ${selectedText.toLowerCase()}`;
        break;
      case 'shorten':
        editedText = selectedText
          .replace(/\b(very|really|extremely|quite|rather|fairly)\s+/gi, '')
          .replace(/\b(that|which) (is|are|was|were)\s+/gi, '')
          .replace(/\bin order to\b/gi, 'to')
          .replace(/\bdue to the fact that\b/gi, 'because')
          .trim();
        break;
      case 'expand':
        editedText = selectedText + ' This approach provides significant value by offering concrete benefits and actionable insights that readers can immediately implement.';
        break;
      case 'professionalize':
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
        editedText = selectedText + ' According to recent industry studies, this approach has shown measurable improvements in key performance metrics.';
        break;
      default:
        return;
    }
    
    if (onTextReplace) {
      onTextReplace(selectedText, editedText, editType);
    }
    
    window.dispatchEvent(new CustomEvent('blogwriter:replaceSelectedText', { 
      detail: { 
        originalText: selectedText,
        editedText: editedText,
        editType: editType
      } 
    }));
    
    setSelectionMenu(null);
  };

  useEffect(() => {
    if (!selectionMenu) return;

    const handleGlobalClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-selection-menu]') && !target.closest('[data-fact-check-results]')) {
        setSelectionMenu(null);
      }
    };

    const timer = setTimeout(() => {
      document.addEventListener('mousedown', handleGlobalClick);
    }, 0);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', handleGlobalClick);
    };
  }, [selectionMenu]);

  useEffect(() => {
    return () => {
      setFactCheckProgress(null);
      if (selectionTimeoutRef.current) {
        clearTimeout(selectionTimeoutRef.current);
      }
    };
  }, []);

  const handleTextSelection = () => {
    if (selectionTimeoutRef.current) {
      clearTimeout(selectionTimeoutRef.current);
    }

    selectionTimeoutRef.current = setTimeout(() => {
      try {
        let text = '';
        let rect: DOMRect | null = null;
        let startPos = 0;
        let endPos = 0;

        const el = contentRef.current;
        if (el instanceof HTMLTextAreaElement) {
          const start = el.selectionStart;
          const end = el.selectionEnd;
          startPos = start;
          endPos = end;
          if (start !== end) {
            text = el.value.substring(start, end).trim();
            try {
              const textRect = el.getBoundingClientRect();
              const lineHeight = parseFloat(getComputedStyle(el).lineHeight) || 20;
              const linesBefore = el.value.substring(0, start).split('\n').length - 1;
              rect = new DOMRect(
                textRect.left + 10,
                textRect.top + (linesBefore * lineHeight) + 10,
                100,
                20
              );
            } catch (_) {}
          }
        } else {
          const sel = window.getSelection();
          if (sel && sel.rangeCount > 0) {
            text = (sel.toString() || '').trim();
            if (text.length >= 10) {
              rect = sel.getRangeAt(0).getBoundingClientRect();
            }
          }
        }

        if (!text || text.length < 10) {
          setSelectionMenu(null);
          return;
        }

        if (!rect || (rect.width === 0 && rect.height === 0)) {
          if (el) {
            const elRect = el.getBoundingClientRect();
            const x = Math.max(8, Math.min(elRect.left + (elRect.width / 2), window.innerWidth - 280));
            const y = Math.max(8, elRect.top + window.scrollY - 60);
            setSelectionMenu({ x, y, text, start: startPos, end: endPos });
            return;
          }
          setSelectionMenu(null);
          return;
        }

        const x = Math.max(8, Math.min(rect.left + (rect.width / 2), window.innerWidth - 280));
        const y = Math.max(8, rect.top + window.scrollY - 60);

        setSelectionMenu({ x, y, text, start: startPos, end: endPos });
      } catch (error) {
        console.error('Text selection error:', error);
        setSelectionMenu(null);
      }
    }, 150);
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
    ...smartTypingAssist,
    renderSelectionMenu: () => (
      <>
        <CompactSelectionMenu
          selectionMenu={selectionMenu}
          factCheckResults={factCheckResults}
          isFactChecking={isFactChecking}
          factCheckProgress={factCheckProgress}
          smartSuggestion={smartTypingAssist.smartSuggestion}
          isGeneratingSuggestion={smartTypingAssist.isGeneratingSuggestion}
          allSuggestions={smartTypingAssist.allSuggestions}
          suggestionIndex={smartTypingAssist.suggestionIndex}
          showContinueWritingPrompt={smartTypingAssist.showContinueWritingPrompt}
          onCheckFacts={handleCheckFacts}
          onGenerateChart={handleGenerateChart}
          onFindLinks={handleFindLinks}
          onCloseFactCheckResults={handleCloseFactCheckResults}
          onQuickEdit={handleQuickEdit}
          onAcceptSuggestion={smartTypingAssist.handleAcceptSuggestion}
          onRejectSuggestion={smartTypingAssist.handleRejectSuggestion}
          onNextSuggestion={smartTypingAssist.handleNextSuggestion}
          onRequestSuggestion={smartTypingAssist.handleRequestSuggestion}
          onDismissPrompt={smartTypingAssist.handleDismissPrompt}
          onFormatText={(type: string) => {
            if (selectionMenu) {
              onFormatText?.(type, selectionMenu.start, selectionMenu.end);
            } else {
              onFormatText?.(type);
            }
            setSelectionMenu(null);
          }}
        />
        {chartModalOpen && (
          <ChartGeneratorModal
            isOpen={chartModalOpen}
            onClose={() => setChartModalOpen(false)}
            defaultText={chartModalText}
            onChartGenerated={handleChartGenerated}
          />
        )}
        {linkModalOpen && (
          <LinkSearchModal
            isOpen={linkModalOpen}
            onClose={() => setLinkModalOpen(false)}
            sectionHeading=""
            sectionText={linkModalText}
            selectedText={linkModalText}
            onRewordAccept={handleLinkRewordAccept}
          />
        )}
      </>
    )
  };
};

export default useBlogTextSelectionHandler;
export type { BlogTextSelectionHandlerProps };
