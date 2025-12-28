import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Skeleton,
  Box,
} from '@mui/material';

const KnowledgeTableSkeleton = ({ rows = 10 }) => {
  return (
    <TableContainer component={Paper} elevation={2}>
      <Table>
        <TableHead>
          <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
            <TableCell>
              <Skeleton width="100%" height={24} />
            </TableCell>
            <TableCell>
              <Skeleton width="100%" height={24} />
            </TableCell>
            <TableCell>
              <Skeleton width="100%" height={24} />
            </TableCell>
            <TableCell>
              <Skeleton width="100%" height={24} />
            </TableCell>
            <TableCell align="right">
              <Skeleton width="100%" height={24} />
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {Array.from({ length: rows }).map((_, index) => (
            <TableRow key={index}>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  <Skeleton variant="circular" width={32} height={32} />
                  <Box flex={1}>
                    <Skeleton width="100%" height={18} sx={{ mb: 0.5 }} />
                    <Skeleton width="80%" height={14} />
                  </Box>
                </Box>
              </TableCell>
              <TableCell>
                <Skeleton width="100%" height={18} />
              </TableCell>
              <TableCell>
                <Skeleton width="100%" height={18} />
              </TableCell>
              <TableCell>
                <Skeleton width="100%" height={18} />
              </TableCell>
              <TableCell align="right">
                <Box display="flex" gap={0.5} justifyContent="flex-end">
                  <Skeleton width={36} height={36} sx={{ borderRadius: 1 }} />
                  <Skeleton width={36} height={36} sx={{ borderRadius: 1 }} />
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default KnowledgeTableSkeleton;
