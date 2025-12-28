import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import Card from '../common/Card';

export const PortScanner = ({ ports }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPorts = React.useMemo(() => {
    if (!ports) return [];
    return ports.filter(
      (port) =>
        port.port.toString().includes(searchTerm) ||
        (port.service && port.service.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (port.process && port.process.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [ports, searchTerm]);

  return (
    <Card title="Port Usage">
      <TextField
        fullWidth
        size="small"
        placeholder="Search ports..."
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
              <TableCell>Port</TableCell>
              <TableCell>Protocol</TableCell>
              <TableCell>Service</TableCell>
              <TableCell>Process</TableCell>
              <TableCell>PID</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredPorts.length > 0 ? (
              filteredPorts.map((port, index) => (
                <TableRow key={`${port.port}-${index}`} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {port.port}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={port.protocol || 'TCP'}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{port.service || '-'}</TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {port.process || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>{port.pid || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={port.status || 'LISTEN'}
                      size="small"
                      color={port.status === 'LISTEN' ? 'success' : 'default'}
                    />
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="text.secondary" py={2}>
                    No ports found
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredPorts.length > 0 && (
        <Typography variant="caption" color="text.secondary" mt={1} display="block">
          {filteredPorts.length} port{filteredPorts.length !== 1 ? 's' : ''} in use
        </Typography>
      )}
    </Card>
  );
};

export default PortScanner;
