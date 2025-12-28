import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  Button,
  Tooltip,
} from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import FolderIcon from '@mui/icons-material/Folder';
import CategoryIcon from '@mui/icons-material/Category';
import AccountTreeIcon from '@mui/icons-material/AccountTree';

const getLevelColor = (agentId) => {
  if (agentId?.startsWith('L1')) return '#E74C3C';
  if (agentId?.startsWith('L2')) return '#3498DB';
  if (agentId?.startsWith('L3')) return '#2ECC71';
  return '#FF8C42';
};

const getLevelLabel = (agentId) => {
  if (agentId?.startsWith('L1')) return 'Level 1';
  if (agentId?.startsWith('L2')) return 'Level 2';
  if (agentId?.startsWith('L3')) return 'Level 3';
  return 'Custom';
};

const AgentCard = ({ agent, onClick }) => {
  const levelColor = getLevelColor(agent.id);
  const levelLabel = getLevelLabel(agent.id);

  return (
    <Card
      elevation={2}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        borderTop: `4px solid ${levelColor}`,
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: 6,
          borderTopWidth: '6px',
        },
      }}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`${agent.name || 'Unnamed Agent'} - ${agent.id} agent card`}
      onKeyPress={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Box
            sx={{
              p: 1,
              borderRadius: 2,
              bgcolor: `${levelColor}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mr: 1.5,
            }}
          >
            <SmartToyIcon sx={{ fontSize: 28, color: levelColor }} />
          </Box>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Tooltip title={`${agent.id} - ${levelLabel}`} arrow>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <Chip
                  label={agent.id}
                  size="small"
                  sx={{
                    bgcolor: levelColor,
                    color: 'white',
                    fontWeight: 600,
                    fontSize: '0.75rem',
                  }}
                />
                <Chip
                  label={levelLabel}
                  size="small"
                  variant="outlined"
                  sx={{
                    borderColor: levelColor,
                    color: levelColor,
                    fontWeight: 600,
                    fontSize: '0.75rem',
                  }}
                />
              </Box>
            </Tooltip>
          </Box>
        </Box>

        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            mb: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            minHeight: '3em',
          }}
        >
          {agent.name || 'Unnamed Agent'}
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {agent.category && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CategoryIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {agent.category}
              </Typography>
            </Box>
          )}

          {agent.knowledge_files !== undefined && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FolderIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {agent.knowledge_files} KB files
              </Typography>
            </Box>
          )}

          {agent.sub_agents !== undefined && agent.sub_agents > 0 && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccountTreeIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {agent.sub_agents} sub-agents
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>

      <CardActions sx={{ pt: 0, px: 2, pb: 2 }}>
        <Button
          size="small"
          sx={{
            color: levelColor,
            '&:hover': {
              bgcolor: `${levelColor}20`,
            },
          }}
          fullWidth
        >
          View Details
        </Button>
      </CardActions>
    </Card>
  );
};

export default AgentCard;
