/**
 * CompetitorsGrid Component
 * Displays discovered competitors in a grid layout
 */

import React, { useState } from 'react';
import {
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Avatar,
  Button,
  Box,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tooltip
} from '@mui/material';
import {
  Business as BusinessIcon,
  OpenInNew as OpenInNewIcon,
  Delete as DeleteIcon,
  Add as AddIcon
} from '@mui/icons-material';

export interface Competitor {
  url: string;
  domain: string;
  title: string;
  summary: string;
  relevance_score: number;
  highlights?: string[];
  favicon?: string;
  image?: string;
  published_date?: string;
  author?: string;
  competitive_insights: {
    business_model: string;
    target_audience: string;
  };
  content_insights: {
    content_focus: string;
    content_quality: string;
  };
}

interface CompetitorsGridProps {
  competitors: Competitor[];
  onShowHighlights: (competitor: Competitor) => void;
  onRemoveCompetitor?: (index: number) => void;
  onAddCompetitor?: (competitor: Competitor) => void;
}

// Utility function to get favicon URL
const getFaviconUrl = (url: string): string => {
  try {
    const domain = new URL(url).hostname;
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
  } catch {
    return '';
  }
};

const CompetitorsGrid: React.FC<CompetitorsGridProps> = ({
  competitors,
  onShowHighlights,
  onRemoveCompetitor,
  onAddCompetitor
}) => {
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [newCompetitorUrl, setNewCompetitorUrl] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddSubmit = async () => {
    if (!newCompetitorUrl) return;
    
    setIsAdding(true);
    try {
      // Create a basic competitor object
      // In a real implementation, you might want to fetch metadata here or let the parent handle it
      let domain = '';
      try {
        domain = new URL(newCompetitorUrl).hostname;
      } catch {
        domain = newCompetitorUrl;
      }

      const newCompetitor: Competitor = {
        url: newCompetitorUrl.startsWith('http') ? newCompetitorUrl : `https://${newCompetitorUrl}`,
        domain: domain,
        title: domain,
        summary: 'Manually added competitor',
        relevance_score: 1.0,
        competitive_insights: {
          business_model: 'Unknown',
          target_audience: 'Unknown'
        },
        content_insights: {
          content_focus: 'Unknown',
          content_quality: 'Unknown'
        }
      };

      if (onAddCompetitor) {
        onAddCompetitor(newCompetitor);
      }
      setOpenAddDialog(false);
      setNewCompetitorUrl('');
    } catch (error) {
      console.error('Error adding competitor:', error);
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography 
            variant="h6" 
            fontWeight={600} 
            sx={{ color: '#1a202c !important' }} // Force dark text
        >
            <BusinessIcon sx={{ mr: 1, verticalAlign: 'middle', color: '#667eea !important' }} />
            Discovered Competitors ({competitors.length})
        </Typography>
        {onAddCompetitor && (
            <Button
                variant="outlined"
                size="small"
                startIcon={<AddIcon />}
                onClick={() => setOpenAddDialog(true)}
                sx={{ textTransform: 'none' }}
            >
                Add Competitor
            </Button>
        )}
      </Box>

      <Grid container spacing={3}>
        {competitors.map((competitor, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} xl={2} key={index}>
            <Card sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%)',
              border: '1px solid #81d4fa',
              boxShadow: '0 4px 12px rgba(3, 169, 244, 0.15)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 20px rgba(3, 169, 244, 0.25)'
              },
              position: 'relative'
            }}>
              {onRemoveCompetitor && (
                  <IconButton
                    size="small"
                    onClick={() => onRemoveCompetitor(index)}
                    sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        bgcolor: 'rgba(255,255,255,0.7)',
                        '&:hover': { bgcolor: 'rgba(255,255,255,0.9)', color: 'error.main' }
                    }}
                  >
                      <DeleteIcon fontSize="small" />
                  </IconButton>
              )}

              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="flex-start" gap={2} mb={2}>
                  <Avatar 
                    sx={{ 
                      width: 40, 
                      height: 40,
                      backgroundColor: '#f8fafc',
                      border: '1px solid #e2e8f0'
                    }}
                    src={competitor.favicon || getFaviconUrl(competitor.url)}
                    onError={(e) => {
                      // Hide the image if it fails to load
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  >
                    <BusinessIcon sx={{ color: '#667eea' }} />
                  </Avatar>
                  <Box flex={1} pr={onRemoveCompetitor ? 3 : 0}>
                    <Typography 
                      variant="h6" 
                      fontWeight={600} 
                      gutterBottom
                      sx={{ color: '#1a202c !important', wordBreak: 'break-word' }} // Force dark text for readability
                    >
                      {competitor.title}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      gutterBottom
                      sx={{ color: '#4a5568 !important', wordBreak: 'break-all' }} // Force dark text for readability
                    >
                      {competitor.domain}
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      <Chip 
                        label={`${Math.round(competitor.relevance_score * 100)}% Match`}
                        color="primary"
                        size="small"
                      />
                      {competitor.published_date && (
                        <Chip 
                          label={new Date(competitor.published_date).toLocaleDateString()}
                          variant="outlined"
                          size="small"
                          sx={{ 
                            fontSize: '0.7rem',
                            height: 20,
                            '& .MuiChip-label': { px: 1 }
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>

                <Typography 
                  variant="body2" 
                  mb={2}
                  sx={{ color: '#2d3748 !important' }} // Force dark text for readability
                >
                  {competitor.summary.length > 150 
                    ? `${competitor.summary.substring(0, 150)}...` 
                    : competitor.summary
                  }
                </Typography>
              </CardContent>

              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button
                  size="small"
                  startIcon={<OpenInNewIcon />}
                  onClick={() => window.open(competitor.url, '_blank')}
                >
                  Visit Website
                </Button>
                {competitor.highlights && competitor.highlights.length > 0 && (
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => onShowHighlights(competitor)}
                  >
                    Highlights
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Add Competitor Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
        <DialogTitle>Add Competitor Manually</DialogTitle>
        <DialogContent>
            <Typography variant="body2" color="textSecondary" paragraph>
                Enter the URL of a competitor website to include in the analysis.
            </Typography>
            <TextField
                autoFocus
                margin="dense"
                label="Competitor URL"
                type="url"
                fullWidth
                variant="outlined"
                value={newCompetitorUrl}
                onChange={(e) => setNewCompetitorUrl(e.target.value)}
                placeholder="https://example.com"
            />
        </DialogContent>
        <DialogActions>
            <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
            <Button onClick={handleAddSubmit} variant="contained" disabled={!newCompetitorUrl}>
                Add Competitor
            </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default CompetitorsGrid;
