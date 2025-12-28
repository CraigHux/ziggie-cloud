import React from 'react';
import { Box, Typography, Chip, Divider, Button } from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';
import Card from '../common/Card';
import {
  getFileIcon,
  getFileColor,
  formatFileSize,
  formatRelativeDate,
} from './utils/fileIcons';

/**
 * Display detailed information about selected file
 */
export const FileDetails = ({ file, onDownload }) => {
  if (!file) {
    return (
      <Card title="File Details">
        <Box textAlign="center" py={6}>
          <Typography variant="body2" color="text.secondary">
            Select a file to view details
          </Typography>
        </Box>
      </Card>
    );
  }

  const IconComponent = getFileIcon(file.type);

  const handleDownload = () => {
    if (onDownload) {
      onDownload(file);
    }
  };

  return (
    <Card title="File Details">
      <Box display="flex" flexDirection="column" gap={2}>
        {/* File Icon */}
        <Box textAlign="center" py={2}>
          <Box
            sx={{
              width: 80,
              height: 80,
              margin: '0 auto',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: (theme) => theme.palette[getFileColor(file.type)]?.light || 'grey.200',
            }}
          >
            <IconComponent sx={{ fontSize: 40 }} color={getFileColor(file.type)} />
          </Box>
        </Box>

        {/* Filename */}
        <Box>
          <Typography
            variant="h6"
            fontWeight={600}
            textAlign="center"
            sx={{
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
            }}
          >
            {file.filename}
          </Typography>
        </Box>

        <Divider />

        {/* Metadata */}
        <Box display="flex" flexDirection="column" gap={1.5}>
          {/* Type */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2" color="text.secondary">
              Type
            </Typography>
            <Chip
              label={file.type || 'Unknown'}
              size="small"
              color={getFileColor(file.type)}
              sx={{ textTransform: 'capitalize' }}
            />
          </Box>

          {/* Size */}
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              Size
            </Typography>
            <Typography variant="body2" fontWeight={600}>
              {formatFileSize(file.size_bytes)}
            </Typography>
          </Box>

          {/* Created */}
          {file.created_at && (
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Created
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {formatRelativeDate(file.created_at)}
              </Typography>
            </Box>
          )}

          {/* Modified */}
          {file.modified_at && (
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Modified
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {formatRelativeDate(file.modified_at)}
              </Typography>
            </Box>
          )}

          {/* Path */}
          {file.path && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Path
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  wordBreak: 'break-all',
                  bgcolor: 'grey.100',
                  p: 1,
                  borderRadius: 1,
                  display: 'block',
                  fontFamily: 'monospace',
                }}
              >
                {file.path}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Video-specific metadata */}
        {file.type === 'video' && file.metadata && (
          <>
            <Divider />
            <Box display="flex" flexDirection="column" gap={1.5}>
              <Typography variant="subtitle2" fontWeight={600}>
                Video Information
              </Typography>

              {file.metadata.creator && (
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Creator
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {file.metadata.creator}
                  </Typography>
                </Box>
              )}

              {file.metadata.duration && (
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Duration
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {file.metadata.duration}
                  </Typography>
                </Box>
              )}

              {file.metadata.has_transcript !== undefined && (
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    Transcript
                  </Typography>
                  <Chip
                    label={file.metadata.has_transcript ? 'Available' : 'Not Available'}
                    size="small"
                    color={file.metadata.has_transcript ? 'success' : 'default'}
                  />
                </Box>
              )}
            </Box>
          </>
        )}

        <Divider />

        {/* Actions */}
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={handleDownload}
          fullWidth
        >
          Download
        </Button>
      </Box>
    </Card>
  );
};

export default FileDetails;
