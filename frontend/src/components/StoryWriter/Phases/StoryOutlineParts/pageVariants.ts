import { Variants } from 'framer-motion';

export const easeInOut = [0.22, 0.61, 0.36, 1] as const;
export const easeOut = [0.4, 0, 1, 1] as const;

export const leftPageVariants: Variants = {
  enter: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? -20 : 20,
    x: direction === 0 ? 0 : direction > 0 ? -80 : 80,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: 'center',
  }),
  center: {
    rotateY: 0,
    x: 0,
    opacity: 1,
    transformOrigin: 'center',
    transition: { duration: 0.55, ease: easeInOut },
  },
  exit: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? 15 : -15,
    x: direction === 0 ? 0 : direction > 0 ? 60 : -60,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: 'center',
    transition: { duration: 0.4, ease: easeOut },
  }),
};

export const rightPageVariants: Variants = {
  enter: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? 25 : -25,
    x: direction === 0 ? 0 : direction > 0 ? 110 : -110,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: direction >= 0 ? 'right center' : 'left center',
  }),
  center: {
    rotateY: 0,
    x: 0,
    opacity: 1,
    transformOrigin: 'center',
    transition: { duration: 0.55, ease: easeInOut },
  },
  exit: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? -25 : 25,
    x: direction === 0 ? 0 : direction > 0 ? -90 : 90,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: direction >= 0 ? 'left center' : 'right center',
    transition: { duration: 0.4, ease: easeOut },
  }),
};

