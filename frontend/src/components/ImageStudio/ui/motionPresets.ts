import { type Variants, type Easing } from 'framer-motion';

export const easeOutSmooth: Easing = [0.4, 0, 0.2, 1];
export const easeEmphasis: Easing = [0.22, 0.61, 0.36, 1];

export const fadeSlideVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: easeOutSmooth },
  },
};

export const cardLiftVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.45, ease: easeEmphasis },
  },
  hover: {
    y: -4,
    transition: { duration: 0.2, ease: easeOutSmooth },
  },
};

export const shimmerVariants: Variants = {
  initial: { opacity: 0.4 },
  animate: {
    opacity: [0.4, 0.7, 0.4],
    transition: { duration: 1.6, repeat: Infinity, ease: 'easeInOut' },
  },
};

