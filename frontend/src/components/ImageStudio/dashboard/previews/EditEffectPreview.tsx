import React from 'react';
import { Box, Stack, Typography, Chip, Tooltip } from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { editBeforeAfter } from '../constants';

export const EditEffectPreview: React.FC = () => {
  const [exampleIndex, setExampleIndex] = React.useState(0);
  const pair = editBeforeAfter[exampleIndex];

  return (
    <Box
      sx={{
        mt: 2,
        borderRadius: 3,
        border: '1px solid rgba(255,255,255,0.08)',
        background: 'rgba(15,23,42,0.5)',
        p: 2,
      }}
    >
      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="overline" sx={{ color: '#fcd34d', letterSpacing: 2 }}>
          Before → After
        </Typography>
        <Tooltip
          title={
            <Stack spacing={1}>
              <Typography variant="body2">
                Hover to reveal the original upload vs. AI-edited output. Perfect for showing background swaps,
                inpainting, or relighting.
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap">
                {['Erase objects cleanly', 'Smart relight', 'Replace backgrounds'].map(label => (
                  <Chip
                    key={label}
                    size="small"
                    label={label}
                    sx={{ background: 'rgba(236,252,203,0.12)', color: '#fef3c7', borderRadius: 999 }}
                  />
                ))}
              </Stack>
            </Stack>
          }
        >
          <InfoOutlinedIcon sx={{ fontSize: 18, color: 'rgba(252,211,77,0.85)', cursor: 'pointer' }} />
        </Tooltip>
      </Stack>
      <Box
        sx={{
          '--gap': '8px',
          display: 'grid',
          position: 'relative',
          width: '100%',
          borderRadius: 3,
          overflow: 'hidden',
          border: '4px solid #22d3ee',
          minHeight: { xs: 260, md: 300 },
          '& > img': {
            '--progress': 'calc(-1 * var(--gap))',
            gridArea: '1 / 1',
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transition: 'clip-path 0.4s 0.1s',
          },
          '& > img:first-of-type': {
            clipPath: 'polygon(0 0, calc(100% + var(--progress)) 0, 0 calc(100% + var(--progress)))',
          },
          '& > img:last-of-type': {
            clipPath: 'polygon(100% 100%, 100% calc(0% - var(--progress)), calc(0% - var(--progress)) 100%)',
          },
          '&:hover > img:last-of-type, &:hover > img:first-of-type:hover': {
            '--progress': 'calc(50% - var(--gap))',
          },
          '&:hover > img:first-of-type, &:hover > img:first-of-type:hover + img': {
            '--progress': 'calc(-50% - var(--gap))',
          },
        }}
      >
        <Box component="img" src={pair.before} alt="Original asset" />
        <Box component="img" src={pair.after} alt="Edited asset" />
        <Stack
          direction="row"
          spacing={1}
          sx={{
            position: 'absolute',
            top: 12,
            right: 12,
            background: 'rgba(15,23,42,0.8)',
            borderRadius: 999,
            px: 1,
            py: 0.5,
            boxShadow: '0 10px 20px rgba(2,6,23,0.5)',
          }}
        >
          {editBeforeAfter.map((_, idx) => (
            <Box
              key={idx}
              onClick={() => setExampleIndex(idx)}
              sx={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: idx === exampleIndex ? '#f472b6' : 'rgba(255,255,255,0.4)',
                cursor: 'pointer',
              }}
            />
          ))}
        </Stack>
        <Stack
          direction="row"
          spacing={1}
          sx={{
            position: 'absolute',
            bottom: 12,
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(15,23,42,0.85)',
            px: 1.5,
            py: 0.75,
            borderRadius: 999,
            boxShadow: '0 10px 25px rgba(2,6,23,0.6)',
          }}
        >
          <Chip label="Original" size="small" sx={{ background: '#fef3c7', color: '#78350f', fontWeight: 600 }} />
          <Chip label="Edited" size="small" sx={{ background: '#a5b4fc', color: '#1e1b4b', fontWeight: 600 }} />
        </Stack>
      </Box>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5 }}>
        Prompt used: {pair.prompt}
      </Typography>
    </Box>
  );
};

