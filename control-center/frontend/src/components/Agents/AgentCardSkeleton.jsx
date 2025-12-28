import React from 'react';
import { Card, CardContent, CardActions, Box, Skeleton } from '@mui/material';

const AgentCardSkeleton = () => {
  return (
    <Card
      elevation={2}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderTop: '4px solid #333',
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Skeleton
            variant="rectangular"
            width={44}
            height={44}
            sx={{ borderRadius: 2, mr: 1.5 }}
          />
          <Box sx={{ flex: 1 }}>
            <Skeleton width={80} height={24} sx={{ mb: 0.5 }} />
          </Box>
        </Box>

        <Skeleton width="90%" height={32} sx={{ mb: 1 }} />
        <Skeleton width="70%" height={32} sx={{ mb: 2 }} />

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Skeleton width="60%" height={20} />
          <Skeleton width="50%" height={20} />
        </Box>
      </CardContent>

      <CardActions sx={{ pt: 0, px: 2, pb: 2 }}>
        <Skeleton width="100%" height={36} sx={{ borderRadius: 1 }} />
      </CardActions>
    </Card>
  );
};

export default AgentCardSkeleton;
