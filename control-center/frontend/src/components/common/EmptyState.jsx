import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Inbox as InboxIcon } from '@mui/icons-material';

/**
 * Reusable empty state component
 * Displays when no data is available with optional icon, text, and action
 */
export const EmptyState = ({
  icon: IconComponent = InboxIcon,
  title = 'No items',
  description = '',
  actionLabel = '',
  onAction = null,
  iconSize = 48,
  compact = false,
}) => {
  const padding = compact ? 3 : 6;

  return (
    <Box
      py={padding}
      textAlign="center"
      display="flex"
      flexDirection="column"
      alignItems="center"
      gap={compact ? 1.5 : 2}
    >
      <IconComponent
        sx={{
          fontSize: iconSize,
          color: 'text.disabled',
          opacity: 0.5,
        }}
      />
      <Box>
        <Typography
          variant={compact ? 'body2' : 'body1'}
          color="text.secondary"
          fontWeight={600}
        >
          {title}
        </Typography>
        {description && (
          <Typography
            variant="caption"
            color="text.secondary"
            display="block"
            mt={0.5}
          >
            {description}
          </Typography>
        )}
      </Box>
      {actionLabel && onAction && (
        <Button
          variant="outlined"
          size={compact ? 'small' : 'medium'}
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;
