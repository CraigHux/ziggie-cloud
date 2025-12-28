import React from 'react';
import { Grid, Card, CardContent, Box, Skeleton } from '@mui/material';

const SystemMetricSkeleton = () => {
  return (
    <Grid container spacing={3}>
      {/* System Stats Section */}
      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Box display="flex" gap={2}>
              {[1, 2, 3, 4].map((i) => (
                <Box key={i} flex={1}>
                  <Skeleton width="100%" height={60} sx={{ mb: 1 }} />
                  <Skeleton width="80%" height={20} />
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* System Information Skeleton */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Skeleton width={180} height={28} sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={1.5}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Box key={i} display="flex" justifyContent="space-between">
                  <Skeleton width="40%" height={20} />
                  <Skeleton width="45%" height={20} />
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Stats Skeleton */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Skeleton width={150} height={28} sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={1.5}>
              {[1, 2, 3, 4].map((i) => (
                <Box key={i} display="flex" justifyContent="space-between" alignItems="center">
                  <Skeleton width="50%" height={20} />
                  <Skeleton width="30%" height={24} />
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Port Scanner Skeleton */}
      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Skeleton width={150} height={28} sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={1}>
              {[1, 2, 3, 4, 5].map((i) => (
                <Box key={i} display="flex" gap={1} alignItems="center">
                  <Skeleton width="10%" height={20} />
                  <Skeleton width="20%" height={20} />
                  <Skeleton width="20%" height={20} />
                  <Skeleton width="25%" height={20} />
                  <Skeleton width="15%" height={20} />
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Process List Skeleton */}
      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Skeleton width={150} height={28} sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={1}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Box key={i} display="flex" gap={1} alignItems="center">
                  <Skeleton width="25%" height={20} />
                  <Skeleton width="15%" height={20} />
                  <Skeleton width="15%" height={20} />
                  <Skeleton width="15%" height={20} />
                  <Skeleton width="20%" height={20} />
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default SystemMetricSkeleton;
