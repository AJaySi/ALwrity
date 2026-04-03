import React from "react";
import { Stack, Box, Typography, Chip, Paper } from "@mui/material";
import { Search as SearchIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface ResearchTabProps {
  analysis: PodcastAnalysis;
}

export const ResearchTab: React.FC<ResearchTabProps> = ({ analysis }) => {
  if (!analysis.research_queries || analysis.research_queries.length === 0) {
    return (
      <AnalysisTabContent title="Research Queries" icon={<SearchIcon />}>
        <Typography variant="body2" sx={{ color: "#64748b" }}>
          No research queries generated yet.
        </Typography>
      </AnalysisTabContent>
    );
  }

  return (
    <AnalysisTabContent title="Research Queries" icon={<SearchIcon />}>
      <Stack spacing={2}>
        {analysis.research_queries.map((rq: { query: string; rationale: string }, idx: number) => (
          <Paper key={idx} elevation={0} sx={{ p: 2, bgcolor: "#f8fafc", border: "1px solid rgba(0,0,0,0.08)", borderRadius: 2 }}>
            <Stack direction="row" alignItems="flex-start" gap={1.5}>
              <Chip label={idx + 1} size="small" sx={{ minWidth: 24, bgcolor: "#4f46e5", color: "#fff" }} />
              <Box>
                <Typography variant="body2" sx={{ color: "#0f172a", fontWeight: 600, mb: 0.5 }}>
                  {rq.query}
                </Typography>
                <Typography variant="caption" sx={{ color: "#64748b" }}>
                  Rationale: {rq.rationale}
                </Typography>
              </Box>
            </Stack>
          </Paper>
        ))}
      </Stack>
    </AnalysisTabContent>
  );
};
