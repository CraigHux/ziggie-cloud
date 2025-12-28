import React from 'react';
import { Grid, Box, Typography, LinearProgress, Skeleton } from '@mui/material';
import {
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
} from '@mui/icons-material';
import { LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts';
import Card from '../common/Card';

const StatCard = ({ title, value, unit, icon: Icon, data, color, loading }) => {
  const percentage = parseFloat(value) || 0;

  if (loading) {
    return (
      <Card>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Skeleton variant="rectangular" width={48} height={48} sx={{ borderRadius: 2 }} />
          <Box flex={1}>
            <Skeleton variant="text" width="60%" height={20} />
            <Skeleton variant="text" width="80%" height={40} />
          </Box>
        </Box>
        <Skeleton variant="rectangular" height={8} sx={{ borderRadius: 4, mb: 2 }} />
        <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1 }} />
      </Card>
    );
  }

  return (
    <Card>
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        <Box
          sx={{
            p: 1.5,
            borderRadius: 2,
            bgcolor: `${color}.main`,
            color: 'white',
            display: 'flex',
          }}
        >
          <Icon />
        </Box>
        <Box flex={1}>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h4" fontWeight={700}>
            {value}
            <Typography component="span" variant="h6" color="text.secondary">
              {unit}
            </Typography>
          </Typography>
        </Box>
      </Box>

      <LinearProgress
        variant="determinate"
        value={percentage}
        sx={{
          height: 8,
          borderRadius: 4,
          bgcolor: 'action.hover',
          '& .MuiLinearProgress-bar': {
            bgcolor: `${color}.main`,
          },
        }}
        aria-label={`${title} at ${value}${unit}`}
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
      />

      {data && data.length > 0 && (
        <Box mt={2} height={60}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <Line
                type="monotone"
                dataKey="value"
                stroke={color === 'primary' ? '#2196f3' : color === 'secondary' ? '#f50057' : '#4caf50'}
                strokeWidth={2}
                dot={false}
              />
              <Tooltip />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Card>
  );
};

export const SystemStats = ({ stats, loading }) => {
  const cpuUsage = stats?.cpu?.usage_percent || stats?.cpu?.usage || 0;
  const memoryUsage = stats?.memory?.percent || 0;
  const diskUsage = stats?.disk?.percent || 0;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <StatCard
          title="CPU Usage"
          value={cpuUsage.toFixed(1)}
          unit="%"
          icon={SpeedIcon}
          color="primary"
          data={stats?.cpu?.history}
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <StatCard
          title="Memory Usage"
          value={memoryUsage.toFixed(1)}
          unit="%"
          icon={MemoryIcon}
          color="secondary"
          data={stats?.memory?.history}
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <StatCard
          title="Disk Usage"
          value={diskUsage.toFixed(1)}
          unit="%"
          icon={StorageIcon}
          color="success"
          data={stats?.disk?.history}
          loading={loading}
        />
      </Grid>
    </Grid>
  );
};

export default SystemStats;
