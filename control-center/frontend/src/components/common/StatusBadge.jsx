import React from 'react';
import { Chip } from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Circle as CircleIcon,
} from '@mui/icons-material';

const statusConfig = {
  running: {
    label: 'Running',
    color: 'success',
    icon: CheckCircleIcon,
  },
  stopped: {
    label: 'Stopped',
    color: 'error',
    icon: ErrorIcon,
  },
  starting: {
    label: 'Starting',
    color: 'warning',
    icon: WarningIcon,
  },
  error: {
    label: 'Error',
    color: 'error',
    icon: ErrorIcon,
  },
  unknown: {
    label: 'Unknown',
    color: 'default',
    icon: CircleIcon,
  },
};

export const StatusBadge = ({ status, label, size = 'small', showIcon = true }) => {
  const config = statusConfig[status?.toLowerCase()] || statusConfig.unknown;
  const Icon = config.icon;

  return (
    <Chip
      label={label || config.label}
      color={config.color}
      size={size}
      icon={showIcon ? <Icon /> : undefined}
      sx={{
        fontWeight: 600,
        '& .MuiChip-icon': {
          fontSize: '1rem',
        },
      }}
    />
  );
};

export default StatusBadge;
