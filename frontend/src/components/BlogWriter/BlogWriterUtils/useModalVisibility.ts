import { useState, useEffect, useRef } from 'react';

interface UseModalVisibilityProps {
  mediumPolling: { isPolling: boolean };
  rewritePolling: { isPolling: boolean };
  outlinePolling: { isPolling: boolean };
}

export const useModalVisibility = ({
  mediumPolling,
  rewritePolling,
  outlinePolling,
}: UseModalVisibilityProps) => {
  const [showModal, setShowModal] = useState(false);
  const [modalStartTime, setModalStartTime] = useState<number | null>(null);
  const [isMediumGenerationStarting, setIsMediumGenerationStarting] = useState(false);
  const [showOutlineModal, setShowOutlineModal] = useState(false);

  // Add minimum display time for modal
  useEffect(() => {
    if ((mediumPolling.isPolling || rewritePolling.isPolling || isMediumGenerationStarting) && !showModal) {
      setShowModal(true);
      setModalStartTime(Date.now());
    } else if (!mediumPolling.isPolling && !rewritePolling.isPolling && !isMediumGenerationStarting && showModal) {
      const elapsed = Date.now() - (modalStartTime || 0);
      const minDisplayTime = 2000; // 2 seconds minimum
      
      if (elapsed < minDisplayTime) {
        setTimeout(() => {
          setShowModal(false);
          setModalStartTime(null);
        }, minDisplayTime - elapsed);
      } else {
        setShowModal(false);
        setModalStartTime(null);
      }
    }
  }, [mediumPolling.isPolling, rewritePolling.isPolling, isMediumGenerationStarting, showModal, modalStartTime]);

  // Handle outline modal visibility with proper timeout cleanup
  const outlineHideRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (outlinePolling.isPolling && !showOutlineModal) {
      setShowOutlineModal(true);
    } else if (!outlinePolling.isPolling && showOutlineModal) {
      outlineHideRef.current = setTimeout(() => {
        setShowOutlineModal(false);
        outlineHideRef.current = null;
      }, 1000);
    }
    return () => {
      if (outlineHideRef.current) {
        clearTimeout(outlineHideRef.current);
        outlineHideRef.current = null;
      }
    };
  }, [outlinePolling.isPolling, showOutlineModal]);

  return {
    showModal,
    setShowModal,
    showOutlineModal,
    setShowOutlineModal,
    isMediumGenerationStarting,
    setIsMediumGenerationStarting,
  };
};

