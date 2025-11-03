import { useRef, useEffect } from 'react';
import { debug } from '../../../utils/debug';

interface UseBlogWriterRefsProps {
  research: any;
  outline: any[];
  outlineConfirmed: boolean;
  contentConfirmed: boolean;
  sections: Record<string, string>;
  currentPhase: string;
  isSEOAnalysisModalOpen: boolean;
  resetUserSelection: () => void;
}

export const useBlogWriterRefs = ({
  research,
  outline,
  outlineConfirmed,
  contentConfirmed,
  sections,
  currentPhase,
  isSEOAnalysisModalOpen,
  resetUserSelection,
}: UseBlogWriterRefsProps) => {
  // Track when outlines/content become available for the first time
  const prevOutlineLenRef = useRef<number>(outline.length);
  const prevOutlineConfirmedRef = useRef<boolean>(outlineConfirmed);
  const prevContentConfirmedRef = useRef<boolean>(contentConfirmed);
  
  useEffect(() => {
    const prevLen = prevOutlineLenRef.current;
    if (research && prevLen === 0 && outline.length > 0) {
      resetUserSelection();
    }
    prevOutlineLenRef.current = outline.length;
  }, [research, outline.length, resetUserSelection]);

  // Only reset user selection when transitioning from not-confirmed to confirmed
  useEffect(() => {
    const wasConfirmed = prevOutlineConfirmedRef.current;
    if (!wasConfirmed && outlineConfirmed && Object.keys(sections).length > 0) {
      resetUserSelection(); // Allow auto-progression to content phase
    }
    prevOutlineConfirmedRef.current = outlineConfirmed;
  }, [outlineConfirmed, sections, resetUserSelection]);

  useEffect(() => {
    const wasConfirmed = prevContentConfirmedRef.current;
    if (!wasConfirmed && contentConfirmed) {
      resetUserSelection(); // Allow auto-progression to SEO phase
    }
    prevContentConfirmedRef.current = contentConfirmed;
  }, [contentConfirmed, resetUserSelection]);

  // Log critical state changes only (reduce noise)
  const lastPhaseRef = useRef<string>('');
  const lastSeoOpenRef = useRef<boolean>(false);
  const lastSectionsLenRef = useRef<number>(0);

  useEffect(() => {
    if (currentPhase !== lastPhaseRef.current) {
      debug.log('[BlogWriter] Phase changed', { currentPhase });
      lastPhaseRef.current = currentPhase;
    }
  }, [currentPhase]);

  useEffect(() => {
    const open = isSEOAnalysisModalOpen;
    if (open !== lastSeoOpenRef.current) {
      debug.log('[BlogWriter] SEO modal', { isOpen: open });
      lastSeoOpenRef.current = open;
    }
  }, [isSEOAnalysisModalOpen]);

  useEffect(() => {
    const len = Object.keys(sections || {}).length;
    if (len !== lastSectionsLenRef.current) {
      debug.log('[BlogWriter] Sections updated', { count: len });
      lastSectionsLenRef.current = len;
    }
  }, [sections]);
};

