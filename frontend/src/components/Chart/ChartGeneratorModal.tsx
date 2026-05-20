import React, { useState, useCallback, useEffect } from 'react';
import { chartApi, ChartGenerateResponse } from '../../services/chartApi';

interface ChartGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultText?: string;
  context?: {
    title?: string;
    section?: any;
    outline?: any;
    research?: any;
    sectionId?: string;
  };
  onChartGenerated?: (result: ChartGenerateResponse & { sectionId?: string }) => void;
}

const VALID_CHART_TYPES = [
  { value: 'bar_comparison', label: 'Bar Comparison' },
  { value: 'bar_horizontal', label: 'Horizontal Bar' },
  { value: 'line_trend', label: 'Line Trend' },
  { value: 'pie', label: 'Pie Chart' },
  { value: 'stacked_bar', label: 'Stacked Bar' },
  { value: 'bullet_points', label: 'Bullet Points' },
];

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0,0,0,0.5)',
  zIndex: 2000,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
};

const modalStyle: React.CSSProperties = {
  background: '#fff',
  width: '100%',
  maxWidth: '680px',
  borderRadius: 12,
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  maxHeight: '90vh',
};

const headerStyle: React.CSSProperties = {
  padding: '16px 20px',
  borderBottom: '1px solid #e0e0e0',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  color: '#202124',
};

