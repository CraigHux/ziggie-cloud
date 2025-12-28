import React, { useState } from 'react';
import {
  Grid,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Terminal as TerminalIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import Card from '../common/Card';

const actions = [
  { label: 'Start ComfyUI', icon: PlayArrowIcon, action: 'start-comfyui', color: 'success' },
  { label: 'Stop All Services', icon: StopIcon, action: 'stop-all', color: 'error' },
  { label: 'Restart N8N', icon: RefreshIcon, action: 'restart-n8n', color: 'warning' },
  { label: 'Run Port Scan', icon: SearchIcon, action: 'port-scan', color: 'info' },
  { label: 'Open Terminal', icon: TerminalIcon, action: 'terminal', color: 'primary' },
];

export const QuickActions = ({ onAction }) => {
  const [confirmDialog, setConfirmDialog] = useState({ open: false, action: null });

  const handleAction = (actionId) => {
    // Show confirmation for destructive actions
    if (actionId === 'stop-all') {
      setConfirmDialog({ open: true, action: actionId });
    } else {
      onAction && onAction(actionId);
    }
  };

  const handleConfirm = () => {
    if (confirmDialog.action) {
      onAction && onAction(confirmDialog.action);
    }
    setConfirmDialog({ open: false, action: null });
  };

  const handleCancel = () => {
    setConfirmDialog({ open: false, action: null });
  };

  return (
    <>
      <Card title="Quick Actions">
        <Grid container spacing={2}>
          {actions.map((action) => {
            const Icon = action.icon;
            return (
              <Grid item xs={12} sm={6} md={4} key={action.action}>
                <Button
                  fullWidth
                  variant="outlined"
                  color={action.color}
                  startIcon={<Icon />}
                  onClick={() => handleAction(action.action)}
                  sx={{
                    py: 1.5,
                    justifyContent: 'flex-start',
                    textTransform: 'none',
                    fontWeight: 600,
                  }}
                >
                  {action.label}
                </Button>
              </Grid>
            );
          })}
        </Grid>
      </Card>

      <Dialog
        open={confirmDialog.open}
        onClose={handleCancel}
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-description"
      >
        <DialogTitle id="confirm-dialog-title">
          Confirm Stop All Services
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="confirm-dialog-description">
            Are you sure you want to stop all running services? This action will terminate all active services immediately.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleConfirm} color="error" variant="contained" autoFocus>
            Stop All Services
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default QuickActions;
