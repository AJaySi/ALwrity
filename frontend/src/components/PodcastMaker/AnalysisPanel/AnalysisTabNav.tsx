import React from "react";
import { Stack, Button, Typography, Box } from "@mui/material";
import { Input as InputIcon, Groups as GroupsIcon, ListAlt as ListAltIcon, EditNote as EditNoteIcon, Search as SearchIcon, AutoAwesome as AutoAwesomeIcon, Lightbulb as TipsIcon, Quiz as TalkIcon, RecordVoiceOver as VoiceIcon } from "@mui/icons-material";

export type TabId = "inputs" | "audience" | "content" | "outline" | "titles" | "research" | "hook" | "takeaways" | "guest" | "cta";

interface TabConfig {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

export const ANALYSIS_TABS: TabConfig[] = [
  { id: "inputs", label: "Your Inputs", icon: <InputIcon /> },
  { id: "audience", label: "Audience", icon: <GroupsIcon /> },
  { id: "content", label: "Content", icon: <ListAltIcon /> },
  { id: "outline", label: "Outline", icon: <ListAltIcon /> },
  { id: "titles", label: "Titles", icon: <EditNoteIcon /> },
  { id: "research", label: "Research", icon: <SearchIcon /> },
  { id: "hook", label: "Hook", icon: <AutoAwesomeIcon /> },
  { id: "takeaways", label: "Takeaways", icon: <TipsIcon /> },
  { id: "guest", label: "Guest", icon: <TalkIcon /> },
  { id: "cta", label: "CTA", icon: <VoiceIcon /> },
];

const getTabButtonStyles = (isActive: boolean) => ({
  background: isActive
    ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    : "transparent",
  color: isActive ? "#fff" : "#64748b",
  border: isActive ? "none" : "1px solid rgba(0,0,0,0.1)",
  borderRadius: 2,
  px: 2,
  py: 1,
  fontSize: "0.75rem",
  fontWeight: 600,
  textTransform: "none" as const,
  transition: "all 0.2s ease",
  "&:hover": {
    background: isActive
      ? "linear-gradient(135deg, #764ba2 0%, #667eea 100%)"
      : "rgba(102,126,234,0.08)",
  },
});

interface AnalysisTabNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export const AnalysisTabNav: React.FC<AnalysisTabNavProps> = ({ activeTab, onTabChange }) => {
  return (
    <Stack direction="row" flexWrap="wrap" gap={1}>
      {ANALYSIS_TABS.map((tab) => (
        <Button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          startIcon={tab.icon}
          sx={getTabButtonStyles(activeTab === tab.id)}
        >
          {tab.label}
        </Button>
      ))}
    </Stack>
  );
};

export const AnalysisTabContent: React.FC<{ children: React.ReactNode; title?: string; icon?: React.ReactNode }> = ({
  children,
  title,
  icon,
}) => (
  <Box>
    {title && (
      <Typography
        variant="subtitle2"
        sx={{
          mb: 2,
          color: "#0f172a",
          fontWeight: 700,
          display: "flex",
          alignItems: "center",
          gap: 0.5,
        }}
      >
        {icon}
        {title}
      </Typography>
    )}
    {children}
  </Box>
);