const ChartGeneratorModal: React.FC<ChartGeneratorModalProps> = ({
  isOpen,
  onClose,
  defaultText,
  context,
  onChartGenerated,
}) => {
  const [mode, setMode] = useState<'ai' | 'manual'>('ai');
  const [textInput, setTextInput] = useState(defaultText || '');
  const [chartType, setChartType] = useState('bar_comparison');
  const [title, setTitle] = useState(context?.title || '');
  const [chartDataJson, setChartDataJson] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewResult, setPreviewResult] = useState<ChartGenerateResponse | null>(null);
  const [resolvedPreviewUrl, setResolvedPreviewUrl] = useState<string>('');

  useEffect(() => {
    if (previewResult?.preview_url) {
      chartApi.getPreviewUrl(previewResult.preview_url).then(setResolvedPreviewUrl);
    } else {
      setResolvedPreviewUrl('');
    }
  }, [previewResult]);

  const sectionTitle = context?.section?.heading || context?.title || 'Generate Chart';

  const handleAiGenerate = useCallback(async () => {
    if (!textInput.trim()) return;
    setIsGenerating(true);
    setError(null);
    setPreviewResult(null);
    try {
      const sectionHeading = context?.section?.heading || context?.title || '';
      const sectionKeyPoints = context?.section?.key_points || undefined;
      const result = await chartApi.generateChartFromText(textInput, title, sectionHeading, sectionKeyPoints);
      if (result.warnings && result.warnings.length > 0) {
        console.warn('[ChartGenerator] Warnings:', result.warnings);
      }
      if (result.preview_url) {
        setPreviewResult(result);
      } else {
        setError('Chart generation returned empty result. Try different text.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to generate chart');
    } finally {
      setIsGenerating(false);
    }
  }, [textInput, title, context]);

  const handleManualGenerate = useCallback(async () => {
    if (!chartDataJson.trim()) {
      setError('Please provide chart data JSON');
      return;
    }
    let parsedData: Record<string, any>;
    try {
      parsedData = JSON.parse(chartDataJson);
    } catch {
      setError('Invalid JSON format for chart data');
      return;
    }
    setIsGenerating(true);
    setError(null);
    setPreviewResult(null);
    try {
      const result = await chartApi.generateChartExplicit({
        chart_data: parsedData,
        chart_type: chartType,
        title,
      });
      if (result.preview_url) {
        setPreviewResult(result);
      } else {
        setError('Chart generation returned empty result. Check chart data format.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to generate chart');
    } finally {
      setIsGenerating(false);
    }
  }, [chartDataJson, chartType, title]);

  const handleConfirm = useCallback(() => {
    if (previewResult && onChartGenerated) {
      onChartGenerated({
        ...previewResult,
        sectionId: context?.section?.id || context?.sectionId,
      });
    }
    onClose();
  }, [previewResult, onChartGenerated, context, onClose]);

  if (!isOpen) return null;

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>{sectionTitle} — Chart</h3>
          <button
            onClick={onClose}
            style={{
              border: 'none',
              background: 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)',
              color: '#5f6368',
              borderRadius: 8,
              padding: '8px 20px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: 500,
            }}
          >
            Close
          </button>
        </div>

        <div style={{ padding: 20, overflow: 'auto', flex: 1 }}>
          {/* Mode Selector */}
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <button
              onClick={() => setMode('ai')}
              style={{
                flex: 1,
                padding: '10px 16px',
                border: `2px solid ${mode === 'ai' ? '#4f46e5' : '#e0e0e0'}`,
                borderRadius: 8,
                background: mode === 'ai' ? '#eef2ff' : '#fff',
                color: mode === 'ai' ? '#4f46e5' : '#666',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              ✨ AI Generate
            </button>
            <button
              onClick={() => setMode('manual')}
              style={{
                flex: 1,
                padding: '10px 16px',
                border: `2px solid ${mode === 'manual' ? '#4f46e5' : '#e0e0e0'}`,
                borderRadius: 8,
                background: mode === 'manual' ? '#eef2ff' : '#fff',
                color: mode === 'manual' ? '#4f46e5' : '#666',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '14px',
              }}
            >
              📊 Manual
            </button>
          </div>

          {/* Title */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#333', marginBottom: 4 }}>
              Chart Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Optional chart title..."
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #ddd',
                borderRadius: 6,
                fontSize: '14px',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {mode === 'ai' ? (
            /* AI Mode */
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#333', marginBottom: 4 }}>
                Text to Visualize
              </label>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste or type text containing data, statistics, or key points. The AI will determine the best chart type and extract the data automatically."
                rows={6}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #ddd',
                  borderRadius: 6,
                  fontSize: '14px',
                  resize: 'vertical',
                  boxSizing: 'border-box',
                }}
              />
              <button
                onClick={handleAiGenerate}
                disabled={isGenerating || !textInput.trim()}
                style={{
                  marginTop: 8,
                  padding: '10px 24px',
                  background: isGenerating || !textInput.trim() ? '#ccc' : '#4f46e5',
                  color: 'white',
                  border: 'none',
                  borderRadius: 8,
                  fontSize: '14px',
                  fontWeight: 600,
                  cursor: isGenerating ? 'not-allowed' : 'pointer',
                  width: '100%',
                }}
              >
                {isGenerating ? 'Generating...' : '🪄 Generate Chart from Text'}
              </button>
            </div>
          ) : (
            /* Manual Mode */
            <div style={{ marginBottom: 16 }}>
              <div style={{ marginBottom: 12 }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#333', marginBottom: 4 }}>
                  Chart Type
                </label>
                <select
                  value={chartType}
                  onChange={(e) => setChartType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #ddd',
                    borderRadius: 6,
                    fontSize: '14px',
                    boxSizing: 'border-box',
                  }}
                >
                  {VALID_CHART_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#333', marginBottom: 4 }}>
                  Chart Data (JSON)
                </label>
                <textarea
                  value={chartDataJson}
                  onChange={(e) => setChartDataJson(e.target.value)}
                  placeholder={`{\n  "labels": ["A", "B", "C"],\n  "values": [30, 50, 20]\n}`}
                  rows={6}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    border: '1px solid #ddd',
                    borderRadius: 6,
                    fontSize: '13px',
                    fontFamily: 'monospace',
                    resize: 'vertical',
                    boxSizing: 'border-box',
                  }}
                />
                <button
                  onClick={handleManualGenerate}
                  disabled={isGenerating || !chartDataJson.trim()}
                  style={{
                    marginTop: 8,
                    padding: '10px 24px',
                    background: isGenerating || !chartDataJson.trim() ? '#ccc' : '#4f46e5',
                    color: 'white',
                    border: 'none',
                    borderRadius: 8,
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: isGenerating ? 'not-allowed' : 'pointer',
                    width: '100%',
                  }}
                >
                  {isGenerating ? 'Generating...' : '📊 Generate Chart'}
                </button>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{
              padding: '10px 14px',
              background: '#fef2f2',
              border: '1px solid #fca5a5',
              borderRadius: 8,
              color: '#991b1b',
              fontSize: '13px',
              marginBottom: 12,
            }}>
              {error}
            </div>
          )}

          {/* Warnings */}
          {previewResult?.warnings && previewResult.warnings.length > 0 && (
            <div style={{
              padding: '10px 14px',
              background: '#fffbeb',
              border: '1px solid #fbbf24',
              borderRadius: 8,
              color: '#92400e',
              fontSize: '13px',
              marginBottom: 12,
            }}>
              <strong>Note:</strong> {previewResult.warnings.join(' ')}
            </div>
          )}

          {/* Preview */}
          {previewResult && previewResult.preview_url && (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#333', marginBottom: 8 }}>
                Preview {previewResult.chart_type && (
                  <span style={{ color: '#666', fontWeight: 400, marginLeft: 8 }}>
                    ({previewResult.chart_type.replace(/_/g, ' ')})
                  </span>
                )}
              </div>
              <img
                src={resolvedPreviewUrl}
                alt="Chart preview"
                style={{
                  maxWidth: '100%',
                  borderRadius: 8,
                  border: '1px solid #e0e0e0',
                  background: '#1a1a1a',
                }}
              />
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button
                  onClick={handleConfirm}
                  style={{
                    flex: 1,
                    padding: '10px 20px',
                    background: '#16a34a',
                    color: 'white',
                    border: 'none',
                    borderRadius: 8,
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  ✓ Use This Chart
                </button>
                <button
                  onClick={() => setPreviewResult(null)}
                  style={{
                    padding: '10px 20px',
                    background: '#f5f5f5',
                    color: '#666',
                    border: '1px solid #ddd',
                    borderRadius: 8,
                    fontSize: '14px',
                    cursor: 'pointer',
                  }}
                >
                  Regenerate
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChartGeneratorModal;