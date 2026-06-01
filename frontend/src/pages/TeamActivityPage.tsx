import React, { useState } from 'react';
import { Box, Typography, Chip, Button } from '@mui/material';
import { useAgentHuddleFeed } from '../hooks/useAgentHuddleFeed';
import CommitteeSummary from '../components/TeamActivity/CommitteeSummary';
import CommitteeAuditTable from '../components/TeamActivity/CommitteeAuditTable';
import AlertBanner from '../components/TeamActivity/AlertBanner';
import AgentStatusPanel from '../components/TeamActivity/AgentStatusPanel';
import ActivityLog from '../components/TeamActivity/ActivityLog';
import QualityAuditPanel from '../components/TeamActivity/QualityAuditPanel';
import TrendSignalsPanel from '../components/TeamActivity/TrendSignalsPanel';
import AgentHelpModal from '../components/TeamActivity/AgentHelpModal';

const TeamActivityPage: React.FC = () => {
  const { runs, events, alerts, approvals, connectionMode } = useAgentHuddleFeed();
  const [auditMode, setAuditMode] = useState(false);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: 'rgba(255,255,255,0.95)' }}>
          Team Activity
        </Typography>
        <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
          <Chip
            label={connectionMode === 'sse' ? 'Live' : 'Polling'}
            size="small"
            sx={{ height: 24, fontSize: 11, fontWeight: 600, bgcolor: connectionMode === 'sse' ? 'rgba(76,175,80,0.15)' : 'rgba(255,152,0,0.15)', color: connectionMode === 'sse' ? '#4caf50' : '#ff9800' }}
          />
          <Button
            size="small"
            variant={auditMode ? 'contained' : 'outlined'}
            onClick={() => setAuditMode(!auditMode)}
            sx={{
              fontSize: 12,
              fontWeight: 600,
              textTransform: 'none',
              borderRadius: 2,
              ...(auditMode
                ? {
                    background: 'linear-gradient(135deg, rgba(102,126,234,0.8), rgba(118,75,162,0.8))',
                    color: '#fff',
                    boxShadow: '0 4px 15px rgba(102,126,234,0.3)',
                  }
                : {
                    color: 'rgba(255,255,255,0.7)',
                    borderColor: 'rgba(255,255,255,0.2)',
                    '&:hover': { borderColor: 'rgba(255,255,255,0.4)', bgcolor: 'rgba(255,255,255,0.05)' },
                  }),
            }}
          >
            {auditMode ? '← Summary' : 'Advanced Audit ▾'}
          </Button>
          <AgentHelpModal />
        </Box>
      </Box>

      {auditMode ? (
        <CommitteeAuditTable events={events} />
      ) : (
        <>
          {/* 1. Alerts + Approvals need attention */}
          <AlertBanner alerts={alerts} approvals={approvals} />

          {/* 2. Committee decision brief */}
          <CommitteeSummary events={events} />

          {/* 3. Quality audit (ContentGuardianAgent) */}
          <QualityAuditPanel events={events} />

          {/* 4. Trend signals (TrendSurferAgent) */}
          <TrendSignalsPanel events={events} />

          {/* 5. Agent health at a glance */}
          <AgentStatusPanel events={events} runs={runs} alerts={alerts} />

          {/* 6. Raw activity feed (collapsed by default) */}
          <ActivityLog runs={runs} events={events} />
        </>
      )}
    </Box>
  );
};

export default TeamActivityPage;
