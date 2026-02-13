import React, { useMemo, useRef, useState, useEffect } from 'react';
import { Box, Typography, Paper, Stack, Button, Alert, TextField, CircularProgress, Slider, FormControlLabel, Checkbox, MenuItem, Tooltip, Chip, Divider, Grid, IconButton, Modal, Fade, Backdrop } from '@mui/material';
import { keyframes } from '@mui/system';
import { Mic, GraphicEq, Timer, CloudUpload, Stop, PlayArrow, InfoOutlined, TextFields, HelpOutline, AutoAwesome, Campaign, MicNone, Podcasts, RestartAlt, Undo } from '@mui/icons-material';
import { createVoiceClone, createVoiceDesign, getLatestVoiceClone, setBrandVoice } from '../../../../api/brandAssets';
import { OperationButton } from '../../../shared/OperationButton';

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
`;

export const VoiceAvatarPlaceholder: React.FC<{ domainName?: string; onVoiceSet?: () => void }> = ({ domainName, onVoiceSet }) => {
  const [recording, setRecording] = useState(false);
  const [recordSeconds, setRecordSeconds] = useState(0);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioPreviewUrl, setAudioPreviewUrl] = useState<string | null>(null);

  const [engine, setEngine] = useState<'minimax' | 'qwen3'>('qwen3');
  const [customVoiceId, setCustomVoiceId] = useState('');
  const [model, setModel] = useState('speech-02-hd');
  const [previewText, setPreviewText] = useState('Hello! Welcome to Alwrity! This is a preview of your cloned voice. I hope you enjoy it!');
  const [needNoiseReduction, setNeedNoiseReduction] = useState(false);
  const [needVolumeNormalization, setNeedVolumeNormalization] = useState(false);
  const [accuracy, setAccuracy] = useState(0.7);
  const [languageBoost, setLanguageBoost] = useState('auto');
  const [qualityPreset, setQualityPreset] = useState<'clean' | 'noisy' | 'accent'>('clean');
  const [qwenLanguage, setQwenLanguage] = useState('auto');
  const [referenceText, setReferenceText] = useState('');
  const [voiceDescription, setVoiceDescription] = useState('');

  // Debounce text inputs for token calculation to prevent button flickering
  const [debouncedPreviewText, setDebouncedPreviewText] = useState(previewText);
  const [debouncedVoiceDescription, setDebouncedVoiceDescription] = useState(voiceDescription);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedPreviewText(previewText);
    }, 500);
    return () => clearTimeout(handler);
  }, [previewText]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedVoiceDescription(voiceDescription);
    }, 500);
    return () => clearTimeout(handler);
  }, [voiceDescription]);

  const [cloning, setCloning] = useState(false);
  const [saving, setSaving] = useState(false);
  const STORAGE_KEY = 'voice_clone_result_url';
  const STORAGE_BACKUP_KEY = 'voice_clone_result_url_backup';

  const [resultAudioUrl, setResultAudioUrl] = useState<string | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved && saved.length > 0 ? saved : null;
    } catch { return null; }
  });

  const [archivedResultAudioUrl, setArchivedResultAudioUrl] = useState<string | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_BACKUP_KEY);
      return saved && saved.length > 0 ? saved : null;
    } catch { return null; }
  });

  // Auto-save to localStorage
  useEffect(() => {
    try {
      if (resultAudioUrl) {
        localStorage.setItem(STORAGE_KEY, resultAudioUrl);
      }
    } catch (e) {
      console.warn('Failed to save voice clone url to localStorage', e);
    }
  }, [resultAudioUrl]);

  // Auto-save backup to localStorage
  useEffect(() => {
    try {
      if (archivedResultAudioUrl) {
        localStorage.setItem(STORAGE_BACKUP_KEY, archivedResultAudioUrl);
      } else {
        localStorage.removeItem(STORAGE_BACKUP_KEY);
      }
    } catch (e) {
      console.warn('Failed to save archived voice url to localStorage', e);
    }
  }, [archivedResultAudioUrl]);

  const handleReDo = () => {
    if (resultAudioUrl) {
      setArchivedResultAudioUrl(resultAudioUrl);
    }
    setResultAudioUrl(null);
    setSuccess(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleRestore = () => {
    if (archivedResultAudioUrl) {
      setResultAudioUrl(archivedResultAudioUrl);
      setArchivedResultAudioUrl(null);
      setSuccess('Restored previous voice');
    }
  };
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [inputType, setInputType] = useState<'mic' | 'upload' | 'text'>('mic');
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [activeCard, setActiveCard] = useState(0);

  // Helper for enterprise styling
  const TextFieldProps = {
    variant: "outlined" as const,
    size: "small" as const,
    fullWidth: true,
    InputLabelProps: { 
      shrink: true, 
      sx: { fontWeight: 700, color: '#374151', fontSize: '0.875rem' } 
    },
    InputProps: {
      sx: { 
        borderRadius: '8px', 
        bgcolor: '#FFFFFF',
        fontSize: '0.875rem',
        color: '#111827',
        boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
        transition: 'all 0.2s ease-in-out',
        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#7C3AED' },
        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#7C3AED', borderWidth: '2px', boxShadow: '0 0 0 3px rgba(124, 58, 237, 0.1)' },
        '& .MuiInputBase-input': { color: '#111827' }
      }
    },
    FormHelperTextProps: {
      sx: { fontSize: '0.75rem', color: '#6B7280', mx: 1, mt: 0.5, lineHeight: 1.4 }
    }
  };

  const operation = useMemo(() => ({
    provider: 'audio',
    operation_type: inputType === 'text' ? 'voice_design' : 'voice_clone',
    actual_provider_name: 'alwrity',
    model: engine === 'minimax' ? 'minimax/voice-clone' : 'alwrity-ai/qwen3-tts/voice-clone',
    tokens_requested: (debouncedPreviewText?.trim()?.length || 0) + (inputType === 'text' ? (debouncedVoiceDescription?.trim()?.length || 0) : 0),
  }), [inputType, engine, debouncedPreviewText, debouncedVoiceDescription]);

  // Load latest voice on mount
  useEffect(() => {
    const loadLatestVoice = async () => {
      try {
        const response = await getLatestVoiceClone();
        if (response.success) {
           // Prioritize local draft
           if (response.preview_audio_url && !localStorage.getItem(STORAGE_KEY)) {
              setResultAudioUrl(response.preview_audio_url);
           }
           if (response.custom_voice_id) setCustomVoiceId(response.custom_voice_id);
        }
      } catch (err) {
         console.error(err);
      }
    };
    loadLatestVoice();
  }, []);

  // Auto-dismiss toast
  useEffect(() => {
      if (success || error) {
          const timer = setTimeout(() => {
            setSuccess(null);
            setError(null);
          }, 5000);
          return () => clearTimeout(timer);
      }
  }, [success, error]);

  const handleSetAsBrandVoice = async () => {
      if (!resultAudioUrl) return;
      setSaving(true);
      setError(null);
      setSuccess(null);
      try {
          const resp = await setBrandVoice({
              audio_url: resultAudioUrl,
              custom_voice_id: customVoiceId,
              voice_description: voiceDescription
          });
          if (resp.success) {
              setSuccess('Voice generated successfully. Use this for generating your Brand Voice.');
              // Persist selection state locally
              try {
                localStorage.setItem('brand_voice_selection', JSON.stringify({
                  set: true,
                  timestamp: new Date().toISOString(),
                  url: resultAudioUrl
                }));
              } catch (e) {
                console.warn('Failed to save voice selection to storage', e);
              }
              if (onVoiceSet) onVoiceSet();
          } else {
              setError(resp.error || 'Failed to set brand voice');
          }
      } catch (e: any) {
          setError(e.message || 'Failed to set brand voice');
      } finally {
          setSaving(false);
      }
  };

  const defaultVoiceId = useMemo(() => {
    const base = (domainName || 'Alwrity').replace(/[^a-zA-Z0-9]/g, '').slice(0, 16) || 'Alwrity';
    const ts = new Date();
    const y = ts.getFullYear();
    const m = String(ts.getMonth() + 1).padStart(2, '0');
    const d = String(ts.getDate()).padStart(2, '0');
    const rand = Math.floor(10 + Math.random() * 90);
    return `V${base}${y}${m}${d}${rand}`;
  }, [domainName]);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard((prev) => (prev + 1) % 3);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!customVoiceId && defaultVoiceId) {
        setCustomVoiceId(defaultVoiceId);
    }
  }, [defaultVoiceId, customVoiceId]);

  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<number | null>(null);

  const browserLocaleLanguage = useMemo(() => {
    const locale = (navigator.language || '').toLowerCase();
    if (locale.startsWith('hi')) return 'Hindi';
    if (locale.startsWith('en')) return 'English';
    if (locale.startsWith('es')) return 'Spanish';
    if (locale.startsWith('fr')) return 'French';
    if (locale.startsWith('de')) return 'German';
    if (locale.startsWith('pt')) return 'Portuguese';
    if (locale.startsWith('it')) return 'Italian';
    if (locale.startsWith('ja')) return 'Japanese';
    if (locale.startsWith('ko')) return 'Korean';
    if (locale.startsWith('zh')) return 'Chinese';
    if (locale.startsWith('ru')) return 'Russian';
    if (locale.startsWith('ar')) return 'Arabic';
    if (locale.startsWith('nl')) return 'Dutch';
    if (locale.startsWith('tr')) return 'Turkish';
    if (locale.startsWith('uk')) return 'Ukrainian';
    if (locale.startsWith('vi')) return 'Vietnamese';
    if (locale.startsWith('id')) return 'Indonesian';
    if (locale.startsWith('th')) return 'Thai';
    if (locale.startsWith('pl')) return 'Polish';
    if (locale.startsWith('ro')) return 'Romanian';
    if (locale.startsWith('el')) return 'Greek';
    if (locale.startsWith('cs')) return 'Czech';
    if (locale.startsWith('fi')) return 'Finnish';
    return 'auto';
  }, []);

  const ensureCustomVoiceId = () => {
    if (!customVoiceId) setCustomVoiceId(defaultVoiceId);
  };

  const cleanupRecording = () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    recorderRef.current = null;
    chunksRef.current = [];
    setRecording(false);
    setRecordSeconds(0);
  };

  const startRecording = async () => {
    setError(null);
    setSuccess(null);
    setResultAudioUrl(null);
    if (engine === 'minimax') {
      ensureCustomVoiceId();
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Microphone is not supported in this browser.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream);
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        try {
          const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' });
          const file = new File([blob], `voice_sample_${Date.now()}.webm`, { type: blob.type });
          if (file.size > 15 * 1024 * 1024) {
            setError('Recorded file is too large. Please keep it short (5–20 seconds).');
            return;
          }
          setAudioFile(file);
          const url = URL.createObjectURL(blob);
          setAudioPreviewUrl(url);
        } finally {
          cleanupRecording();
        }
      };

      recorder.start();
      setRecording(true);
      setRecordSeconds(0);
      timerRef.current = window.setInterval(() => {
        setRecordSeconds((s) => {
          const next = s + 1;
          if (next >= 20) {
            stopRecording();
          }
          return next;
        });
      }, 1000);
    } catch (e: any) {
      setError(e?.message || 'Failed to access microphone');
      cleanupRecording();
    }
  };

  const stopRecording = () => {
    try {
      if (recorderRef.current && recorderRef.current.state !== 'inactive') {
        recorderRef.current.stop();
      } else {
        cleanupRecording();
      }
    } catch {
      cleanupRecording();
    }
  };

  const handleUpload = (file: File | null) => {
    if (!file) return;
    setError(null);
    setSuccess(null);
    setResultAudioUrl(null);
    if (engine === 'minimax') {
      ensureCustomVoiceId();
    }
    if (file.size > 15 * 1024 * 1024) {
      setError('Audio file is too large. Maximum is 15MB.');
      return;
    }
    setAudioFile(file);
    try {
      const url = URL.createObjectURL(file);
      setAudioPreviewUrl(url);
    } catch {
      setAudioPreviewUrl(null);
    }
  };

  const handleClone = async () => {
    // Voice Design (Text to Voice)
    if (inputType === 'text') {
        if (!voiceDescription.trim()) {
            setError('Please provide a voice description.');
            return;
        }
        if (!previewText.trim()) {
            setError('Please provide text to speak.');
            return;
        }

        setCloning(true);
        setError(null);
        setSuccess(null);
        setResultAudioUrl(null);
        setArchivedResultAudioUrl(null);

        try {
            const resp = await createVoiceDesign({
                text: previewText,
                voiceDescription: voiceDescription,
                language: qwenLanguage
            });

            if (resp.success) {
                setSuccess(resp.message || 'Voice generated successfully');
                setResultAudioUrl(resp.preview_audio_url || null);
            } else {
                setError(resp.error || 'Voice generation failed');
            }
        } catch (e: any) {
            setError(e?.message || 'Voice generation failed');
        } finally {
            setCloning(false);
        }
        return;
    }

    // Voice Cloning (Audio to Voice)
    if (!audioFile) {
      setError('Please record or upload a short audio clip first.');
      return;
    }
    if (engine === 'minimax' && !customVoiceId) {
      setError('Custom Voice ID is required.');
      return;
    }
    if (engine === 'qwen3' && (!previewText || previewText.trim().length === 0)) {
      setError('Text is required for Qwen3 voice clone.');
      return;
    }

    setCloning(true);
    setError(null);
    setSuccess(null);
    setResultAudioUrl(null);
    setArchivedResultAudioUrl(null);
    try {
      const resp = await createVoiceClone({
        audioFile,
        engine,
        customVoiceId: engine === 'minimax' ? customVoiceId : undefined,
        model: engine === 'minimax' ? model : undefined,
        text: previewText.length > 2000 ? previewText.slice(0, 2000) : previewText,
        referenceText: engine === 'qwen3' && referenceText.trim() ? referenceText.trim() : undefined,
        language: engine === 'qwen3' ? qwenLanguage : undefined,
        needNoiseReduction,
        needVolumeNormalization,
        accuracy,
        languageBoost,
      });
      if (resp.success) {
        setSuccess('Voice generated successfully. Use this for generating your Brand Voice.');
        setResultAudioUrl(resp.preview_audio_url || null);
      } else {
        setError(resp.error || 'Voice clone failed');
      }
    } catch (e: any) {
      setError(e?.message || 'Voice clone failed');
    } finally {
      setCloning(false);
    }
  };

  const applyQualityPreset = (preset: 'clean' | 'noisy' | 'accent') => {
    setQualityPreset(preset);
    if (preset === 'clean') {
      setNeedNoiseReduction(false);
      setNeedVolumeNormalization(false);
      setAccuracy(0.75);
      return;
    }
    if (preset === 'noisy') {
      setNeedNoiseReduction(true);
      setNeedVolumeNormalization(true);
      setAccuracy(0.65);
      return;
    }
    setNeedNoiseReduction(false);
    setNeedVolumeNormalization(true);
    setAccuracy(0.85);
    setLanguageBoost(browserLocaleLanguage);
  };

  const cardSx = {
    p: 1.5,
    borderRadius: '12px',
    bgcolor: '#FFFFFF',
    border: '1px solid #E5E7EB',
    boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
  };

  const gradientAccent = 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)';

  return (
    <Box sx={{ py: 1, px: 0, minHeight: '100%' }}>
      <Stack spacing={1.5}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ color: '#111827', fontWeight: 800, letterSpacing: '-0.02em', fontSize: '1rem' }}>
            Voice Clone {domainName ? domainName : ''}
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              startIcon={<HelpOutline sx={{ fontSize: 14 }} />}
              onClick={() => setShowInfoModal(true)}
              size="small"
              sx={{ 
                color: '#7C3AED', 
                fontWeight: 700, 
                textTransform: 'none',
                fontSize: '0.7rem',
                '&:hover': { bgcolor: 'rgba(124, 58, 237, 0.05)' }
              }}
            >
              What, How & Why
            </Button>
            <Tooltip 
              title={
                <Box sx={{ p: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>Voice Quality Guidance</Typography>
                  <Typography variant="body2" component="div" sx={{ opacity: 0.9, fontSize: '0.75rem' }}>
                    • Use a clean 5–20s clip with one speaker.<br/>
                    • Minimize background noise and echo.<br/>
                    • Maintain natural pacing and clear articulation.<br/>
                    • High-quality microphones yield better clones.
                  </Typography>
                </Box>
              }
              arrow
              placement="left"
            >
              <Chip
                icon={<InfoOutlined sx={{ color: '#FFFFFF !important', fontSize: '12px' }} />}
                label="Quality Tips"
                size="small"
                sx={{
                  background: gradientAccent,
                  color: '#FFFFFF',
                  fontWeight: 'bold',
                  borderRadius: '6px',
                  height: '22px',
                  fontSize: '0.65rem',
                  boxShadow: '0 2px 6px rgba(124, 58, 237, 0.2)',
                  cursor: 'help'
                }}
              />
            </Tooltip>
          </Stack>
        </Box>

        <Paper sx={cardSx} elevation={0}>
          <Stack spacing={1.5}>
            {/* Restore Option */}
            {!resultAudioUrl && archivedResultAudioUrl && (
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Undo />}
                onClick={handleRestore}
                sx={{ 
                  textTransform: 'none', 
                  fontWeight: 600,
                  borderStyle: 'dashed',
                  borderColor: '#7C3AED',
                  color: '#7C3AED',
                  bgcolor: 'rgba(124, 58, 237, 0.05)',
                  '&:hover': { 
                    borderStyle: 'solid',
                    bgcolor: 'rgba(124, 58, 237, 0.1)'
                  }
                }}
              >
                Restore Last Generated Voice
              </Button>
            )}
            {!resultAudioUrl && (
            <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1.5 }}>
              <Box sx={{ 
                width: '100%', 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 1.5,
                p: 1,
                borderRadius: '12px',
                bgcolor: '#F9FAFB',
                border: '1px solid #F3F4F6'
              }}>
                <Tooltip 
                  title={
                    <Box sx={{ p: 0.5 }}>
                      <Typography variant="subtitle2" fontWeight="bold" sx={{ fontSize: '0.8rem' }}>Record Live Sample</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>Capture your voice directly using your microphone. Ideal for quick, authentic Alwrity samples.</Typography>
                    </Box>
                  } 
                  arrow
                >
                  <Box
                    onClick={() => setInputType('mic')}
                    sx={{
                      p: 1,
                      borderRadius: '12px',
                      background: inputType === 'mic' ? gradientAccent : 'transparent',
                      color: inputType === 'mic' ? '#FFFFFF' : '#9CA3AF',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 70,
                      height: 70,
                      cursor: 'pointer',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: inputType === 'mic' ? '0 4px 12px rgba(124, 58, 237, 0.2)' : 'none',
                      border: inputType === 'mic' ? 'none' : '2px dashed #E5E7EB',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        color: inputType === 'mic' ? '#FFFFFF' : '#7C3AED',
                        borderColor: '#7C3AED'
                      },
                    }}
                  >
                    <Mic sx={{ fontSize: 28 }} />
                    <Typography variant="caption" sx={{ mt: 0.25, fontWeight: 700, fontSize: '0.6rem' }}>RECORD</Typography>
                  </Box>
                </Tooltip>

                <Tooltip 
                  title={
                    <Box sx={{ p: 0.5 }}>
                      <Typography variant="subtitle2" fontWeight="bold" sx={{ fontSize: '0.8rem' }}>Upload High-Quality File</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>Provide a pre-recorded WAV or MP3. Best for professional recordings with zero noise.</Typography>
                    </Box>
                  } 
                  arrow
                >
                  <Box
                    onClick={() => setInputType('upload')}
                    sx={{
                      p: 1,
                      borderRadius: '12px',
                      background: inputType === 'upload' ? gradientAccent : 'transparent',
                      color: inputType === 'upload' ? '#FFFFFF' : '#9CA3AF',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 70,
                      height: 70,
                      cursor: 'pointer',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: inputType === 'upload' ? '0 4px 12px rgba(124, 58, 237, 0.2)' : 'none',
                      border: inputType === 'upload' ? 'none' : '2px dashed #E5E7EB',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        color: inputType === 'upload' ? '#FFFFFF' : '#EC4899',
                        borderColor: '#EC4899'
                      },
                    }}
                  >
                    <CloudUpload sx={{ fontSize: 28 }} />
                    <Typography variant="caption" sx={{ mt: 0.25, fontWeight: 700, fontSize: '0.6rem' }}>UPLOAD</Typography>
                  </Box>
                </Tooltip>

                <Tooltip 
                  title={
                    <Box sx={{ p: 0.5 }}>
                      <Typography variant="subtitle2" fontWeight="bold" sx={{ fontSize: '0.8rem' }}>Type Voice Profile</Typography>
                      <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>Describe the vocal characteristics (e.g., age, tone, accent) instead of providing a sample.</Typography>
                    </Box>
                  } 
                  arrow
                >
                  <Box
                    onClick={() => setInputType('text')}
                    sx={{
                      p: 1,
                      borderRadius: '12px',
                      background: inputType === 'text' ? gradientAccent : 'transparent',
                      color: inputType === 'text' ? '#FFFFFF' : '#9CA3AF',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 70,
                      height: 70,
                      cursor: 'pointer',
                      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      boxShadow: inputType === 'text' ? '0 4px 12px rgba(124, 58, 237, 0.2)' : 'none',
                      border: inputType === 'text' ? 'none' : '2px dashed #E5E7EB',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        color: inputType === 'text' ? '#FFFFFF' : '#4B5563',
                        borderColor: '#4B5563'
                      },
                    }}
                  >
                    <TextFields sx={{ fontSize: 28 }} />
                    <Typography variant="caption" sx={{ mt: 0.25, fontWeight: 700, fontSize: '0.6rem' }}>DESCRIBE</Typography>
                  </Box>
                </Tooltip>
              </Box>

              <Box sx={{ width: '100%', minHeight: 70, display: 'flex', justifyContent: 'center' }}>
                {inputType === 'mic' && (
                  <Stack spacing={2} sx={{ width: '100%' }}>
                    <Stack direction="row" spacing={1.5} alignItems="center" sx={{ bgcolor: '#F3F4F6', p: 1, borderRadius: '12px', width: '100%', position: 'relative' }}>
                    <Box
                      onClick={() => (recording ? stopRecording() : startRecording())}
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        bgcolor: recording ? '#EF4444' : '#7C3AED',
                        color: '#FFFFFF',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        animation: recording ? `${pulse} 2s infinite` : 'none',
                        boxShadow: '0 4px 10px rgba(0,0,0,0.1)'
                      }}
                    >
                      {recording ? <Stop sx={{ fontSize: 18 }} /> : <Mic sx={{ fontSize: 18 }} />}
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" fontWeight="800" color="#111827" sx={{ fontSize: '0.8rem' }}>
                        {recording ? 'Recording...' : 'Ready to Record'}
                      </Typography>
                      <Typography variant="caption" color="#4B5563" sx={{ fontSize: '0.7rem' }}>
                        {recording ? `${recordSeconds}s elapsed` : 'Click to start (5-20s)'}
                      </Typography>
                    </Box>
                    
                    {/* Area 1: Source Recording Display */}
                    <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'flex-end', alignItems: 'center', px: 2 }}>
                        {recording ? (
                           <Typography variant="caption" sx={{ fontWeight: 700, color: '#EF4444', animation: `${pulse} 1.5s infinite` }}>
                             ● Recording Sample...
                           </Typography>
                        ) : audioPreviewUrl ? (
                           <Stack direction="row" alignItems="center" spacing={1} sx={{ width: '100%', maxWidth: 300 }}>
                              <Typography variant="caption" sx={{ fontWeight: 700, color: '#7C3AED', whiteSpace: 'nowrap' }}>
                                 Source Sample:
                              </Typography>
                              <audio controls src={audioPreviewUrl} style={{ height: '30px', width: '100%' }} />
                           </Stack>
                        ) : null}
                    </Box>
                  </Stack>

                  <Box sx={{ width: '100%' }}>
                    <Typography variant="caption" sx={{ fontWeight: 700, color: '#4B5563', mb: 1, display: 'block', fontSize: '0.7rem' }}>
                      Read one of these scripts to capture your voice:
                    </Typography>
                    <Stack spacing={1}>
                      {[
                        "Hi, I'm excited to use AI to scale my content creation. This voice clone will help me stay consistent across all my channels.",
                        "At our company, we value transparency and innovation. We strive to deliver the best solutions for our clients every single day.",
                        "Imagine a world where creativity knows no bounds. Where your ideas can take flight and reach millions of people instantly."
                      ].map((text, i) => (
                        <Paper key={i} elevation={0} sx={{ p: 1, bgcolor: '#FFFFFF', border: '1px solid #E5E7EB', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.2s', '&:hover': { borderColor: '#7C3AED', bgcolor: '#F9FAFB', transform: 'translateY(-1px)' } }}>
                           <Typography variant="body2" sx={{ fontSize: '0.75rem', color: '#374151', lineHeight: 1.4, fontStyle: 'italic' }}>"{text}"</Typography>
                        </Paper>
                      ))}
                    </Stack>
                  </Box>
                  </Stack>
                )}

                {inputType === 'upload' && (
                  <Box
                    component="label"
                    sx={{
                      width: '100%',
                      p: 2,
                      border: '2px dashed #D1D5DB',
                      borderRadius: '12px',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 1,
                      cursor: 'pointer',
                      bgcolor: '#F9FAFB',
                      '&:hover': { bgcolor: '#F3F4F6', borderColor: '#7C3AED' }
                    }}
                  >
                    <CloudUpload sx={{ fontSize: 32, color: '#7C3AED' }} />
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="subtitle2" fontWeight="800" color="#111827" sx={{ fontSize: '0.85rem' }}>Click to Upload Audio</Typography>
                      <Typography variant="caption" color="#6B7280" sx={{ fontSize: '0.75rem' }}>WAV, MP3, or M4A (Max 10MB)</Typography>
                    </Box>
                    <input type="file" hidden accept="audio/*" onChange={(e) => handleUpload(e.target.files?.[0] || null)} />
                  </Box>
                )}

                {inputType === 'text' && (
                  <Box sx={{ width: '100%' }}>
                    <TextField
                      {...TextFieldProps}
                      label="Voice Description"
                      multiline
                      rows={2}
                      placeholder="e.g., A calm, middle-aged male voice with a slight British accent and deep resonance..."
                      value={voiceDescription}
                      onChange={(e) => setVoiceDescription(e.target.value)}
                      helperText="Describe the specific vocal qualities you want for your brand"
                    />
                  </Box>
                )}
              </Box>
            </Box>
            )}

            {error && <Alert severity="error" sx={{ borderRadius: '8px', py: 0, fontSize: '0.8rem' }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ borderRadius: '8px', py: 0, fontSize: '0.8rem' }}>{success}</Alert>}

            {/* Configuration Section */}
            <Fade in={!!(resultAudioUrl || audioPreviewUrl || audioFile || (inputType === 'text' && voiceDescription?.trim().length > 0))}>
              <Stack spacing={1.5}>
                {!resultAudioUrl && (
                  <>
                {(audioPreviewUrl || audioFile || (inputType === 'text' && voiceDescription?.trim().length > 0)) && <Divider sx={{ borderColor: '#F3F4F6' }} />}
                
                {/* Inputs for Voice Cloning (Mic/Upload) - Shown only after sample available */}
                {inputType !== 'text' && (audioPreviewUrl || audioFile) && (
                  <Grid container spacing={1.5}>
                    <Grid item xs={12} md={4}>
                      <TextField
                        select
                        {...TextFieldProps}
                        label="Clone Engine"
                        value={engine}
                        onChange={(e) => {
                          const next = e.target.value as 'minimax' | 'qwen3';
                          setEngine(next);
                          if (next === 'minimax') ensureCustomVoiceId();
                        }}
                        helperText="Select the AI engine for your voice clone"
                      >
                        <MenuItem value="qwen3" sx={{ fontSize: '0.8rem' }}>Qwen3-TTS (High Efficiency)</MenuItem>
                        <MenuItem value="minimax" sx={{ fontSize: '0.8rem' }}>MiniMax (Premium Reusable ID)</MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        {...TextFieldProps}
                        label="Custom Voice ID"
                        placeholder="e.g., upbeat_female_25"
                        value={customVoiceId}
                        onChange={(e) => setCustomVoiceId(e.target.value)}
                        helperText="A unique identifier for your custom voice model"
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        select
                        {...TextFieldProps}
                        label="Model Quality"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        disabled={engine !== 'minimax'}
                        helperText="HD is higher quality, Turbo is faster"
                      >
                        {['speech-02-hd', 'speech-02-turbo', 'speech-2.6-hd', 'speech-2.6-turbo'].map((m) => (
                          <MenuItem key={m} value={m} sx={{ fontSize: '0.8rem' }}>{m}</MenuItem>
                        ))}
                      </TextField>
                    </Grid>

                    {engine === 'qwen3' && (
                      <>
                        <Grid item xs={12} md={6}>
                          <TextField
                            select
                            {...TextFieldProps}
                            label="Native Language"
                            value={qwenLanguage}
                            onChange={(e) => setQwenLanguage(e.target.value)}
                            helperText="The primary language of the source speaker"
                          >
                            {['auto', 'English', 'Chinese', 'Spanish', 'French', 'German'].map(l => (
                              <MenuItem key={l} value={l} sx={{ fontSize: '0.8rem' }}>{l}</MenuItem>
                            ))}
                          </TextField>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <TextField
                            {...TextFieldProps}
                            label="Reference Transcript"
                            placeholder="e.g., The quick brown fox jumps over the lazy dog."
                            value={referenceText}
                            onChange={(e) => setReferenceText(e.target.value)}
                            helperText="A written transcript of your audio sample for better alignment"
                          />
                        </Grid>
                      </>
                    )}
                  </Grid>
                )}

                {/* Inputs for Voice Design (Text) - Shown only after description provided */}
                {inputType === 'text' && voiceDescription?.trim().length > 0 && (
                   <Grid container spacing={1.5}>
                     <Grid item xs={12} md={6}>
                          <TextField
                            select
                            {...TextFieldProps}
                            label="Native Language"
                            value={qwenLanguage}
                            onChange={(e) => setQwenLanguage(e.target.value)}
                            helperText="The language to generate the voice in"
                          >
                            {['auto', 'English', 'Chinese', 'Spanish', 'French', 'German'].map(l => (
                              <MenuItem key={l} value={l} sx={{ fontSize: '0.8rem' }}>{l}</MenuItem>
                            ))}
                          </TextField>
                     </Grid>
                   </Grid>
                )}

                {/* Common Inputs - Preview Text (Text to Speak) */}
                {/* Show this for Design Mode (after desc) OR Clone Mode (after sample) */}
                {((inputType === 'text' && voiceDescription?.trim().length > 0) || (inputType !== 'text' && (audioPreviewUrl || audioFile))) && (
                   <Grid container spacing={1.5} sx={{ mt: 0 }}>
                      <Grid item xs={12}>
                        <TextField
                          {...TextFieldProps}
                          label="Text to Speak (Preview)"
                          multiline
                          rows={2}
                          value={previewText}
                          onChange={(e) => setPreviewText(e.target.value)}
                          placeholder="Enter text for the AI to speak..."
                          helperText="This text will be spoken by your generated voice clone."
                        />
                      </Grid>
                   </Grid>
                )}

                {/* Generate Button - Show for Design Mode (after desc) OR Clone Mode (after sample) */}
                {((inputType === 'text' && voiceDescription?.trim().length > 0) || (inputType !== 'text' && (audioPreviewUrl || audioFile))) && (
                  <Stack direction="row" spacing={2} justifyContent="flex-end" sx={{ mt: 0.5 }}>
                    <OperationButton
                      operation={operation}
                      label={engine === 'minimax' ? 'Initialize Premium Clone' : 'Generate your brand Voice'}
                      onClick={handleClone}
                      checkOnMount={true}
                      disabled={cloning}
                      loading={cloning}
                      sx={{
                        background: gradientAccent,
                        color: '#FFFFFF',
                        textTransform: 'none',
                        fontWeight: '800',
                        borderRadius: '8px',
                        py: 0.75,
                        px: 3,
                        fontSize: '0.875rem',
                        '&:hover': { opacity: 0.9, transform: 'translateY(-1px)' },
                        '&:disabled': { background: '#E0E0E0', color: '#9CA3AF' }
                      }}
                    />
                  </Stack>
                )}
                  </>
                )}

                {resultAudioUrl && (
                  <Stack spacing={1} sx={{ mt: 0.5, p: 1, bgcolor: '#F9FAFB', borderRadius: '8px', border: '1px solid #F3F4F6' }}>
                    {audioPreviewUrl && (
                      <Box>
                        <Typography variant="caption" fontWeight="800" sx={{ color: '#7C3AED', textTransform: 'uppercase', mb: 0.25, display: 'block', fontSize: '0.65rem' }}>
                          Source Recording
                        </Typography>
                        <audio controls src={audioPreviewUrl} style={{ width: '100%', height: '28px' }} />
                      </Box>
                    )}
                    {resultAudioUrl && (
                      <Box>
                        <Typography variant="caption" fontWeight="800" sx={{ color: '#EC4899', textTransform: 'uppercase', mb: 0.25, display: 'block', fontSize: '0.65rem' }}>
                          Generated AI Voice Preview
                        </Typography>
                        <audio controls src={resultAudioUrl} style={{ width: '100%', height: '28px' }} />
                        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                          <Button
                            variant="outlined"
                            onClick={handleReDo}
                            size="small"
                            startIcon={<RestartAlt />}
                            sx={{
                              flex: 1,
                              textTransform: 'none',
                              fontWeight: 600,
                              borderColor: '#E5E7EB',
                              color: '#6B7280',
                              '&:hover': { borderColor: '#9CA3AF', bgcolor: '#F9FAFB' }
                            }}
                          >
                            Redo
                          </Button>
                          <Button 
                            variant="contained" 
                            size="small"
                            onClick={handleSetAsBrandVoice}
                            disabled={saving}
                            sx={{ 
                              flex: 2, 
                              background: gradientAccent, 
                              fontWeight: 'bold',
                              textTransform: 'none',
                              fontSize: '0.8rem'
                            }}
                          >
                            {saving ? 'Setting...' : 'Set as Brand Voice'}
                          </Button>
                        </Stack>
                      </Box>
                    )}
                  </Stack>
                )}
              </Stack>
            </Fade>
          </Stack>
        </Paper>

        <Grid container spacing={1.5} sx={{ mt: 1 }}>
          {[
            { icon: <Mic fontSize="small" />, text: "1. Record/Upload Sample" },
            { icon: <GraphicEq fontSize="small" />, text: "2. AI Clones Voice" },
            { icon: <Campaign fontSize="small" />, text: "3. Generate Content" }
          ].map((item, index) => (
            <Grid item xs={4} key={index}>
               <Paper
                 elevation={0}
                 sx={{
                   p: 1,
                   height: '100%',
                   background: activeCard === index 
                     ? 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)' 
                     : '#FFFFFF',
                   border: activeCard === index ? '1px solid #3B82F6' : '1px solid #E5E7EB',
                   borderRadius: '8px',
                   display: 'flex',
                   flexDirection: 'row',
                   alignItems: 'center',
                   justifyContent: 'center',
                   gap: 0.5,
                   textAlign: 'left',
                   transition: 'all 0.5s ease',
                   transform: activeCard === index ? 'scale(1.02)' : 'scale(1)',
                   opacity: activeCard === index ? 1 : 0.7,
                   boxShadow: activeCard === index ? '0 4px 12px rgba(59, 130, 246, 0.15)' : 'none'
                 }}
               >
                 <Box sx={{ color: activeCard === index ? '#2563EB' : '#9CA3AF', display: 'flex', transition: 'color 0.3s' }}>
                   {item.icon}
                 </Box>
                 <Typography variant="caption" sx={{ fontWeight: 700, fontSize: '0.65rem', color: activeCard === index ? '#1E3A8A' : '#6B7280', lineHeight: 1.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                   {item.text}
                 </Typography>
               </Paper>
            </Grid>
          ))}
        </Grid>
      </Stack>
      <Modal
        open={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{ timeout: 500 }}
      >
        <Fade in={showInfoModal}>
          <Box sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: { xs: '90%', md: 600 },
            bgcolor: 'background.paper',
            borderRadius: '24px',
            boxShadow: 24,
            p: 4,
            outline: 'none'
          }}>
            <Stack spacing={3}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <Box sx={{ p: 1.5, borderRadius: '12px', bgcolor: 'rgba(124, 58, 237, 0.1)', color: '#7C3AED' }}>
                  <AutoAwesome fontSize="large" />
                </Box>
                <Box>
                  <Typography variant="h5" fontWeight="800" sx={{ color: '#111827' }}>
                    Voice Cloning: What, How & Why
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Understanding the power of Alwrity AI Voice
                  </Typography>
                </Box>
              </Box>

              <Divider />

              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#111827', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <MicNone sx={{ color: '#7C3AED' }} /> What is it?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                    Voice Cloning captures the unique tone, pitch, and cadence of your voice to create a digital AI replica. This allows you to generate audio content without recording every single word manually.
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#111827', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <GraphicEq sx={{ color: '#EC4899' }} /> How does it work?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                    Our AI analyzes a short 5-20 second sample of your speech. It maps over 100 vocal characteristics to build a neural model. Once created, you can simply type text, and the AI will speak it in your exact voice.
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle1" fontWeight="800" sx={{ color: '#111827', display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Campaign sx={{ color: '#F59E0B' }} /> Why use it?
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                    • <b>Consistency:</b> Maintain a perfect brand voice across all videos and podcasts.<br/>
                    • <b>Scale:</b> Create hours of content in minutes by just typing scripts.<br/>
                    • <b>Edits:</b> Fix mistakes in your audio by simply editing the text, no re-recording needed.
                  </Typography>
                </Box>
              </Stack>

              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button 
                  variant="contained" 
                  onClick={() => setShowInfoModal(false)}
                  sx={{ 
                    borderRadius: '10px', 
                    textTransform: 'none', 
                    fontWeight: 'bold',
                    background: gradientAccent
                  }}
                >
                  Got it, let's create!
                </Button>
              </Box>
            </Stack>
          </Box>
        </Fade>
      </Modal>
    </Box>
  );
};
