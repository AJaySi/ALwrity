import React, { useState, useMemo, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  InputAdornment,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Chip,
  IconButton,
  Stack,
  Button,
  ButtonGroup,
  Tabs,
  Tab,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Search,
  GridView,
  ViewList,
  Favorite,
  FavoriteBorder,
  Download,
  Share,
  Delete,
  Image as ImageIcon,
  VideoLibrary,
  TextFields,
  AudioFile,
  Collections,
  History,
  Star,
  MoreVert,
  Upload,
  CalendarToday,
  FilterList,
  CheckCircle,
  HourglassEmpty,
  Error as ErrorIcon,
  Refresh,
} from '@mui/icons-material';
import { ImageStudioLayout } from './ImageStudioLayout';
import { useContentAssets, AssetFilters, ContentAsset } from '../../hooks/useContentAssets';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const getStatusIcon = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return <CheckCircle sx={{ color: '#10b981', fontSize: 18 }} />;
    case 'processing':
      return <HourglassEmpty sx={{ color: '#f59e0b', fontSize: 18 }} />;
    case 'failed':
      return <ErrorIcon sx={{ color: '#ef4444', fontSize: 18 }} />;
    default:
      return <HourglassEmpty sx={{ color: '#6b7280', fontSize: 18 }} />;
  }
};

const getStatusChip = (status: string) => {
  const statusLower = status?.toLowerCase() || 'completed';
  const colors: Record<string, { bg: string; color: string }> = {
    completed: { bg: 'rgba(16,185,129,0.2)', color: '#10b981' },
    processing: { bg: 'rgba(245,158,11,0.2)', color: '#f59e0b' },
    failed: { bg: 'rgba(239,68,68,0.2)', color: '#ef4444' },
    pending: { bg: 'rgba(107,114,128,0.2)', color: '#6b7280' },
  };
  const style = colors[statusLower] || colors.completed;
  return (
    <Chip
      icon={getStatusIcon(status)}
      label={statusLower}
      size="small"
      sx={{
        background: style.bg,
        color: style.color,
        fontWeight: 600,
        textTransform: 'capitalize',
      }}
    />
  );
};

