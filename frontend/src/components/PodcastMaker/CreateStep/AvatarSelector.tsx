import React from "react";
import { Stack, Box, Typography, Tabs, Tab, CircularProgress, Button, IconButton, Tooltip, alpha, useTheme, useMediaQuery } from "@mui/material";
import {
  Person as PersonIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Collections as CollectionsIcon,
  Delete as DeleteIcon,
  AutoAwesome as AutoAwesomeIcon,
  CloudUpload as CloudUploadIcon,
  PhotoCamera as PhotoCameraIcon,
} from "@mui/icons-material";
import { AvatarAssetBrowser } from "../AvatarAssetBrowser";
import { CameraSelfie } from "../CameraSelfie";
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
  handleCameraSelfie: (imageDataUrl: string) => void;
  handleRemoveAvatar: () => void;
  handleMakePresentable: () => void;
  makingPresentable: boolean;
  avatarPreviewBlobUrl: string | null;
  brandAvatarFromDb?: string | null;
  brandAvatarBlobUrl?: string | null;
  cameraSelfieOpen: boolean;
  setCameraSelfieOpen: (open: boolean) => void;
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
  handleCameraSelfie,
  handleRemoveAvatar,
  handleMakePresentable,
  makingPresentable,
  avatarPreviewBlobUrl,
  brandAvatarFromDb,
  brandAvatarBlobUrl,
  cameraSelfieOpen,
  setCameraSelfieOpen,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  // Shorter tab labels for mobile
  const tabLabels = isMobile 
    ? ["Brand", "Library", "Selfie", "Upload"]
    : ["Use Brand Avatar", "Asset Library", "Take Selfie", "Upload Your Photo"];

  return (
    <Box
      sx={{
        flex: 1,
        minWidth: 0,
        p: { xs: 1.5, sm: 2.5 },
        borderRadius: 2,
        background: "#ffffff",
        border: "1px solid rgba(15, 23, 42, 0.08)",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.04)",
      }}
    >
      <Stack direction={{ xs: "column", sm: "row" }} spacing={{ xs: 1, sm: 1.5 }} alignItems={{ xs: "flex-start", sm: "center" }} sx={{ mb: 2 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Box
            sx={{
              width: 24,
              height: 24,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 2px 8px rgba(102, 126, 234, 0.25)",
            }}
          >
            <Typography sx={{ color: "#fff", fontSize: "0.75rem", fontWeight: 700 }}>3</Typography>
          </Box>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: 1.5,
              background: "linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <PersonIcon fontSize="small" sx={{ color: "#667eea" }} />
          </Box>
          <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "0.9375rem" }}>
            Podcast Presenter Avatar
          </Typography>
        </Stack>
        <Tooltip
          title={
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                Avatar Options:
              </Typography>
              <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                <strong>Brand Avatar:</strong> Use your configured brand avatar for consistency.<br/><br/>
                <strong>Asset Library:</strong> Choose from your previously uploaded images.<br/><br/>
                <strong>Take a Selfie:</strong> Use your camera to capture a photo instantly for your podcast presenter.<br/><br/>
                <strong>Upload your photo:</strong> We'll enhance it into a professional podcast presenter using AI.
              </Typography>
            </Box>
          }
          arrow
          placement="top"
        >
          <InfoIcon fontSize="small" sx={{ color: "#94a3b8", cursor: "help", ml: { xs: 0, sm: 0 } }} />
        </Tooltip>
      </Stack>
      
      <Stack direction={{ xs: "column", lg: "row" }} spacing={3} alignItems="flex-start">
        {/* Left Side: Tabs & Content */}
        <Box sx={{ flex: 1, width: "100%" }}>
          <Tabs 
            value={avatarTab} 
            onChange={setAvatarTab}
            variant="scrollable"
            scrollButtons={isMobile ? "auto" : false}
            allowScrollButtonsMobile={isMobile}
            sx={{ 
              mb: { xs: 2, sm: 3 },
              minHeight: { xs: 36, sm: 48 },
              "& .MuiTabs-scrollButtons": {
                color: "#64748b",
                "&.Mui-disabled": { opacity: 0.3 },
              },
              "& .MuiTabs-indicator": {
                display: "none",
              },
              "& .MuiTabs-flexContainer": {
                gap: { xs: 0.5, sm: 1.5 },
              },
              "& .MuiTab-root": {
                textTransform: "none",
                minHeight: { xs: 32, sm: 44 },
                fontWeight: 600,
                fontSize: { xs: "0.7rem", sm: "0.875rem" },
                borderRadius: { xs: "6px", sm: "12px" },
                px: { xs: 1, sm: 2.5 },
                minWidth: { xs: "auto", sm: 0 },
                color: "#64748b",
                border: "1.5px solid #e2e8f0",
                transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                backgroundColor: "#ffffff",
                "&:hover": {
                  borderColor: "#cbd5e1",
                  backgroundColor: "#f8fafc",
                  transform: { xs: "none", sm: "translateY(-1px)" },
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
            {tabLabels.map((label, index) => (
              <Tab key={index} label={label} />
            ))}
          </Tabs>

          {avatarTab === 0 && (
            <Stack spacing={2}>
              <Box sx={{ minHeight: { xs: 160, sm: 200 }, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", bgcolor: "#f8fafc", borderRadius: 2, p: { xs: 1.5, sm: 2 }, position: "relative" }}>
                {loadingBrandAvatar ? (
                  <CircularProgress size={32} />
                ) : avatarPreview && avatarPreview === brandAvatarFromDb ? (
                  <Stack spacing={2} alignItems="center" sx={{ width: "100%", maxWidth: { xs: 220, sm: 280 } }}>
                    <Box sx={{ position: "relative", width: "100%" }}>
                      <Box
                        component="img"
                        src={avatarPreviewBlobUrl || ""}
                        alt="Selected Brand Avatar"
                        sx={{
                          width: "100%",
                          height: "auto",
                          maxHeight: { xs: 160, sm: 200 },
                          objectFit: "contain",
                          borderRadius: 2,
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
                  <Stack spacing={2} alignItems="center" sx={{ width: "100%", maxWidth: { xs: 220, sm: 280 } }}>
                    <Box
                      component="img"
                      src={brandAvatarBlobUrl || ""}
                      alt="Available Brand Avatar"
                      sx={{
                        width: "100%",
                        height: "auto",
                        maxHeight: { xs: 160, sm: 200 },
                        objectFit: "contain",
                        borderRadius: 2,
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
                    <PersonIcon sx={{ fontSize: { xs: 36, sm: 48 }, color: "#cbd5e1" }} />
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center", px: 2 }}>
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
                  p: { xs: 1, sm: 1.5 },
                  borderRadius: 1.5,
                  background: alpha("#f0f4ff", 0.6),
                  border: "1px solid rgba(99, 102, 241, 0.2)",
                }}
              >
                <Typography variant="body2" sx={{ color: "#0f172a", fontSize: { xs: "0.75rem", sm: "0.875rem" }, fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <AutoAwesomeIcon fontSize="small" sx={{ color: "#667eea" }} />
                  Brand Avatar
                </Typography>
                <Typography variant="body2" sx={{ color: "#475569", fontSize: { xs: "0.75rem", sm: "0.8125rem" }, lineHeight: 1.6 }}>
                  Select your pre-configured brand avatar to maintain consistency. If not selected, a new AI presenter will be generated.
                </Typography>
              </Box>
            </Stack>
          )}

          {avatarTab === 1 && (
            <Stack spacing={2}>
              <Box sx={{ minHeight: { xs: 240, sm: 300 }, position: "relative" }}>
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
                  p: { xs: 1, sm: 1.5 },
                  borderRadius: 1.5,
                  background: alpha("#f8fafc", 0.8),
                  border: "1px solid rgba(15, 23, 42, 0.1)",
                }}
              >
                <Typography variant="body2" sx={{ color: "#0f172a", fontSize: { xs: "0.75rem", sm: "0.875rem" }, fontWeight: 600, mb: 0.5, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <CollectionsIcon fontSize="small" sx={{ color: "#64748b" }} />
                  Asset Library
                </Typography>
                <Typography variant="body2" sx={{ color: "#475569", fontSize: { xs: "0.75rem", sm: "0.8125rem" }, lineHeight: 1.6 }}>
                  Select from your previously uploaded images. Filter by favorites or search to find the perfect presenter.
                </Typography>
              </Box>
            </Stack>
          )}

          {avatarTab === 2 && (
            <Stack spacing={2}>
              <Box>
                {avatarFile && avatarPreview ? (
                  <Stack spacing={2} alignItems="center" sx={{ bgcolor: "#f8fafc", borderRadius: 2, p: { xs: 1.5, sm: 2 } }}>
                    <Box sx={{ position: "relative", display: "inline-block", width: "100%", maxWidth: { xs: 220, sm: 280 } }}>
                      <Box
                        component="img"
                        src={avatarPreviewBlobUrl || avatarPreview || ""}
                        alt="Selfie preview"
                        sx={{
                          width: "100%",
                          height: "auto",
                          maxHeight: { xs: 160, sm: 200 },
                          objectFit: "contain",
                          borderRadius: 2,
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
                        title="Transform your selfie into a professional podcast presenter."
                        arrow
                        placement="top"
                      >
                        <Box sx={{ width: "100%", maxWidth: { xs: 220, sm: 280 } }}>
                          <Button
                            onClick={handleMakePresentable}
                            disabled={makingPresentable}
                            variant="contained"
                            startIcon={!makingPresentable ? <AutoAwesomeIcon fontSize="small" /> : <CircularProgress size={14} thickness={5} sx={{ color: "rgba(255,255,255,0.92)" }} />}
                            sx={{
                              width: "100%",
                              textTransform: "none",
                              fontSize: { xs: "0.75rem", sm: "0.875rem" },
                              fontWeight: 600,
                              borderRadius: 2.5,
                              color: "#f8fbff",
                              px: 1.8,
                              border: "1px solid rgba(148, 211, 255, 0.6)",
                              background: "linear-gradient(120deg, #0ea5e9 0%, #2563eb 55%, #1d4ed8 100%)",
                              boxShadow: "0 8px 18px rgba(37, 99, 235, 0.28), inset 0 1px 0 rgba(255,255,255,0.22)",
                              "&:hover": {
                                background: "linear-gradient(120deg, #38bdf8 0%, #2563eb 50%, #1e40af 100%)",
                                boxShadow: "0 12px 24px rgba(29, 78, 216, 0.35), inset 0 1px 0 rgba(255,255,255,0.26)",
                                transform: "translateY(-1px)",
                              },
                              "&.Mui-disabled": {
                                color: "#e2e8f0",
                                borderColor: "rgba(186, 230, 253, 0.7)",
                                background: "linear-gradient(120deg, #0ea5e9 0%, #2563eb 55%, #1d4ed8 100%)",
                                opacity: 0.78,
                              },
                            }}
                          >
                            {makingPresentable ? "Transforming..." : "Make Presentable"}
                          </Button>
                        </Box>
                      </Tooltip>
                    )}
                  </Stack>
                ) : (
                  <Box
                    component="button"
                    onClick={() => setCameraSelfieOpen(true)}
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      width: "100%",
                      minHeight: { xs: 160, sm: 200 },
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
                    <PhotoCameraIcon sx={{ color: "#94a3b8", fontSize: { xs: 28, sm: 36 }, mb: 1.5 }} />
                    <Typography variant="body2" sx={{ color: "#64748b", fontWeight: 600, mb: 0.5 }}>
                      Take a Selfie
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#94a3b8", textAlign: "center", px: 2, lineHeight: 1.5 }}>
                      Use your camera to capture a photo instantly
                    </Typography>
                  </Box>
                )}
              </Box>
              <Box
                sx={{
                  p: { xs: 1, sm: 1.5 },
                  borderRadius: 1.5,
                  background: alpha("#f0f4ff", 0.6),
                  border: "1px solid rgba(99, 102, 241, 0.2)",
                }}
              >
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <PhotoCameraIcon fontSize="small" sx={{ color: "#667eea" }} />
                  <Typography variant="body2" sx={{ color: "#0f172a", fontSize: { xs: "0.75rem", sm: "0.8125rem" }, fontWeight: 600 }}>
                    Capture a photo using your device camera and use "Make Presentable" to enhance it. Camera access required.
                  </Typography>
                </Stack>
              </Box>
            </Stack>
          )}

          {avatarTab === 3 && (
            <Stack spacing={2}>
              <Box>
                {avatarFile && avatarPreview ? (
                  <Stack spacing={2} alignItems="center" sx={{ bgcolor: "#f8fafc", borderRadius: 2, p: { xs: 1.5, sm: 2 } }}>
                    <Box sx={{ position: "relative", display: "inline-block" }}>
                      <Box
                        component="img"
                        src={avatarPreviewBlobUrl || avatarPreview || ""}
                        alt="Avatar preview"
                        sx={{
                          width: { xs: 120, sm: 160 },
                          height: { xs: 120, sm: 160 },
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
                        <Box sx={{ width: "100%", maxWidth: { xs: 200, sm: 280 } }}>
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
                      minHeight: { xs: 160, sm: 200 },
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
                    <CloudUploadIcon sx={{ color: "#94a3b8", fontSize: { xs: 28, sm: 36 }, mb: 1.5 }} />
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
                  p: { xs: 1, sm: 1.5 },
                  borderRadius: 1.5,
                  background: alpha("#f0f4ff", 0.6),
                  border: "1px solid rgba(99, 102, 241, 0.2)",
                }}
              >
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <CloudUploadIcon fontSize="small" sx={{ color: "#667eea" }} />
                  <Typography variant="body2" sx={{ color: "#0f172a", fontSize: { xs: "0.75rem", sm: "0.8125rem" }, fontWeight: 600 }}>
                    Upload a photo and use "Make Presentable" to enhance it into a professional presenter. Supported: JPG, PNG, WebP (max 5MB)
                  </Typography>
                </Stack>
              </Box>
            </Stack>
          )}
        </Box>
      </Stack>

      {/* Camera Selfie Dialog */}
      <CameraSelfie
        open={cameraSelfieOpen}
        onClose={() => setCameraSelfieOpen(false)}
        onCapture={handleCameraSelfie}
      />
    </Box>
  );
};
