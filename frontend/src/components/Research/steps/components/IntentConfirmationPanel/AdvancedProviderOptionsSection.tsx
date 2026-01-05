/**
 * AdvancedProviderOptionsSection Component
 * 
 * Advanced provider options section with AI-optimized settings.
 * This is specific to IntentConfirmationPanel and includes AI justifications.
 */

import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Tooltip,
  Button,
} from '@mui/material';
import {
  Info as InfoIcon,
} from '@mui/icons-material';
import { AnalyzeIntentResponse } from '../../../types/intent.types';
import { ProviderAvailability } from '../../../../../api/researchConfig';
import { ExaOptions } from '../ExaOptions';
import { TavilyOptions } from '../TavilyOptions';
import { ProviderChips } from '../ProviderChips';
import { ResearchProvider } from '../../../../../services/blogWriterApi';

interface AdvancedProviderOptionsSectionProps {
  intentAnalysis: AnalyzeIntentResponse;
  providerAvailability: ProviderAvailability;
  config: any;
  onConfigUpdate: (updates: any) => void;
  showAdvancedOptions: boolean;
  onAdvancedOptionsChange: (show: boolean) => void;
}

export const AdvancedProviderOptionsSection: React.FC<AdvancedProviderOptionsSectionProps> = ({
  intentAnalysis,
  providerAvailability,
  config,
  onConfigUpdate,
  showAdvancedOptions,
  onAdvancedOptionsChange,
}) => {
  return (
    <>
      {/* Toggle Advanced Options Button */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
        <Button
          size="small"
          variant="text"
          onClick={() => onAdvancedOptionsChange(!showAdvancedOptions)}
          sx={{
            color: '#64748b',
            fontSize: '12px',
            '&:hover': {
              backgroundColor: '#f8fafc',
              color: '#0ea5e9',
            },
          }}
        >
          {showAdvancedOptions ? '▲ Hide Advanced Options' : '▼ Show Advanced Options'}
        </Button>
      </Box>

      {/* Advanced Options Section */}
      {showAdvancedOptions && (
        <Box sx={{
          mt: 2,
          pt: 2,
          borderTop: '1px dashed rgba(14, 165, 233, 0.3)',
        }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography
              variant="subtitle2"
              sx={{
                color: '#0c4a6e',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              ⚙️ AI-Optimized Settings
            </Typography>
            <Tooltip title="These settings were AI-configured based on your research intent. Hover over each for explanation." arrow>
              <InfoIcon sx={{ fontSize: 16, color: '#94a3b8', cursor: 'help' }} />
            </Tooltip>
          </Box>

          {/* AI Justification Banner */}
          {intentAnalysis?.optimized_config?.provider_justification && (
            <Box sx={{
              mb: 2,
              p: 1.5,
              backgroundColor: '#f0fdf4',
              border: '1px solid #86efac',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 1,
            }}>
              <span style={{ fontSize: '14px' }}>🤖</span>
              <Typography variant="body2" sx={{ color: '#166534', fontSize: '12px' }}>
                <strong>AI Recommendation:</strong> {intentAnalysis.optimized_config.provider_justification}
              </Typography>
            </Box>
          )}

          {/* Provider Selection with Justification */}
          <Box mb={2}>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <Typography variant="caption" color="#666" fontWeight={600}>
                Research Provider
              </Typography>
              {intentAnalysis?.optimized_config?.provider_justification && (
                <Tooltip title={intentAnalysis.optimized_config.provider_justification} arrow>
                  <Chip
                    label="AI"
                    size="small"
                    sx={{
                      height: '16px',
                      fontSize: '9px',
                      backgroundColor: '#dcfce7',
                      color: '#166534',
                    }}
                  />
                </Tooltip>
              )}
            </Box>
            <ProviderChips providerAvailability={providerAvailability} />
            {/* Provider Selector */}
            <Box sx={{ mt: 1 }}>
              <select
                value={config.provider || 'exa'}
                onChange={(e) => onConfigUpdate({ provider: e.target.value as ResearchProvider })}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0',
                  fontSize: '13px',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                }}
              >
                {providerAvailability.exa_available && <option value="exa">Exa</option>}
                {providerAvailability.tavily_available && <option value="tavily">Tavily</option>}
                <option value="google">Google</option>
              </select>
            </Box>
          </Box>

          {/* Provider-specific Options with AI tooltips */}
          {config.provider === 'exa' && providerAvailability.exa_available && (
            <>
              {/* AI Settings Summary for Exa */}
              {intentAnalysis?.optimized_config && (
                <Box sx={{
                  mb: 2,
                  p: 1.5,
                  backgroundColor: '#f8fafc',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0',
                }}>
                  <Typography variant="caption" color="#666" fontWeight={600} gutterBottom display="block">
                    AI-Selected Exa Settings
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                    {intentAnalysis.optimized_config.exa_type && (
                      <Tooltip title={intentAnalysis.optimized_config.exa_type_justification || 'Search type'} arrow>
                        <Chip
                          label={`Type: ${intentAnalysis.optimized_config.exa_type}`}
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#e0f2fe', color: '#0369a1' }}
                        />
                      </Tooltip>
                    )}
                    {intentAnalysis.optimized_config.exa_category && (
                      <Tooltip title={intentAnalysis.optimized_config.exa_category_justification || 'Category focus'} arrow>
                        <Chip
                          label={`Category: ${intentAnalysis.optimized_config.exa_category}`}
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#fef3c7', color: '#92400e' }}
                        />
                      </Tooltip>
                    )}
                    {intentAnalysis.optimized_config.exa_date_filter && (
                      <Tooltip title={intentAnalysis.optimized_config.exa_date_justification || 'Date filter'} arrow>
                        <Chip
                          label={`Since: ${intentAnalysis.optimized_config.exa_date_filter.split('T')[0]}`}
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#f3e8ff', color: '#7c3aed' }}
                        />
                      </Tooltip>
                    )}
                  </Box>
                </Box>
              )}
              <ExaOptions
                config={config}
                onConfigUpdate={onConfigUpdate}
              />
            </>
          )}

          {config.provider === 'tavily' && providerAvailability.tavily_available && (
            <>
              {/* AI Settings Summary for Tavily */}
              {intentAnalysis?.optimized_config && (
                <Box sx={{
                  mb: 2,
                  p: 1.5,
                  backgroundColor: '#f8fafc',
                  borderRadius: '6px',
                  border: '1px solid #e2e8f0',
                }}>
                  <Typography variant="caption" color="#666" fontWeight={600} gutterBottom display="block">
                    AI-Selected Tavily Settings
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                    {intentAnalysis.optimized_config.tavily_topic && (
                      <Tooltip title={intentAnalysis.optimized_config.tavily_topic_justification || 'Topic category'} arrow>
                        <Chip
                          label={`Topic: ${intentAnalysis.optimized_config.tavily_topic}`}
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#e0f2fe', color: '#0369a1' }}
                        />
                      </Tooltip>
                    )}
                    {intentAnalysis.optimized_config.tavily_search_depth && (
                      <Tooltip title={intentAnalysis.optimized_config.tavily_search_depth_justification || 'Search depth'} arrow>
                        <Chip
                          label={`Depth: ${intentAnalysis.optimized_config.tavily_search_depth}`}
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#fef3c7', color: '#92400e' }}
                        />
                      </Tooltip>
                    )}
                    {intentAnalysis.optimized_config.tavily_time_range && (
                      <Tooltip title={intentAnalysis.optimized_config.tavily_time_range_justification || 'Time filter'} arrow>
                        <Chip
                          label={`Time: ${intentAnalysis.optimized_config.tavily_time_range}`}
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#dcfce7', color: '#166534' }}
                        />
                      </Tooltip>
                    )}
                    {intentAnalysis.optimized_config.tavily_include_answer && (
                      <Tooltip title={intentAnalysis.optimized_config.tavily_include_answer_justification || 'AI answer'} arrow>
                        <Chip
                          label="AI Answer ✓"
                          size="small"
                          sx={{ fontSize: '11px', backgroundColor: '#f3e8ff', color: '#7c3aed' }}
                        />
                      </Tooltip>
                    )}
                  </Box>
                </Box>
              )}
              <TavilyOptions
                config={config}
                onConfigUpdate={onConfigUpdate}
              />
            </>
          )}
        </Box>
      )}
    </>
  );
};
