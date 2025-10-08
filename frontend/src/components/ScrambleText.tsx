import React, { useRef, useEffect } from 'react';
import { useScramble } from '../hooks/useScramble';

interface ScrambleTextProps {
  text: string;
  duration?: number;
  delay?: number;
  restartInterval?: number;
  className?: string;
  style?: React.CSSProperties;
  as?: React.ElementType;
}

export const ScrambleText: React.FC<ScrambleTextProps> = ({
  text,
  duration = 750,
  delay = 0,
  restartInterval = 7000,
  className = '',
  style = {},
  as: Component = 'span',
}) => {
  const { displayText, start, stop } = useScramble({ text, duration });
  const ref = useRef<HTMLElement>(null);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    // A flag to ensure our timeouts don't run after unmount
    let isMounted = true;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            if (!isMounted) return;
            start();
            if (intervalRef.current) clearInterval(intervalRef.current);
            intervalRef.current = window.setInterval(start, restartInterval);
          }, delay);
        } else {
          stop();
          if (intervalRef.current) clearInterval(intervalRef.current);
        }
      },
      { threshold: 0.2, rootMargin: '0px' }
    );

    observer.observe(element);

    return () => {
      isMounted = false;
      observer.disconnect();
      if (intervalRef.current) clearInterval(intervalRef.current);
      stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [delay, restartInterval, text]); // Re-run effect if text or config changes. start/stop are stable.

  return (
    <Component ref={ref} className={className} style={style}>
      {displayText}
    </Component>
  );
};
