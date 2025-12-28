import React from 'react';
import { Grid, Box, Skeleton, Card, CardContent } from '@mui/material';

const DashboardSkeleton = () => {
  return (
    <Box>
      {/* Title Skeleton */}
      <Skeleton width={200} height={40} sx={{ mb: 3 }} />

      <Grid container spacing={3}>
        {/* System Stats Skeleton */}
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

        {/* Services Widget Skeleton */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Skeleton width={150} height={28} sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={1.5}>
                {[1, 2, 3].map((i) => (
                  <Box key={i}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Skeleton width="40%" height={20} />
                      <Skeleton width="30%" height={20} />
                    </Box>
                    <Skeleton width="100%" height={16} />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions Skeleton */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Skeleton width={150} height={28} sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={1.5}>
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} width="100%" height={40} sx={{ borderRadius: 1 }} />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Summary Skeleton */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Skeleton width={150} height={28} sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={2}>
                <Box>
                  <Skeleton width="60%" height={40} sx={{ mb: 0.5 }} />
                  <Skeleton width="80%" height={18} />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  {[1, 2, 3].map((i) => (
                    <Box key={i} flex={1}>
                      <Skeleton width="100%" height={32} sx={{ mb: 0.5 }} />
                      <Skeleton width="90%" height={16} />
                    </Box>
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Knowledge Skeleton */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Skeleton width={150} height={28} sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={1.5}>
                {[1, 2, 3, 4].map((i) => (
                  <Box key={i} py={1} borderBottom="1px solid" borderColor="divider">
                    <Skeleton width="90%" height={18} sx={{ mb: 0.5 }} />
                    <Skeleton width="70%" height={14} />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity Skeleton */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Skeleton width={150} height={28} sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={1.5}>
                {[1, 2, 3].map((i) => (
                  <Box key={i} py={1.5}>
                    <Skeleton width="80%" height={18} sx={{ mb: 0.5 }} />
                    <Skeleton width="60%" height={14} />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardSkeleton;
