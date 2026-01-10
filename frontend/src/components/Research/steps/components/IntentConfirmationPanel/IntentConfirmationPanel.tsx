/**
 * IntentConfirmationPanel Component (Refactored)
 * 
 * Main orchestrator component that composes smaller, focused components.
 * Shows the AI-inferred research intent and allows user to confirm or modify.
 */

import React, { useState, useEffect } from 'react';
import { Paper, Box } from '@mui/material';
import {
  ResearchIntent,
  AnalyzeIntentResponse,
  ResearchQuery,
  ExpectedDeliverable,
  TrendsConfig,
} from '../../../types/intent.types';
import { ProviderAvailability } from '../../../../../api/researchConfig';

// Sub-components
import { LoadingState } from './LoadingState';
import { IntentConfirmationHeader } from './IntentConfirmationHeader';
import { PrimaryQuestionEditor } from './PrimaryQuestionEditor';
import { IntentSummaryGrid } from './IntentSummaryGrid';
import { DeliverablesSelector } from './DeliverablesSelector';
import { ResearchQueriesSection } from './ResearchQueriesSection';
import { TrendsConfigSection } from './TrendsConfigSection';
import { AdvancedProviderOptionsSection } from './AdvancedProviderOptionsSection';
import { ExpandableDetails } from './ExpandableDetails';
import { ActionButtons } from './ActionButtons';

export interface IntentConfirmationPanelProps {
  isAnalyzing: boolean;
  intentAnalysis: AnalyzeIntentResponse | null;
  confirmedIntent: ResearchIntent | null;
  onConfirm: (intent: ResearchIntent, state?: any) => void; // Added optional state parameter
  onUpdateField: <K extends keyof ResearchIntent>(field: K, value: ResearchIntent[K]) => void;
  onExecute: (selectedQueries?: ResearchQuery[]) => void;
  onDismiss: () => void;
  isExecuting: boolean;
  showAdvancedOptions?: boolean;
  onAdvancedOptionsChange?: (show: boolean) => void;
  providerAvailability?: ProviderAvailability | null;
  config?: any;
  onConfigUpdate?: (updates: any) => void;
  wizardState?: any; // Add wizard state for draft saving
}

export const IntentConfirmationPanel: React.FC<IntentConfirmationPanelProps> = ({
  isAnalyzing,
  intentAnalysis,
  confirmedIntent,
  onConfirm,
  onUpdateField,
  onExecute,
  onDismiss,
  isExecuting,
  showAdvancedOptions = false,
  onAdvancedOptionsChange,
  providerAvailability,
  config,
  onConfigUpdate,
  wizardState,
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [selectedQueries, setSelectedQueries] = useState<Set<number>>(
    new Set(intentAnalysis?.suggested_queries?.map((_, idx) => idx) || [])
  );
  const [editedQueries, setEditedQueries] = useState<ResearchQuery[]>(
    intentAnalysis?.suggested_queries || []
  );
  const [editedTrendsConfig, setEditedTrendsConfig] = useState<TrendsConfig | null>(
    intentAnalysis?.trends_config || null
  );

  // Update edited queries and trends config when intentAnalysis changes
  useEffect(() => {
    if (intentAnalysis?.suggested_queries) {
      setEditedQueries(intentAnalysis.suggested_queries);
      setSelectedQueries(new Set(intentAnalysis.suggested_queries.map((_, idx) => idx)));
    }
    if (intentAnalysis?.trends_config) {
      setEditedTrendsConfig(intentAnalysis.trends_config);
    }
  }, [intentAnalysis]);

  // Loading state
  if (isAnalyzing) {
    return <LoadingState />;
  }

  // No analysis yet
  if (!intentAnalysis || !intentAnalysis.success) {
    return null;
  }

  const intent = intentAnalysis.intent;

  const handleDeliverableToggle = (deliverable: ExpectedDeliverable) => {
    const current = intent.expected_deliverables || [];
    const updated = current.includes(deliverable)
      ? current.filter(d => d !== deliverable)
      : [...current, deliverable];
    onUpdateField('expected_deliverables', updated);
  };

  const handleExecute = () => {
    const updatedIntent = { ...intent };
    // Pass wizard state to onConfirm for draft saving
    onConfirm(updatedIntent, wizardState);
    const queriesToUse = Array.from(selectedQueries)
      .sort((a, b) => a - b)
      .map(idx => editedQueries[idx])
      .filter(q => q && q.query.trim().length > 0);
    
    // Store updated trends config in intentAnalysis for execution
    // The execution hook will use trends_config from intentAnalysis
    if (editedTrendsConfig && intentAnalysis) {
      intentAnalysis.trends_config = editedTrendsConfig;
    }
    
    onExecute(queriesToUse);
  };

  const handleTrendsConfigUpdate = (updatedConfig: TrendsConfig) => {
    setEditedTrendsConfig(updatedConfig);
    // Also update intentAnalysis to keep it in sync
    if (intentAnalysis) {
      intentAnalysis.trends_config = updatedConfig;
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        mt: 2,
        borderRadius: 2,
        border: '1px solid #e0e0e0',
        backgroundColor: '#ffffff',
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      }}
    >
      {/* Header */}
      <IntentConfirmationHeader
        intentAnalysis={intentAnalysis}
        onDismiss={onDismiss}
      />

      {/* Main Content */}
      <Box sx={{ p: 2, backgroundColor: '#ffffff' }}>
        {/* Primary Question */}
        <PrimaryQuestionEditor
          intent={intent}
          onUpdate={(value) => onUpdateField('primary_question', value)}
        />

        {/* Quick Summary Grid */}
        <IntentSummaryGrid
          intent={intent}
          queriesCount={editedQueries.length}
          onUpdateField={onUpdateField}
        />

        {/* Deliverables Selector */}
        <DeliverablesSelector
          intent={intent}
          onToggle={handleDeliverableToggle}
        />

        {/* Research Queries Section */}
        <ResearchQueriesSection
          queries={editedQueries}
          selectedQueries={selectedQueries}
          onQueriesChange={setEditedQueries}
          onSelectionChange={setSelectedQueries}
        />

        {/* Google Trends Section */}
        {editedTrendsConfig && (
          <TrendsConfigSection 
            trendsConfig={editedTrendsConfig}
            onUpdate={handleTrendsConfigUpdate}
          />
        )}

        {/* Advanced Options Section */}
        {providerAvailability && config && onConfigUpdate && onAdvancedOptionsChange && (
          <AdvancedProviderOptionsSection
            intentAnalysis={intentAnalysis}
            providerAvailability={providerAvailability}
            config={config}
            onConfigUpdate={onConfigUpdate}
            showAdvancedOptions={showAdvancedOptions}
            onAdvancedOptionsChange={onAdvancedOptionsChange}
          />
        )}

        {/* Expandable Details */}
        <ExpandableDetails
          intentAnalysis={intentAnalysis}
          expanded={showDetails}
          intent={intent}
          onUpdateField={onUpdateField}
        />

        {/* Action Buttons */}
        <ActionButtons
          showDetails={showDetails}
          onToggleDetails={() => setShowDetails(!showDetails)}
          onExecute={handleExecute}
          isExecuting={isExecuting}
          canExecute={selectedQueries.size > 0}
        />
      </Box>
    </Paper>
  );
};

export default IntentConfirmationPanel;
