import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Tabs,
  Tab,
} from '@mui/material';
import axios from 'axios';
import CloseIcon from '@mui/icons-material/Close';
import FolderIcon from '@mui/icons-material/Folder';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import DescriptionIcon from '@mui/icons-material/Description';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const API_BASE = 'http://127.0.0.1:54112';

const getLevelColor = (agentId) => {
  if (agentId?.startsWith('L1')) return '#E74C3C';
  if (agentId?.startsWith('L2')) return '#3498DB';
  if (agentId?.startsWith('L3')) return '#2ECC71';
  return '#FF8C42';
};

const AgentDetailModal = ({ agent, open, onClose }) => {
  const [tab, setTab] = useState(0);
  const [knowledgeFiles, setKnowledgeFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const levelColor = getLevelColor(agent.id);

  useEffect(() => {
    if (open && agent.id) {
      fetchKnowledgeFiles();
    }
  }, [open, agent.id]);

  const fetchKnowledgeFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE}/api/agents/${agent.id}/knowledge`, {
        timeout: 10000,
      });
      setKnowledgeFiles(response.data.files || []);
    } catch (error) {
      console.error('Error fetching knowledge files:', error);
      setError(error.message || 'Failed to load knowledge files');
      setKnowledgeFiles([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderTop: `6px solid ${levelColor}`,
        },
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              bgcolor: `${levelColor}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <SmartToyIcon sx={{ fontSize: 32, color: levelColor }} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <Chip
              label={agent.id}
              sx={{
                bgcolor: levelColor,
                color: 'white',
                fontWeight: 600,
                mb: 0.5,
              }}
            />
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              {agent.name || 'Unnamed Agent'}
            </Typography>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {agent.description && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" color="text.secondary">
              {agent.description}
            </Typography>
          </Box>
        )}

        <Tabs
          value={tab}
          onChange={(e, newValue) => setTab(newValue)}
          sx={{
            mb: 2,
            '& .MuiTab-root.Mui-selected': {
              color: levelColor,
            },
            '& .MuiTabs-indicator': {
              backgroundColor: levelColor,
            },
          }}
        >
          <Tab label="Overview" />
          <Tab label={`Knowledge Base (${knowledgeFiles.length})`} />
          {agent.sub_agents && agent.sub_agents > 0 && (
            <Tab label={`Sub-Agents (${agent.sub_agents})`} />
          )}
        </Tabs>

        {tab === 0 && (
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Agent Information
            </Typography>
            <List dense>
              {agent.category && (
                <ListItem>
                  <ListItemText
                    primary="Category"
                    secondary={agent.category}
                  />
                </ListItem>
              )}
              <ListItem>
                <ListItemText
                  primary="Level"
                  secondary={agent.id?.split('.')[0] || 'Unknown'}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Knowledge Files"
                  secondary={`${agent.knowledge_files || 0} files`}
                />
              </ListItem>
              {agent.sub_agents !== undefined && (
                <ListItem>
                  <ListItemText
                    primary="Sub-Agents"
                    secondary={`${agent.sub_agents} agents`}
                  />
                </ListItem>
              )}
            </List>
          </Box>
        )}

        {tab === 1 && (
          <Box>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress sx={{ color: levelColor }} />
              </Box>
            ) : error ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="error" gutterBottom>
                  Error loading knowledge files
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {error}
                </Typography>
                <Button
                  variant="outlined"
                  onClick={fetchKnowledgeFiles}
                  sx={{ color: levelColor, borderColor: levelColor }}
                >
                  Retry
                </Button>
              </Box>
            ) : knowledgeFiles.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <FolderIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography color="text.secondary">
                  No knowledge base files found
                </Typography>
              </Box>
            ) : (
              <List>
                {knowledgeFiles.map((file, index) => (
                  <ListItem key={index} divider={index < knowledgeFiles.length - 1}>
                    <ListItemIcon>
                      <DescriptionIcon sx={{ color: levelColor }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name || file.filename || `File ${index + 1}`}
                      secondary={
                        file.category
                          ? `Category: ${file.category}`
                          : file.size
                          ? `Size: ${(file.size / 1024).toFixed(1)} KB`
                          : 'No metadata'
                      }
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        )}

        {tab === 2 && agent.sub_agents && (
          <Box>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <AccountTreeIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography color="text.secondary">
                {agent.sub_agents} sub-agents available
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Sub-agent details coming soon
              </Typography>
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} sx={{ color: levelColor }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgentDetailModal;
