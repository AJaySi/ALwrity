import React, { useMemo } from 'react';
import { Box } from '@mui/material';
import { motion } from 'framer-motion';
import { TerminalTypography } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';
import { UsageLimitRing } from '../../../shared/UsageLimitRing';
import { DashboardData } from '../../../../types/billing';

interface UsageLimitRingsProps {
  currentUsage: DashboardData['current_usage'];
  limits: DashboardData['limits'];
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
}

/**
 * UsageLimitRings - Displays circular progress rings for key usage limits
 */
export const UsageLimitRings: React.FC<UsageLimitRingsProps> = ({
  currentUsage,
  limits,
  terminalTheme = false,
  TypographyComponent
}) => {
  // Calculate image calls - check multiple possible sources
  const imageCalls = useMemo(() => {
    // Primary: provider_breakdown.image
    const imageFromBreakdown = currentUsage.provider_breakdown?.image?.calls ?? 0;
    const imageEditFromBreakdown = currentUsage.provider_breakdown?.image_edit?.calls ?? 0;
    
    // Fallback: Check if there's a stability key (legacy)
    const stabilityFromBreakdown = currentUsage.provider_breakdown?.stability?.calls ?? 0;
    
    // Sum all image-related calls
    const total = imageFromBreakdown + imageEditFromBreakdown + stabilityFromBreakdown;
    
    // Debug logging (can be removed in production)
    if (total > 0 || imageFromBreakdown > 0 || stabilityFromBreakdown > 0) {
      console.log('[UsageLimitRings] Image calls calculation:', {
        image: imageFromBreakdown,
        image_edit: imageEditFromBreakdown,
        stability: stabilityFromBreakdown,
        total,
        provider_breakdown_keys: Object.keys(currentUsage.provider_breakdown || {})
      });
    }
    
    return total;
  }, [currentUsage.provider_breakdown]);

  // Calculate video calls - check multiple possible sources
  const videoCalls = useMemo(() => {
    // Primary: provider_breakdown.video
    const videoFromBreakdown = currentUsage.provider_breakdown?.video?.calls ?? 0;
    
    // Debug logging (can be removed in production)
    if (videoFromBreakdown > 0) {
      console.log('[UsageLimitRings] Video calls calculation:', {
        video: videoFromBreakdown,
        provider_breakdown_keys: Object.keys(currentUsage.provider_breakdown || {})
      });
    }
    
    return videoFromBreakdown;
  }, [currentUsage.provider_breakdown]);

  const keyLimits = [
    {
      label: 'AI Calls',
      used: currentUsage.total_calls,
      limit: limits.limits.ai_text_generation_calls || limits.limits.gemini_calls || limits.limits.openai_calls || 50,
      color: '#3b82f6',
      unlimited: limits.limits.ai_text_generation_calls === 0 && limits.limits.gemini_calls === 0 && limits.limits.openai_calls === 0,
    },
    {
      label: 'Images',
      used: imageCalls,
      limit: limits.limits.stability_calls || 50,
      color: '#a855f7',
      unlimited: limits.limits.stability_calls === 0,
    },
    {
      label: 'Videos',
      used: videoCalls,
      limit: limits.limits.video_calls,
      color: '#ec4899',
      unlimited: limits.limits.video_calls === 0,
    },
    {
      label: 'Audio',
      used: currentUsage.provider_breakdown?.audio?.calls ?? 0,
      limit: limits.limits.audio_calls,
      color: '#22c55e',
      unlimited: limits.limits.audio_calls === 0,
    }
  ].filter(item => item.unlimited || item.limit > 0);

  if (keyLimits.length === 0) return null;

  return (
    <Box sx={{ mb: 3 }}>
      <TypographyComponent variant="subtitle2" sx={{ 
        fontWeight: 600,
        mb: 2,
        color: terminalTheme ? terminalColors.text : 'rgba(255,255,255,0.9)'
      }}>
        Usage Limits Overview
      </TypographyComponent>
      <Box sx={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 2 }}>
        {keyLimits.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1, duration: 0.4 }}
          >
            {item.unlimited ? (
              <Box
                sx={{
                  width: 100,
                  height: 100,
                  borderRadius: '50%',
                  border: `2px dashed ${item.color}`,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'rgba(255,255,255,0.04)',
                }}
              >
                <TypographyComponent sx={{ fontSize: 26, fontWeight: 700, color: item.color, lineHeight: 1 }}>∞</TypographyComponent>
                <TypographyComponent sx={{ fontSize: 10, opacity: 0.8, mt: 0.5 }}>{item.label}</TypographyComponent>
              </Box>
            ) : (
              <UsageLimitRing
                used={item.used}
                limit={item.limit}
                label={item.label}
                color={item.color}
                size={100}
                terminalTheme={terminalTheme}
                terminalColors={terminalColors}
              />
            )}
          </motion.div>
        ))}
      </Box>
    </Box>
  );
};
