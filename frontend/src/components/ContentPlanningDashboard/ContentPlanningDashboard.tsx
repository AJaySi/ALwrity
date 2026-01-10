import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Container,
  AppBar,
  Toolbar,
  IconButton,
  Alert,
  Drawer,
  Button,
  Badge
} from '@mui/material';
import {
  Psychology as StrategyIcon,
  CalendarToday as CalendarIcon,
  Analytics as AnalyticsIcon,
  Search as SearchIcon,
  Lightbulb as AIInsightsIcon,
  Close as CloseIcon,
  Add as CreateIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import ContentStrategyTab from './tabs/ContentStrategyTab';
import CalendarTab from './tabs/CalendarTab';
import AnalyticsTab from './tabs/AnalyticsTab';
import GapAnalysisTab from './tabs/GapAnalysisTab';
import CreateTab from './tabs/CreateTab';
import AIInsightsPanel from './components/AIInsightsPanel';
import SystemStatusIndicator from './components/SystemStatusIndicator';
import ProgressIndicator from './components/ProgressIndicator';
import { useContentPlanningStore } from '../../stores/contentPlanningStore';
import { 
  contentPlanningOrchestrator, 
  DashboardData 
} from '../../services/contentPlanningOrchestrator';
import { StrategyCalendarProvider } from '../../contexts/StrategyCalendarContext';

// CopilotKit actions will be initialized in a separate component

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`content-planning-tabpanel-${index}`}
      aria-labelledby={`content-planning-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `content-planning-tab-${index}`,
    'aria-controls': `content-planning-tabpanel-${index}`,
  };
}

const ContentPlanningDashboard: React.FC = () => {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    strategies: [],
    gapAnalyses: [],
    aiInsights: [],
    aiRecommendations: [],
    calendarEvents: [],
    healthStatus: {
      backend: false,
      database: false,
      aiServices: false
    }
  });
  const [progressExpanded, setProgressExpanded] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiInsightsDrawerOpen, setAiInsightsDrawerOpen] = useState(false);

  const { 
    updateStrategies,
    updateCalendarEvents,
    updateGapAnalyses,
    updateAIInsights
  } = useContentPlanningStore();

  // CopilotKit actions will be initialized in a separate component
  // that's rendered inside the CopilotSidebar context

  // Initialize orchestrator callbacks
  useEffect(() => {
    contentPlanningOrchestrator.setDataUpdateCallback((data) => {
      setDashboardData(prev => ({ ...prev, ...data }));
      
      // Update store with new data
      if (data.strategies) updateStrategies(data.strategies);
      if (data.calendarEvents) updateCalendarEvents(data.calendarEvents);
      if (data.gapAnalyses) updateGapAnalyses(data.gapAnalyses);
      if (data.aiInsights || data.aiRecommendations) {
        updateAIInsights({
          insights: data.aiInsights || [],
          recommendations: data.aiRecommendations || []
        });
      }
    });
  }, [updateStrategies, updateCalendarEvents, updateGapAnalyses, updateAIInsights]);

  // Handle navigation state for active tab
  useEffect(() => {
    if (location.state?.activeTab !== undefined) {
      setActiveTab(location.state.activeTab);
    }
  }, [location.state]);

  // Load dashboard data using orchestrator
  // Note: ProtectedRoute ensures user is authenticated before this component renders
  useEffect(() => {
    const loadDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        await contentPlanningOrchestrator.loadDashboardData();
        setLoading(false);
      } catch (error: any) {
        console.error('Error loading dashboard data:', error);
        setError(error.message || 'Failed to load dashboard data');
        setLoading(false);
      }
    };

    // Wrap in try-catch to handle any unexpected errors
    try {
      loadDashboardData();
    } catch (error: any) {
      console.error('Unexpected error in dashboard:', error);
      setError('An unexpected error occurred while loading the dashboard');
      setLoading(false);
    }
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const tabs = [
    { label: 'CONTENT STRATEGY', icon: <StrategyIcon />, component: <ContentStrategyTab /> },
    { label: 'CALENDAR', icon: <CalendarIcon />, component: <CalendarTab /> },
    { label: 'ANALYTICS', icon: <AnalyticsIcon />, component: <AnalyticsTab /> },
    { label: 'GAP ANALYSIS', icon: <SearchIcon />, component: <GapAnalysisTab /> },
    { label: 'CREATE', icon: <CreateIcon />, component: <CreateTab /> }
  ];

  const totalAIItems = (dashboardData.aiInsights?.length || 0) + (dashboardData.aiRecommendations?.length || 0);

  return (
    <StrategyCalendarProvider>
      <Container maxWidth={false} sx={{ height: '100vh', p: 0 }}>
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Content Planning Dashboard
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <SystemStatusIndicator />
            
            {/* AI Insights Button with Badge */}
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button
                variant="outlined"
                startIcon={<AIInsightsIcon />}
                onClick={() => setAiInsightsDrawerOpen(true)}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  '&:hover': {
                    borderColor: 'primary.dark',
                    backgroundColor: 'primary.50'
                  }
                }}
              >
                <Badge badgeContent={totalAIItems} color="primary" sx={{ mr: 1 }}>
                  AI Insights
                </Badge>
              </Button>
            </motion.div>
          </Box>
        </Toolbar>
      </AppBar>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      {/* Progress Indicator */}
      {loading && (
        <Box sx={{ m: 2 }}>
          <ProgressIndicator
            expanded={progressExpanded}
            onToggleExpanded={() => setProgressExpanded(!progressExpanded)}
          />
        </Box>
      )}

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            aria-label="content planning tabs"
            sx={{
              '& .MuiTab-root': {
                textTransform: 'none',
                fontWeight: 600,
                minHeight: 64,
                fontSize: '0.875rem'
              }
            }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {tab.icon}
                    {tab.label}
                  </Box>
                }
                {...a11yProps(index)}
              />
            ))}
          </Tabs>
        </Box>

        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {tabs.map((tab, index) => (
                <TabPanel key={index} value={activeTab} index={index}>
                  {tab.component}
                </TabPanel>
              ))}
            </motion.div>
          </AnimatePresence>
        </Box>
      </Box>

      {/* AI Insights Drawer */}
      <Drawer
        anchor="right"
        open={aiInsightsDrawerOpen}
        onClose={() => setAiInsightsDrawerOpen(false)}
        PaperProps={{
          sx: {
            width: { xs: '100%', sm: 400 },
            maxWidth: '100vw'
          }
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">AI Insights & Recommendations</Typography>
            <IconButton onClick={() => setAiInsightsDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
        <AIInsightsPanel />
      </Drawer>
    </Container>
    </StrategyCalendarProvider>
  );
};

export default ContentPlanningDashboard; 