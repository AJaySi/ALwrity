import React from 'react';
import { 
  Box, 
  TextField, 
  InputAdornment, 
  IconButton, 
  Typography, 
  Tooltip 
} from '@mui/material';
import { 
  Search as SearchIcon, 
  Clear as ClearIcon, 
  FilterList as FilterIcon 
} from '@mui/icons-material';
import { SearchContainer, CategoryChip } from './styled';
import { SearchFilterProps } from './types';

const SearchFilter: React.FC<SearchFilterProps> = ({
  searchQuery,
  onSearchChange,
  onClearSearch,
  selectedCategory,
  onCategoryChange,
  selectedSubCategory,
  onSubCategoryChange,
  toolCategories,
  theme,
  onCategoryClick
}) => {
  // Helper function to get tool count from a category
  const getToolCount = (category: any): number => {
    if ('tools' in category) {
      return category.tools.length;
    } else if ('subCategories' in category) {
      return Object.values(category.subCategories).reduce((total: number, subCat: any) => total + subCat.tools.length, 0);
    }
    return 0;
  };

  // Descriptions for category tooltips
  const categoryDescriptions: Record<string, string> = {
    'Generate Content': 'AI multimodal generators: Blog, Image, Audio, Video.',
    'SEO Tools': 'Enterprise SEO analysis, technical tools, and optimization utilities.',
    'Social Media': 'Platform writers for Facebook, LinkedIn, Twitter, Instagram, YouTube.',
    'Dashboards': 'Analytics dashboards: SEO, Social, Website, Strategy, and Calendar.'
  };
  return (
    <SearchContainer>
      {/* Single Row Layout: Search Input + Category Filters */}
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
        {/* Search Input - Takes available space */}
        <Box sx={{ flex: '1 1 300px', minWidth: '250px' }}>
          <TextField
            fullWidth
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.85)' }} />
                </InputAdornment>
              ),
              endAdornment: searchQuery && (
                <InputAdornment position="end">
                  <IconButton onClick={onClearSearch} size="small">
                    <ClearIcon sx={{ color: 'rgba(255, 255, 255, 0.85)' }} />
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: 'white',
                background: 'linear-gradient(135deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.08) 100%)',
                borderRadius: 2.5,
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.2), 0 6px 18px rgba(0,0,0,0.25)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.28)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.85)',
                },
                '& input::placeholder': {
                  color: 'rgba(255, 255, 255, 0.85)',
                  opacity: 1,
                },
              },
            }}
          />
        </Box>

        {/* Filter Icon */}
        <Tooltip title="Filter by category">
          <IconButton sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            <FilterIcon />
          </IconButton>
        </Tooltip>

        {/* Category Filter Chips - Inline with search */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
          <CategoryChip
            label="All Tools"
            onClick={() => onCategoryClick ? onCategoryClick(null, toolCategories) : onCategoryChange(null)}
            active={selectedCategory === null}
            theme={theme}
            toolCount={Object.values(toolCategories).reduce((total, category) => total + getToolCount(category), 0)}
          />
          {Object.keys(toolCategories).map((category) => {
            const cat = toolCategories[category] as any;
            const gradient = (cat && cat.gradient) || undefined;
            const desc = categoryDescriptions[category] || `Filter tools by ${category}.`;
            return (
              <Tooltip 
                key={category} 
                title={`${desc} Total tools: ${getToolCount(cat)}.`} 
                placement="top"
                arrow
                enterDelay={300}
              >
                <CategoryChip
                  label={category}
                  onClick={() => onCategoryClick ? onCategoryClick(category, cat) : onCategoryChange(category)}
                  active={selectedCategory === category}
                  theme={theme}
                  toolCount={getToolCount(cat)}
                  gradient={gradient}
                />
              </Tooltip>
            );
          })}
        </Box>
      </Box>

      {/* Sub-category Filter for SEO Tools */}
      {selectedCategory === 'SEO Tools' && 'subCategories' in toolCategories['SEO Tools'] && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1, fontWeight: 600 }}>
            Filter by sub-category:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <CategoryChip
              label="All SEO Tools"
              onClick={() => onSubCategoryChange(null)}
              active={selectedSubCategory === null}
              theme={theme}
            />
            {Object.keys(toolCategories['SEO Tools'].subCategories).map((subCategory) => (
              <CategoryChip
                key={subCategory}
                label={subCategory}
                onClick={() => onSubCategoryChange(subCategory)}
                active={selectedSubCategory === subCategory}
                theme={theme}
              />
            ))}
          </Box>
        </Box>
      )}
    </SearchContainer>
  );
};

export default SearchFilter; 