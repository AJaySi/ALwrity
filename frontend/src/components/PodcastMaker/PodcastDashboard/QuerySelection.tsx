import React from "react";
import {
  Stack,
  Typography,
  Chip,
  Tooltip,
  Alert,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  alpha,
} from "@mui/material";
import { Search as SearchIcon, AutoAwesome as AutoAwesomeIcon } from "@mui/icons-material";
import { ResearchProvider } from "../../../services/blogWriterApi";
import { Query } from "../types";
import { GlassyCard, glassyCardSx, PrimaryButton } from "../ui";

interface QuerySelectionProps {
  queries: Query[];
  selectedQueries: Set<string>;
  researchProvider: ResearchProvider;
  isResearching: boolean;
  onToggleQuery: (id: string) => void;
  onProviderChange: (provider: ResearchProvider) => void;
  onRunResearch: () => void;
}

export const QuerySelection: React.FC<QuerySelectionProps> = ({
  queries,
  selectedQueries,
  researchProvider,
  isResearching,
  onToggleQuery,
  onProviderChange,
  onRunResearch,
}) => {
  const selectedCount = selectedQueries.size;

  return (
    <GlassyCard
      sx={{
        ...glassyCardSx,
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
        boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
        color: "#0f172a",
      }}
    >
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
          <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#0f172a", fontWeight: 700 }}>
            <SearchIcon />
            Research Queries
          </Typography>
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel>Provider</InputLabel>
              <Select
                value={researchProvider}
                onChange={(e) => onProviderChange(e.target.value as ResearchProvider)}
                label="Provider"
                disabled={isResearching}
                size="small"
                sx={{
                  backgroundColor: "#f8fafc",
                  "&:hover": {
                    backgroundColor: "#f1f5f9",
                  },
                }}
              >
                <MenuItem value="google">
                  <Stack direction="row" spacing={1} alignItems="center">
                    <SearchIcon fontSize="small" />
                    <span>Standard Research</span>
                  </Stack>
                </MenuItem>
                <MenuItem value="exa">
                  <Stack direction="row" spacing={1} alignItems="center">
                    <AutoAwesomeIcon fontSize="small" />
                    <span>Deep Research</span>
                  </Stack>
                </MenuItem>
              </Select>
            </FormControl>
            <Chip
              label={`${selectedCount} / ${queries.length} selected`}
              size="small"
              color={selectedCount > 0 ? "primary" : "default"}
            />
          </Stack>
        </Stack>

        <Tooltip
          title={
            researchProvider === "google"
              ? "Standard Research: Fast, fact-checked results with source citations"
              : "Deep Research: Comprehensive analysis with competitor insights and trending topics"
          }
          arrow
        >
          <Alert
            severity="info"
            sx={{
              background: "#e0f2fe",
              border: "1px solid #bae6fd",
              color: "#0f172a",
            }}
          >
            <Typography variant="caption" sx={{ color: "#0f172a" }}>
              {researchProvider === "google"
                ? "Select at least one query (recommended: 3+ for balanced coverage). Standard research provides fact-checked results with source citations."
                : "Select queries for deep research. This mode provides comprehensive analysis with competitor insights and trending topics."}
            </Typography>
          </Alert>
        </Tooltip>

        <List>
          {queries.map((q) => (
            <ListItem key={q.id} disablePadding>
              <ListItemButton
                onClick={() => onToggleQuery(q.id)}
                disabled={isResearching}
                sx={{
                  borderRadius: 2,
                  mb: 1,
                  border: "1px solid rgba(0,0,0,0.08)",
                  background: "#f8fafc",
                  "&:hover": { background: alpha("#667eea", 0.08) },
                }}
              >
                <Checkbox checked={selectedQueries.has(q.id)} edge="start" />
                <ListItemText
                  primary={q.query}
                  secondary={q.rationale}
                  primaryTypographyProps={{ variant: "body2", fontWeight: 600, color: "#0f172a" }}
                  secondaryTypographyProps={{ variant: "caption", sx: { color: "#475569" } }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
          <PrimaryButton
            onClick={onRunResearch}
            disabled={selectedCount === 0 || isResearching}
            loading={isResearching}
            startIcon={<SearchIcon />}
            tooltip={
              selectedCount === 0
                ? "Select at least one query to run research"
                : `Run research with ${selectedCount} selected ${selectedCount === 1 ? "query" : "queries"}`
            }
          >
            {isResearching ? "Running Research..." : "Run Research"}
          </PrimaryButton>
        </Box>
      </Stack>
    </GlassyCard>
  );
};

