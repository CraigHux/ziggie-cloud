import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  InputAdornment,
  Alert,
} from '@mui/material';
import axios from 'axios';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DescriptionIcon from '@mui/icons-material/Description';
import FolderIcon from '@mui/icons-material/Folder';
import SearchIcon from '@mui/icons-material/Search';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import VerifiedIcon from '@mui/icons-material/Verified';

const API_BASE = 'http://127.0.0.1:54112';

const KnowledgeFilesTab = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/api/knowledge/files`);
      setFiles(response.data.files || []);
    } catch (err) {
      console.error('Error fetching KB files:', err);
      setError('Failed to load knowledge base files');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#2ECC71';
    if (confidence >= 0.6) return '#F39C12';
    return '#E74C3C';
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHrs / 24);

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHrs > 0) return `${diffHrs} hour${diffHrs > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  // Group files by category
  const groupedFiles = files.reduce((acc, file) => {
    const category = file.category || 'Uncategorized';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(file);
    return acc;
  }, {});

  // Filter files based on search
  const filteredGroups = Object.entries(groupedFiles).reduce((acc, [category, categoryFiles]) => {
    const filtered = categoryFiles.filter(
      (file) =>
        file.filename?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        file.title?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    if (filtered.length > 0) {
      acc[category] = filtered;
    }
    return acc;
  }, {});

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress sx={{ color: '#8B5CF6' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="Search knowledge base files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: '#8B5CF6' }} />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {Object.keys(filteredGroups).length === 0 ? (
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
            px: 3,
            bgcolor: 'background.paper',
            borderRadius: 2,
          }}
        >
          <FolderIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No files found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchQuery ? 'Try a different search query' : 'No knowledge base files available'}
          </Typography>
        </Box>
      ) : (
        Object.entries(filteredGroups).map(([category, categoryFiles]) => (
          <Accordion
            key={category}
            defaultExpanded
            sx={{
              mb: 2,
              '&:before': { display: 'none' },
              boxShadow: 2,
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                bgcolor: 'rgba(139, 92, 246, 0.05)',
                '&:hover': {
                  bgcolor: 'rgba(139, 92, 246, 0.1)',
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <FolderIcon sx={{ color: '#8B5CF6' }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {category}
                </Typography>
                <Chip
                  label={`${categoryFiles.length} file${categoryFiles.length !== 1 ? 's' : ''}`}
                  size="small"
                  sx={{
                    bgcolor: '#8B5CF6',
                    color: 'white',
                    fontWeight: 600,
                  }}
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <List>
                {categoryFiles.map((file, index) => (
                  <ListItem
                    key={index}
                    divider={index < categoryFiles.length - 1}
                    sx={{
                      '&:hover': {
                        bgcolor: 'rgba(139, 92, 246, 0.05)',
                      },
                    }}
                  >
                    <ListItemIcon>
                      <DescriptionIcon sx={{ color: '#8B5CF6' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Typography variant="body1" sx={{ fontWeight: 500 }}>
                            {file.filename || file.title || 'Unnamed File'}
                          </Typography>
                          {file.confidence !== undefined && (
                            <Chip
                              icon={<VerifiedIcon sx={{ fontSize: 14 }} />}
                              label={`${(file.confidence * 100).toFixed(0)}%`}
                              size="small"
                              sx={{
                                bgcolor: getConfidenceColor(file.confidence) + '20',
                                color: getConfidenceColor(file.confidence),
                                fontWeight: 600,
                                fontSize: '0.75rem',
                              }}
                            />
                          )}
                        </Box>
                      }
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 0.5 }}>
                          {file.created_at && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                              <Typography variant="caption" color="text.secondary">
                                {formatTimeAgo(file.created_at)}
                              </Typography>
                            </Box>
                          )}
                          {file.source && (
                            <Typography variant="caption" color="text.secondary">
                              Source: {file.source}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))
      )}
    </Box>
  );
};

export default KnowledgeFilesTab;