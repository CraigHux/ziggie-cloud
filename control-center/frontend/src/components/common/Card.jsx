import React from 'react';
import { Card as MuiCard, CardContent, CardHeader, Box } from '@mui/material';

export const Card = ({ title, subtitle, children, action, sx, ...props }) => {
  return (
    <MuiCard sx={{ height: '100%', ...sx }} {...props}>
      {title && (
        <CardHeader
          title={title}
          subheader={subtitle}
          action={action}
          sx={{
            borderBottom: '1px solid',
            borderColor: 'divider',
            pb: 1.5,
          }}
        />
      )}
      <CardContent>
        {children}
      </CardContent>
    </MuiCard>
  );
};

export default Card;
