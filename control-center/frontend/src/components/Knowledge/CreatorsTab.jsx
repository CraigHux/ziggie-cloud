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
  Button,
  ButtonGroup,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
} from '@mui/material';
import axios from 'axios';
import PersonIcon from '@mui/icons-material/Person';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const API_BASE = 'http://127.0.0.1:54112';

const CreatorsTab = () => {
  const [creators, setCreators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scanningCreators, setScanningCreators] = useState(new Set());

  useEffect(() => {
    fetchCreators();
  }, []);

  const fetchCreators = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/api/knowledge/creators`);
      setCreators(response.data.creators || []);
    } catch (err) {
      console.error('Error fetching creators:', err);
      setError('Failed to load YouTube creators');
    } finally {
      setLoading(false);
    }
  };

  const handleScanCreator = async (creatorId) => {
    setScanningCreators((prev) => new Set(prev).add(creatorId));
    try {
      await axios.post(`${API_BASE}/api/knowledge/scan`, {
        creator_id: creatorId,
      });
      await fetchCreators();
    } catch (err) {
      console.error('Error scanning creator:', err);
    } finally {
      setScanningCreators((prev) => {
        const newSet = new Set(prev);
        newSet.delete(creatorId);
        return newSet;
      });
    }
  };

  const handleScanAll = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/api/knowledge/scan`, { scan_all: true });
      await fetchCreators();
    } catch (err) {
      console.error('Error scanning all creators:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return '#E74C3C';
      case 'high':
        return '#F39C12';
      case 'medium':
        return '#3498DB';
      default:
        return '#95A5A6';
    }
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHrs / 24);

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHrs > 0) return `${diffHrs} hour${diffHrs > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  // Group creators by priority
  const groupedCreators = creators.reduce((acc, creator) => {
    const priority = creator.priority || 'low';
    if (!acc[priority]) {
      acc[priority] = [];
    }
    acc[priority].push(creator);
    return acc;
  }, {});

  const priorityOrder = ['critical', 'high', 'medium', 'low'];

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
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ fontWeight: 600, color: '#8B5CF6' }}>
            YouTube Creators ({creators.length})
          </Typography>
          <ButtonGroup variant="outlined">
            <Button
              startIcon={<RefreshIcon />}
              onClick={fetchCreators}
              sx={{
                color: '#8B5CF6',
                borderColor: '#8B5CF6',
                '&:hover': {
                  borderColor: '#8B5CF6',
                  bgcolor: 'rgba(139, 92, 246, 0.1)',
                },
              }}
            >
              Refresh
            </Button>
            <Button
              startIcon={<PlayCircleOutlineIcon />}
              onClick={handleScanAll}
              sx={{
                color: '#8B5CF6',
                borderColor: '#8B5CF6',
                '&:hover': {
                  borderColor: '#8B5CF6',
                  bgcolor: 'rgba(139, 92, 246, 0.1)',
                },
              }}
            >
              Scan All
            </Button>
          </ButtonGroup>
        </Box>
      </Paper>

      {creators.length === 0 ? (
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
            px: 3,
            bgcolor: 'background.paper',
            borderRadius: 2,
          }}
        >
          <PersonIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No creators found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No YouTube creators configured for scanning
          </Typography>
        </Box>
      ) : (
        priorityOrder.map((priority) => {
          const priorityCreators = groupedCreators[priority] || [];
          if (priorityCreators.length === 0) return null;

          return (
            <Accordion
              key={priority}
              defaultExpanded={priority === 'critical' || priority === 'high'}
              sx={{
                mb: 2,
                '&:before': { display: 'none' },
                boxShadow: 2,
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                sx={{
                  bgcolor: `${getPriorityColor(priority)}10`,
                  '&:hover': {
                    bgcolor: `${getPriorityColor(priority)}20`,
                  },
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <Chip
                    label={priority.toUpperCase()}
                    size="small"
                    sx={{
                      bgcolor: getPriorityColor(priority),
                      color: 'white',
                      fontWeight: 700,
                      minWidth: 80,
                    }}
                  />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {priority.charAt(0).toUpperCase() + priority.slice(1)} Priority
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ({priorityCreators.length})
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {priorityCreators.map((creator, index) => {
                    const isScanning = scanningCreators.has(creator.id);
                    return (
                      <ListItem
                        key={creator.id || index}
                        divider={index < priorityCreators.length - 1}
                        secondaryAction={
                          <Tooltip title="Scan channel">
                            <IconButton
                              edge="end"
                              onClick={() => handleScanCreator(creator.id)}
                              disabled={isScanning}
                              aria-label={`Scan ${creator.name || creator.channel_name || \'creator\'} channel`}
                              sx={{
                                color: '#8B5CF6',
                                '&:hover': {
                                  bgcolor: 'rgba(139, 92, 246, 0.1)',
                                },
                              }}
                            >
                              {isScanning ? (
                                <CircularProgress size={24} sx={{ color: '#8B5CF6' }} />
                              ) : (
                                <PlayCircleOutlineIcon />
                              )}
                            </IconButton>
                          </Tooltip>
                        }
                        sx={{
                          '&:hover': {
                            bgcolor: 'rgba(139, 92, 246, 0.05)',
                          },
                        }}
                      >
                        <ListItemIcon>
                          <PersonIcon sx={{ color: getPriorityColor(priority) }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                                {creator.name || creator.channel_name || 'Unknown Creator'}
                              </Typography>
                              {creator.videos_scanned > 0 && (
                                <Chip
                                  icon={<CheckCircleIcon sx={{ fontSize: 14 }} />}
                                  label={`${creator.videos_scanned} videos`}
                                  size="small"
                                  sx={{
                                    bgcolor: '#2ECC7120',
                                    color: '#2ECC71',
                                    fontSize: '0.75rem',
                                  }}
                                />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 0.5 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                                <Typography variant="caption" color="text.secondary">
                                  Last scan: {formatTimeAgo(creator.last_scan)}
                                </Typography>
                              </Box>
                              {creator.channel_url && (
                                <Typography
                                  variant="caption"
                                  color="primary"
                                  component="a"
                                  href={creator.channel_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  sx={{ textDecoration: 'none' }}
                                >
                                  View Channel
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                    );
                  })}
                </List>
              </AccordionDetails>
            </Accordion>
          );
        })
      )}
    </Box>
  );
};

export default CreatorsTab;