import React, { useState } from 'react';
import {
  Box,
  Container,
  Alert,
  Snackbar,
  useTheme
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import AskAlwrityIcon from '../../assets/images/AskAlwrity-min.ico';

// Shared components
import DashboardHeader from '../shared/DashboardHeader';
import SystemStatusIndicator from '../ContentPlanningDashboard/components/SystemStatusIndicator';
import LoadingSkeleton from '../shared/LoadingSkeleton';
import ErrorDisplay from '../shared/ErrorDisplay';
import ContentLifecyclePillars from './ContentLifecyclePillars';
import AnalyticsInsights from './components/AnalyticsInsights';
import ToolsModal from './components/ToolsModal';
import EnhancedBillingDashboard from '../billing/EnhancedBillingDashboard';
import CompactSidebar from './components/CompactSidebar';

// Shared types and utilities
import { Tool } from '../shared/types';
import { getFilteredCategories, getToolsForCategory } from '../shared/utils';

// Zustand stores
import { useDashboardStore } from '../../stores/dashboardStore';
import { useWorkflowStore } from '../../stores/workflowStore';

// Data
import { toolCategories } from '../../data/toolCategories';

// Main dashboard component
const MainDashboard: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  
  // Sidebar state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true);
  
  // Zustand store hooks
  const {
    loading,
    error,
    searchQuery,
    selectedCategory,
    selectedSubCategory,
    favorites,
    snackbar,
    toggleFavorite,
    setSearchQuery,
    setSelectedCategory,
    setSelectedSubCategory,
    showSnackbar,
    hideSnackbar,
  } = useDashboardStore();

  // Workflow store hooks
  const {
    currentWorkflow,
    workflowProgress,
    isLoading: workflowLoading,
    generateDailyWorkflow,
    startWorkflow,
    pauseWorkflow,
    stopWorkflow
  } = useWorkflowStore();

  // Initialize workflow on component mount
  React.useEffect(() => {
    const initializeWorkflow = async () => {
      try {
        // Generate daily workflow for current user
        // In a real app, you'd get the actual user ID from auth context
        const userId = 'demo-user'; // Replace with actual user ID
        await generateDailyWorkflow(userId);
      } catch (error) {
        console.warn('Failed to initialize workflow:', error);
      }
    };

    initializeWorkflow();
  }, [generateDailyWorkflow]);

  // Debug logging for workflow state
  React.useEffect(() => {
    console.log('Workflow Debug:', {
      currentWorkflow,
      workflowProgress,
      isWorkflowActive: currentWorkflow?.workflowStatus === 'in_progress',
      workflowStatus: currentWorkflow?.workflowStatus,
      hasWorkflow: !!currentWorkflow
    });
  }, [currentWorkflow, workflowProgress]);

  // State to track if we need to start a newly generated workflow
  const [shouldStartWorkflow, setShouldStartWorkflow] = React.useState(false);

  // Tools Modal state
  const [toolsModalOpen, setToolsModalOpen] = React.useState(false);
  const [modalCategoryName, setModalCategoryName] = React.useState<string | null>(null);
  const [modalCategory, setModalCategory] = React.useState<any>(null);
  const [searchResults, setSearchResults] = React.useState<Tool[]>([]);

  // Handle workflow start
  const handleStartWorkflow = async () => {
    try {
      if (currentWorkflow) {
        await startWorkflow(currentWorkflow.id);
      } else {
        // Generate workflow first, then mark that we should start it
        await generateDailyWorkflow('demo-user');
        setShouldStartWorkflow(true);
      }
    } catch (error) {
      console.error('Failed to start workflow:', error);
    }
  };

  // Auto-start workflow after generation
  React.useEffect(() => {
    if (shouldStartWorkflow && currentWorkflow && currentWorkflow.workflowStatus === 'not_started') {
      const startGeneratedWorkflow = async () => {
        try {
          await startWorkflow(currentWorkflow.id);
          setShouldStartWorkflow(false);
        } catch (error) {
          console.error('Failed to start generated workflow:', error);
          setShouldStartWorkflow(false);
        }
      };
      startGeneratedWorkflow();
    }
  }, [shouldStartWorkflow, currentWorkflow, startWorkflow]);

  // Handle workflow pause
  const handlePauseWorkflow = async () => {
    if (currentWorkflow) {
      try {
        await pauseWorkflow(currentWorkflow.id);
      } catch (error) {
        console.error('Failed to pause workflow:', error);
      }
    }
  };

  // Handle workflow stop
  const handleStopWorkflow = async () => {
    if (currentWorkflow) {
      try {
        await stopWorkflow(currentWorkflow.id);
      } catch (error) {
        console.error('Failed to stop workflow:', error);
      }
    }
  };

  // Resume Plan modal from header In-Progress button
  const handleResumePlanModal = () => {
    // Programmatically click the Plan pillar Today chip
    const planChip = document.querySelector('[data-pillar-id="plan"]');
    if (planChip) {
      (planChip as HTMLElement).click();
    }
  };

  const handleToolClick = (tool: Tool) => {
    console.log('Navigating to tool:', tool.path);
    if (tool.path) {
      navigate(tool.path);
      return;
    }
    showSnackbar(`Launching ${tool.name}...`, 'info');
  };

  // Handle category click to open modal
  const handleCategoryClick = (categoryName: string | null, categoryData?: any) => {
    setModalCategoryName(categoryName);
    setModalCategory(categoryData);
    setToolsModalOpen(true);
  };

  // Handle search to show results in modal with debouncing
  React.useEffect(() => {
    if (searchQuery && searchQuery.length >= 2) { // Only search after 2+ characters
      const timeoutId = setTimeout(() => {
        // Get all tools from all categories that match search
        const allTools: Tool[] = [];
        Object.values(toolCategories).forEach(category => {
          if (category) {
            const tools = getToolsForCategory(category, null);
            allTools.push(...tools);
          }
        });
        
        const filtered = allTools.filter(tool => 
          tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          tool.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          tool.features.some(feature => feature.toLowerCase().includes(searchQuery.toLowerCase()))
        );
        
        setSearchResults(filtered);
        setModalCategoryName(null);
        setModalCategory(null);
        setToolsModalOpen(true);
      }, 500); // 500ms delay

      return () => clearTimeout(timeoutId);
    } else if (searchQuery && searchQuery.length < 2) {
      // Close modal if search query is too short
      setToolsModalOpen(false);
    }
  }, [searchQuery]);

  // Close modal and clear search
  const handleCloseModal = () => {
    setToolsModalOpen(false);
    setModalCategoryName(null);
    setModalCategory(null);
    setSearchResults([]);
    if (searchQuery) {
      setSearchQuery('');
    }
  };

  // Note: filteredCategories removed as it's not used in the current implementation

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return <ErrorDisplay error={error} />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        padding: theme.spacing(4),
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.03"%3E%3Ccircle cx="40" cy="40" r="3"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          pointerEvents: 'none',
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '50%',
          left: '50%',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          transform: 'translate(-50%, -50%)',
          pointerEvents: 'none',
          zIndex: 0,
        },
      }}
    >
      <Container 
        maxWidth="xl" 
        sx={{ 
          position: 'relative', 
          zIndex: 1,
        }}
      >
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Dashboard Header */}
            <DashboardHeader
              title="Alwrity Content Hub"
              subtitle=""
              statusChips={[]}
              rightContent={<SystemStatusIndicator />}
              customIcon={AskAlwrityIcon}
              workflowControls={{
                onStartWorkflow: handleStartWorkflow,
                onPauseWorkflow: handlePauseWorkflow,
                onStopWorkflow: handleStopWorkflow,
                onResumePlanModal: handleResumePlanModal,
                isWorkflowActive: currentWorkflow?.workflowStatus === 'in_progress',
                completedTasks: workflowProgress?.completedTasks || 0,
                totalTasks: workflowProgress?.totalTasks || 0,
                isLoading: workflowLoading
              }}
            />


            {/* Content Lifecycle Pillars - First Panel */}
            <ContentLifecyclePillars />

            {/* Side-by-side layout for Areas 2 and 3 */}
            <Box sx={{ display: 'flex', gap: 3, mt: 3 }}>
              {/* Area 2: Search Tools Sidebar */}
              <Box sx={{ 
                width: sidebarCollapsed ? 60 : 280,
                transition: 'width 0.3s ease-in-out',
                flexShrink: 0
              }}>
                <CompactSidebar
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  onClearSearch={() => setSearchQuery('')}
                  selectedCategory={selectedCategory}
                  onCategoryChange={setSelectedCategory}
                  selectedSubCategory={selectedSubCategory}
                  onSubCategoryChange={setSelectedSubCategory}
                  toolCategories={toolCategories}
                  onCategoryClick={handleCategoryClick}
                  collapsed={sidebarCollapsed}
                  onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
                  theme={theme}
                  favorites={favorites}
                  onToolClick={handleToolClick}
                />
              </Box>

              {/* Area 3: Analytics and Billing */}
              <Box sx={{ flex: 1, minWidth: 0 }}>
                {/* Analytics Insights - Good/Bad/Ugly */}
                <AnalyticsInsights />

                {/* Billing & Usage Dashboard */}
                <EnhancedBillingDashboard />
              </Box>
            </Box>

            {/* Tools Modal */}
            <ToolsModal
              open={toolsModalOpen}
              onClose={handleCloseModal}
              categoryName={modalCategoryName || undefined}
              category={modalCategory}
              searchQuery={searchQuery}
              searchResults={searchResults}
              onToolClick={handleToolClick}
              favorites={favorites}
              onToggleFavorite={toggleFavorite}
            />
          </motion.div>
        </AnimatePresence>

        {/* Enhanced Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={3000}
          onClose={hideSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={hideSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </Box>
  );
};

export default MainDashboard; 