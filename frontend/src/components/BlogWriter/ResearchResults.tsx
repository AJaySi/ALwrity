import React, { useState, useEffect } from 'react';
import { BlogResearchResponse } from '../../services/blogWriterApi';
import { ResearchSources, ResearchGrounding } from './ResearchComponents';

interface ResearchResultsProps {
  research: BlogResearchResponse;
}

export const ResearchResults: React.FC<ResearchResultsProps> = ({ research }) => {
  const [showAnglesModal, setShowAnglesModal] = useState(false);
  const [showCompetitorModal, setShowCompetitorModal] = useState(false);
  const [showGroundingModal, setShowGroundingModal] = useState(false);
  const [showToast, setShowToast] = useState(false);

  // Show toast message on component mount
  useEffect(() => {
    setShowToast(true);
    const timer = setTimeout(() => {
      setShowToast(false);
    }, 4000); // Show for 4 seconds

    return () => clearTimeout(timer);
  }, []);

  



  const renderAnglesModal = () => {
    if (!showAnglesModal) return null;
    
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
        zIndex: 1000
      }}
      onClick={() => setShowAnglesModal(false)}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          padding: '24px',
          maxWidth: '600px',
          maxHeight: '80vh',
          overflow: 'auto',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)'
        }}
        onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ margin: 0, color: '#333', fontSize: '18px' }}>💡 Content Angles ({research.suggested_angles.length})</h3>
            <button
              onClick={() => setShowAnglesModal(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#666',
                padding: '0',
                width: '30px',
                height: '30px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              ×
            </button>
          </div>
          
          <div style={{ display: 'grid', gap: '12px' }}>
            {research.suggested_angles.map((angle, index) => (
              <div key={index} style={{
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                padding: '16px',
                backgroundColor: '#fafafa',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f0f0f0';
                e.currentTarget.style.borderColor = '#1976d2';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fafafa';
                e.currentTarget.style.borderColor = '#e0e0e0';
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    backgroundColor: '#1976d2',
                    color: 'white',
                    width: '24px',
                    height: '24px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {index + 1}
                  </span>
                  <h4 style={{ margin: 0, fontSize: '14px', fontWeight: '500', color: '#333' }}>
                    {angle}
                  </h4>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };









  const renderCompetitorModal = () => {
    if (!showCompetitorModal) return null;

    const ca = research.competitor_analysis || {} as any;
    const top_competitors: string[] = Array.isArray(ca.top_competitors) ? ca.top_competitors : [];
    const opportunities: string[] = Array.isArray(ca.opportunities) ? ca.opportunities : [];
    const competitive_advantages: string[] = Array.isArray(ca.competitive_advantages) ? ca.competitive_advantages : [];
    const market_positioning: string | undefined = typeof ca.market_positioning === 'string' ? ca.market_positioning : undefined;

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
        zIndex: 1000
      }}
      onClick={() => setShowCompetitorModal(false)}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '800px',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #e5e7eb'
        }}
        onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h3 style={{ margin: 0, color: '#1f2937', fontSize: '24px', fontWeight: '700' }}>📈 Competitor Analysis</h3>
            <button
              onClick={() => setShowCompetitorModal(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#6b7280',
                padding: '8px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
                e.currentTarget.style.color = '#374151';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#6b7280';
              }}
            >
              ×
            </button>
          </div>
          
          <div style={{ display: 'grid', gap: '20px' }}>
            {/* Summary cards */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px'
            }}>
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '20px', 
                background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                borderLeft: '4px solid #0ea5e9'
              }}>
                <div style={{ fontSize: '14px', color: '#0369a1', fontWeight: '600', marginBottom: '8px' }}>Top Competitors</div>
                <div style={{ fontSize: '32px', fontWeight: '700', color: '#0c4a6e' }}>{top_competitors.length}</div>
              </div>
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '20px', 
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                borderLeft: '4px solid #22c55e'
              }}>
                <div style={{ fontSize: '14px', color: '#15803d', fontWeight: '600', marginBottom: '8px' }}>Opportunities</div>
                <div style={{ fontSize: '32px', fontWeight: '700', color: '#166534' }}>{opportunities.length}</div>
              </div>
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '20px', 
                background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
                borderLeft: '4px solid #f59e0b'
              }}>
                <div style={{ fontSize: '14px', color: '#d97706', fontWeight: '600', marginBottom: '8px' }}>Competitive Advantages</div>
                <div style={{ fontSize: '32px', fontWeight: '700', color: '#92400e' }}>{competitive_advantages.length}</div>
              </div>
            </div>

            {/* Market positioning */}
            {market_positioning && (
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '24px', 
                background: '#ffffff',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
              }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>🎯 Market Positioning</h4>
                <p style={{ margin: 0, color: '#4b5563', lineHeight: '1.7', fontSize: '15px' }}>{market_positioning}</p>
              </div>
            )}

            {/* Lists */}
            {top_competitors.length > 0 && (
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '24px', 
                background: '#ffffff',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
              }}>
                <h4 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>🏁 Top Competitors ({top_competitors.length})</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {top_competitors.map((c, i) => (
                    <span key={i} style={{ 
                      background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)', 
                      color: '#1e40af', 
                      padding: '8px 16px', 
                      borderRadius: '20px', 
                      fontSize: '13px',
                      fontWeight: '500',
                      border: '1px solid #93c5fd'
                    }}>{c}</span>
                  ))}
                </div>
              </div>
            )}

            {opportunities.length > 0 && (
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '24px', 
                background: '#ffffff',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
              }}>
                <h4 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>🚀 Opportunities ({opportunities.length})</h4>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#4b5563', lineHeight: '1.7', fontSize: '15px' }}>
                  {opportunities.map((o, i) => (
                    <li key={i} style={{ marginBottom: '8px' }}>{o}</li>
                  ))}
                </ul>
              </div>
            )}

            {competitive_advantages.length > 0 && (
              <div style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '12px', 
                padding: '24px', 
                background: '#ffffff',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
              }}>
                <h4 style={{ margin: '0 0 16px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>✅ Competitive Advantages ({competitive_advantages.length})</h4>
                <ul style={{ margin: 0, paddingLeft: '20px', color: '#4b5563', lineHeight: '1.7', fontSize: '15px' }}>
                  {competitive_advantages.map((a, i) => (
                    <li key={i} style={{ marginBottom: '8px' }}>{a}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderGroundingModal = () => {
    if (!showGroundingModal) return null;

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
        zIndex: 1000
      }}
      onClick={() => setShowGroundingModal(false)}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '32px',
          maxWidth: '900px',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #e5e7eb'
        }}
        onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h3 style={{ margin: 0, color: '#1f2937', fontSize: '24px', fontWeight: '700' }}>🔗 Grounding Analysis</h3>
            <button
              onClick={() => setShowGroundingModal(false)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                color: '#6b7280',
                padding: '8px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f3f4f6';
                e.currentTarget.style.color = '#374151';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = '#6b7280';
              }}
            >
              ×
            </button>
          </div>
          
          {/* Grounding Content */}
          <ResearchGrounding research={research} />
        </div>
      </div>
    );
  };

  return (
    <>
      <style>
        {`
          @keyframes slideInRight {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        border: '1px solid #e0e0e0',
        margin: '16px 0'
      }}>
      {/* Header */}
      <div style={{ 
        padding: '16px', 
        borderBottom: '1px solid #e0e0e0',
        backgroundColor: '#f8f9fa'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
        <h2 style={{ margin: 0, color: '#333', fontSize: '18px' }}>
            📊 Research Results for {research.keywords?.join(', ') || 'Your Topic'}
        </h2>
        </div>
          
          {/* Action Chips */}
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {/* Competitor Analysis Chip */}
            <div 
              onClick={() => setShowCompetitorModal(true)}
              style={{
                backgroundColor: '#f0f9ff',
                color: '#1e40af',
                border: '1px solid #3b82f6',
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#dbeafe';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f0f9ff';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              📈 Competitor Analysis
            </div>

            {/* Grounding Analysis Chip */}
            <div 
              onClick={() => setShowGroundingModal(true)}
              style={{
                backgroundColor: '#faf5ff',
                color: '#7c3aed',
                border: '1px solid #8b5cf6',
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f3e8ff';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#faf5ff';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              🔗 Grounding Analysis
            </div>

            {/* Use Research Blog Topics Chip */}
            <div 
              onClick={() => setShowAnglesModal(true)}
              style={{
                backgroundColor: '#e8f5e8',
                color: '#2e7d32',
                border: '1px solid #4caf50',
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#c8e6c9';
                e.currentTarget.style.transform = 'scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#e8f5e8';
                e.currentTarget.style.transform = 'scale(1)';
              }}
            >
              📝 Use Research Blog Topics
            </div>
          </div>
        </div>
        
      </div>


      {/* Toast Message */}
      {showToast && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          backgroundColor: '#10b981',
          color: 'white',
          padding: '12px 20px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: '500',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          animation: 'slideInRight 0.3s ease-out'
        }}>
          <span>✅</span>
          <span>Google Search grounding analysis completed with {research.sources.length} sources and {research.search_queries?.length || 0} search queries</span>
        </div>
      )}


      {/* Content */}
      <ResearchSources research={research} />
      
      {/* Modals */}
      {renderAnglesModal()}
      {renderCompetitorModal()}
      {renderGroundingModal()}
      </div>
    </>
  );
};

export default ResearchResults;
