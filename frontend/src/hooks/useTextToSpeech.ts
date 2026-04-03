import { useState, useCallback, useRef, useEffect, useMemo } from 'react';

export interface SpeechSynthesisOptions {
  voice?: SpeechSynthesisVoice;
  rate?: number;    // 0.1 to 10
  pitch?: number;   // 0 to 2
  volume?: number; // 0 to 1
}

export interface UseTextToSpeechReturn {
  speak: (text: string, options?: SpeechSynthesisOptions) => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  isSupported: boolean;
  isSpeaking: boolean;
  isPaused: boolean;
  voices: SpeechSynthesisVoice[];
  currentText: string | null;
}

// Singleton to manage global speech synthesis state
let globalIsSpeaking = false;
let globalIsPaused = false;
let globalCurrentText: string | null = null;
let globalOnStateChange: ((state: { isSpeaking: boolean; isPaused: boolean; currentText: string | null }) => void) | null = null;

const notifyStateChange = () => {
  if (globalOnStateChange) {
    globalOnStateChange({
      isSpeaking: globalIsSpeaking,
      isPaused: globalIsPaused,
      currentText: globalCurrentText,
    });
  }
};

export const useTextToSpeech = (): UseTextToSpeechReturn => {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  
  const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  // Initialize singleton listener
  useEffect(() => {
    globalOnStateChange = (state) => {
      // Force re-render by using state setter (handled through component-local state)
    };
    return () => {
      globalOnStateChange = null;
    };
  }, []);

  // Load available voices
  useEffect(() => {
    if (!isSupported) return;

    synthRef.current = window.speechSynthesis;

    const loadVoices = () => {
      const availableVoices = synthRef.current?.getVoices() || [];
      setVoices(availableVoices);
    };

    loadVoices();
    
    // Voices may load asynchronously
    synthRef.current.onvoiceschanged = loadVoices;

    // Cleanup on unmount - stop any ongoing speech
    return () => {
      if (synthRef.current) {
        synthRef.current.cancel();
        synthRef.current.onvoiceschanged = null;
      }
    };
  }, [isSupported]);

  const stop = useCallback(() => {
    if (synthRef.current) {
      synthRef.current.cancel();
    }
    globalIsSpeaking = false;
    globalIsPaused = false;
    globalCurrentText = null;
    notifyStateChange();
  }, []);

  const pause = useCallback(() => {
    if (synthRef.current && globalIsSpeaking && !globalIsPaused) {
      synthRef.current.pause();
      globalIsPaused = true;
      notifyStateChange();
    }
  }, []);

  const resume = useCallback(() => {
    if (synthRef.current && globalIsPaused) {
      synthRef.current.resume();
      globalIsPaused = false;
      notifyStateChange();
    }
  }, []);

  const speak = useCallback((text: string, options?: SpeechSynthesisOptions) => {
    if (!isSupported || !synthRef.current || !text?.trim()) return;

    // Stop any current speech first
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Apply options
    if (options?.voice) {
      utterance.voice = options.voice;
    }
    if (options?.rate !== undefined) {
      utterance.rate = Math.max(0.1, Math.min(10, options.rate));
    }
    if (options?.pitch !== undefined) {
      utterance.pitch = Math.max(0, Math.min(2, options.pitch));
    }
    if (options?.volume !== undefined) {
      utterance.volume = Math.max(0, Math.min(1, options.volume));
    }

    // Set up event handlers
    utterance.onstart = () => {
      globalIsSpeaking = true;
      globalIsPaused = false;
      globalCurrentText = text;
      notifyStateChange();
    };

    utterance.onend = () => {
      globalIsSpeaking = false;
      globalIsPaused = false;
      globalCurrentText = null;
      notifyStateChange();
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      globalIsSpeaking = false;
      globalIsPaused = false;
      globalCurrentText = null;
      notifyStateChange();
    };

    utterance.onpause = () => {
      globalIsPaused = true;
      notifyStateChange();
    };
    utterance.onresume = () => {
      globalIsPaused = false;
      notifyStateChange();
    };

    synthRef.current.speak(utterance);
  }, [isSupported]);

  // Use local state for reactivity but sync with global state
  const [localIsSpeaking, setLocalIsSpeaking] = useState(false);
  const [localIsPaused, setLocalIsPaused] = useState(false);
  const [localCurrentText, setLocalCurrentText] = useState<string | null>(null);

  // Sync with global state periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setLocalIsSpeaking(globalIsSpeaking);
      setLocalIsPaused(globalIsPaused);
      setLocalCurrentText(globalCurrentText);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return {
    speak,
    stop,
    pause,
    resume,
    isSupported,
    isSpeaking: localIsSpeaking,
    isPaused: localIsPaused,
    voices,
    currentText: localCurrentText,
  };
};

export default useTextToSpeech;
