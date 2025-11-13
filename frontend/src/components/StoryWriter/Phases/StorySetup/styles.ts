// Shared styles for Story Setup components

export const textFieldStyles = {
  '& .MuiOutlinedInput-root': {
    backgroundColor: '#FFFFFF',
    color: '#1A1611',
    '& fieldset': {
      borderColor: '#8D6E63',
      borderWidth: '1.5px',
    },
    '&:hover fieldset': {
      borderColor: '#5D4037',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#3E2723',
      borderWidth: '2px',
    },
  },
  '& .MuiInputLabel-root': {
    color: '#3E2723',
    fontWeight: 500,
    '&.Mui-focused': {
      color: '#1A1611',
      fontWeight: 600,
    },
    '&.Mui-required': {
      '&::after': {
        color: '#D32F2F',
      },
    },
  },
  '& .MuiFormHelperText-root': {
    color: '#5D4037',
    fontSize: '0.875rem',
    fontWeight: 400,
    marginTop: '4px',
  },
  '& .MuiInputBase-input': {
    color: '#1A1611',
    '&::placeholder': {
      color: '#8D6E63',
      opacity: 0.7,
    },
  },
  '& .MuiSelect-select': {
    color: '#1A1611',
  },
  '& .MuiMenuItem-root': {
    color: '#1A1611',
    '&:hover': {
      backgroundColor: '#F7F3E9',
    },
    '&.Mui-selected': {
      backgroundColor: '#E8E5D3',
      '&:hover': {
        backgroundColor: '#E8E5D3',
      },
    },
  },
};

export const paperStyles = {
  p: 4,
  mt: 2,
  backgroundColor: '#F7F3E9', // Warm cream/parchment color
  color: '#2C2416', // Dark brown text for readability
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
};

export const accordionStyles = {
  mb: 2,
  backgroundColor: '#FAF9F6', // Slightly lighter cream for accordions
  '&:before': {
    display: 'none', // Remove default border
  },
};

export const cardStyles = {
  backgroundColor: '#FAF9F6', // Slightly lighter cream for cards
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.08)',
};

