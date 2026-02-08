import React, { useMemo, useRef, useState } from 'react';
import { Box, Typography, Paper, Stack, Button, Alert, TextField, CircularProgress, Slider, FormControlLabel, Checkbox, MenuItem, Tooltip, Chip, Divider, Grid, IconButton, Modal, Fade, Backdrop } from '@mui/material';
import { keyframes } from '@mui/system';
import { Mic, GraphicEq, Timer, CloudUpload, Stop, PlayArrow, InfoOutlined, TextFields, HelpOutline, AutoAwesome, Campaign, MicNone } from '@mui/icons-material';
import { createVoiceClone } from '../../../../api/brandAssets';
import { OperationButton } from '../../../shared/OperationButton';

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
`;

export const VoiceAvatarPlaceholder: React.FC<{ domainName?: string }> = ({ domainName }) => {
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

  const [cloning, setCloning] = useState(false);
  const [resultAudioUrl, setResultAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [inputType, setInputType] = useState<'mic' | 'upload' | 'text'>('mic');
  const [showInfoModal, setShowInfoModal] = useState(false);

  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<number | null>(null);

  const defaultVoiceId = useMemo(() => {
    const base = (domainName || 'Alwrity').replace(/[^a-zA-Z0-9]/g, '').slice(0, 16) || 'Alwrity';
    const ts = new Date();
    const y = ts.getFullYear();
    const m = String(ts.getMonth() + 1).padStart(2, '0');
    const d = String(ts.getDate()).padStart(2, '0');
    const rand = Math.floor(10 + Math.random() * 90);
    return `V${base}${y}${m}${d}${rand}`;
  }, [domainName]);

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
        setSuccess(resp.message || 'Voice clone created');
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

  const inputSx = {
    '& .MuiInputLabel-root': { 
      color: '#374151', 
      fontSize: '12px', 
      fontWeight: 600,
      mb: 0.5,
    },
    '& .MuiOutlinedInput-root': { 
      height: '34px', 
      bgcolor: '#FFFFFF',
      borderRadius: '8px',
      fontSize: '13px',
      color: '#111827',
      '& fieldset': { borderColor: '#D1D5DB', borderWidth: '1px' },
      '&:hover fieldset': { borderColor: '#7C3AED' },
      '&.Mui-focused fieldset': { borderColor: '#7C3AED', borderWidth: '2px' },
    },
    '& .MuiInputBase-input': { 
      height: '34px', 
      color: '#111827', 
      fontWeight: 400,
      padding: '0 10px',
      '&::placeholder': { color: '#6B7280', opacity: 1 }
    },
  };

  const cardSx = {
    p: 1.5,
    borderRadius: '12px',
    bgcolor: '#FFFFFF',
    border: '1px solid #E5E7EB',
    boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
  };

  const gradientAccent = 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)';

  return (
    <Box sx={{ py: 1.5, px: 0, minHeight: '100%' }}>
      <Stack spacing={2}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" sx={{ color: '#111827', fontWeight: 800, letterSpacing: '-0.02em', fontSize: '1.1rem' }}>
            Voice Clone {domainName ? domainName : ''}
          </Typography>
          <Stack direction="row" spacing={1}>
            <Button
              startIcon={<HelpOutline sx={{ fontSize: 16 }} />}
              onClick={() => setShowInfoModal(true)}
              size="small"
              sx={{ 
                color: '#7C3AED', 
                fontWeight: 700, 
                textTransform: 'none',
                fontSize: '0.75rem',
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
                icon={<InfoOutlined sx={{ color: '#FFFFFF !important', fontSize: '14px' }} />}
                label="Quality Tips"
                size="small"
                sx={{
                  background: gradientAccent,
                  color: '#FFFFFF',
                  fontWeight: 'bold',
                  borderRadius: '6px',
                  height: '24px',
                  fontSize: '0.7rem',
                  boxShadow: '0 4px 10px rgba(124, 58, 237, 0.2)',
                  cursor: 'help'
                }}
              />
            </Tooltip>
          </Stack>
        </Box>

        <Paper sx={cardSx} elevation={0}>
          <Stack spacing={1.5}>
            <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1.5 }}>
              <Box sx={{ 
                width: '100%', 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 2,
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
                      p: 1.5,
                      borderRadius: '12px',
                      background: inputType === 'mic' ? gradientAccent : 'transparent',
                      color: inputType === 'mic' ? '#FFFFFF' : '#9CA3AF',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 80,
                      height: 80,
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
                    <Mic sx={{ fontSize: 32 }} />
                    <Typography variant="caption" sx={{ mt: 0.25, fontWeight: 700, fontSize: '0.65rem' }}>RECORD</Typography>
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
                      p: 1.5,
                      borderRadius: '12px',
                      background: inputType === 'upload' ? gradientAccent : 'transparent',
                      color: inputType === 'upload' ? '#FFFFFF' : '#9CA3AF',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 80,
                      height: 80,
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
                    <CloudUpload sx={{ fontSize: 32 }} />
                    <Typography variant="caption" sx={{ mt: 0.25, fontWeight: 700, fontSize: '0.65rem' }}>UPLOAD</Typography>
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
                      p: 1.5,
                      borderRadius: '12px',
                      background: inputType === 'text' ? gradientAccent : 'transparent',
                      color: inputType === 'text' ? '#FFFFFF' : '#9CA3AF',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 80,
                      height: 80,
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
                    <TextFields sx={{ fontSize: 32 }} />
                    <Typography variant="caption" sx={{ mt: 0.25, fontWeight: 700, fontSize: '0.65rem' }}>DESCRIBE</Typography>
                  </Box>
                </Tooltip>
              </Box>

              <Box sx={{ width: '100%', minHeight: 80, display: 'flex', justifyContent: 'center' }}>
                {inputType === 'mic' && (
                  <Stack direction="row" spacing={2} alignItems="center" sx={{ bgcolor: '#F3F4F6', p: 1.5, borderRadius: '12px', width: '100%' }}>
                    <Box
                      onClick={() => (recording ? stopRecording() : startRecording())}
                      sx={{
                        width: 48,
                        height: 48,
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
                      {recording ? <Stop sx={{ fontSize: 20 }} /> : <Mic sx={{ fontSize: 20 }} />}
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" fontWeight="800" color="#111827" sx={{ fontSize: '0.85rem' }}>
                        {recording ? 'Recording in Progress...' : 'Ready to Record'}
                      </Typography>
                      <Typography variant="caption" color="#4B5563" sx={{ fontSize: '0.75rem' }}>
                        {recording ? `Speak clearly. Elapsed time: ${recordSeconds}s` : 'Click the button to start recording your 5-20s sample.'}
                      </Typography>
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
                    <Tooltip title="Describe the specific vocal qualities you want for your brand" arrow>
                      <Typography sx={inputSx['& .MuiInputLabel-root']}>Describe Vocal Characteristics</Typography>
                    </Tooltip>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                      placeholder="e.g., A calm, middle-aged male voice with a slight British accent and deep resonance..."
                      sx={{...inputSx, '& .MuiOutlinedInput-root': { ...inputSx['& .MuiOutlinedInput-root'], height: 'auto', fontSize: '0.8rem' }}}
                    />
                    <Typography variant="caption" sx={{ color: '#6B7280', mt: 0.5, display: 'block', fontSize: '0.7rem' }}>
                      Note: Text-to-Voice description is coming soon. Currently, audio samples provide the best accuracy.
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>

            {error && <Alert severity="error" sx={{ borderRadius: '8px', py: 0, fontSize: '0.8rem' }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ borderRadius: '8px', py: 0, fontSize: '0.8rem' }}>{success}</Alert>}

            {/* Configuration Section - Only shown after sample provided */}
            {(audioPreviewUrl || audioFile) && (
              <Fade in={!!(audioPreviewUrl || audioFile)}>
                <Stack spacing={1.5}>
                  <Divider sx={{ borderColor: '#F3F4F6' }} />
                  
                  <Grid container spacing={1.5}>
                    <Grid item xs={12} md={4}>
                      <Tooltip title="Select the AI engine for your voice clone" arrow>
                        <Typography sx={inputSx['& .MuiInputLabel-root']}>Clone Engine</Typography>
                      </Tooltip>
                      <TextField
                        select
                        fullWidth
                        value={engine}
                        onChange={(e) => {
                          const next = e.target.value as 'minimax' | 'qwen3';
                          setEngine(next);
                          if (next === 'minimax') ensureCustomVoiceId();
                        }}
                        sx={inputSx}
                      >
                        <MenuItem value="qwen3" sx={{ fontSize: '0.8rem' }}>Qwen3-TTS (High Efficiency)</MenuItem>
                        <MenuItem value="minimax" sx={{ fontSize: '0.8rem' }}>MiniMax (Premium Reusable ID)</MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Tooltip title="A unique identifier for your custom voice model" arrow>
                        <Typography sx={inputSx['& .MuiInputLabel-root']}>Custom Voice ID</Typography>
                      </Tooltip>
                      <TextField
                  fullWidth
                  placeholder="e.g., upbeat_female_25"
                  value={customVoiceId}
                  onChange={(e) => setCustomVoiceId(e.target.value)}
                  disabled={engine !== 'minimax'}
                  sx={inputSx}
                  variant="outlined"
                  inputProps={{ 'aria-label': 'Custom Voice ID' }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Tooltip title="Choose the processing quality of the voice model. HD is higher quality, Turbo is faster." arrow>
                  <Typography sx={inputSx['& .MuiInputLabel-root']}>Model Quality</Typography>
                </Tooltip>
                <TextField
                  select
                  fullWidth
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  disabled={engine !== 'minimax'}
                  sx={inputSx}
                  variant="outlined"
                >
                        {['speech-02-hd', 'speech-02-turbo', 'speech-2.6-hd', 'speech-2.6-turbo'].map((m) => (
                          <MenuItem key={m} value={m} sx={{ fontSize: '0.8rem' }}>{m}</MenuItem>
                        ))}
                      </TextField>
                    </Grid>

                    <Grid item xs={12}>
                      <Tooltip title="The text used to preview your cloned voice" arrow>
                        <Typography sx={inputSx['& .MuiInputLabel-root']}>Preview Script</Typography>
                      </Tooltip>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        placeholder="e.g., Hello! Welcome to our brand. How can I help you today?"
                        value={previewText}
                        onChange={(e) => setPreviewText(e.target.value)}
                        sx={{...inputSx, '& .MuiOutlinedInput-root': { ...inputSx['& .MuiOutlinedInput-root'], height: 'auto', fontSize: '0.8rem' }}}
                        inputProps={{ 'aria-label': 'Preview Text' }}
                      />
                    </Grid>

                    {engine === 'qwen3' && (
                      <>
                        <Grid item xs={12} md={6}>
                          <Tooltip title="The primary language of the source speaker" arrow>
                            <Typography sx={inputSx['& .MuiInputLabel-root']}>Native Language</Typography>
                          </Tooltip>
                          <TextField
                            select
                            fullWidth
                            value={qwenLanguage}
                            onChange={(e) => setQwenLanguage(e.target.value)}
                            sx={inputSx}
                          >
                            {['auto', 'English', 'Chinese', 'Spanish', 'French', 'German'].map(l => (
                              <MenuItem key={l} value={l} sx={{ fontSize: '0.8rem' }}>{l}</MenuItem>
                            ))}
                          </TextField>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Tooltip title="A written transcript of your audio sample for better alignment" arrow>
                            <Typography sx={inputSx['& .MuiInputLabel-root']}>Reference Transcript</Typography>
                          </Tooltip>
                          <TextField
                            fullWidth
                            placeholder="e.g., The quick brown fox jumps over the lazy dog."
                            value={referenceText}
                            onChange={(e) => setReferenceText(e.target.value)}
                            sx={inputSx}
                          />
                        </Grid>
                      </>
                    )}
                  </Grid>

                  <Stack direction="row" spacing={2} justifyContent="flex-end" sx={{ mt: 0.5 }}>
                    <OperationButton
                      operation={{
                        provider: 'audio',
                        operation_type: 'voice_clone',
                        actual_provider_name: 'alwrity',
                        model: engine === 'minimax' ? 'minimax/voice-clone' : 'alwrity-ai/qwen3-tts/voice-clone',
                        tokens_requested: engine === 'qwen3' ? (previewText?.trim()?.length || 0) : 0,
                      }}
                      label={engine === 'minimax' ? 'Initialize Premium Clone' : 'Generate AI Voice'}
                      onClick={handleClone}
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

                  {(audioPreviewUrl || resultAudioUrl) && (
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
                        </Box>
                      )}
                    </Stack>
                  )}
                </Stack>
              </Fade>
            )}
          </Stack>
        </Paper>
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
