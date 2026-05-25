import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Divider from '@mui/material/Divider';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import ArticleIcon from '@mui/icons-material/Article';
import HelpIcon from '@mui/icons-material/Help';
import HeaderControls from '../../shared/HeaderControls';
import PhaseNavigation, { PhaseActionHandlers } from '../PhaseNavigation';

interface HeaderBarProps {
  phases: any[];
  currentPhase: string;
  onPhaseClick: (phaseId: string) => void;
  copilotKitAvailable?: boolean;
  actionHandlers?: PhaseActionHandlers;
  researchKeywords?: string;
  hasResearch?: boolean;
  hasOutline?: boolean;
  outlineConfirmed?: boolean;
  hasContent?: boolean;
  contentConfirmed?: boolean;
  hasSEOAnalysis?: boolean;
  seoRecommendationsApplied?: boolean;
  hasSEOMetadata?: boolean;
  onNewBlog?: () => void;
  onMyBlogs?: () => void;
  onHelp?: () => void;
}

export const HeaderBar: React.FC<HeaderBarProps> = ({ 
  phases, currentPhase, onPhaseClick, copilotKitAvailable = true, actionHandlers,
  researchKeywords = '', hasResearch = false, hasOutline = false, outlineConfirmed = false,
  hasContent = false, contentConfirmed = false, hasSEOAnalysis = false,
  seoRecommendationsApplied = false, hasSEOMetadata = false,
  onNewBlog, onMyBlogs, onHelp,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const isMenuOpen = Boolean(anchorEl);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => setAnchorEl(event.currentTarget);
  const handleMenuClose = () => setAnchorEl(null);

  const handleNewBlog = () => { handleMenuClose(); onNewBlog?.(); };
  const handleMyBlogs = () => { handleMenuClose(); onMyBlogs?.(); };
  const handleHelp = () => { handleMenuClose(); onHelp?.(); };

  return (
    <Box sx={{
      width: '100%',
      background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%)',
      borderRadius: 3,
      p: { xs: 1.5, md: 2.5 },
      border: '1px solid rgba(37, 99, 235, 0.15)',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0, left: 0, right: 0,
        height: '3px',
        background: 'linear-gradient(90deg, #2563eb 0%, #3b82f6 50%, #60a5fa 100%)',
      },
    }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1}>
        <Stack direction="row" alignItems="center" gap={1.5}>
          <Box sx={{
            width: { xs: 36, md: 44 },
            height: { xs: 36, md: 44 },
            borderRadius: 2,
            background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
          }}>
            <ArticleIcon sx={{ color: '#fff', fontSize: { xs: 20, md: 24 } }} />
          </Box>
          <Typography variant="h5" sx={{
            background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 700,
            fontSize: { xs: '1.1rem', sm: '1.25rem', md: '1.5rem' },
            letterSpacing: '-0.02em',
          }}>
            AI Blog Writer
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1} alignItems="center">
          <HeaderControls colorMode="light" showAlerts={true} showUser={true} />

          <IconButton onClick={handleMenuOpen} sx={{
            background: isMenuOpen
              ? 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)'
              : 'rgba(37, 99, 235, 0.1)',
            border: '1px solid',
            borderColor: isMenuOpen ? 'transparent' : 'rgba(37, 99, 235, 0.3)',
            borderRadius: 2,
            p: 1,
            transition: 'all 0.2s ease',
            '&:hover': {
              background: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
              borderColor: 'transparent',
              transform: 'scale(1.05)',
            },
          }}>
            {isMenuOpen ? <CloseIcon sx={{ color: '#fff', fontSize: 20 }} /> : <MenuIcon sx={{ color: '#2563eb', fontSize: 20 }} />}
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={isMenuOpen}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            PaperProps={{
              sx: {
                mt: 1, minWidth: 220, borderRadius: 2,
                background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                border: '1px solid rgba(37, 99, 235, 0.3)',
                boxShadow: '0 10px 40px rgba(37, 99, 235, 0.25)',
                '& .MuiMenuItem-root': {
                  color: 'rgba(255, 255, 255, 0.85)',
                  px: 2, py: 1.5,
                  transition: 'all 0.15s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)',
                    color: '#fff',
                  },
                },
                '& .MuiListItemIcon-root': { color: '#60a5fa', minWidth: 36 },
                '& .MuiDivider-root': { borderColor: 'rgba(37, 99, 235, 0.2)', my: 0.5 },
              },
            }}
          >
            <MenuItem onClick={handleNewBlog}>
              <ListItemIcon><AddIcon fontSize="small" /></ListItemIcon>
              <ListItemText primary="New Blog" primaryTypographyProps={{ fontWeight: 600 }} />
            </MenuItem>
            <MenuItem onClick={handleMyBlogs}>
              <ListItemIcon><ArticleIcon fontSize="small" /></ListItemIcon>
              <ListItemText primary="My Blogs" primaryTypographyProps={{ fontWeight: 500 }} />
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleHelp}>
              <ListItemIcon><HelpIcon fontSize="small" /></ListItemIcon>
              <ListItemText primary="Help & Docs" primaryTypographyProps={{ fontWeight: 500 }} />
            </MenuItem>
          </Menu>
        </Stack>
      </Stack>

      <Box sx={{ mt: 1 }}>
        <PhaseNavigation
          phases={phases}
          currentPhase={currentPhase}
          onPhaseClick={onPhaseClick}
          copilotKitAvailable={copilotKitAvailable}
          actionHandlers={actionHandlers}
          researchKeywords={researchKeywords}
          hasResearch={hasResearch}
          hasOutline={hasOutline}
          outlineConfirmed={outlineConfirmed}
          hasContent={hasContent}
          contentConfirmed={contentConfirmed}
          hasSEOAnalysis={hasSEOAnalysis}
          seoRecommendationsApplied={seoRecommendationsApplied}
          hasSEOMetadata={hasSEOMetadata}
        />
      </Box>
    </Box>
  );
};

export default HeaderBar;