export const AssetLibrary: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [idSearch, setIdSearch] = useState('');
  const [modelSearch, setModelSearch] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list'); // Default to list like reference
  const [tabValue, setTabValue] = useState(0);
  const [filterType, setFilterType] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedAssets, setSelectedAssets] = useState<Set<number>>(new Set());
  const [page, setPage] = useState(0);
  const [pageSize] = useState(50);
  const [anchorEl, setAnchorEl] = useState<{ [key: number]: HTMLElement | null }>({});
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(0);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Build filters based on UI state
  const filters: AssetFilters = useMemo(() => {
    const baseFilters: AssetFilters = {
      limit: pageSize,
      offset: page * pageSize,
    };

    // Combine all search terms
    const searchTerms: string[] = [];
    if (debouncedSearch) searchTerms.push(debouncedSearch);
    if (idSearch) searchTerms.push(idSearch);
    if (modelSearch) searchTerms.push(modelSearch);
    
    if (searchTerms.length > 0) {
      baseFilters.search = searchTerms.join(' ');
    }

    if (filterType !== 'all') {
      if (filterType === 'images') baseFilters.asset_type = 'image';
      else if (filterType === 'videos') baseFilters.asset_type = 'video';
      else if (filterType === 'audio') baseFilters.asset_type = 'audio';
      else if (filterType === 'text') baseFilters.asset_type = 'text';
      else if (filterType === 'favorites') baseFilters.favorites_only = true;
    }

    if (tabValue === 1) {
      baseFilters.favorites_only = true;
    }

    return baseFilters;
  }, [debouncedSearch, idSearch, modelSearch, filterType, tabValue, page, pageSize]);

  const { assets, loading, error, total, toggleFavorite, deleteAsset, trackUsage, refetch } = useContentAssets(filters);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(0);
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedAssets(new Set(assets.map(a => a.id)));
    } else {
      setSelectedAssets(new Set());
    }
  };

  const handleSelectAsset = (assetId: number, checked: boolean) => {
    const newSelected = new Set(selectedAssets);
    if (checked) {
      newSelected.add(assetId);
    } else {
      newSelected.delete(assetId);
    }
    setSelectedAssets(newSelected);
  };

  const handleBulkDelete = async () => {
    if (selectedAssets.size === 0) return;
    if (!window.confirm(`Delete ${selectedAssets.size} selected asset(s)?`)) return;
    
    try {
      await Promise.all(Array.from(selectedAssets).map(id => deleteAsset(id)));
      setSelectedAssets(new Set());
      setSnackbar({ open: true, message: `${selectedAssets.size} asset(s) deleted`, severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to delete assets', severity: 'error' });
    }
  };

  const handleBulkDownload = async () => {
    if (selectedAssets.size === 0) return;
    
    try {
      const selectedAssetsData = assets.filter(a => selectedAssets.has(a.id));
      await Promise.all(selectedAssetsData.map(asset => trackUsage(asset.id, 'download')));
      
      // Open each in new tab
      selectedAssetsData.forEach(asset => {
        window.open(asset.file_url, '_blank');
      });
      
      setSnackbar({ open: true, message: `Downloading ${selectedAssets.size} asset(s)`, severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to download assets', severity: 'error' });
    }
  };

  const handleFavorite = async (assetId: number) => {
    try {
      await toggleFavorite(assetId);
      const asset = assets.find(a => a.id === assetId);
      setSnackbar({
        open: true,
        message: asset?.is_favorite ? 'Removed from favorites' : 'Added to favorites',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to update favorite', severity: 'error' });
    }
  };

  const handleDelete = async (assetId: number) => {
    if (!window.confirm('Are you sure you want to delete this asset?')) return;
    try {
      await deleteAsset(assetId);
      setSnackbar({ open: true, message: 'Asset deleted', severity: 'success' });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to delete asset', severity: 'error' });
    }
  };

  const handleDownload = async (asset: ContentAsset) => {
    try {
      await trackUsage(asset.id, 'download');
      window.open(asset.file_url, '_blank');
    } catch (err) {
      console.error('Error downloading:', err);
    }
  };

  const handleShare = async (asset: ContentAsset) => {
    try {
      await trackUsage(asset.id, 'share');
      if (navigator.share) {
        await navigator.share({
          title: asset.title || asset.filename,
          text: asset.description,
          url: asset.file_url,
        });
      } else {
        await navigator.clipboard.writeText(asset.file_url);
        setSnackbar({ open: true, message: 'Link copied to clipboard', severity: 'success' });
      }
    } catch (err) {
      console.error('Error sharing:', err);
    }
  };

  const handleMenuOpen = (assetId: number, event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl({ ...anchorEl, [assetId]: event.currentTarget });
  };

  const handleMenuClose = (assetId: number) => {
    setAnchorEl({ ...anchorEl, [assetId]: null });
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    } catch {
      return dateString;
    }
  };

  const getAssetPreview = (asset: ContentAsset) => {
    if (asset.asset_type === 'image') {
      return (
        <Box
          component="img"
          src={asset.file_url}
          alt={asset.title || asset.filename}
          sx={{
            width: 80,
            height: 80,
            objectFit: 'cover',
            borderRadius: 1,
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        />
      );
    } else if (asset.asset_type === 'video') {
      return (
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: 1,
            background: 'rgba(99,102,241,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <VideoLibrary sx={{ color: '#c7d2fe', fontSize: 32 }} />
        </Box>
      );
    } else if (asset.asset_type === 'audio') {
      return (
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: 1,
            background: 'rgba(59,130,246,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <AudioFile sx={{ color: '#93c5fd', fontSize: 32 }} />
        </Box>
      );
    } else {
      return (
        <Box
          sx={{
            width: 80,
            height: 80,
            borderRadius: 1,
            background: 'rgba(107,114,128,0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <TextFields sx={{ color: '#d1d5db', fontSize: 32 }} />
        </Box>
      );
    }
  };

  const filteredAssets = useMemo(() => {
    let filtered = assets;
    
    if (statusFilter !== 'all') {
      filtered = filtered.filter(a => (a.metadata?.status || 'completed') === statusFilter);
    }
    
    if (dateFilter) {
      const filterDate = new Date(dateFilter);
      filtered = filtered.filter(a => {
        const assetDate = new Date(a.created_at);
        return assetDate.toDateString() === filterDate.toDateString();
      });
    }
    
    return filtered;
  }, [assets, statusFilter, dateFilter]);

  return (
    <ImageStudioLayout>
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1600,
          mx: 'auto',
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          background: 'rgba(15,23,42,0.72)',
          p: { xs: 3, md: 4 },
          backdropFilter: 'blur(25px)',
        }}
      >
        <Stack spacing={3}>
          {/* Header */}
          <Box>
            <Typography
              variant="h3"
              fontWeight={800}
              sx={{
                background: 'linear-gradient(120deg,#ede9fe,#c7d2fe)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1,
              }}
            >
              Asset Library
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Unified content archive for all ALwrity tools: Story Writer, Image Studio, Blog Writer, LinkedIn, Facebook, SEO Tools, and more.
            </Typography>
          </Box>

          {/* Reminder Banner */}
          <Alert
            severity="warning"
            icon={<Star />}
            sx={{
              background: 'rgba(245,158,11,0.1)',
              border: '1px solid rgba(245,158,11,0.3)',
              color: '#fbbf24',
            }}
          >
            <Typography variant="body2" fontWeight={600}>
              Your outputs are stored permanently. Download and organize them for easy access across all your projects.
            </Typography>
          </Alert>

          <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)' }} />

          {/* Advanced Search and Filters */}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                placeholder="ID"
                value={idSearch}
                onChange={e => setIdSearch(e.target.value)}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    background: 'rgba(15,23,42,0.5)',
                    color: '#f8fafc',
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search model..."
                value={modelSearch}
                onChange={e => setModelSearch(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search sx={{ color: 'rgba(255,255,255,0.6)', fontSize: 18 }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    background: 'rgba(15,23,42,0.5)',
                    color: '#f8fafc',
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                type="date"
                placeholder="Pick a date"
                value={dateFilter}
                onChange={e => setDateFilter(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <CalendarToday sx={{ color: 'rgba(255,255,255,0.6)', fontSize: 18 }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    background: 'rgba(15,23,42,0.5)',
                    color: '#f8fafc',
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel sx={{ color: 'rgba(255,255,255,0.6)' }}>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={e => setStatusFilter(e.target.value)}
                  label="Status"
                  sx={{
                    background: 'rgba(15,23,42,0.5)',
                    color: '#f8fafc',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255,255,255,0.2)',
                    },
                  }}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="processing">Processing</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel sx={{ color: 'rgba(255,255,255,0.6)' }}>Type</InputLabel>
                <Select
                  value={filterType}
                  onChange={e => setFilterType(e.target.value)}
                  label="Type"
                  sx={{
                    background: 'rgba(15,23,42,0.5)',
                    color: '#f8fafc',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255,255,255,0.2)',
                    },
                  }}
                >
                  <MenuItem value="all">All Assets</MenuItem>
                  <MenuItem value="images">Images</MenuItem>
                  <MenuItem value="videos">Videos</MenuItem>
                  <MenuItem value="audio">Audio</MenuItem>
                  <MenuItem value="text">Text</MenuItem>
                  <MenuItem value="favorites">Favorites</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Bulk Actions */}
          {selectedAssets.size > 0 && (
            <Box
              sx={{
                display: 'flex',
                gap: 2,
                alignItems: 'center',
                p: 2,
                background: 'rgba(99,102,241,0.1)',
                borderRadius: 2,
                border: '1px solid rgba(99,102,241,0.3)',
              }}
            >
              <Typography variant="body2" sx={{ color: '#c7d2fe' }}>
                {selectedAssets.size} selected
              </Typography>
              <Button
                size="small"
                variant="contained"
                startIcon={<Download />}
                onClick={handleBulkDownload}
                sx={{
                  background: 'rgba(59,130,246,0.3)',
                  '&:hover': { background: 'rgba(59,130,246,0.5)' },
                }}
              >
                Download
              </Button>
              <Button
                size="small"
                variant="contained"
                startIcon={<Delete />}
                onClick={handleBulkDelete}
                sx={{
                  background: 'rgba(239,68,68,0.3)',
                  '&:hover': { background: 'rgba(239,68,68,0.5)' },
                }}
              >
                Delete
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => setSelectedAssets(new Set())}
                sx={{ ml: 'auto', color: 'rgba(255,255,255,0.6)' }}
              >
                Clear
              </Button>
            </Box>
          )}

          {/* Action Buttons */}
          <Stack direction="row" spacing={2} alignItems="center">
            <Button
              variant="contained"
              startIcon={<Download />}
              onClick={handleBulkDownload}
              disabled={selectedAssets.size === 0}
              sx={{
                background: 'linear-gradient(90deg,#3b82f6,#2563eb)',
                textTransform: 'none',
              }}
            >
              Download
            </Button>
            <Button
              variant="contained"
              startIcon={<Delete />}
              onClick={handleBulkDelete}
              disabled={selectedAssets.size === 0}
              sx={{
                background: 'linear-gradient(90deg,#ef4444,#dc2626)',
                textTransform: 'none',
              }}
            >
              Delete
            </Button>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => refetch()}
              sx={{ ml: 'auto', textTransform: 'none' }}
            >
              Reset
            </Button>
            <Button
              variant="contained"
              startIcon={<Search />}
              onClick={() => refetch()}
              sx={{
                background: 'linear-gradient(90deg,#6366f1,#4f46e5)',
                textTransform: 'none',
              }}
            >
              Search
            </Button>
            <ButtonGroup>
              <Button
                variant={viewMode === 'grid' ? 'contained' : 'outlined'}
                onClick={() => setViewMode('grid')}
                startIcon={<GridView />}
                size="small"
              >
                Grid
              </Button>
              <Button
                variant={viewMode === 'list' ? 'contained' : 'outlined'}
                onClick={() => setViewMode('list')}
                startIcon={<ViewList />}
                size="small"
              >
                List
              </Button>
            </ButtonGroup>
          </Stack>

          {/* Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'rgba(255,255,255,0.08)' }}>
            <Tabs value={tabValue} onChange={handleTabChange} sx={{ '& .MuiTab-root': { color: 'rgba(255,255,255,0.6)' } }}>
              <Tab icon={<Collections />} iconPosition="start" label="All Assets" />
              <Tab icon={<Favorite />} iconPosition="start" label="Favorites" />
              <Tab icon={<History />} iconPosition="start" label="Recent" />
              <Tab icon={<Star />} iconPosition="start" label="Collections" />
            </Tabs>
          </Box>

          {/* Content */}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : filteredAssets.length === 0 ? (
            <Box
              sx={{
                textAlign: 'center',
                py: 8,
                color: 'rgba(255,255,255,0.5)',
              }}
            >
              <ImageIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
              <Typography variant="h6" gutterBottom>
                No assets found
              </Typography>
              <Typography variant="body2">
                Generated content from all ALwrity tools will appear here.
              </Typography>
            </Box>
          ) : viewMode === 'list' ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedAssets.size === filteredAssets.length && filteredAssets.length > 0}
                        indeterminate={selectedAssets.size > 0 && selectedAssets.size < filteredAssets.length}
                        onChange={e => handleSelectAll(e.target.checked)}
                        sx={{ color: 'rgba(255,255,255,0.6)' }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>ID</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>Model</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>Outputs</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>Created</TableCell>
                    <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAssets.map(asset => (
                    <TableRow
                      key={asset.id}
                      sx={{
                        '&:hover': { background: 'rgba(255,255,255,0.05)' },
                        cursor: 'pointer',
                      }}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedAssets.has(asset.id)}
                          onChange={e => handleSelectAsset(asset.id, e.target.checked)}
                          onClick={e => e.stopPropagation()}
                          sx={{ color: 'rgba(255,255,255,0.6)' }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#c7d2fe',
                            fontFamily: 'monospace',
                            fontSize: '0.75rem',
                            cursor: 'pointer',
                            '&:hover': { textDecoration: 'underline' },
                          }}
                          onClick={() => {
                            navigator.clipboard.writeText(String(asset.id));
                            setSnackbar({ open: true, message: 'ID copied', severity: 'success' });
                          }}
                        >
                          {String(asset.id).slice(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            color: '#f8fafc',
                            cursor: 'pointer',
                            '&:hover': { textDecoration: 'underline' },
                          }}
                        >
                          {asset.model || asset.provider || asset.source_module.replace(/_/g, ' ')}
                        </Typography>
                      </TableCell>
                      <TableCell>{getStatusChip(asset.metadata?.status || 'completed')}</TableCell>
                      <TableCell>{getAssetPreview(asset)}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>
                          {formatDate(asset.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={0.5}>
                          <Tooltip title="Upload">
                            <IconButton size="small" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                              <Upload fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Download">
                            <IconButton
                              size="small"
                              onClick={() => handleDownload(asset)}
                              sx={{ color: 'rgba(255,255,255,0.6)' }}
                            >
                              <Download fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="More">
                            <IconButton
                              size="small"
                              onClick={e => handleMenuOpen(asset.id, e)}
                              sx={{ color: 'rgba(255,255,255,0.6)' }}
                            >
                              <MoreVert fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Menu
                            anchorEl={anchorEl[asset.id]}
                            open={Boolean(anchorEl[asset.id])}
                            onClose={() => handleMenuClose(asset.id)}
                          >
                            <MenuItem onClick={() => { handleFavorite(asset.id); handleMenuClose(asset.id); }}>
                              <ListItemIcon>
                                {asset.is_favorite ? <Favorite fontSize="small" /> : <FavoriteBorder fontSize="small" />}
                              </ListItemIcon>
                              <ListItemText>{asset.is_favorite ? 'Remove Favorite' : 'Add Favorite'}</ListItemText>
                            </MenuItem>
                            <MenuItem onClick={() => { handleShare(asset); handleMenuClose(asset.id); }}>
                              <ListItemIcon>
                                <Share fontSize="small" />
                              </ListItemIcon>
                              <ListItemText>Share</ListItemText>
                            </MenuItem>
                            <MenuItem
                              onClick={() => {
                                handleDelete(asset.id);
                                handleMenuClose(asset.id);
                              }}
                              sx={{ color: '#ef4444' }}
                            >
                              <ListItemIcon>
                                <Delete fontSize="small" sx={{ color: '#ef4444' }} />
                              </ListItemIcon>
                              <ListItemText>Delete</ListItemText>
                            </MenuItem>
                          </Menu>
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Grid container spacing={3}>
              {filteredAssets.map(asset => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={asset.id}>
                  <Card
                    sx={{
                      background: 'rgba(15,23,42,0.5)',
                      border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: 3,
                      overflow: 'hidden',
                      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 10px 25px rgba(124,58,237,0.25)',
                      },
                    }}
                  >
                    <Box sx={{ position: 'relative', aspectRatio: asset.asset_type === 'video' ? '16/9' : '1' }}>
                      {asset.asset_type === 'image' ? (
                        <CardMedia
                          component="img"
                          image={asset.file_url}
                          alt={asset.title || asset.filename}
                          sx={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                        />
                      ) : asset.asset_type === 'video' ? (
                        <Box
                          component="video"
                          src={asset.file_url}
                          controls
                          sx={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                          }}
                        />
                      ) : (
                        <Box
                          sx={{
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            background: 'rgba(99,102,241,0.2)',
                            color: '#c7d2fe',
                          }}
                        >
                          {asset.asset_type === 'audio' ? <AudioFile /> : <TextFields />}
                        </Box>
                      )}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          display: 'flex',
                          gap: 1,
                        }}
                      >
                        <IconButton
                          size="small"
                          onClick={() => handleFavorite(asset.id)}
                          sx={{
                            background: 'rgba(15,23,42,0.8)',
                            color: asset.is_favorite ? '#fbbf24' : 'rgba(255,255,255,0.6)',
                            '&:hover': { background: 'rgba(15,23,42,0.95)' },
                          }}
                        >
                          {asset.is_favorite ? <Favorite /> : <FavoriteBorder />}
                        </IconButton>
                      </Box>
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 8,
                          left: 8,
                        }}
                      >
                        <Chip
                          label={asset.source_module.replace(/_/g, ' ')}
                          size="small"
                          sx={{
                            background: 'rgba(15,23,42,0.8)',
                            color: '#c7d2fe',
                            fontSize: '0.7rem',
                          }}
                        />
                      </Box>
                    </Box>
                    <CardContent>
                      <Typography variant="subtitle2" fontWeight={600} gutterBottom noWrap>
                        {asset.title || asset.filename}
                      </Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mb: 1 }}>
                        {getStatusChip(asset.metadata?.status || 'completed')}
                        <Chip
                          label={asset.asset_type}
                          size="small"
                          sx={{ background: 'rgba(99,102,241,0.2)', color: '#c7d2fe' }}
                        />
                        {asset.cost > 0 && (
                          <Chip
                            label={`$${asset.cost.toFixed(2)}`}
                            size="small"
                            sx={{ background: 'rgba(16,185,129,0.2)', color: '#6ee7b7' }}
                          />
                        )}
                      </Stack>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 1 }}>
                        {formatDate(asset.created_at)}
                      </Typography>
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <IconButton
                          size="small"
                          onClick={() => handleDownload(asset)}
                          sx={{ color: 'rgba(255,255,255,0.6)' }}
                        >
                          <Download />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleShare(asset)}
                          sx={{ color: 'rgba(255,255,255,0.6)' }}
                        >
                          <Share />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(asset.id)}
                          sx={{ color: 'rgba(255,255,255,0.6)' }}
                        >
                          <Delete />
                        </IconButton>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}

          {/* Pagination */}
          {total > pageSize && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4, gap: 2, alignItems: 'center' }}>
              <Button
                disabled={page === 0}
                onClick={() => setPage(p => Math.max(0, p - 1))}
                sx={{ color: 'rgba(255,255,255,0.8)' }}
              >
                Previous
              </Button>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                Page {page + 1} of {Math.ceil(total / pageSize)} ({total} total)
              </Typography>
              <Button
                disabled={(page + 1) * pageSize >= total}
                onClick={() => setPage(p => p + 1)}
                sx={{ color: 'rgba(255,255,255,0.8)' }}
              >
                Next
              </Button>
            </Box>
          )}

          <Snackbar
            open={snackbar.open}
            autoHideDuration={3000}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
              {snackbar.message}
            </Alert>
          </Snackbar>
        </Stack>
      </Paper>
    </ImageStudioLayout>
  );
};
