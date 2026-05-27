import React, { useState, useCallback, useEffect, useRef } from "react";
import { Box, Typography, TextField, Tooltip, Button, CircularProgress, alpha, Stack, Chip, IconButton, Collapse } from "@mui/material";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import MicIcon from "@mui/icons-material/Mic";
import StopIcon from "@mui/icons-material/Stop";
import LanguageIcon from "@mui/icons-material/Language";
import NewspaperIcon from "@mui/icons-material/Newspaper";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import SchoolIcon from "@mui/icons-material/School";
import PublicIcon from "@mui/icons-material/Public";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import { Knobs } from "../types";
import { podcastApi } from "../../../services/podcastApi";
import { WebsitePreviewModal } from "./WebsitePreviewModal";

export const TOPIC_PLACEHOLDERS = [
  "Industry insights: Latest trends in AI for Content Marketing",
  "Product deep-dive: How our new feature solves common pain points",
  "Educational: 5 ways to improve your workflow with automation",
  "Thought leadership: The future of decentralized finance (DeFi)",
  "Interview prep: Key questions for your next tech hiring round",
  "Podcast prep: Analyzing the impact of remote work on mental health",
];

interface TopicUrlInputProps {
  value: string;
  onChange: (value: string) => void;
  isUrl: boolean;
  showAIDetailsButton: boolean;
  onAIDetailsClick?: () => void;
  onTrendingTopicsClick?: () => void;
  onCategoryResearchClick?: (category: "news" | "finance" | "research-paper" | "personal-site", websiteUrl?: string) => void;
  placeholderIndex: number;
  loading?: boolean;
  loadingMessage?: string;
  trendingLoading?: boolean;
  categoryResearchLoading?: boolean;
  // Estimated cost - can be a number (from pre-estimate) or object (from analyze response)
  estimatedCost?: number | {
    analysisCost: number;
    researchCost: number;
    scriptCost: number;
    ttsCost: number;
    voiceCloneCost: number;
    avatarCost: number;
    videoCost: number;
    total: number;
  } | null;
  duration?: number;
  speakers?: number;
  knobs?: Knobs;
  podcastMode?: string;
  // Website extraction data - passed from parent for use with AI enhance
  extractedData?: {
    title?: string;
    text?: string;
    summary?: string;
    highlights?: string[];
    url: string;
    image?: string;
    favicon?: string;
    subpages?: Array<{id?: string; title?: string; url?: string; summary?: string; text?: string}>;
  } | null;
  setExtractedData?: (data: any) => void;
}

interface SpeechRecognitionType {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  onresult: ((event: { results: { isFinal: boolean; [index: number]: { transcript: string } }[], resultIndex: number }) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognitionType;
    webkitSpeechRecognition: new () => SpeechRecognitionType;
  }
}

