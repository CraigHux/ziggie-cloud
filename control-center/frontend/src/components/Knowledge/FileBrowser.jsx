import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Typography,
} from '@mui/material';
import { Visibility as ViewIcon } from '@mui/icons-material';
import Card from '../common/Card';
import LoadingSpinner from '../common/LoadingSpinner';
import {
  getFileIcon,
  getFileColor,
  formatFileSize,
  formatRelativeDate,
  truncateFilename,
} from './utils/fileIcons';

/**
 * File browser table with pagination
 */
export const FileBrowser = ({
  files = [],
  loading,
  page = 0,
  rowsPerPage = 20,
  totalFiles = 0,
  onPageChange,
  onRowsPerPageChange,
  onFileSelect,
  selectedFileId,
}) => {
  const handleChangePage = (event, newPage) => {
    if (onPageChange) {
      onPageChange(newPage);
    }
  };

  const handleChangeRowsPerPage = (event) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    if (onRowsPerPageChange) {
      onRowsPerPageChange(newRowsPerPage);
    }
  };

  const handleRowClick = (file) => {
    if (onFileSelect) {
      onFileSelect(file);
    }
  };

  if (loading && files.length === 0) {
    return (
      <Card title="Files">
        <LoadingSpinner message="Loading files..." />
      </Card>
    );
  }

  return (
    <Card title="Files" subtitle={`${totalFiles} total files`}>
      {files.length === 0 ? (
        <Box textAlign="center" py={6}>
          <Typography variant="h6" color="text.secondary">
            No files found
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={1}>
            Try adjusting your search or filters
          </Typography>
        </Box>
      ) : (
        <>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell width={40}></TableCell>
                  <TableCell>Filename</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Size</TableCell>
                  <TableCell>Modified</TableCell>
                  <TableCell width={60} align="center">
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {files.map((file, index) => {
                  const IconComponent = getFileIcon(file.type);
                  const isSelected = selectedFileId === file.id;

                  // Add fallbacks for missing data
                  const displayName = truncateFilename(file.filename || `Document ${index + 1}`, 50);
                  const displayType = file.type || (file.path?.split('.').pop() || 'File');
                  const displaySize = file.size_bytes !== undefined ? formatFileSize(file.size_bytes) : '--';
                  const displayDate = formatRelativeDate(file.modified_at || file.created_at) || 'Unknown';

                  return (
                    <TableRow
                      key={file.id || file.path || index}
                      hover
                      onClick={() => handleRowClick(file)}
                      sx={{
                        cursor: 'pointer',
                        bgcolor: isSelected ? 'action.selected' : 'inherit',
                        '&:hover': {
                          bgcolor: isSelected ? 'action.selected' : 'action.hover',
                        },
                      }}
                    >
                      <TableCell>
                        <IconComponent
                          fontSize="small"
                          color={getFileColor(displayType)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={isSelected ? 600 : 400}>
                          {displayName}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={displayType}
                          size="small"
                          color={getFileColor(displayType)}
                          sx={{ textTransform: 'capitalize' }}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="text.secondary">
                          {displaySize}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {displayDate}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRowClick(file);
                          }}
                          aria-label="view details"
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>

          {totalFiles > 0 ? (
            <TablePagination
              component="div"
              count={totalFiles}
              page={page}
              rowsPerPage={rowsPerPage}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              rowsPerPageOptions={[10, 20, 50, 100]}
            />
          ) : (
            <Box py={2} px={2}>
              <Typography variant="body2" color="text.secondary" textAlign="center">
                No items to display
              </Typography>
            </Box>
          )}
        </>
      )}
    </Card>
  );
};

export default FileBrowser;
