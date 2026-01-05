/**
 * IntentConfirmationPanel Module
 * 
 * Refactored modular components for intent confirmation panel.
 * Each component handles a specific responsibility.
 */

export { IntentConfirmationPanel } from './IntentConfirmationPanel';
export type { IntentConfirmationPanelProps } from './IntentConfirmationPanel';

// Export sub-components for potential reuse
export { LoadingState } from './LoadingState';
export { EditableField } from './EditableField';
export { IntentConfirmationHeader } from './IntentConfirmationHeader';
export { PrimaryQuestionEditor } from './PrimaryQuestionEditor';
export { IntentSummaryGrid } from './IntentSummaryGrid';
export { DeliverablesSelector } from './DeliverablesSelector';
export { QueryEditor } from './QueryEditor';
export { ResearchQueriesSection } from './ResearchQueriesSection';
export { TrendsConfigSection } from './TrendsConfigSection';
export { AdvancedProviderOptionsSection } from './AdvancedProviderOptionsSection';
export { ExpandableDetails } from './ExpandableDetails';
export { ActionButtons } from './ActionButtons';