export const TopicUrlInput: React.FC<TopicUrlInputProps> = ({
  value,
  onChange,
  isUrl,
  showAIDetailsButton,
  onAIDetailsClick,
  onTrendingTopicsClick,
  onCategoryResearchClick,
  placeholderIndex,
  loading = false,
  loadingMessage,
  trendingLoading = false,
  categoryResearchLoading = false,
  estimatedCost,
  duration = 1,
  speakers = 1,
  knobs,
  podcastMode = "audio_video",
  extractedData: extractedDataProp,
  setExtractedData: setExtractedDataProp,
}) => {
  // Helper to get total cost from various estimate formats (number | object | null)
  const getTotalCost = (cost: number | { total: number } | null | undefined): number | null => {
    if (cost === null || cost === undefined) return null;
    if (typeof cost === "number") return cost;
    if (typeof cost === "object" && "total" in cost) return cost.total;
    return null;
  };
  
  const totalCost = getTotalCost(estimatedCost);
  
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognitionType | null>(null);

  // Use props if provided, otherwise use local state (for backward compatibility)
  const [localExtractedData, setLocalExtractedData] = useState<any>(null);
  const _extractedData = extractedDataProp !== undefined ? extractedDataProp : localExtractedData;
  const _setExtractedData = setExtractedDataProp || setLocalExtractedData;

  // Website extraction state
  const [showWebsiteInput, setShowWebsiteInput] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedData, setExtractedData] = useState<{title?: string; text?: string; summary?: string; highlights?: string[]; url: string; image?: string; favicon?: string; subpages?: Array<{id?: string; title?: string; url?: string; summary?: string; text?: string}>} | null>(null);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [websiteError, setWebsiteError] = useState<string | null>(null);

  const isSupported = typeof window !== 'undefined' && (window.SpeechRecognition !== undefined || window.webkitSpeechRecognition !== undefined);

  const getBrowserLanguage = (): string => {
    const lang = (navigator.language || '').toLowerCase();
    if (lang.startsWith('en')) return 'en-US';
    if (lang.startsWith('hi')) return 'hi-IN';
    if (lang.startsWith('es')) return 'es-ES';
    if (lang.startsWith('fr')) return 'fr-FR';
    if (lang.startsWith('de')) return 'de-DE';
    if (lang.startsWith('zh')) return 'zh-CN';
    if (lang.startsWith('ja')) return 'ja-JP';
    if (lang.startsWith('ko')) return 'ko-KR';
    return 'en-US';
  };

  const startListening = useCallback(() => {
    if (!isSupported) {
      setError('Speech recognition is not supported in this browser. Try Chrome or Edge.');
      return;
    }

    setError(null);

    const SpeechRecognitionAPI = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!recognitionRef.current) {
      const recognition = new SpeechRecognitionAPI() as SpeechRecognitionType;
      recognition.lang = getBrowserLanguage();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;

      recognition.onresult = (event) => {
        let transcript = '';
        let isFinal = false;

        for (let i = 0; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            isFinal = true;
          }
        }

        if (isFinal) {
          const newValue = value ? `${value} ${transcript.trim()}`.trim() : transcript.trim();
          onChange(newValue);
        }
      };

      recognition.onerror = (event) => {
        console.error('[Speech] Error:', event.error);
        if (event.error === 'not-allowed') {
          setError('Microphone access denied. Please allow microphone access in your browser settings.');
        } else if (event.error === 'network') {
          setError('Network error. Please check your internet connection.');
        } else if (event.error !== 'aborted') {
          setError(`Speech recognition error: ${event.error}`);
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    recognitionRef.current.onstart = () => {
      setIsListening(true);
    };

    try {
      recognitionRef.current.start();
    } catch (e) {
      console.error('[Speech] Start error:', e);
      setError('Failed to start speech recognition. Please try again.');
    }
  }, [isSupported, onChange, value]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  }, []);

  const handleMicClick = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, stopListening, startListening]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  return (
    <Box
      sx={{
        p: 0,
        borderRadius: 3,
        background: "#ffffff",
        border: "1px solid",
        borderColor: "#e2e8f0",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 8px 30px rgba(15, 23, 42, 0.12)",
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "3px",
          background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
        },
      }}
    >
{/* Header with gradient background */}
      <Box flex={1} display="flex" flexDirection="column" sx={{ background: "linear-gradient(180deg, #eff6ff 0%, #f0f9ff 60%, #ffffff 100%)", px: 3, pt: 3, pb: 2, borderBottom: "1px solid #e0e7ff" }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1.5 }}>
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Box
              sx={{
                width: 28,
                height: 28,
                borderRadius: "50%",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 2px 8px rgba(102, 126, 234, 0.3), inset 0 1px 0 rgba(255,255,255,0.2)",
              }}
            >
              <Typography sx={{ color: "#fff", fontSize: "0.75rem", fontWeight: 700 }}>1</Typography>
            </Box>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: "linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "inset 0 1px 0 rgba(255,255,255,0.5)",
              }}
            >
              <LightbulbIcon sx={{ color: "#6366f1", fontSize: "1.1rem" }} />
            </Box>
          </Stack>
          
          <Stack direction="row" spacing={1} alignItems="center">
            {!showWebsiteInput && (
              <Chip
                icon={<LanguageIcon sx={{ fontSize: "0.875rem !important" }} />}
                label="Your Website"
                onClick={() => setShowWebsiteInput(true)}
                disabled={loading}
                size="small"
                sx={{
                  background: "rgba(102, 126, 234, 0.08)",
                  color: "#667eea",
                  border: "1px solid rgba(102, 126, 234, 0.25)",
                  fontWeight: 600,
                  fontSize: "0.75rem",
                  height: 26,
                  "&:hover": {
                    background: "rgba(102, 126, 234, 0.15)",
                    transform: "scale(1.02)",
                  },
                }}
              />
            )}
            
            <Tooltip
              title={
                totalCost && estimatedCost ? (
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Estimated Cost:
                    </Typography>
                    <Typography variant="body2" component="div" sx={{ fontSize: "0.875rem", lineHeight: 1.6 }}>
                      Total: ${totalCost}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: "0.75rem", opacity: 0.9, mt: 0.5, display: "block" }}>
                      Based on {duration} min, {speakers} speaker{speakers > 1 ? "s" : ""}, {podcastMode} mode
                    </Typography>
                  </Box>
                ) : (
                  "Estimate unavailable. Pricing data not found."
                )
              }
              arrow
              placement="top"
            >
              <Chip
                icon={<AttachMoneyIcon sx={{ fontSize: "0.875rem !important" }} />}
                label={totalCost ? `Est. $${totalCost}` : "Est. Unavailable"}
                size="small"
                sx={{
                  background: totalCost ? "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.12) 100%)" : "rgba(100, 116, 139, 0.12)",
                  color: totalCost ? "#059669" : "#475569",
                  fontWeight: 600,
                  border: totalCost ? "1px solid rgba(16, 185, 129, 0.2)" : "1px solid rgba(100, 116, 139, 0.25)",
                  fontSize: "0.75rem",
                  height: 26,
                  cursor: "help",
                }}
              />
            </Tooltip>
          </Stack>
        </Stack>

        {/* Website input row - appears when user clicks "Your Website" chip */}
        <Collapse in={showWebsiteInput}>
          <Box sx={{ mt: 1.5, mb: 1.5, display: "flex", alignItems: "center", gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="https://yourdomain.com (enter your website home page)"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              disabled={isExtracting}
              error={!!websiteError}
              helperText={websiteError}
              sx={{
                "& .MuiOutlinedInput-root": {
                  backgroundColor: "#f8fafc",
                  fontSize: "0.875rem",
                  "&.Mui-focused": {
                    backgroundColor: "#ffffff",
                  },
                },
              }}
            />
            <Button
              variant="contained"
              size="small"
              onClick={async () => {
                if (!websiteUrl.trim()) {
                  setWebsiteError("Please enter a website URL");
                  return;
                }
                setWebsiteError(null);
                setIsExtracting(true);
                try {
                  const result = await podcastApi.extractUrl({ url: websiteUrl.trim() });
                  if (result.success) {
                    const extractionData = {
                      title: result.title || "",
                      text: result.text || "",
                      summary: result.summary || "",
                      highlights: result.highlights || [],
                      url: result.url,
                      image: result.image || undefined,
                      favicon: result.favicon || undefined,
                      subpages: result.subpages || [],
                    };
                    _setExtractedData(extractionData);
                    
                    // Save to backend for future use
                    try {
                      await podcastApi.saveWebsiteExtraction({
                        title: extractionData.title,
                        text: extractionData.text,
                        summary: extractionData.summary,
                        highlights: extractionData.highlights,
                        url: extractionData.url,
                        subpages: extractionData.subpages,
                      });
                    } catch (saveErr) {
                      console.warn("[TopicUrlInput] Failed to save extraction:", saveErr);
                    }
                    
                    setShowPreviewModal(true);
                  } else {
                    setWebsiteError(result.error || "Failed to extract content");
                  }
                } catch (err: any) {
                  setWebsiteError(err?.message || "Failed to extract content");
                } finally {
                  setIsExtracting(false);
                }
              }}
              disabled={isExtracting || !websiteUrl.trim()}
              sx={{
                textTransform: "none",
                fontWeight: 600,
                fontSize: "0.8125rem",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                whiteSpace: "nowrap",
                "&:hover": {
                  background: "linear-gradient(135deg, #7c8ff0 0%, #8a5cb3 100%)",
                },
              }}
            >
              {isExtracting ? <CircularProgress size={16} sx={{ color: "#fff" }} /> : "Extract"}
            </Button>
          </Box>
        </Collapse>

        <Box sx={{ position: "relative" }}>
          <Tooltip
            title={
              isListening
                ? "Listening... Click the mic to stop."
                : isUrl
                ? "We detected a URL. We'll fetch insights from this page."
                : "Enter a concise idea, paste a blog URL, or click the mic to speak your topic."
            }
            arrow
            placement="top"
          >
            <TextField
              fullWidth
              multiline
              rows={5}
              placeholder={!value ? `e.g., "${TOPIC_PLACEHOLDERS[placeholderIndex]}" or paste a URL` : ""}
              inputProps={{
                sx: {
                  "&::placeholder": { color: "#94a3b8", opacity: 1 },
                  color: "#1e293b",
                },
              }}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              size="small"
              disabled={isListening}
              helperText={
                error
                  ? error
                  : isListening
                  ? "Listening... Speak your topic now."
                  : isUrl
                  ? "URL detected. We'll analyze this page content."
                  : "Enter a clear, concise topic. You can also click the mic to speak."
              }
              sx={{
                "& .MuiOutlinedInput-root": {
                  backgroundColor: isListening ? "rgba(16, 185, 129, 0.04)" : "#f8fafc",
                  border: isListening ? "2px solid rgba(16, 185, 129, 0.5)" : "2px solid rgba(102, 126, 234, 0.2)",
                  borderRadius: 2,
                  fontSize: "1rem",
                  transition: "all 0.2s ease",
                  "&:hover": {
                    backgroundColor: "#ffffff",
                    borderColor: isListening ? "rgba(16, 185, 129, 0.7)" : "rgba(102, 126, 234, 0.4)",
                    boxShadow: isListening ? "0 2px 8px rgba(16, 185, 129, 0.15)" : "0 2px 8px rgba(102, 126, 234, 0.1)",
                  },
                  "&.Mui-focused": {
                    backgroundColor: "#ffffff",
                    borderColor: isListening ? "#10b981" : isUrl ? "#10b981" : "#667eea",
                    borderWidth: 2,
                    boxShadow: isListening 
                      ? "0 0 0 4px rgba(16, 185, 129, 0.1)"
                      : isUrl 
                      ? "0 0 0 4px rgba(16, 185, 129, 0.1)" 
                      : "0 0 0 4px rgba(102, 126, 234, 0.1)",
                  },
                },
                "& .MuiOutlinedInput-input": {
                  fontSize: "1rem",
                  lineHeight: 1.7,
                  color: "#1e293b",
                  fontWeight: 500,
                  "&::placeholder": {
                    color: "#64748b",
                    opacity: 1,
                    fontWeight: 400,
                  },
                },
                "& .MuiFormHelperText-root": {
                  color: error ? "#ef4444" : isListening ? "#059669" : isUrl ? "#059669" : "#64748b",
                  fontSize: "0.8125rem",
                  fontWeight: 500,
                  mt: 1,
                },
              }}
            />
          </Tooltip>

          {/* Mic button with listening indicator - positioned inside the textarea bottom-right */}
          {isSupported && !loading && (
            <Box sx={{ position: "absolute", bottom: isListening ? 32 : 44, right: 4, zIndex: 2, display: "flex", alignItems: "center", gap: 1 }}>
              {isListening && (
                <Typography
                  sx={{
                    fontSize: "0.7rem",
                    fontWeight: 600,
                    color: "#059669",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    px: 1,
                    py: 0.25,
                    borderRadius: 1,
                    border: "1px solid rgba(16, 185, 129, 0.2)",
                    whiteSpace: "nowrap",
                    animation: "fadeIn 0.2s ease",
                    "@keyframes fadeIn": {
                      from: { opacity: 0, transform: "translateX(4px)" },
                      to: { opacity: 1, transform: "translateX(0)" },
                    },
                  }}
                >
                  Listening...
                </Typography>
              )}
              <IconButton
                onClick={handleMicClick}
                disabled={loading}
                size="small"
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  background: isListening
                    ? "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                    : "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)",
                  color: isListening ? "#fff" : "#667eea",
                  border: isListening 
                    ? "2px solid rgba(16, 185, 129, 0.3)" 
                    : "1px solid rgba(102, 126, 234, 0.25)",
                  boxShadow: isListening 
                    ? "0 0 0 4px rgba(16, 185, 129, 0.15), 0 2px 8px rgba(16, 185, 129, 0.3)"
                    : "0 2px 6px rgba(102, 126, 234, 0.15)",
                  animation: isListening ? "pulse-mic 1.5s ease-in-out infinite" : "none",
                  "&:hover": {
                    background: isListening
                      ? "linear-gradient(135deg, #34d399 0%, #10b981 100%)"
                      : "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                    transform: "scale(1.05)",
                  },
                  "&.Mui-disabled": {
                    background: "rgba(100, 116, 139, 0.08)",
                    color: "#94a3b8",
                    border: "1px solid rgba(100, 116, 139, 0.15)",
                  },
                  "@keyframes pulse-mic": {
                    "0%": { boxShadow: "0 0 0 4px rgba(16, 185, 129, 0.15), 0 2px 8px rgba(16, 185, 129, 0.3)" },
                    "50%": { boxShadow: "0 0 0 8px rgba(16, 185, 129, 0.08), 0 2px 12px rgba(16, 185, 129, 0.4)" },
                    "100%": { boxShadow: "0 0 0 4px rgba(16, 185, 129, 0.15), 0 2px 8px rgba(16, 185, 129, 0.3)" },
                  },
                }}
              >
                {isListening ? (
                  <StopIcon sx={{ fontSize: "1.1rem" }} />
                ) : (
                  <MicIcon sx={{ fontSize: "1.1rem" }} />
                )}
              </IconButton>
            </Box>
          )}
        </Box>

        {/* Category Research Chips - News + Finance + Research Papers + Personal Website */}
        {showAIDetailsButton && !isUrl && onCategoryResearchClick && (
          <Box sx={{ display: "flex", justifyContent: "flex-start", mt: 1.5, gap: 1, flexWrap: "wrap" }}>
            <Chip
              icon={categoryResearchLoading ? <CircularProgress size={14} sx={{ color: "#667eea !important" }} /> : <NewspaperIcon sx={{ fontSize: "0.875rem !important" }} />}
              label="News"
              onClick={() => onCategoryResearchClick("news")}
              disabled={categoryResearchLoading || loading}
              size="small"
              sx={{
                background: "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)",
                color: "#667eea",
                border: "1px solid rgba(102, 126, 234, 0.3)",
                fontWeight: 600,
                fontSize: "0.8125rem",
                "&:hover": {
                  background: "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)",
                  transform: "scale(1.02)",
                },
              }}
            />
            <Chip
              icon={categoryResearchLoading ? <CircularProgress size={14} sx={{ color: "#10b981 !important" }} /> : <ShowChartIcon sx={{ fontSize: "0.875rem !important" }} />}
              label="Finance"
              onClick={() => onCategoryResearchClick("finance")}
              disabled={categoryResearchLoading || loading}
              size="small"
              sx={{
                background: "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)",
                color: "#10b981",
                border: "1px solid rgba(16, 185, 129, 0.3)",
                fontWeight: 600,
                fontSize: "0.8125rem",
                "&:hover": {
                  background: "linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%)",
                  transform: "scale(1.02)",
                },
              }}
            />
            <Chip
              icon={categoryResearchLoading ? <CircularProgress size={14} sx={{ color: "#8b5cf6 !important" }} /> : <SchoolIcon sx={{ fontSize: "0.875rem !important" }} />}
              label="Research Papers"
              onClick={() => onCategoryResearchClick("research-paper")}
              disabled={categoryResearchLoading || loading}
              size="small"
              sx={{
                background: "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%)",
                color: "#8b5cf6",
                border: "1px solid rgba(139, 92, 246, 0.3)",
                fontWeight: 600,
                fontSize: "0.8125rem",
                "&:hover": {
                  background: "linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%)",
                  transform: "scale(1.02)",
                },
              }}
            />
            <Chip
              icon={categoryResearchLoading ? <CircularProgress size={14} sx={{ color: "#f59e0b !important" }} /> : <PublicIcon sx={{ fontSize: "0.875rem !important" }} />}
              label="Personal Site"
              onClick={() => onCategoryResearchClick("personal-site", value)}
              disabled={categoryResearchLoading || loading}
              size="small"
              sx={{
                background: "linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%)",
                color: "#f59e0b",
                border: "1px solid rgba(245, 158, 11, 0.3)",
                fontWeight: 600,
                fontSize: "0.8125rem",
                "&:hover": {
                  background: "linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%)",
                  transform: "scale(1.02)",
                },
              }}
            />
          </Box>
        )}
        
        {/* Enhance topic with AI button + Get Trending Topics - appears when user types (and not a URL) */}
        {showAIDetailsButton && !isUrl && (
          <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 1.5, flexDirection: { xs: "column", sm: "row" }, alignItems: { xs: "stretch", sm: "flex-end" }, gap: 1 }}>
            <Button
              size="small"
              variant="contained"
              startIcon={
                trendingLoading ? (
                  <CircularProgress size={14} thickness={5} sx={{ color: "rgba(255,255,255,0.92)" }} />
                ) : (
                  <TrendingUpIcon />
                )
              }
              onClick={onTrendingTopicsClick}
              disabled={trendingLoading || loading}
              sx={{
                textTransform: "none",
                fontSize: "0.875rem",
                fontWeight: 600,
                borderRadius: 2.5,
                color: "#f8fbff",
                px: 2,
                py: 0.75,
                border: "1px solid rgba(16, 185, 129, 0.4)",
                background: "linear-gradient(120deg, #10b981 0%, #059669 55%, #047857 100%)",
                boxShadow: "0 8px 18px rgba(16, 185, 129, 0.28), inset 0 1px 0 rgba(255,255,255,0.22)",
                "&:hover": {
                  background: "linear-gradient(120deg, #34d399 0%, #10b981 50%, #059669 100%)",
                  boxShadow: "0 12px 24px rgba(16, 185, 129, 0.35), inset 0 1px 0 rgba(255,255,255,0.26)",
                  transform: "translateY(-1px)",
                },
                "&.Mui-disabled": {
                  color: "#e2e8f0",
                  borderColor: "rgba(110, 231, 183, 0.7)",
                  background: "linear-gradient(120deg, #10b981 0%, #059669 55%, #047857 100%)",
                  opacity: 0.78,
                },
              }}
            >
              {trendingLoading ? "Fetching Trends..." : "Get Trending Topics"}
            </Button>
            <Button
              size="small"
              variant="contained"
              startIcon={
                loading ? (
                  <CircularProgress size={14} thickness={5} sx={{ color: "rgba(255,255,255,0.92)" }} />
                ) : (
                  <AutoAwesomeIcon />
                )
              }
              onClick={onAIDetailsClick}
              disabled={loading || trendingLoading}
              sx={{
                textTransform: "none",
                fontSize: "0.875rem",
                fontWeight: 600,
                borderRadius: 2.5,
                color: "#f8fbff",
                px: 2,
                py: 0.75,
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
              {loading ? "Enhancing Topic With AI..." : "Enhance Topic With AI"}
            </Button>
          </Box>
        )}
        {loading && (
          <Typography sx={{ fontSize: "0.75rem", color: "#1d4ed8", fontWeight: 600, mt: 0.5, textAlign: "right" }}>
            {loadingMessage || "Analyzing your topic and improving clarity..."}
          </Typography>
        )}
      </Box>

      {/* Website Preview Modal */}
      <WebsitePreviewModal
        open={showPreviewModal}
        extractedData={_extractedData}
        onClose={() => {
          setShowPreviewModal(false);
          setShowWebsiteInput(false);
          setWebsiteUrl("");
        }}
        onUseTextOnly={() => {
          if (extractedData?.summary) {
            const newValue = extractedData.title 
              ? `${extractedData.title}: ${extractedData.summary}` 
              : extractedData.summary;
            onChange(newValue);
          }
          setShowPreviewModal(false);
          setShowWebsiteInput(false);
          setWebsiteUrl("");
        }}
        onAnalyzeContent={() => {
          // Phase 2: Will trigger full website analysis
          console.log("[TopicUrlInput] Analyze Content clicked - Phase 2 feature");
        }}
      />
    </Box>
  );
};