import React, { useState, useCallback, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Box,
  Typography,
  TextField,
  InputAdornment,
  CircularProgress,
  Card,
  CardMedia,
  CardContent,
  IconButton,
  Alert,
  Tooltip,
  Stack,
} from '@mui/material';
import {
  Search,
  Close,
  CheckCircle,
  Favorite,
  FavoriteBorder,
  Collections,
} from '@mui/icons-material';
import { useContentAssets, ContentAsset } from '../../hooks/useContentAssets';
import { fetchMediaBlobUrl } from '../../utils/fetchMediaBlobUrl';

export interface AssetLibraryImageModalProps {
  open: boolean;
  onClose: () => void;
  onSelect: (asset: ContentAsset) => void;
  title?: string;
  sourceModule?: string | string[]; // Optional filter by source module(s) (e.g., 'youtube_creator', 'podcast_maker', or ['youtube_creator', 'podcast_maker'])
  allowFavoritesOnly?: boolean; // Optional favorites-only filter toggle
}

/**
 * Reusable modal to browse and pick images from the Asset Library.
 * Image-only, with search and optional favorites/source filtering.
 */
export const AssetLibraryImageModal: React.FC<AssetLibraryImageModalProps> = ({
  open,
  onClose,
  onSelect,
  title = 'Select Image from Asset Library',
  sourceModule,
  allowFavoritesOnly = false,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAsset, setSelectedAsset] = useState<ContentAsset | null>(null);
  const [page, setPage] = useState(0);
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [imageBlobUrls, setImageBlobUrls] = useState<Map<number, string>>(new Map());
  const [loadingImages, setLoadingImages] = useState<Set<number>>(new Set());
  const pageSize = 24;

  // Filter for images only
  const filters = {
    asset_type: 'image' as const,
    source_module: sourceModule,
    search: searchQuery || undefined,
    favorites_only: allowFavoritesOnly && favoritesOnly ? true : undefined,
    limit: pageSize,
    offset: page * pageSize,
  };

  const { assets, loading, error, total, toggleFavorite, refetch } = useContentAssets(filters);

  // Check if a URL requires authentication (internal API endpoints)
  const isAuthenticatedUrl = useCallback((url: string): boolean => {
    if (!url) return false;
    return url.includes('/api/podcast/') || 
           url.includes('/api/youtube/') || 
           url.includes('/api/story/') ||
           (url.startsWith('/') && !url.startsWith('//'));
  }, []);

  // Load blob URLs for authenticated images
  useEffect(() => {
    if (!open || assets.length === 0) {
      // Clean up blob URLs when modal closes or no assets
      setImageBlobUrls(prev => {
        prev.forEach((url) => {
          if (url.startsWith('blob:')) {
            URL.revokeObjectURL(url);
          }
        });
        return new Map();
      });
      setLoadingImages(new Set());
      return;
    }

    const loadBlobUrls = async () => {
      const newBlobUrls = new Map<number, string>();
      const newLoadingImages = new Set<number>();

      for (const asset of assets) {
        if (!asset.file_url) continue;

        // Check if this is an authenticated endpoint
        if (isAuthenticatedUrl(asset.file_url)) {
          newLoadingImages.add(asset.id);
          try {
            const blobUrl = await fetchMediaBlobUrl(asset.file_url);
            if (blobUrl) {
              newBlobUrls.set(asset.id, blobUrl);
            }
          } catch (err) {
            console.error(`[AssetLibraryImageModal] Failed to load image for asset ${asset.id}:`, err);
          } finally {
            newLoadingImages.delete(asset.id);
          }
        } else {
          // External URL, use directly
          newBlobUrls.set(asset.id, asset.file_url);
        }
      }

      setImageBlobUrls(prev => {
        // Clean up old blob URLs that are no longer needed
        prev.forEach((url, id) => {
          if (!newBlobUrls.has(id) && url.startsWith('blob:')) {
            URL.revokeObjectURL(url);
          }
        });
        return newBlobUrls;
      });
      setLoadingImages(newLoadingImages);
    };

    loadBlobUrls();

    // Cleanup function
    return () => {
      // Don't clean up here - let the next effect handle it
    };
  }, [assets, open, isAuthenticatedUrl]);

  // Cleanup blob URLs on unmount
  useEffect(() => {
    return () => {
      imageBlobUrls.forEach((url) => {
        if (url.startsWith('blob:')) {
          URL.revokeObjectURL(url);
        }
      });
    };
  }, [imageBlobUrls]);

  const handleClose = useCallback(() => {
    onClose();
    setSelectedAsset(null);
    setSearchQuery('');
    setPage(0);
    setFavoritesOnly(false);
  }, [onClose]);

  const handleSelect = useCallback(() => {
    if (selectedAsset) {
      onSelect(selectedAsset);
      handleClose();
    }
  }, [selectedAsset, onSelect, handleClose]);

  const handleAssetClick = useCallback((asset: ContentAsset) => {
    setSelectedAsset(asset);
  }, []);

  const handleFavoriteToggle = useCallback(
    async (assetId: number, e: React.MouseEvent) => {
      e.stopPropagation();
      try {
        await toggleFavorite(assetId);
        refetch();
      } catch (err) {
        console.error('Error toggling favorite:', err);
      }
    },
    [toggleFavorite, refetch]
  );

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          maxHeight: '90vh',
          backgroundColor: '#ffffff',
        },
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" spacing={1} alignItems="center">
            <Collections sx={{ color: '#FF0000' }} />
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#111827' }}>
              {title}
            </Typography>
          </Stack>
          <IconButton onClick={handleClose} size="small" sx={{ color: '#6b7280' }}>
            <Close />
          </IconButton>
        </Stack>
      </DialogTitle>

      <DialogContent dividers sx={{ backgroundColor: '#f9fafb' }}>
        {/* Search and Filters */}
        <Box sx={{ mb: 3 }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <TextField
              fullWidth
              placeholder="Search images by title, description, or tags..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(0);
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: '#9ca3af' }} />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: '#ffffff',
                  '& fieldset': {
                    borderColor: '#d1d5db',
                  },
                },
              }}
            />
            {allowFavoritesOnly && (
              <Button
                variant={favoritesOnly ? 'contained' : 'outlined'}
                startIcon={<Favorite />}
                onClick={() => {
                  setFavoritesOnly(!favoritesOnly);
                  setPage(0);
                }}
                sx={{
                  minWidth: 160,
                  borderColor: '#d1d5db',
                  color: favoritesOnly ? '#ffffff' : '#6b7280',
                  bgcolor: favoritesOnly ? '#ef4444' : 'transparent',
                  '&:hover': {
                    borderColor: '#9ca3af',
                    bgcolor: favoritesOnly ? '#dc2626' : '#f9fafb',
                  },
                }}
              >
                {favoritesOnly ? 'Favorites' : 'All Images'}
              </Button>
            )}
          </Stack>
          <Typography variant="body2" sx={{ color: '#6b7280', mt: 1.5 }}>
            {loading
              ? 'Loading...'
              : total > 0
              ? `${total} image${total !== 1 ? 's' : ''} found`
              : 'No images found'}
          </Typography>
        </Box>

        {/* Error State */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && assets.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        ) : assets.length === 0 ? (
          /* Empty State */
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Collections sx={{ fontSize: 64, color: '#d1d5db', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#6b7280', mb: 1 }}>
              {searchQuery ? 'No images found matching your search.' : 'No images in your asset library yet.'}
            </Typography>
            <Typography variant="body2" sx={{ color: '#9ca3af' }}>
              {searchQuery ? 'Try a different search term.' : 'Generate some images first to see them here.'}
            </Typography>
          </Box>
        ) : (
          /* Image Grid */
          <Box
            sx={{
              maxHeight: 'calc(90vh - 280px)',
              overflowY: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                backgroundColor: '#f1f5f9',
              },
              '&::-webkit-scrollbar-thumb': {
                backgroundColor: '#cbd5e1',
                borderRadius: '4px',
                '&:hover': {
                  backgroundColor: '#94a3b8',
                },
              },
            }}
          >
            <Grid container spacing={2}>
              {assets.map((asset) => (
                <Grid item xs={6} sm={4} md={3} key={asset.id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      position: 'relative',
                      border: selectedAsset?.id === asset.id ? '2px solid #FF0000' : '1px solid #e5e7eb',
                      borderRadius: 2,
                      overflow: 'hidden',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        boxShadow: 4,
                        borderColor: selectedAsset?.id === asset.id ? '#FF0000' : '#9ca3af',
                        transform: 'translateY(-2px)',
                      },
                    }}
                    onClick={() => handleAssetClick(asset)}
                  >
                    {/* Image */}
                    <Box sx={{ position: 'relative', paddingTop: '100%' }}>
                      {loadingImages.has(asset.id) ? (
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            bgcolor: '#f3f4f6',
                          }}
                        >
                          <CircularProgress size={24} />
                        </Box>
                      ) : (
                        <CardMedia
                          component="img"
                          image={imageBlobUrls.get(asset.id) || asset.file_url}
                          alt={asset.title || 'Asset'}
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            bgcolor: '#f3f4f6', // Fallback background while loading
                          }}
                          onError={(e) => {
                            // Fallback if image fails to load
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                          }}
                        />
                      )}

                      {/* Selected Indicator */}
                      {selectedAsset?.id === asset.id && (
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            bgcolor: '#FF0000',
                            borderRadius: '50%',
                            p: 0.5,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                          }}
                        >
                          <CheckCircle sx={{ color: 'white', fontSize: 20 }} />
                        </Box>
                      )}

                      {/* Favorite Button */}
                      <Tooltip title={asset.is_favorite ? 'Remove from favorites' : 'Add to favorites'}>
                        <IconButton
                          size="small"
                          sx={{
                            position: 'absolute',
                            top: 8,
                            left: 8,
                            bgcolor: 'rgba(255, 255, 255, 0.9)',
                            '&:hover': { bgcolor: 'white' },
                            transition: 'all 0.2s',
                          }}
                          onClick={(e) => handleFavoriteToggle(asset.id, e)}
                        >
                          {asset.is_favorite ? (
                            <Favorite sx={{ color: '#ef4444', fontSize: 18 }} />
                          ) : (
                            <FavoriteBorder sx={{ color: '#6b7280', fontSize: 18 }} />
                          )}
                        </IconButton>
                      </Tooltip>
                    </Box>

                    {/* Title */}
                    {asset.title && (
                      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                        <Typography
                          variant="caption"
                          sx={{
                            display: 'block',
                            fontWeight: 500,
                            color: '#111827',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                          title={asset.title}
                        >
                          {asset.title}
                        </Typography>
                        {asset.source_module && (
                          <Typography
                            variant="caption"
                            sx={{
                              display: 'block',
                              color: '#6b7280',
                              fontSize: '0.7rem',
                              mt: 0.25,
                            }}
                          >
                            {asset.source_module.replace('_', ' ')}
                          </Typography>
                        )}
                      </CardContent>
                    )}
                  </Card>
                </Grid>
              ))}
            </Grid>

            {/* Load More (if needed) */}
            {total > (page + 1) * pageSize && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Button variant="outlined" onClick={() => setPage(page + 1)} disabled={loading}>
                  {loading ? <CircularProgress size={20} /> : 'Load More'}
                </Button>
              </Box>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, backgroundColor: '#ffffff', borderTop: '1px solid #e5e7eb' }}>
        <Button onClick={handleClose} sx={{ color: '#6b7280' }}>
          Cancel
        </Button>
        <Button
          variant="contained"
          color="error"
          onClick={handleSelect}
          disabled={!selectedAsset}
          startIcon={selectedAsset ? <CheckCircle /> : undefined}
          sx={{
            minWidth: 140,
            '&:disabled': {
              backgroundColor: '#e5e7eb',
              color: '#9ca3af',
            },
          }}
        >
          Select Image
        </Button>
      </DialogActions>
    </Dialog>
  );
};

