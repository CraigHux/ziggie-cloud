import React from 'react';
import {
  Paper,
  Box,
  TextField,
  ToggleButtonGroup,
  ToggleButton,
  IconButton,
  Tooltip,
  InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import ClearIcon from '@mui/icons-material/Clear';

const AgentFilters = ({ filters, onChange, onRefresh }) => {
  const handleLevelChange = (event, newLevel) => {
    if (newLevel !== null) {
      onChange({ ...filters, level: newLevel });
    }
  };

  const handleSearchChange = (event) => {
    onChange({ ...filters, search: event.target.value });
  };

  const handleClearSearch = () => {
    onChange({ ...filters, search: '' });
  };

  const handleClearFilters = () => {
    onChange({ level: 'all', search: '' });
  };

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        <TextField
          placeholder="Search agents..."
          value={filters.search}
          onChange={handleSearchChange}
          size="small"
          sx={{ flex: 1, minWidth: 200 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#FF8C42' }} />
              </InputAdornment>
            ),
            endAdornment: filters.search && (
              <InputAdornment position="end">
                <IconButton
                  size="small"
                  onClick={handleClearSearch}
                  aria-label="Clear search"
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <ToggleButtonGroup
          value={filters.level}
          exclusive
          onChange={handleLevelChange}
          size="small"
          sx={{
            '& .MuiToggleButton-root': {
              color: 'text.primary',
              '&.Mui-selected': {
                bgcolor: '#FF8C42',
                color: 'white',
                '&:hover': {
                  bgcolor: '#E67E3A',
                },
              },
            },
          }}
        >
          <ToggleButton value="all">All</ToggleButton>
          <ToggleButton value="l1">L1</ToggleButton>
          <ToggleButton value="l2">L2</ToggleButton>
          <ToggleButton value="l3">L3</ToggleButton>
        </ToggleButtonGroup>

        <Tooltip title="Refresh">
          <IconButton
            onClick={onRefresh}
            aria-label="Refresh agents"
            sx={{
              color: '#FF8C42',
              '&:hover': {
                bgcolor: 'rgba(255, 140, 66, 0.1)',
              },
            }}
          >
            <RefreshIcon />
          </IconButton>
        </Tooltip>

        {(filters.level !== 'all' || filters.search) && (
          <Tooltip title="Clear all filters">
            <IconButton
              onClick={handleClearFilters}
              aria-label="Clear all filters"
              sx={{
                color: 'error.main',
                '&:hover': {
                  bgcolor: 'rgba(231, 76, 60, 0.1)',
                },
              }}
            >
              <ClearIcon />
            </IconButton>
          </Tooltip>
        )}
      </Box>
    </Paper>
  );
};

export default AgentFilters;
