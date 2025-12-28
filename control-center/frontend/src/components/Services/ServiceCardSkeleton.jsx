import React from 'react';
import { Card, CardContent, CardActions, Box, Skeleton } from '@mui/material';

const ServiceCardSkeleton = () => {
  return (
    <Card elevation={2}>
      <CardContent sx={{ pb: 1 }}>
        {/* Service Header */}
        <Box display="flex" alignItems="center" mb={2}>
          <Skeleton variant="circular" width={44} height={44} sx={{ mr: 1.5 }} />
          <Box flex={1}>
            <Skeleton width="70%" height={24} sx={{ mb: 0.5 }} />
            <Skeleton width="90%" height={16} />
          </Box>
        </Box>

        {/* Status Badge */}
        <Box mb={2}>
          <Skeleton width={100} height={28} sx={{ borderRadius: 1 }} />
        </Box>

        {/* Service Description */}
        <Skeleton width="100%" height={40} sx={{ mb: 2 }} />

        {/* Service Details */}
        <Box display="flex" flexDirection="column" gap={1}>
          <Box display="flex" justifyContent="space-between">
            <Skeleton width="40%" height={18} />
            <Skeleton width="30%" height={18} />
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Skeleton width="40%" height={18} />
            <Skeleton width="30%" height={18} />
          </Box>
        </Box>
      </CardContent>

      {/* Action Buttons */}
      <CardActions sx={{ pt: 0, px: 2, pb: 2, display: 'flex', gap: 1 }}>
        <Skeleton width="100%" height={36} sx={{ borderRadius: 1 }} />
        <Skeleton width="100%" height={36} sx={{ borderRadius: 1 }} />
      </CardActions>
    </Card>
  );
};

export default ServiceCardSkeleton;
