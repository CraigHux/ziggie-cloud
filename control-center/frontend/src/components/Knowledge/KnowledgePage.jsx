import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Alert,
  Snackbar,
  Skeleton,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Scanner as ScanIcon,
} from '@mui/icons-material';
import KnowledgeStats from './KnowledgeStats';
import KnowledgeSearch from './KnowledgeSearch';
import FileBrowser from './FileBrowser';
import FileDetails from './FileDetails';
import KnowledgeTableSkeleton from './KnowledgeTableSkeleton';
import { knowledgeAPI } from '../../services/api';
import { translateErrorMessage } from '../../utils/errorTranslations';

export const KnowledgePage = () => {
  const [stats, setStats] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filesLoading, setFilesLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [totalFiles, setTotalFiles] = useState(0);

  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({ type: '', sort: 'name' });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadFiles();
  }, [page, rowsPerPage, filters, searchQuery]);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [statsRes, filesRes] = await Promise.allSettled([
        knowledgeAPI.getStats(),
        knowledgeAPI.getFiles(1, rowsPerPage),
      ]);

      if (statsRes.status === 'fulfilled') {
        setStats(statsRes.value.data);
      }

      if (filesRes.status === 'fulfilled') {
        const data = filesRes.value.data;
        setFiles(data.files || []);
        setTotalFiles(data.total || 0);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to load knowledge base data:', err);
      setError(translateErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadFiles = async () => {
    setFilesLoading(true);
    try {
      if (searchQuery && searchQuery.length >= 3) {
        const response = await knowledgeAPI.search(searchQuery);
        const results = response.data.results || [];
        const searchFiles = results.map(r => r.file);
        setFiles(searchFiles);
        setTotalFiles(results.length);
      } else {
        const apiPage = page + 1;
        const response = await knowledgeAPI.getFiles(
          apiPage,
          rowsPerPage,
          filters.type,
          filters.sort
        );
        const data = response.data;
        setFiles(data.files || []);
        setTotalFiles(data.total || 0);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to load files:', err);
      setError(translateErrorMessage(err));
    } finally {
      setFilesLoading(false);
    }
  };

  const handleScan = async () => {
    setScanning(true);
    try {
      await knowledgeAPI.triggerScan();
      setSnackbar({
        open: true,
        message: 'Knowledge base scan initiated',
        severity: 'success',
      });

      setTimeout(() => {
        loadInitialData();
      }, 2000);
    } catch (err) {
      setSnackbar({
        open: true,
        message: `Scan failed: ${translateErrorMessage(err)}`,
        severity: 'error',
      });
    } finally {
      setScanning(false);
    }
  };

  const handleRefresh = () => {
    loadInitialData();
    setSelectedFile(null);
  };

  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    setPage(0);
  }, []);

  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
    setPage(0);
  }, []);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (newRowsPerPage) => {
    setRowsPerPage(newRowsPerPage);
    setPage(0);
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };

  const handleDownload = (file) => {
    setSnackbar({
      open: true,
      message: `Download functionality for ${file.filename} would be implemented here`,
      severity: 'info',
    });
  };

  if (loading) {
    return (
      <Box>
        <Skeleton width={200} height={40} sx={{ mb: 3 }} />
        <Box mb={3}>
          <KnowledgeTableSkeleton />
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" fontWeight={700}>
          Knowledge Base
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<ScanIcon />}
            onClick={handleScan}
            disabled={scanning}
          >
            {scanning ? 'Scanning...' : 'Scan'}
          </Button>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box mb={3}>
        <KnowledgeStats stats={stats} loading={loading} />
      </Box>

      <Box mb={3}>
        <KnowledgeSearch
          onSearch={handleSearch}
          onFilterChange={handleFilterChange}
          disabled={filesLoading}
        />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {filesLoading ? (
            <KnowledgeTableSkeleton rows={5} />
          ) : (
            <FileBrowser
              files={files}
              loading={filesLoading}
              page={page}
              rowsPerPage={rowsPerPage}
              totalFiles={totalFiles}
              onPageChange={handlePageChange}
              onRowsPerPageChange={handleRowsPerPageChange}
              onFileSelect={handleFileSelect}
              selectedFileId={selectedFile?.id}
            />
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <FileDetails file={selectedFile} onDownload={handleDownload} />
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default KnowledgePage;
