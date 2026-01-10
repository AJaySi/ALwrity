import React, { useEffect } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface AnimatedNumberProps {
  value: number;
  format?: (n: number) => string;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}

/**
 * AnimatedNumber - Smoothly animates number changes
 * 
 * Usage:
 *   <AnimatedNumber value={1234.56} format={(n) => `$${n.toFixed(2)}`} />
 *   <AnimatedNumber value={1000} prefix="$" decimals={2} />
 */
export const AnimatedNumber: React.FC<AnimatedNumberProps> = ({ 
  value, 
  format,
  duration = 1,
  decimals = 0,
  prefix = '',
  suffix = ''
}) => {
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { 
    stiffness: 50, 
    damping: 30,
    duration: duration * 1000
  });
  
  const display = useTransform(spring, (latest) => {
    const rounded = decimals > 0 ? Number(latest.toFixed(decimals)) : Math.round(latest);
    if (format) {
      return format(rounded);
    }
    return `${prefix}${rounded.toLocaleString()}${suffix}`;
  });

  useEffect(() => {
    motionValue.set(value);
  }, [value, motionValue]);

  return <motion.span>{display}</motion.span>;
};

export default AnimatedNumber;
