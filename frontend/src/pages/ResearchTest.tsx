import React, { useState } from 'react';
import { ResearchWizard } from '../components/Research';
import { BlogResearchResponse } from '../services/blogWriterApi';

const samplePresets = [
  {
    name: 'AI Marketing Tools',
    keywords: 'AI in marketing, automation tools, customer engagement',
    industry: 'Technology',
  },
  {
    name: 'Small Business SEO',
    keywords: 'local SEO, small business, Google My Business',
    industry: 'Marketing',
  },
  {
    name: 'Content Strategy',
    keywords: 'content planning, editorial calendar, content creation',
    industry: 'Marketing',
  },
];

export const ResearchTest: React.FC = () => {
  const [results, setResults] = useState<BlogResearchResponse | null>(null);
  const [showDebug, setShowDebug] = useState(false);
  const [presetKeywords, setPresetKeywords] = useState<string[] | undefined>();
  const [presetIndustry, setPresetIndustry] = useState<string | undefined>();

  const handleComplete = (researchResults: BlogResearchResponse) => {
    setResults(researchResults);
  };

  const handlePresetClick = (preset: typeof samplePresets[0]) => {
    setPresetKeywords(preset.keywords.split(',').map(k => k.trim()));
    setPresetIndustry(preset.industry);
    setResults(null);
  };

  const handleReset = () => {
    setPresetKeywords(undefined);
    setPresetIndustry(undefined);
    setResults(null);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#1976d2',
        color: 'white',
        padding: '20px',
        marginBottom: '20px',
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <h1 style={{ margin: 0, fontSize: '28px' }}>🔬 Research Component Test Page</h1>
          <p style={{ margin: '8px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
            Test the modular research wizard component
          </p>
        </div>
      </div>

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 20px', display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        {/* Left Panel - Controls */}
        <div style={{ flex: '1 1 300px', minWidth: '300px' }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#333', fontSize: '18px' }}>
              🎯 Quick Presets
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {samplePresets.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePresetClick(preset)}
                  style={{
                    padding: '12px',
                    backgroundColor: '#f0f7ff',
                    border: '1px solid #b3d9ff',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#e3f2fd';
                    e.currentTarget.style.borderColor = '#90caf9';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#f0f7ff';
                    e.currentTarget.style.borderColor = '#b3d9ff';
                  }}
                >
                  <div style={{ fontWeight: '600', color: '#1976d2', marginBottom: '4px' }}>
                    {preset.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {preset.keywords}
                  </div>
                </button>
              ))}
            </div>
            
            <button
              onClick={handleReset}
              style={{
                marginTop: '12px',
                padding: '8px 16px',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ddd',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '13px',
                width: '100%',
              }}
            >
              ↻ Reset Test
            </button>
          </div>

          {/* Debug Panel */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ margin: 0, color: '#333', fontSize: '18px' }}>
                🐛 Debug Panel
              </h3>
              <label style={{ cursor: 'pointer', fontSize: '14px' }}>
                <input
                  type="checkbox"
                  checked={showDebug}
                  onChange={(e) => setShowDebug(e.target.checked)}
                  style={{ marginRight: '6px' }}
                />
                Show Debug
              </label>
            </div>

            {showDebug && (
              <div style={{
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                padding: '12px',
                fontSize: '12px',
                fontFamily: 'monospace',
                maxHeight: '400px',
                overflow: 'auto',
              }}>
                <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Main Content - Wizard */}
        <div style={{ flex: '2 1 800px' }}>
          <ResearchWizard
            initialKeywords={presetKeywords}
            initialIndustry={presetIndustry}
            onComplete={handleComplete}
          />
        </div>
      </div>

      {/* Footer Stats */}
      {results && (
        <div style={{
          backgroundColor: 'white',
          borderTop: '2px solid #e0e0e0',
          padding: '20px',
          marginTop: '40px',
        }}>
          <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <h3 style={{ margin: '0 0 16px 0', color: '#333', fontSize: '18px' }}>
              📊 Research Statistics
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div style={{
                backgroundColor: '#e3f2fd',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #90caf9',
              }}>
                <div style={{ fontSize: '12px', color: '#1976d2', fontWeight: '600', marginBottom: '4px' }}>
                  Sources Found
                </div>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#1976d2' }}>
                  {results.sources.length}
                </div>
              </div>

              <div style={{
                backgroundColor: '#f3e5f5',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #ce93d8',
              }}>
                <div style={{ fontSize: '12px', color: '#7b1fa2', fontWeight: '600', marginBottom: '4px' }}>
                  Content Angles
                </div>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#7b1fa2' }}>
                  {results.suggested_angles.length}
                </div>
              </div>

              <div style={{
                backgroundColor: '#e8f5e8',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #81c784',
              }}>
                <div style={{ fontSize: '12px', color: '#2e7d32', fontWeight: '600', marginBottom: '4px' }}>
                  Search Queries
                </div>
                <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#2e7d32' }}>
                  {results.search_queries?.length || 0}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchTest;

