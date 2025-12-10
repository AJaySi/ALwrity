/**
 * Shared styles for YouTube Creator Studio
 */

import { YT_RED, YT_TEXT } from './constants';

export const inputSx = {
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#fff',
    color: YT_TEXT,
    borderRadius: 1,
    '& fieldset': {
      borderColor: '#c6c6c6',
    },
    '&:hover fieldset': {
      borderColor: YT_RED,
    },
    '&.Mui-focused fieldset': {
      borderColor: YT_RED,
      boxShadow: '0 0 0 2px rgba(255,0,0,0.08)',
    },
    '& input::placeholder, & textarea::placeholder': {
      color: '#5f6368',
      opacity: 1,
    },
  },
};

export const selectSx = {
  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#c6c6c6' },
  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: YT_RED },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: YT_RED },
  '& .MuiSelect-select': { color: YT_TEXT, backgroundColor: '#fff' },
};

export const labelSx = { color: '#5f6368', '&.Mui-focused': { color: YT_RED } };
export const helperSx = { color: '#5f6368' };

