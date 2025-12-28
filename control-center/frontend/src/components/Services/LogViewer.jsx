import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  IconButton,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Close as CloseIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { servicesAPI } from '../../services/api';

export const LogViewer = ({ serviceName, open, onClose }) => {
  const [logs, setLogs] = useState('');
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const logContainerRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (open && serviceName) {
      fetchLogs();
    }
  }, [open, serviceName]);

  useEffect(() => {
    if (autoRefresh && open) {
      intervalRef.current = setInterval(() => {
        fetchLogs();
      }, 2000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh, open]);

  const fetchLogs = async () => {
    if (!serviceName) return;
    setLoading(true);
    try {
      const response = await servicesAPI.getLogs(serviceName, 500);
      setLogs(response.data.logs || 'No logs available');
      // Auto-scroll to bottom
      if (logContainerRef.current) {
        logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
      }
    } catch (err) {
      console.error('Failed to fetch logs:', err);
      setLogs(`Error fetching logs: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${serviceName}-logs-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLogs = searchTerm
    ? logs.split('\n').filter(line => line.toLowerCase().includes(searchTerm.toLowerCase())).join('\n')
    : logs;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            Logs: {serviceName}
          </Typography>
          <IconButton onClick={onClose} size="small" aria-label="Close log viewer">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Box display="flex" gap={2} mb={2} alignItems="center">
          <TextField
            size="small"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
            sx={{ flex: 1 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto-refresh"
          />
          <IconButton onClick={fetchLogs} disabled={loading} color="primary" aria-label="Refresh logs">
            <RefreshIcon />
          </IconButton>
          <IconButton onClick={handleDownload} color="primary" aria-label="Download logs">
            <DownloadIcon />
          </IconButton>
        </Box>

        <Box
          ref={logContainerRef}
          sx={{
            bgcolor: 'grey.900',
            color: 'grey.100',
            p: 2,
            borderRadius: 1,
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            minHeight: 400,
            maxHeight: 600,
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-all',
          }}
        >
          {filteredLogs || 'No logs available'}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default LogViewer;
