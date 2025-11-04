import React from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface GoogleSearchModalProps {
  research: BlogResearchResponse;
  onClose: () => void;
}

export const GoogleSearchModal: React.FC<GoogleSearchModalProps> = ({ research, onClose }) => {
  if (!research.search_widget && !research.search_queries?.length) {
    return null;
  }

  const handleSearchClick = (query: string) => {
    // Open Google Search in new tab per Google requirements
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    window.open(searchUrl, '_blank', 'noopener,noreferrer');
  };

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
      zIndex: 1000,
      backdropFilter: 'blur(4px)'
    }}
    onClick={onClose}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        maxWidth: '800px',
        width: '90%',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        border: '1px solid #e5e7eb',
        position: 'relative'
      }}
      onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '24px',
          borderBottom: '2px solid #f3f4f6',
          paddingBottom: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              backgroundColor: '#f8fafc',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid #e2e8f0'
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="#4285F4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h3 style={{ 
                margin: 0, 
                color: '#1f2937', 
                fontSize: '24px', 
                fontWeight: '700' 
              }}>
                Google Search Suggestions
              </h3>
              <p style={{ 
                margin: '4px 0 0 0', 
                color: '#6b7280', 
                fontSize: '14px' 
              }}>
                Explore related searches and sources
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '28px',
              cursor: 'pointer',
              color: '#6b7280',
              padding: '8px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease',
              width: '40px',
              height: '40px'
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

        {/* Google Search Widget - Display exactly as provided per Google requirements */}
        {research.search_widget && (
          <div style={{ 
            marginBottom: '32px',
            width: '100%',
            padding: '20px',
            backgroundColor: '#f8fafc',
            borderRadius: '12px',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ 
              marginBottom: '12px',
              fontSize: '13px',
              fontWeight: '600',
              color: '#475569',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>🔍</span>
              <span>Search Suggestions (Click to open in Google)</span>
            </div>
            {/* Render Google's HTML exactly as provided - no modifications */}
            <div 
              dangerouslySetInnerHTML={{ __html: research.search_widget }}
            />
          </div>
        )}

        {/* Search Queries List */}
        {research.search_queries && research.search_queries.length > 0 && (
          <div style={{ marginTop: '32px' }}>
            <h4 style={{ 
              margin: '0 0 16px 0', 
              color: '#1f2937', 
              fontSize: '18px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>📋</span>
              Additional Search Queries
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {research.search_queries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleSearchClick(query)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    backgroundColor: 'white',
                    border: '1px solid #d1d5db',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px',
                    color: '#374151',
                    transition: 'all 0.2s ease',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9fafb';
                    e.currentTarget.style.borderColor = '#4285F4';
                    e.currentTarget.style.transform = 'translateX(4px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'white';
                    e.currentTarget.style.borderColor = '#d1d5db';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }}
                >
                  <span style={{ flex: 1 }}>{query}</span>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ flexShrink: 0 }}>
                    <path d="M7 17L17 7M17 7H7M17 7V17" stroke="#4285F4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Info Footer */}
        <div style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: '#eff6ff',
          borderRadius: '8px',
          border: '1px solid #bfdbfe'
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'flex-start', 
            gap: '8px',
            fontSize: '13px',
            color: '#1e40af'
          }}>
            <span style={{ fontSize: '16px', lineHeight: '1.5' }}>ℹ️</span>
            <div>
              <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                About These Suggestions
              </div>
              <div style={{ lineHeight: '1.6' }}>
                These search suggestions are generated by Google's AI to help you explore related topics. 
                Clicking any suggestion will open Google Search in a new tab to find the latest and most relevant information.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GoogleSearchModal;

