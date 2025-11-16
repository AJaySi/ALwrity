export const outlineActionButtonSx = {
  textTransform: 'none',
  borderRadius: '999px',
  fontWeight: 600,
  px: 3,
  py: 1.2,
  borderWidth: 2,
  borderColor: 'rgba(59, 34, 18, 0.35)',
  color: '#3B2618',
  backgroundColor: 'rgba(255, 249, 239, 0.95)',
  boxShadow: '0 14px 26px rgba(26, 22, 17, 0.12)',
  transition: 'all 0.25s ease',
  '&:hover': {
    borderColor: '#3B2618',
    boxShadow: '0 18px 32px rgba(26, 22, 17, 0.18)',
    transform: 'translateY(-2px)',
    backgroundColor: 'rgba(255, 245, 228, 0.98)',
  },
  '&:disabled': {
    opacity: 0.4,
    boxShadow: 'none',
    transform: 'none',
    backgroundColor: 'rgba(255, 255, 255, 0.6)',
  },
} as const;

export const primaryButtonSx = {
  ...outlineActionButtonSx,
  background: 'linear-gradient(125deg, #5d3b24 0%, #a36c3b 45%, #f1c27d 100%)',
  color: '#fff',
  border: 'none',
  boxShadow: '0 20px 40px rgba(93, 59, 36, 0.35)',
  '&:hover': {
    ...outlineActionButtonSx['&:hover'],
    background: 'linear-gradient(125deg, #4c2f1c 0%, #8b552d 45%, #f7d9a0 100%)',
    boxShadow: '0 24px 46px rgba(93, 59, 36, 0.45)',
  },
  '&:disabled': {
    opacity: 0.35,
    boxShadow: 'none',
    cursor: 'not-allowed',
  },
} as const;

