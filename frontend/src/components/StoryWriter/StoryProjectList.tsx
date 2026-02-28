import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography,
  alpha,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import RefreshIcon from "@mui/icons-material/Refresh";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import StarIcon from "@mui/icons-material/Star";
import StarBorderIcon from "@mui/icons-material/StarBorder";
import DeleteIcon from "@mui/icons-material/Delete";
import { GlassyCard, PrimaryButton, SecondaryButton } from "../PodcastMaker/ui";
import {
  storyWriterApi,
  StoryProjectSummary,
  StoryProjectListResponse,
} from "../../services/storyWriterApi";

const glassyCardSx = {
  borderRadius: 3,
  border: "1px solid rgba(255,255,255,0.08)",
  background: alpha("#020617", 0.8),
  backdropFilter: "blur(24px)",
};

interface StoryProjectListProps {
  onSelectProject?: (projectId: string) => void;
}

export function StoryProjectList({ onSelectProject }: StoryProjectListProps) {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<StoryProjectSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      setLoading(true);
      setError(null);
      const response: StoryProjectListResponse = await storyWriterApi.listStoryProjects({
        order_by: "updated_at",
      });
      setProjects(response.projects);
    } catch (err) {
      setError("Failed to load story projects. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(projectId: string) {
    try {
      setLoading(true);
      await storyWriterApi.deleteStoryProject(projectId);
      setProjects((prev) => prev.filter((p) => p.project_id !== projectId));
    } catch (err) {
      setError("Failed to delete project. Please try again.");
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setProjectToDelete(null);
    }
  }

  async function handleToggleFavorite(projectId: string, current: boolean) {
    try {
      const updated = await storyWriterApi.toggleStoryProjectFavorite(projectId);
      setProjects((prev) =>
        prev.map((p) => (p.project_id === projectId ? { ...p, is_favorite: updated.is_favorite } : p))
      );
    } catch (err) {
      setError("Failed to update favorites. Please try again.");
    }
  }

  function getStatusLabel(status: string | null | undefined) {
    if (!status) return "Draft";
    return status.charAt(0).toUpperCase() + status.slice(1);
  }

  function getStatusColor(status: string | null | undefined) {
    if (status === "completed") return "success";
    if (status === "writing") return "primary";
    if (status === "outline") return "secondary";
    return "default";
  }

  const filteredProjects = useMemo(() => {
    if (!searchQuery) return projects;
    return projects.filter((project) => {
      const titleMatch =
        project.title &&
        project.title.toLowerCase().includes(searchQuery.toLowerCase());
      const idMatch = project.project_id
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      return titleMatch || idMatch;
    });
  }, [projects, searchQuery]);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #020617 0%, #0b1120 40%, #020617 100%)",
        p: { xs: 2, md: 4 },
      }}
    >
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: "auto",
          borderRadius: 4,
          border: "1px solid rgba(148,163,184,0.35)",
          background: alpha("#020617", 0.85),
          backdropFilter: "blur(28px)",
          p: { xs: 3, md: 4 },
        }}
      >
        <Stack spacing={3}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  background: "linear-gradient(135deg, #38bdf8 0%, #a855f7 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  fontWeight: 800,
                  mb: 0.5,
                  display: "flex",
                  alignItems: "center",
                  gap: 1.5,
                }}
              >
                <AutoStoriesIcon fontSize="large" />
                My Story Projects
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Resume your stories or start a new one
              </Typography>
            </Box>
            <Stack direction="row" spacing={1}>
              <SecondaryButton onClick={loadProjects} startIcon={<RefreshIcon />} disabled={loading}>
                Refresh
              </SecondaryButton>
              <PrimaryButton onClick={() => navigate("/story-writer")} startIcon={<PlayArrowIcon />}>
                New Story
              </PrimaryButton>
            </Stack>
          </Stack>

          <TextField
            fullWidth
            placeholder="Search by title or project id..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ color: "rgba(148,163,184,0.9)", mr: 1 }} />,
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                color: "white",
                "& fieldset": { borderColor: "rgba(148,163,184,0.4)" },
                "&:hover fieldset": { borderColor: "rgba(148,163,184,0.7)" },
              },
            }}
          />

          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {loading && (
            <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {!loading && filteredProjects.length === 0 && (
            <GlassyCard sx={glassyCardSx}>
              <Stack spacing={2} alignItems="center" sx={{ p: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  {searchQuery ? "No projects match your search" : "No story projects yet"}
                </Typography>
                <PrimaryButton onClick={() => navigate("/story-writer")} startIcon={<PlayArrowIcon />}>
                  Create Your First Story
                </PrimaryButton>
              </Stack>
            </GlassyCard>
          )}

          {!loading && filteredProjects.length > 0 && (
            <Stack spacing={2}>
              {filteredProjects.map((project) => (
                <GlassyCard
                  key={project.project_id}
                  sx={{
                    ...glassyCardSx,
                    cursor: "pointer",
                    "&:hover": {
                      borderColor: "rgba(56,189,248,0.55)",
                      transform: "translateY(-2px)",
                    },
                    transition: "all 0.2s",
                  }}
                  onClick={() => {
                    if (onSelectProject) {
                      onSelectProject(project.project_id);
                    } else {
                      navigate("/story-writer", { state: { projectId: project.project_id } });
                    }
                  }}
                >
                  <Stack spacing={2}>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Box flex={1}>
                        <Typography variant="h6" sx={{ mb: 1, color: "white" }}>
                          {project.title && project.title.trim().length > 0
                            ? project.title
                            : project.project_id}
                        </Typography>
                        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                          <Chip
                            label={getStatusLabel(project.status)}
                            size="small"
                            color={getStatusColor(project.status) as any}
                            sx={{ background: alpha("#38bdf8", 0.16), color: "#e0f2fe" }}
                          />
                          {project.story_mode && (
                            <Chip
                              label={project.story_mode === "marketing" ? "Marketing" : "Fiction"}
                              size="small"
                              sx={{ background: alpha("#a855f7", 0.16), color: "#f5d0fe" }}
                            />
                          )}
                          {project.story_template && (
                            <Typography variant="caption" color="text.secondary">
                              Template: {project.story_template}
                            </Typography>
                          )}
                          <Typography variant="caption" color="text.secondary">
                            Updated {new Date(project.updated_at).toLocaleDateString()}
                          </Typography>
                        </Stack>
                      </Box>
                      <Stack direction="row" spacing={1}>
                        <Tooltip
                          title={project.is_favorite ? "Remove from favorites" : "Add to favorites"}
                        >
                          <IconButton
                            onClick={(e) => {
                              e.stopPropagation();
                              handleToggleFavorite(project.project_id, project.is_favorite);
                            }}
                            sx={{ color: project.is_favorite ? "#fbbf24" : "rgba(148,163,184,0.9)" }}
                          >
                            {project.is_favorite ? <StarIcon /> : <StarBorderIcon />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete project">
                          <IconButton
                            onClick={(e) => {
                              e.stopPropagation();
                              setProjectToDelete(project.project_id);
                              setDeleteDialogOpen(true);
                            }}
                            sx={{ color: "rgba(148,163,184,0.9)" }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </Stack>
                  </Stack>
                </GlassyCard>
              ))}
            </Stack>
          )}
        </Stack>
      </Paper>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setProjectToDelete(null);
        }}
        PaperProps={{
          sx: {
            background: alpha("#020617", 0.95),
            backdropFilter: "blur(24px)",
            border: "1px solid rgba(148,163,184,0.35)",
          },
        }}
      >
        <DialogTitle sx={{ color: "white" }}>Delete Story Project?</DialogTitle>
        <DialogContent>
          <Typography sx={{ color: "rgba(226,232,240,0.85)" }}>
            Are you sure you want to delete this project? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <SecondaryButton
            onClick={() => {
              setDeleteDialogOpen(false);
              setProjectToDelete(null);
            }}
          >
            Cancel
          </SecondaryButton>
          <PrimaryButton
            onClick={() => {
              if (projectToDelete) {
                handleDelete(projectToDelete);
              }
            }}
            sx={{
              background: "#b91c1c",
              "&:hover": {
                background: "#991b1b",
              },
            }}
          >
            Delete
          </PrimaryButton>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
