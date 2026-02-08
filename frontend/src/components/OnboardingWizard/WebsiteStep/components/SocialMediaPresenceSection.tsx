/**
 * SocialMediaPresenceSection Component
 * Displays social media accounts and their links
 */

import React, { useState } from 'react';
import {
  Typography,
  Grid,
  Card,
  CardContent,
  Avatar,
  Button,
  Box,
  IconButton,
  TextField,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Share as ShareIcon,
  Facebook as FacebookIcon,
  Instagram as InstagramIcon,
  LinkedIn as LinkedInIcon,
  YouTube as YouTubeIcon,
  Twitter as TwitterIcon,
  Edit as EditIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

interface SocialMediaPresenceSectionProps {
  socialMediaAccounts: { [key: string]: string };
  onUpdateAccounts?: (newAccounts: { [key: string]: string }) => void;
  onRefresh?: () => Promise<void> | void;
  isRefreshing?: boolean;
}

const SocialMediaPresenceSection: React.FC<SocialMediaPresenceSectionProps> = ({
  socialMediaAccounts,
  onUpdateAccounts,
  onRefresh,
  isRefreshing = false
}) => {
  const [editingPlatform, setEditingPlatform] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  // Don't render if no social media accounts and no refresh capability
  if (Object.keys(socialMediaAccounts).length === 0 && !onRefresh) {
    return null;
  }

  const handleStartEdit = (platform: string, url: string) => {
    setEditingPlatform(platform);
    setEditValue(url);
  };

  const handleSaveEdit = (platform: string) => {
    if (onUpdateAccounts) {
      const newAccounts = { ...socialMediaAccounts, [platform]: editValue };
      onUpdateAccounts(newAccounts);
    }
    setEditingPlatform(null);
  };

  const handleCancelEdit = () => {
    setEditingPlatform(null);
    setEditValue('');
  };

  const platformIcons: { [key: string]: React.ReactNode } = {
    facebook: <FacebookIcon />,
    instagram: <InstagramIcon />,
    linkedin: <LinkedInIcon />,
    youtube: <YouTubeIcon />,
    twitter: <TwitterIcon />,
    tiktok: <ShareIcon /> // Fallback icon for TikTok
  };

  return (
    <>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography 
          variant="h6" 
          fontWeight={600} 
          sx={{ color: '#1a202c !important' }} // Force dark text
        >
          <ShareIcon sx={{ mr: 1, verticalAlign: 'middle', color: '#667eea !important' }} />
          Social Media Presence
        </Typography>
        {onRefresh && (
            <Tooltip title="Refresh social media data">
                <Box>
                    <IconButton 
                        onClick={onRefresh} 
                        disabled={isRefreshing}
                        size="small"
                        sx={{ ml: 2 }}
                    >
                        {isRefreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
                    </IconButton>
                </Box>
            </Tooltip>
        )}
      </Box>
      
      <Grid container spacing={2} mb={4}>
        {Object.entries(socialMediaAccounts).map(([platform, url]) => {
          if (!url && !editingPlatform) return null;
          
          const isEditing = editingPlatform === platform;

          return (
            <Grid item xs={12} sm={6} md={4} lg={3} xl={2} key={platform}>
              <Card sx={{ 
                height: '100%',
                background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%)',
                border: '1px solid #81d4fa',
                boxShadow: '0 4px 12px rgba(3, 169, 244, 0.15)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 20px rgba(3, 169, 244, 0.25)'
                }
              }}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2}>
                    <Avatar sx={{ width: 40, height: 40, bgcolor: 'primary.main' }}>
                      {platformIcons[platform] || <ShareIcon />}
                    </Avatar>
                    <Box flex={1}>
                      <Typography variant="h6" fontWeight={600} textTransform="capitalize">
                        {platform}
                      </Typography>
                      {isEditing ? (
                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                            <TextField
                                value={editValue}
                                onChange={(e) => setEditValue(e.target.value)}
                                size="small"
                                fullWidth
                                variant="outlined"
                                sx={{ 
                                    '& .MuiInputBase-input': { py: 0.5, fontSize: '0.875rem' },
                                    bgcolor: 'white'
                                }}
                            />
                            <IconButton size="small" onClick={() => handleSaveEdit(platform)} color="primary">
                                <CheckIcon fontSize="small" />
                            </IconButton>
                            <IconButton size="small" onClick={handleCancelEdit} color="error">
                                <CloseIcon fontSize="small" />
                            </IconButton>
                        </Box>
                      ) : (
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                            <Button
                                variant="text"
                                size="small"
                                href={url as string}
                                target="_blank"
                                rel="noopener noreferrer"
                                sx={{ p: 0, minWidth: 'auto', textTransform: 'none' }}
                            >
                                View Profile
                            </Button>
                            {onUpdateAccounts && (
                                <IconButton size="small" onClick={() => handleStartEdit(platform, url as string)}>
                                    <EditIcon fontSize="small" />
                                </IconButton>
                            )}
                        </Box>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </>
  );
};

export default SocialMediaPresenceSection;
