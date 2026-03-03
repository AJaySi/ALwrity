import React from 'react';
import {
  Grid,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Search, CalendarToday } from '@mui/icons-material';

interface AssetFiltersProps {
  idSearch: string;
  setIdSearch: (value: string) => void;
  modelSearch: string;
  setModelSearch: (value: string) => void;
  dateFilter: string;
  setDateFilter: (value: string) => void;
  statusFilter: string;
  setStatusFilter: (value: string) => void;
  filterType: string;
  setFilterType: (value: string) => void;
  searchQuery: string;
  setSearchQuery: (value: string) => void;
  onSearch: (value: string) => void;
}

export const AssetFilters: React.FC<AssetFiltersProps> = ({
  idSearch,
  setIdSearch,
  modelSearch,
  setModelSearch,
  dateFilter,
  setDateFilter,
  statusFilter,
  setStatusFilter,
  filterType,
  setFilterType,
  searchQuery,
  setSearchQuery,
  onSearch,
}) => {
  return (
    <>
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
      
      <TextField
        fullWidth
        size="small"
        placeholder="Search assets (ID, title, tags)..."
        value={searchQuery}
        onChange={(e) => {
          onSearch(e.target.value);
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search sx={{ color: 'rgba(255,255,255,0.6)', fontSize: 18 }} />
            </InputAdornment>
          ),
        }}
        sx={{
          mt: 2,
          '& .MuiOutlinedInput-root': {
            background: 'rgba(15,23,42,0.5)',
            color: '#f8fafc',
          },
        }}
      />
    </>
  );
};
