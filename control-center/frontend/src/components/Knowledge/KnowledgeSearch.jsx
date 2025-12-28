import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Search as SearchIcon, Clear as ClearIcon } from '@mui/icons-material';

/**
 * Search and filter bar for Knowledge Base
 */
export const KnowledgeSearch = ({ onSearch, onFilterChange, disabled }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [fileType, setFileType] = useState('');
  const [sortBy, setSortBy] = useState('name');

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      if (onSearch) {
        onSearch(searchQuery);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery, onSearch]);

  // Notify parent of filter changes
  useEffect(() => {
    if (onFilterChange) {
      onFilterChange({ type: fileType, sort: sortBy });
    }
  }, [fileType, sortBy, onFilterChange]);

  const handleClearSearch = () => {
    setSearchQuery('');
  };

  return (
    <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
      {/* Search Field */}
      <TextField
        size="small"
        placeholder="Search files..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        disabled={disabled}
        sx={{ flex: 1, minWidth: 200 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: searchQuery && (
            <InputAdornment position="end">
              <IconButton
                size="small"
                onClick={handleClearSearch}
                edge="end"
                aria-label="clear search"
              >
                <ClearIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      {/* Type Filter */}
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id="file-type-label">Type</InputLabel>
        <Select
          labelId="file-type-label"
          id="file-type-select"
          value={fileType}
          label="Type"
          onChange={(e) => setFileType(e.target.value)}
          disabled={disabled}
        >
          <MenuItem value="">All Types</MenuItem>
          <MenuItem value="document">Documents</MenuItem>
          <MenuItem value="video">Videos</MenuItem>
          <MenuItem value="transcript">Transcripts</MenuItem>
          <MenuItem value="code">Code</MenuItem>
          <MenuItem value="pdf">PDFs</MenuItem>
          <MenuItem value="image">Images</MenuItem>
        </Select>
      </FormControl>

      {/* Sort By */}
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel id="sort-by-label">Sort By</InputLabel>
        <Select
          labelId="sort-by-label"
          id="sort-by-select"
          value={sortBy}
          label="Sort By"
          onChange={(e) => setSortBy(e.target.value)}
          disabled={disabled}
        >
          <MenuItem value="name">Name (A-Z)</MenuItem>
          <MenuItem value="name_desc">Name (Z-A)</MenuItem>
          <MenuItem value="date">Date (Oldest)</MenuItem>
          <MenuItem value="date_desc">Date (Newest)</MenuItem>
          <MenuItem value="size">Size (Smallest)</MenuItem>
          <MenuItem value="size_desc">Size (Largest)</MenuItem>
          <MenuItem value="type">Type</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );
};

export default KnowledgeSearch;
