import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TextField,
  InputAdornment,
  Paper,
  Typography,
  Chip,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import Card from '../common/Card';

const formatMemory = (bytes) => {
  if (!bytes) return '0 B';
  const mb = bytes / (1024 * 1024);
  if (mb < 1024) return `${mb.toFixed(1)} MB`;
  return `${(mb / 1024).toFixed(2)} GB`;
};

export const ProcessList = ({ processes }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [orderBy, setOrderBy] = useState('memory');
  const [order, setOrder] = useState('desc');

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedProcesses = React.useMemo(() => {
    if (!processes) return [];

    // Map backend format to frontend format
    const normalizedProcesses = processes.map((proc) => ({
      ...proc,
      cpu: proc.cpu_percent || proc.cpu || 0,
      memory: proc.memory_percent || proc.memory || 0,
    }));

    const filtered = normalizedProcesses.filter(
      (proc) =>
        proc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        proc.pid.toString().includes(searchTerm)
    );

    return filtered.sort((a, b) => {
      let aValue = a[orderBy];
      let bValue = b[orderBy];

      if (orderBy === 'name') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (order === 'asc') {
        return aValue < bValue ? -1 : 1;
      }
      return aValue > bValue ? -1 : 1;
    });
  }, [processes, searchTerm, orderBy, order]);

  return (
    <Card title="Running Processes">
      <TextField
        fullWidth
        size="small"
        placeholder="Search processes..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 2 }}
      />

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'pid'}
                  direction={orderBy === 'pid' ? order : 'asc'}
                  onClick={() => handleSort('pid')}
                >
                  PID
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'name'}
                  direction={orderBy === 'name' ? order : 'asc'}
                  onClick={() => handleSort('name')}
                >
                  Name
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={orderBy === 'cpu'}
                  direction={orderBy === 'cpu' ? order : 'asc'}
                  onClick={() => handleSort('cpu')}
                >
                  CPU %
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={orderBy === 'memory'}
                  direction={orderBy === 'memory' ? order : 'asc'}
                  onClick={() => handleSort('memory')}
                >
                  Memory
                </TableSortLabel>
              </TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedProcesses.length > 0 ? (
              sortedProcesses.slice(0, 50).map((proc) => (
                <TableRow key={proc.pid} hover>
                  <TableCell>{proc.pid}</TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                      {proc.name}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {proc.cpu ? `${proc.cpu.toFixed(1)}%` : '0%'}
                  </TableCell>
                  <TableCell align="right">
                    {formatMemory(proc.memory)}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={proc.status || 'running'}
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography variant="body2" color="text.secondary" py={2}>
                    No processes found
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {sortedProcesses.length > 50 && (
        <Typography variant="caption" color="text.secondary" mt={1} display="block">
          Showing top 50 of {sortedProcesses.length} processes
        </Typography>
      )}
    </Card>
  );
};

export default ProcessList;
