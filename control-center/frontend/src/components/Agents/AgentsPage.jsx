import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Box,
  Typography,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import { SmartToy as SmartToyIcon } from '@mui/icons-material';
import AgentStatsWidget from './AgentStatsWidget';
import AgentFilters from './AgentFilters';
import AgentCard from './AgentCard';
import AgentCardSkeleton from './AgentCardSkeleton';
import AgentDetailModal from './AgentDetailModal';
import EmptyState from '../common/EmptyState';
import { agentsAPI } from '../../services/api';
import { translateErrorMessage } from '../../utils/errorTranslations';

const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({ level: 'all', search: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [page, setPage] = useState(1);
  const [retryCount, setRetryCount] = useState(0);
  const itemsPerPage = 20;
  const maxRetries = 3;

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async (isRetry = false) => {
    setLoading(true);
    if (!isRetry) {
      setError(null);
      setRetryCount(0);
    }

    try {
      const [agentsResponse, summaryResponse] = await Promise.all([
        agentsAPI.getAll(),
        agentsAPI.getSummary(),
      ]);

      // Handle different response formats
      const agentsData = agentsResponse.data.agents || agentsResponse.data;
      const agentsList = Array.isArray(agentsData) ? agentsData : [];

      setAgents(agentsList);

      // Map backend stats format to frontend format
      const statsData = summaryResponse.data;
      setStats({
        total: statsData.total || 0,
        l1: statsData.l1_count || 0,
        l2: statsData.l2_count || 0,
        l3: statsData.l3_count || 0,
        by_level: statsData.by_level || {},
      });

      setError(null);
      setRetryCount(0);
    } catch (err) {
      console.error('Error fetching agents:', err);
      setError(translateErrorMessage(err));

      // Auto-retry logic for network errors
      if (retryCount < maxRetries && (err.code === 'ERR_NETWORK' || err.code === 'ECONNABORTED')) {
        const nextRetry = retryCount + 1;
        setRetryCount(nextRetry);
        console.log(`Retrying... (${nextRetry}/${maxRetries})`);
        setTimeout(() => fetchData(true), 2000 * nextRetry); // Exponential backoff
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAgentClick = (agent) => {
    setSelectedAgent(agent);
  };

  const handleCloseModal = () => {
    setSelectedAgent(null);
  };

  // Filter agents based on search and level
  const filteredAgents = agents.filter((agent) => {
    const matchesSearch =
      !filters.search ||
      agent.name?.toLowerCase().includes(filters.search.toLowerCase()) ||
      agent.id?.toLowerCase().includes(filters.search.toLowerCase());

    const matchesLevel =
      filters.level === 'all' || agent.id?.startsWith(filters.level.toUpperCase());

    return matchesSearch && matchesLevel;
  });

  // Paginate
  const totalPages = Math.ceil(filteredAgents.length / itemsPerPage);
  const paginatedAgents = filteredAgents.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography
        variant="h4"
        gutterBottom
        sx={{
          fontWeight: 600,
          color: '#FF8C42',
          mb: 3,
        }}
      >
        AI Agents
      </Typography>

      <AgentStatsWidget stats={stats} loading={loading} />

      <AgentFilters
        filters={filters}
        onChange={setFilters}
        onRefresh={fetchData}
      />

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 3 }}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => fetchData(false)}
            >
              Retry
            </Button>
          }
        >
          {error}
          {retryCount > 0 && (
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Retry attempt {retryCount} of {maxRetries}...
            </Typography>
          )}
        </Alert>
      )}

      {loading ? (
        <Grid container spacing={3}>
          {Array.from({ length: 8 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
              <AgentCardSkeleton />
            </Grid>
          ))}
        </Grid>
      ) : filteredAgents.length === 0 ? (
        <EmptyState
          icon={SmartToyIcon}
          title="No agents found"
          description={
            filters.level !== 'all' || filters.search
              ? `No ${filters.level !== 'all' ? filters.level.toUpperCase() : 'agents'} match your search. (${agents.length} total agents)`
              : 'No agents configured yet'
          }
        />
      ) : (
        <>
          <Grid container spacing={3}>
            {paginatedAgents.map((agent) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
                <AgentCard agent={agent} onClick={() => handleAgentClick(agent)} />
              </Grid>
            ))}
          </Grid>

          {totalPages > 1 && filteredAgents.length > 0 && (
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                mt: 4,
                gap: 2,
              }}
            >
              <Typography variant="body2" color="text.secondary">
                {filteredAgents.length === 0
                  ? 'No items to display'
                  : `Page ${page} of ${totalPages} (${filteredAgents.length} agents)`
                }
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  style={{
                    padding: '8px 16px',
                    background: page === 1 ? '#333' : '#FF8C42',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: page === 1 ? 'not-allowed' : 'pointer',
                  }}
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  style={{
                    padding: '8px 16px',
                    background: page === totalPages ? '#333' : '#FF8C42',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: page === totalPages ? 'not-allowed' : 'pointer',
                  }}
                >
                  Next
                </button>
              </Box>
            </Box>
          )}
        </>
      )}

      {selectedAgent && (
        <AgentDetailModal
          agent={selectedAgent}
          open={!!selectedAgent}
          onClose={handleCloseModal}
        />
      )}
    </Container>
  );
};

export default AgentsPage;
