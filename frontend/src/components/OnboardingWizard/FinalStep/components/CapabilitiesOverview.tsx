import React from 'react';
import {
  Box,
  Paper,
  Zoom,
  Grid,
  Typography,
  Card,
  CardContent
} from '@mui/material';
import {
  Star,
  CheckCircle,
  Lock
} from '@mui/icons-material';
import { Capability } from '../types';

interface CapabilitiesOverviewProps {
  capabilities: Capability[];
}

export const CapabilitiesOverview: React.FC<CapabilitiesOverviewProps> = ({ capabilities }) => {
  return (
    <Zoom in={true} timeout={1200}>
      <Paper elevation={0} sx={{ 
        p: 4, 
        mb: 4,
        background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
        border: '1px solid rgba(245, 158, 11, 0.2)',
        borderRadius: 3
      }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1, color: '#000000 !important' }}>
          <Star sx={{ color: 'warning.main' }} />
          Capabilities Overview
        </Typography>

        <Grid container spacing={2}>
          {capabilities.map((capability) => (
            <Grid item xs={12} sm={6} md={4} key={capability.id}>
              <Card elevation={0} sx={{ 
                background: capability.unlocked ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.05)',
                border: `1px solid ${capability.unlocked ? 'rgba(16, 185, 129, 0.3)' : 'rgba(0, 0, 0, 0.1)'}`,
                borderRadius: 2,
                opacity: capability.unlocked ? 1 : 0.6
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Box sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      background: capability.unlocked 
                        ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                        : 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {React.cloneElement(capability.icon, { 
                        sx: { color: 'white', fontSize: 20 } 
                      })}
                    </Box>
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1, color: '#000000 !important' }}>
                        {capability.title}
                        {capability.unlocked ? (
                          <CheckCircle sx={{ color: 'success.main', fontSize: 16 }} />
                        ) : (
                          <Lock sx={{ color: '#666666 !important', fontSize: 16 }} />
                        )}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" sx={{ mb: 2, color: '#000000 !important' }}>
                    {capability.description}
                  </Typography>
                  {!capability.unlocked && capability.required && (
                    <Box>
                      <Typography variant="caption" sx={{ color: '#000000 !important' }}>
                        Requires: {capability.required.join(', ')}
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Zoom>
  );
};

export default CapabilitiesOverview;
