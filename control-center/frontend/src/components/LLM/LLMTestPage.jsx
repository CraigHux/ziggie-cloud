import React, { useState, useEffect, useContext } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack
} from '@mui/material';
import { AuthContext } from '../../contexts/AuthContext';

const API_URL = 'http://127.0.0.1:54112/api/llm';

function LLMTestPage() {
  const { user } = useContext(AuthContext);
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('llama3.2');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);
  const [models, setModels] = useState([]);

  // Fetch LLM status on mount
  useEffect(() => {
    fetchStatus();
    fetchModels();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/status`);
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      console.error('Failed to fetch LLM status:', err);
    }
  };

  const fetchModels = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/models`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await res.json();
      setModels(data.models || []);
    } catch (err) {
      console.error('Failed to fetch models:', err);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse('');

    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          model: model,
          prompt: prompt,
          stream: false,
          temperature: 0.7
        })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to generate text');
      }

      const data = await res.json();
      setResponse(data.response || 'No response');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setPrompt('');
    setResponse('');
    setError(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        LLM Test Interface
      </Typography>

      {/* Status Banner */}
      {status && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: status.status === 'online' ? 'success.dark' : 'error.dark' }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Chip
              label={status.status.toUpperCase()}
              color={status.status === 'online' ? 'success' : 'error'}
              size="small"
            />
            <Typography variant="body2">
              Service: {status.service} | Version: {status.version?.version || 'N/A'}
            </Typography>
          </Stack>
        </Paper>
      )}

      {/* Model Selection */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Model</InputLabel>
          <Select
            value={model}
            label="Model"
            onChange={(e) => setModel(e.target.value)}
          >
            <MenuItem value="llama3.2">llama3.2 (3B - Fast)</MenuItem>
            <MenuItem value="mistral">mistral (7B - Balanced)</MenuItem>
            <MenuItem value="codellama:7b">codellama:7b (7B - Code)</MenuItem>
          </Select>
        </FormControl>

        {models.length > 0 && (
          <Typography variant="caption" color="text.secondary">
            Available models: {models.map(m => m.name).join(', ')}
          </Typography>
        )}
      </Paper>

      {/* Prompt Input */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Enter your prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Write a hello world function in Python"
          variant="outlined"
          sx={{ mb: 2 }}
        />

        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? 'Generating...' : 'Generate'}
          </Button>
          <Button
            variant="outlined"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </Button>
        </Stack>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Response Display */}
      {response && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Response:
          </Typography>
          <Box
            sx={{
              bgcolor: 'background.default',
              p: 2,
              borderRadius: 1,
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}
          >
            {response}
          </Box>
        </Paper>
      )}

      {/* User Info */}
      {user && (
        <Paper sx={{ p: 2, mt: 3, bgcolor: 'background.default' }}>
          <Typography variant="caption" color="text.secondary">
            Logged in as: {user.username} | Role: {user.role}
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default LLMTestPage;
