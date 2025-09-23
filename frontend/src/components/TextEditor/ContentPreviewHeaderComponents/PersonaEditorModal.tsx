import React, { useState, useEffect } from 'react';

interface PersonaData {
  // Core WritingPersona fields
  id?: number;
  user_id?: number;
  persona_name: string;
  archetype: string;
  core_belief: string;
  brand_voice_description: string;
  linguistic_fingerprint: any;
  platform_adaptations: any;
  confidence_score: number;
  ai_analysis_version: string;
  
  // PlatformPersona fields
  platform_type: string;
  sentence_metrics: any;
  lexical_features: any;
  rhetorical_devices: any;
  tonal_range: any;
  stylistic_constraints: any;
  content_format_rules: any;
  engagement_patterns: any;
  posting_frequency: any;
  content_types: any;
  platform_best_practices: any;
  algorithm_considerations: any;
}

interface PersonaEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  personaData: PersonaData | null;
  onSave: (data: PersonaData, saveToDatabase: boolean) => void;
  platform: string;
}

const PersonaEditorModal: React.FC<PersonaEditorModalProps> = ({
  isOpen,
  onClose,
  personaData,
  onSave,
  platform
}) => {
  const [editedData, setEditedData] = useState<PersonaData | null>(null);
  const [activeTab, setActiveTab] = useState<'core' | 'linguistic' | 'platform' | 'optimization'>('core');
  const [saveToDatabase, setSaveToDatabase] = useState(true);

  useEffect(() => {
    if (personaData) {
      setEditedData({ ...personaData });
    }
  }, [personaData]);

  if (!isOpen || !editedData) return null;

  const handleSave = () => {
    onSave(editedData, saveToDatabase);
  };

  const updateField = (path: string, value: any) => {
    setEditedData(prev => {
      if (!prev) return prev;
      const newData = { ...prev };
      const keys = path.split('.');
      let current: any = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) {
          current[keys[i]] = {};
        }
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  const getFieldValue = (path: string, defaultValue: any = '') => {
    const keys = path.split('.');
    let current: any = editedData;
    
    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        return defaultValue;
      }
    }
    
    return current || defaultValue;
  };

  const tabs = [
    { id: 'core', label: 'Core Identity', icon: '🎭' },
    { id: 'linguistic', label: 'Linguistic', icon: '📝' },
    { id: 'platform', label: 'Platform', icon: '🔗' },
    { id: 'optimization', label: 'Optimization', icon: '⚡' }
  ] as const;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        width: '100%',
        maxWidth: '800px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '24px 24px 0 24px',
          borderBottom: '1px solid #e5e7eb',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: '24px', fontWeight: '700' }}>
                Edit Persona: {getFieldValue('persona_name', 'Untitled Persona')}
              </h2>
              <p style={{ margin: '4px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
                Platform: {platform} • Confidence: {(() => {
                  const score = getFieldValue('confidence_score', 0) || 0;
                  console.log('PersonaEditorModal confidence_score:', score);
                  return score;
                })()}%
              </p>
            </div>
            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                borderRadius: '8px',
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                fontSize: '18px',
                color: 'white'
              }}
            >
              ✕
            </button>
          </div>
          
          {/* Tabs */}
          <div style={{ display: 'flex', gap: '4px' }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: activeTab === tab.id ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                  border: 'none',
                  borderRadius: '8px 8px 0 0',
                  padding: '12px 16px',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease'
                }}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: '24px'
        }}>
          {activeTab === 'core' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                  Persona Name
                </label>
                <input
                  type="text"
                  value={getFieldValue('persona_name', '')}
                  onChange={(e) => updateField('persona_name', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    transition: 'border-color 0.2s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                  Archetype / Guide
                </label>
                <textarea
                  value={getFieldValue('archetype', '')}
                  onChange={(e) => updateField('archetype', e.target.value)}
                  rows={2}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    resize: 'vertical',
                    minHeight: '60px',
                    transition: 'border-color 0.2s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                  Core Belief / Mission
                </label>
                <textarea
                  value={getFieldValue('core_belief', '')}
                  onChange={(e) => updateField('core_belief', e.target.value)}
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    resize: 'vertical',
                    minHeight: '80px',
                    transition: 'border-color 0.2s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                  Brand Voice / Speaking Style
                </label>
                <textarea
                  value={getFieldValue('brand_voice_description', '')}
                  onChange={(e) => updateField('brand_voice_description', e.target.value)}
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    resize: 'vertical',
                    minHeight: '80px',
                    transition: 'border-color 0.2s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Confidence Score
                  </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={getFieldValue('confidence_score', '')}
                      onChange={(e) => updateField('confidence_score', parseInt(e.target.value) || 0)}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#667eea'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    AI Analysis Version
                  </label>
                  <input
                    type="text"
                    value={getFieldValue('ai_analysis_version', '')}
                    onChange={(e) => updateField('ai_analysis_version', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#667eea'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'linguistic' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Sentence Metrics
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Average Sentence Length (words)
                    </label>
                    <input
                      type="number"
                      value={getFieldValue('linguistic_fingerprint.sentence_metrics.average_sentence_length_words', '')}
                      onChange={(e) => updateField('linguistic_fingerprint.sentence_metrics.average_sentence_length_words', parseInt(e.target.value) || '')}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Preferred Sentence Type
                    </label>
                    <select
                      value={getFieldValue('linguistic_fingerprint.sentence_metrics.preferred_sentence_type', '')}
                      onChange={(e) => updateField('linguistic_fingerprint.sentence_metrics.preferred_sentence_type', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                    >
                      <option value="simple_and_compound">Simple and Compound</option>
                      <option value="complex">Complex</option>
                      <option value="mixed">Mixed</option>
                    </select>
                  </div>
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Lexical Features
                </h3>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Go-to Words (comma-separated)
                  </label>
                  <textarea
                    value={getFieldValue('linguistic_fingerprint.lexical_features.go_to_words', []).join(', ')}
                    onChange={(e) => updateField('linguistic_fingerprint.lexical_features.go_to_words', e.target.value.split(',').map(w => w.trim()).filter(w => w))}
                    rows={2}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '60px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                    placeholder="e.g., innovative, strategic, transformative, impactful, leverage"
                  />
                </div>
                <div style={{ marginTop: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Avoid Words (comma-separated)
                  </label>
                  <textarea
                    value={getFieldValue('linguistic_fingerprint.lexical_features.avoid_words', []).join(', ')}
                    onChange={(e) => updateField('linguistic_fingerprint.lexical_features.avoid_words', e.target.value.split(',').map(w => w.trim()).filter(w => w))}
                    rows={2}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '60px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                    placeholder="e.g., buzzwords, jargon, clichés, overly technical terms"
                  />
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Tonal Range
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Default Tone
                    </label>
                    <select
                      value={getFieldValue('tonal_range.default_tone', '')}
                      onChange={(e) => updateField('tonal_range.default_tone', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                    >
                      <option value="professional">Professional</option>
                      <option value="conversational">Conversational</option>
                      <option value="authoritative">Authoritative</option>
                      <option value="inspirational">Inspirational</option>
                      <option value="educational">Educational</option>
                      <option value="friendly">Friendly</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Permissible Tones (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={getFieldValue('tonal_range.permissible_tones', []).join(', ')}
                      onChange={(e) => updateField('tonal_range.permissible_tones', e.target.value.split(',').map(w => w.trim()).filter(w => w))}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                      placeholder="e.g., professional, conversational, authoritative"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'platform' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Content Format Rules
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Character Limit
                    </label>
                    <input
                      type="number"
                      value={getFieldValue('content_format_rules.character_limit', '')}
                      onChange={(e) => updateField('content_format_rules.character_limit', parseInt(e.target.value) || 3000)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Optimal Length
                    </label>
                    <input
                      type="text"
                      value={getFieldValue('content_format_rules.optimal_length', '')}
                      onChange={(e) => updateField('content_format_rules.optimal_length', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                      placeholder="e.g., 150-200 words"
                    />
                  </div>
                </div>
                <div style={{ marginTop: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Paragraph Structure
                  </label>
                  <textarea
                    value={getFieldValue('content_format_rules.paragraph_structure', '')}
                    onChange={(e) => updateField('content_format_rules.paragraph_structure', e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '80px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                  />
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Engagement Patterns
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Posting Frequency
                    </label>
                    <select
                      value={getFieldValue('engagement_patterns.posting_frequency', '')}
                      onChange={(e) => updateField('engagement_patterns.posting_frequency', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                    >
                      <option value="daily">Daily</option>
                      <option value="2-3 times per week">2-3 times per week</option>
                      <option value="weekly">Weekly</option>
                      <option value="bi-weekly">Bi-weekly</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                      Best Posting Times
                    </label>
                    <input
                      type="text"
                      value={getFieldValue('engagement_patterns.best_posting_times', '')}
                      onChange={(e) => updateField('engagement_patterns.best_posting_times', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #e5e7eb',
                        borderRadius: '8px',
                        fontSize: '16px',
                        transition: 'border-color 0.2s ease',
                        outline: 'none'
                      }}
                      placeholder="e.g., Tuesday-Thursday, 8-10 AM or 1-3 PM"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Content Types
                </h3>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Preferred Content Types (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={getFieldValue('content_types.preferred_types', []).join(', ')}
                    onChange={(e) => updateField('content_types.preferred_types', e.target.value.split(',').map(w => w.trim()).filter(w => w))}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                    placeholder="e.g., thought leadership, industry insights, case studies, tips"
                  />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'optimization' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Platform Best Practices
                </h3>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Hashtag Strategy
                  </label>
                  <textarea
                    value={getFieldValue('platform_best_practices.hashtag_strategy', '')}
                    onChange={(e) => updateField('platform_best_practices.hashtag_strategy', e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '80px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                  />
                </div>
                <div style={{ marginTop: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Call-to-Action Style
                  </label>
                  <textarea
                    value={getFieldValue('platform_best_practices.cta_style', '')}
                    onChange={(e) => updateField('platform_best_practices.cta_style', e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '80px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                  />
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Algorithm Considerations
                </h3>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Engagement Optimization
                  </label>
                  <textarea
                    value={getFieldValue('algorithm_considerations.engagement_optimization', '')}
                    onChange={(e) => updateField('algorithm_considerations.engagement_optimization', e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '80px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                  />
                </div>
                <div style={{ marginTop: '16px' }}>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Content Timing
                  </label>
                  <textarea
                    value={getFieldValue('algorithm_considerations.content_timing', '')}
                    onChange={(e) => updateField('algorithm_considerations.content_timing', e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '80px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                  />
                </div>
              </div>

              <div>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#374151' }}>
                  Stylistic Constraints
                </h3>
                <div>
                  <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>
                    Forbidden Elements
                  </label>
                  <textarea
                    value={getFieldValue('stylistic_constraints.forbidden_elements', '')}
                    onChange={(e) => updateField('stylistic_constraints.forbidden_elements', e.target.value)}
                    rows={3}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      minHeight: '80px',
                      transition: 'border-color 0.2s ease',
                      outline: 'none'
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '20px 24px',
          borderTop: '1px solid #e5e7eb',
          backgroundColor: '#f9fafb',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px', color: '#374151' }}>
            <input
              type="checkbox"
              checked={saveToDatabase}
              onChange={(e) => setSaveToDatabase(e.target.checked)}
              style={{ margin: 0 }}
            />
            Save changes to database
            <span style={{ fontSize: '12px', color: '#6b7280' }}>
              {saveToDatabase ? 'Changes will be permanent' : 'Changes will be session-only'}
            </span>
          </label>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={onClose}
              style={{
                padding: '10px 20px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                backgroundColor: 'white',
                color: '#374151',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#d1d5db';
                e.currentTarget.style.backgroundColor = '#f9fafb';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e5e7eb';
                e.currentTarget.style.backgroundColor = 'white';
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '8px',
                backgroundColor: '#667eea',
                color: 'white',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#5a67d8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#667eea';
              }}
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonaEditorModal;