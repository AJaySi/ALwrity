import React, { useState } from 'react';
import { ResearchWizard } from '../components/Research';
import { BlogResearchResponse } from '../services/blogWriterApi';

const samplePresets = [
  {
    name: 'AI Marketing Tools',
    keywords: 'AI in marketing, automation tools, customer engagement',
    industry: 'Technology',
    icon: '🤖',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  },
  {
    name: 'Small Business SEO',
    keywords: 'local SEO, small business, Google My Business',
    industry: 'Marketing',
    icon: '📈',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  },
  {
    name: 'Content Strategy',
    keywords: 'content planning, editorial calendar, content creation',
    industry: 'Marketing',
    icon: '✍️',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
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
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Elements */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '5%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 20s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '10%',
        right: '5%',
        width: '300px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 15s ease-in-out infinite reverse',
      }} />
      
      <style>{`
        @keyframes float {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(20px, 20px); }
        }
        @keyframes shimmer {
          0% { background-position: -1000px 0; }
          100% { background-position: 1000px 0; }
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .card-hover {
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .card-hover:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
      `}</style>
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.7)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(14, 165, 233, 0.15)',
        padding: '16px 24px',
        marginBottom: '20px',
        position: 'relative',
        zIndex: 10,
        boxShadow: '0 1px 3px rgba(14, 165, 233, 0.1)',
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              boxShadow: '0 4px 12px rgba(14, 165, 233, 0.25)',
            }}>
              🔬
            </div>
            <div>
              <h1 style={{ 
                margin: 0, 
                fontSize: '24px', 
                fontWeight: '700',
                color: '#0c4a6e',
                letterSpacing: '-0.01em',
              }}>
                AI-Powered Research Lab
              </h1>
              <p style={{ 
                margin: '2px 0 0 0', 
                fontSize: '13px', 
                color: '#0369a1',
                fontWeight: '400',
              }}>
                Enterprise-grade research intelligence at your fingertips
              </p>
            </div>
          </div>
          
          {/* Status Badge - Moved to Header */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.25)',
            borderRadius: '20px',
            fontSize: '12px',
            color: '#16a34a',
            fontWeight: '600',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#22c55e',
              boxShadow: '0 0 8px rgba(34, 197, 94, 0.6)',
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }} />
            System Online • AI Models Ready
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 24px', display: 'flex', gap: '20px', flexWrap: 'wrap', position: 'relative', zIndex: 10 }}>
        {/* Left Panel - Controls */}
        <div style={{ flex: '1 1 280px', minWidth: '280px' }}>
          {/* Presets Card */}
          <div className="card-hover" style={{
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(14, 165, 233, 0.2)',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '20px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
            animation: 'fadeInUp 0.6s ease-out',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px',
              }}>
                🎯
              </div>
              <h3 style={{ margin: 0, color: '#0c4a6e', fontSize: '18px', fontWeight: '600' }}>
                Quick Start Presets
              </h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {samplePresets.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePresetClick(preset)}
                  className="card-hover"
                  style={{
                    padding: '14px',
                    background: 'rgba(255, 255, 255, 0.9)',
                    border: '1px solid rgba(14, 165, 233, 0.2)',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateX(4px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(14, 165, 233, 0.2)';
                    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateX(0)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '20px' }}>{preset.icon}</span>
                    <div style={{ fontWeight: '600', color: '#0c4a6e', fontSize: '14px' }}>
                      {preset.name}
                    </div>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', lineHeight: '1.5' }}>
                    {preset.keywords}
                  </div>
                  <div style={{
                    marginTop: '6px',
                    display: 'inline-block',
                    padding: '3px 10px',
                    background: 'rgba(14, 165, 233, 0.1)',
                    borderRadius: '10px',
                    fontSize: '10px',
                    color: '#0369a1',
                    fontWeight: '600',
                  }}>
                    {preset.industry}
                  </div>
                </button>
              ))}
            </div>
            
            <button
              onClick={handleReset}
              style={{
                marginTop: '12px',
                padding: '10px 16px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: '10px',
                cursor: 'pointer',
                fontSize: '13px',
                width: '100%',
                color: '#dc2626',
                fontWeight: '500',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
                e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)';
              }}
            >
              ↻ Reset Research
            </button>
          </div>

          {/* Debug Panel */}
          <div className="card-hover" style={{
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(14, 165, 233, 0.2)',
            borderRadius: '16px',
            padding: '20px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
            animation: 'fadeInUp 0.8s ease-out',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '18px',
                }}>
                  🐛
                </div>
                <h3 style={{ margin: 0, color: '#0c4a6e', fontSize: '18px', fontWeight: '600' }}>
                  Debug Console
                </h3>
              </div>
              <label style={{ 
                cursor: 'pointer', 
                fontSize: '12px',
                color: '#64748b',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}>
                <input
                  type="checkbox"
                  checked={showDebug}
                  onChange={(e) => setShowDebug(e.target.checked)}
                  style={{ 
                    marginRight: '0',
                    width: '14px',
                    height: '14px',
                    cursor: 'pointer',
                  }}
                />
                Show Data
              </label>
            </div>

            {showDebug && (
              <div style={{
                background: 'rgba(15, 23, 42, 0.05)',
                borderRadius: '10px',
                padding: '12px',
                fontSize: '11px',
                fontFamily: "'Fira Code', 'Monaco', monospace",
                maxHeight: '350px',
                overflow: 'auto',
                border: '1px solid rgba(14, 165, 233, 0.1)',
              }}>
                <pre style={{ 
                  margin: 0, 
                  whiteSpace: 'pre-wrap', 
                  wordBreak: 'break-word',
                  color: '#475569',
                  lineHeight: '1.6',
                }}>
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Main Content - Wizard */}
        <div style={{ flex: '2 1 800px', animation: 'fadeInUp 0.4s ease-out' }}>
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
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(12px)',
          borderTop: '1px solid rgba(14, 165, 233, 0.15)',
          padding: '24px',
          marginTop: '32px',
          position: 'relative',
          zIndex: 10,
        }}>
          <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                boxShadow: '0 4px 12px rgba(14, 165, 233, 0.25)',
              }}>
                📊
              </div>
              <h3 style={{ 
                margin: 0, 
                color: '#0c4a6e', 
                fontSize: '20px',
                fontWeight: '600',
              }}>
                Research Intelligence Report
              </h3>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div className="card-hover" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '14px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                boxShadow: '0 2px 8px rgba(14, 165, 233, 0.08)',
              }}>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  marginBottom: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  Sources Discovered
                </div>
                <div style={{ 
                  fontSize: '36px', 
                  fontWeight: '700', 
                  color: '#0284c7',
                  lineHeight: '1',
                }}>
                  {results.sources.length}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#64748b', 
                  marginTop: '6px',
                }}>
                  High-quality references
                </div>
              </div>

              <div className="card-hover" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '14px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                boxShadow: '0 2px 8px rgba(14, 165, 233, 0.08)',
              }}>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  marginBottom: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  Content Angles
                </div>
                <div style={{ 
                  fontSize: '36px', 
                  fontWeight: '700', 
                  color: '#0284c7',
                  lineHeight: '1',
                }}>
                  {results.suggested_angles.length}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#64748b', 
                  marginTop: '6px',
                }}>
                  Unique perspectives
                </div>
              </div>

              <div className="card-hover" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '14px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                boxShadow: '0 2px 8px rgba(14, 165, 233, 0.08)',
              }}>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  marginBottom: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  Search Queries
                </div>
                <div style={{ 
                  fontSize: '36px', 
                  fontWeight: '700', 
                  color: '#0284c7',
                  lineHeight: '1',
                }}>
                  {results.search_queries?.length || 0}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#64748b', 
                  marginTop: '6px',
                }}>
                  Optimized searches
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

