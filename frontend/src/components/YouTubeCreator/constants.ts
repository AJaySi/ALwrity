/**
 * Constants for YouTube Creator Studio
 */

export const YT_RED = '#FF0000';
export const YT_BG = '#f9f9f9';
export const YT_BORDER = '#e5e5e5';
export const YT_TEXT = '#0f0f0f';

export const STEPS = ['Plan Your Video', 'Review Scenes', 'Render Video'] as const;

export const RESOLUTIONS = ['480p', '720p', '1080p'] as const;
export type Resolution = typeof RESOLUTIONS[number];

export const DURATION_TYPES = ['shorts', 'medium', 'long'] as const;
export type DurationType = typeof DURATION_TYPES[number];

export const POLLING_INTERVAL_MS = 2000; // 2 seconds

