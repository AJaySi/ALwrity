import React from "react";
import { Stack, Box, Typography, Tabs, Tab, CircularProgress, Button, IconButton, Tooltip, alpha } from "@mui/material";
import {
  Person as PersonIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Collections as CollectionsIcon,
  Delete as DeleteIcon,
  AutoAwesome as AutoAwesomeIcon,
  CloudUpload as CloudUploadIcon,
} from "@mui/icons-material";
import { AvatarAssetBrowser } from "../AvatarAssetBrowser";
import { SecondaryButton } from "../ui";

interface AvatarSelectorProps {
  avatarTab: number;
  setAvatarTab: (event: React.SyntheticEvent, newValue: number) => void;
  avatarFile: File | null;
  avatarPreview: string | null;
  avatarUrl: string | null;
  loadingBrandAvatar: boolean;
  handleUseBrandAvatar: () => void;
  handleAvatarSelectFromLibrary: (url: string) => void;
  handleAvatarChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleRemoveAvatar: () => void;
  handleMakePresentable: () => void;
  makingPresentable: boolean;
  avatarPreviewBlobUrl: string | null;
  brandAvatarFromDb?: string | null;
  brandAvatarBlobUrl?: string | null;
}

export const AvatarSelector: React.FC<AvatarSelectorProps> = ({
  avatarTab,
  setAvatarTab,
  avatarFile,
  avatarPreview,
  avatarUrl,
  loadingBrandAvatar,
  handleUseBrandAvatar,
  handleAvatarSelectFromLibrary,
  handleAvatarChange,
  handleRemoveAvatar,
  handleMakePresentable,
  makingPresentable,
  avatarPreviewBlobUrl,
  brandAvatarFromDb,
  brandAvatarBlobUrl,
}) => {
  const isAuthenticatedUrl = React.useCallback((url: string | null): boolean => {
    if (!url) return false;
    return url.includes('/api/podcast/') || 
           url.includes('/api/youtube/') || 
           url.includes('/api/story/') ||
           (url.startsWith('/') && !url.startsWith('//'));
  }, []);

  return (
    <Box
      sx={{
        flex: 1,
        minWidth: 0,
        p: 2.5,
        borderRadius: 2,
        background: "#ffffff",
        border: "1px solid rgba(15, 23, 42, 0.08)",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
      }}
    >
      <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1.5,
            background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <PersonIcon fontSize="small" sx={{ color: "#667eea" }} />
        </Box>
        <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
          Podcast Presenter Avatar
        </Typography>
        <Tooltip
          title={
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Avatar Options:
              </Typography>
              <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                <strong>Upload your photo:</strong> We'll enhance it into a professional podcast presenter using AI.<br/><br/>
                <strong>Brand Avatar:</strong> Use your configured brand avatar for consistency.<br/><br/>
                <strong>Asset Library:</strong> Choose from your previously uploaded images.
              </Typography>
            </Box>
          }
          arrow
          placement="top"
        >
          <InfoIcon fontSize="small" sx={{ color: "#94a3b8", cursor: "help" }} />
        </Tooltip>
      </Stack>
      
      <Stack direction={{ xs: "column", lg: "row" }} spacing={3} alignItems="flex-start">
        {/* Left Side: Tabs & Content */}
        <Box sx={{ flex: 1, width: "100%" }}>
          <Tabs 
            value={avatarTab} 
            onChange={setAvatarTab}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ 
              mb: 3,
              minHeight: 48,
              "& .MuiTabs-indicator": {
                display: "none",
              },
              "& .MuiTabs-flexContainer": {
                gap: 1.5,
              },
              "& .MuiTab-root": {
                textTransform: "none",
                minHeight: 44,
                fontWeight: 600,
                fontSize: "0.875rem",
                borderRadius: "12px",
                px: 2.5,
                color: "#64748b",
                border: "1.5px solid #e2e8f0",
                transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                backgroundColor: "#ffffff",
                "&:hover": {
                  borderColor: "#cbd5e1",
                  backgroundColor: "#f8fafc",
                  transform: "translateY(-1px)",
                },
                "&.Mui-selected": {
                  color: "#ffffff",
                  borderColor: "transparent",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  boxShadow: "0 4px 12px rgba(102, 126, 234, 0.25)",
                },
              },
            }}
          >
            <Tab label="Use Brand Avatar" />
            <Tab label="Asset Library" />
            <Tab label="Upload Your Photo" />
          </Tabs>

          {avatarTab === 0 && (
            <Stack spacing={2}>
              <Box sx={{ minHeight: 200, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", bgcolor: "#f8fafc", borderRadius: 2, p: 2, position: "relative" }}>
                {loadingBrandAvatar ? (
                  <CircularProgress size={32} />
                ) : avatarPreview && avatarPreview === brandAvatarFromDb ? (
                  <Stack spacing={2} alignItems="center">
                    <Box sx={{ position: "relative" }}>
                      <Box
                        component="img"
                        src={avatarPreviewBlobUrl || ""}
                        alt="Selected Brand Avatar"
                        sx={{
                          width: 160,
                          height: 160,
                          objectFit: "cover",
                          borderRadius: 2.5,
                          border: "2px solid #667eea",
                          boxShadow: "0 4px 12px rgba(102, 126, 234, 0.25)",
                        }}
                      />
                      <IconButton
                        size="small"
                        onClick={handleRemoveAvatar}
                        sx={{
                          position: "absolute",
                          top: -8,
                          right: -8,
                          bgcolor: "white",
                          border: "1.5px solid #e2e8f0",
                          boxShadow: "0 2px 4px rgba(15, 23, 42, 0.1)",
                          "&:hover": {
                            bgcolor: "#fef2f2",
                            borderColor: "#ef4444",
                            color: "#ef4444",
                          },
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <CheckCircleIcon color="primary" fontSize="small" />
                      <Typography variant="body2" sx={{ color: "#64748b", fontStyle: "italic" }}>
                        Active Presenter
                      </Typography>
                    </Stack>
                  </Stack>
                ) : brandAvatarFromDb ? (
                  <Stack spacing={2} alignItems="center">
                    <Box
                      component="img"
                      src={brandAvatarBlobUrl || ""}
                      alt="Available Brand Avatar"
                      sx={{
                        width: 160,
                        height: 160,
                        objectFit: "cover",
                        borderRadius: 2.5,
                        border: "1.5px solid #e2e8f0",
                        opacity: 0.8,
                        filter: "grayscale(0.3)",
                      }}
                    />
                    <Button 
                      variant="contained" 
                      size="small" 
                      onClick={handleUseBrandAvatar}
                      startIcon={<CheckCircleIcon />}
                      sx={{ 
                        borderRadius: "8px",
                        textTransform: "none",
                        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      }}
                    >
                      Use this Avatar
                    </Button>
                  </Stack>
                ) : (
                  <Stack spacing={2} alignItems="center">
                    <PersonIcon sx={{ fontSize: 48, color: "#cbd5e1" }} />
                    <Typography variant="body2" color="text.secondary">
                      No brand avatar found.
                    </Typography>
                    <Button size="small" startIcon={<RefreshIcon />} onClick={() => void handleUseBrandAvatar()}>
                      Retry
                    </Button>
                  </Stack>
                )}
              </Box>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  background: alpha("#f0f4ff", 0.6),
                  border: "1px solid rgba(99, 102, 241, 0.2)",
                }}
              >
                <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.875rem", fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <AutoAwesomeIcon fontSize="small" sx={{ color: "#667eea" }} />
                  Brand Avatar
                </Typography>
                <Typography variant="body2" sx={{ color: "#475569", fontSize: "0.8125rem", lineHeight: 1.6 }}>
                  Select your pre-configured brand avatar to maintain consistency. If not selected, a new AI presenter will be generated.
                </Typography>
              </Box>
            </Stack>
          )}

          {avatarTab === 1 && (
            <Stack spacing={2}>
              <Box sx={{ minHeight: 300, position: "relative" }}>
                {avatarPreview && !avatarFile && (
                  <IconButton
                    size="small"
                    onClick={handleRemoveAvatar}
                    sx={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      zIndex: 10,
                      bgcolor: "white",
                      border: "1.5px solid #e2e8f0",
                      boxShadow: "0 2px 4px rgba(15, 23, 42, 0.1)",
                      "&:hover": {
                        bgcolor: "#fef2f2",
                        borderColor: "#ef4444",
                        color: "#ef4444",
                      },
                    }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                )}
                <AvatarAssetBrowser
                  selectedUrl={avatarUrl}
                  onSelect={(url) => handleAvatarSelectFromLibrary(url)}
                />
              </Box>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  background: alpha("#f8fafc", 0.8),
                  border: "1px solid rgba(15, 23, 42, 0.1)",
                }}
              >
                <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.875rem", fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <CollectionsIcon fontSize="small" sx={{ color: "#64748b" }} />
                  Asset Library
                </Typography>
                <Typography variant="body2" sx={{ color: "#475569", fontSize: "0.8125rem", lineHeight: 1.6 }}>
                  Select from your previously uploaded images. Filter by favorites or search to find the perfect presenter.
                </Typography>
              </Box>
            </Stack>
          )}

          {avatarTab === 2 && (
            <Stack spacing={2}>
              <Box>
                {avatarFile && avatarPreview ? (
                  <Stack spacing={2} alignItems="center" sx={{ bgcolor: "#f8fafc", borderRadius: 2, p: 2 }}>
                    <Box sx={{ position: "relative", display: "inline-block" }}>
                      <Box
                        component="img"
                        src={avatarPreviewBlobUrl || (avatarPreview.startsWith("data:") ? avatarPreview : "")}
                        alt="Avatar preview"
                        sx={{
                          width: 160,
                          height: 160,
                          objectFit: "cover",
                          borderRadius: 2.5,
                          border: "2px solid #e2e8f0",
                          boxShadow: "0 2px 8px rgba(15, 23, 42, 0.08)",
                        }}
                      />
                      <IconButton
                        size="small"
                        onClick={handleRemoveAvatar}
                        sx={{
                          position: "absolute",
                          top: -8,
                          right: -8,
                          bgcolor: "white",
                          border: "1.5px solid #e2e8f0",
                          boxShadow: "0 2px 4px rgba(15, 23, 42, 0.1)",
                          "&:hover": {
                            bgcolor: "#f8fafc",
                            borderColor: "#dc2626",
                            color: "#dc2626",
                          },
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>

                    {avatarUrl && (
                      <Tooltip
                        title="Transform your uploaded photo into a professional podcast presenter."
                        arrow
                        placement="top"
                      >
                        <Box>
                          <SecondaryButton
                            onClick={handleMakePresentable}
                            disabled={makingPresentable}
                            loading={makingPresentable}
                            startIcon={!makingPresentable ? <AutoAwesomeIcon fontSize="small" /> : undefined}
                            sx={{ width: "100%" }}
                          >
                            {makingPresentable ? "Transforming..." : "Make Presentable"}
                          </SecondaryButton>
                        </Box>
                      </Tooltip>
                    )}
                  </Stack>
                ) : (
                  <Box
                    component="label"
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      width: "100%",
                      minHeight: 200,
                      border: "2px dashed #cbd5e1",
                      borderRadius: 2.5,
                      bgcolor: "#f8fafc",
                      cursor: "pointer",
                      transition: "all 0.2s",
                      "&:hover": {
                        borderColor: "#667eea",
                        bgcolor: "#f1f5f9",
                        borderWidth: "2.5px",
                        boxShadow: "0 0 0 3px rgba(102, 126, 234, 0.08)",
                      },
                    }}
                  >
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      style={{ display: "none" }}
                    />
                    <CloudUploadIcon sx={{ color: "#94a3b8", fontSize: 36, mb: 1.5 }} />
                    <Typography variant="body2" sx={{ color: "#64748b", fontWeight: 600, mb: 0.5 }}>
                      Upload Your Photo
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#94a3b8", textAlign: "center", px: 2, lineHeight: 1.5 }}>
                      JPG, PNG, WebP (max 5MB)
                    </Typography>
                  </Box>
                )}
              </Box>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  background: alpha("#f8fafc", 0.8),
                  border: "1px solid rgba(15, 23, 42, 0.1)",
                }}
              >
                <Typography variant="body2" sx={{ color: "#0f172a", fontSize: "0.875rem", fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <CloudUploadIcon fontSize="small" sx={{ color: "#64748b" }} />
                  Upload Your Photo
                </Typography>
                <Typography variant="body2" sx={{ color: "#475569", fontSize: "0.8125rem", lineHeight: 1.6 }}>
                  Upload a new photo and use <strong>"Make Presentable"</strong> to enhance it into a professional presenter using AI.
                </Typography>
              </Box>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 1.5,
                  background: alpha("#f0f4ff", 0.5),
                  border: "1px solid rgba(99, 102, 241, 0.15)",
                }}
              >
                <Typography variant="caption" sx={{ color: "#6366f1", fontSize: "0.8125rem", fontWeight: 500, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <InfoIcon fontSize="inherit" />
                  Supported formats: JPG, PNG, WebP (max 5MB)
                </Typography>
              </Box>
            </Stack>
          )}
        </Box>
      </Stack>
    </Box>
  );
};
