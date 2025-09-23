import React, { useState } from 'react';
import { BlogOutlineSection } from '../../services/blogWriterApi';

interface EnhancedTitleSelectorProps {
  titleOptions: string[];
  selectedTitle?: string;
  onTitleSelect: (title: string) => void;
  onCustomTitle?: (title: string) => void;
  sections: BlogOutlineSection[];
  researchTitles?: string[];
  aiGeneratedTitles?: string[];
}

const EnhancedTitleSelector: React.FC<EnhancedTitleSelectorProps> = ({ 
  titleOptions, 
  selectedTitle, 
  onTitleSelect, 
  onCustomTitle,
  sections,
  researchTitles = [],
  aiGeneratedTitles = []
}) => {
  const [showModal, setShowModal] = useState(false);
  const [customTitle, setCustomTitle] = useState('');

  const handleTitleSelect = (title: string) => {
    onTitleSelect(title);
    setShowModal(false);
  };

  const handleCustomTitleSubmit = () => {
    if (customTitle.trim() && onCustomTitle) {
      onCustomTitle(customTitle.trim());
      setCustomTitle('');
      setShowModal(false);
    }
  };

  const getSectionSummary = () => {
    return sections.map(section => ({
      title: section.heading,
      wordCount: section.target_words || 0,
      subheadings: section.subheadings.length,
      keyPoints: section.key_points.length
    }));
  };

  const sectionSummary = getSectionSummary();

  return (
    <>
      {/* Main Title Display */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        border: '1px solid #e0e0e0',
        padding: '20px',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ margin: '0 0 8px 0', color: '#333', fontSize: '18px' }}>
              📝 Blog Title
            </h3>
            <p style={{ 
              margin: '0', 
              color: '#666', 
              fontSize: '14px',
              wordBreak: 'break-word',
              lineHeight: '1.4',
              maxHeight: '60px',
              overflow: 'hidden',
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical'
            }}>
              {selectedTitle || 'No title selected'}
            </p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            style={{
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            ✨ ALwrity it
          </button>
        </div>
      </div>

      {/* Title Selection Modal */}
      {showModal && (
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
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '32px',
            maxWidth: '900px',
            width: '95%',
            maxHeight: '85vh',
            overflow: 'auto',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            border: '1px solid #e5e7eb'
          }}>
            {/* Modal Header */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '32px',
              paddingBottom: '16px',
              borderBottom: '2px solid #f3f4f6'
            }}>
              <div>
                <h2 style={{ margin: '0 0 4px 0', color: '#1f2937', fontSize: '24px', fontWeight: '600' }}>
                  ✨ ALwrity Title Suggestions
                </h2>
                <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
                  Choose from research-based content angles, AI-generated titles, or create your own
                </p>
              </div>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '28px',
                  cursor: 'pointer',
                  color: '#9ca3af',
                  padding: '4px',
                  borderRadius: '6px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#f3f4f6';
                  e.currentTarget.style.color = '#374151';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = '#9ca3af';
                }}
              >
                ×
              </button>
            </div>

            {/* Section Information */}
            <div style={{ 
              backgroundColor: '#f8f9fa', 
              borderRadius: '8px', 
              padding: '16px', 
              marginBottom: '24px' 
            }}>
              <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#333' }}>
                📋 Current Outline Summary
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '14px', color: '#666' }}>Total Sections</div>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: '#333' }}>{sections.length}</div>
                </div>
                <div>
                  <div style={{ fontSize: '14px', color: '#666' }}>Total Words</div>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: '#333' }}>
                    {sections.reduce((sum, section) => sum + (section.target_words || 0), 0)}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '14px', color: '#666' }}>Subheadings</div>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: '#333' }}>
                    {sections.reduce((sum, section) => sum + section.subheadings.length, 0)}
                  </div>
                </div>
              </div>
              
              {/* Section Details */}
              <div style={{ marginTop: '16px' }}>
                <h5 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>Section Details:</h5>
                <div style={{ display: 'grid', gap: '8px' }}>
                  {sectionSummary.map((section, index) => (
                    <div key={index} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '8px 12px',
                      backgroundColor: 'white',
                      borderRadius: '6px',
                      border: '1px solid #e0e0e0'
                    }}>
                      <span style={{ fontSize: '14px', fontWeight: '500' }}>{section.title}</span>
                      <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#666' }}>
                        <span>{section.wordCount} words</span>
                        <span>{section.subheadings} subheadings</span>
                        <span>{section.keyPoints} key points</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Title Options */}
            <div style={{ display: 'grid', gap: '24px' }}>
              {/* Research Content Angles */}
              {researchTitles.length > 0 && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                    <div style={{ 
                      width: '40px', 
                      height: '40px', 
                      backgroundColor: '#e3f2fd', 
                      borderRadius: '10px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      fontSize: '18px'
                    }}>
                      🔍
                    </div>
                    <div>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>
                        Research Content Angles
                      </h4>
                      <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
                        Titles derived from your research data and content angles
                      </p>
                    </div>
                    <span style={{ 
                      fontSize: '12px', 
                      backgroundColor: '#1976d2', 
                      color: 'white', 
                      padding: '4px 12px', 
                      borderRadius: '16px',
                      fontWeight: '500'
                    }}>
                      {researchTitles.length}
                    </span>
                  </div>
                  <div style={{ display: 'grid', gap: '10px' }}>
                    {researchTitles.map((title, index) => (
                      <button
                        key={`research-${index}`}
                        onClick={() => handleTitleSelect(title)}
                        style={{
                          width: '100%',
                          padding: '16px 20px',
                          border: selectedTitle === title ? '2px solid #1976d2' : '1px solid #e5e7eb',
                          borderRadius: '12px',
                          backgroundColor: selectedTitle === title ? '#f0f9ff' : 'white',
                          cursor: 'pointer',
                          textAlign: 'left',
                          fontSize: '15px',
                          color: '#1f2937',
                          transition: 'all 0.2s ease',
                          lineHeight: '1.4',
                          wordBreak: 'break-word'
                        }}
                        onMouseEnter={(e) => {
                          if (selectedTitle !== title) {
                            e.currentTarget.style.backgroundColor = '#f9fafb';
                            e.currentTarget.style.borderColor = '#d1d5db';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (selectedTitle !== title) {
                            e.currentTarget.style.backgroundColor = 'white';
                            e.currentTarget.style.borderColor = '#e5e7eb';
                          }
                        }}
                      >
                        {title}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* AI-Generated Titles */}
              {aiGeneratedTitles.length > 0 && (
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                    <div style={{ 
                      width: '40px', 
                      height: '40px', 
                      backgroundColor: '#f3e5f5', 
                      borderRadius: '10px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      fontSize: '18px'
                    }}>
                      🤖
                    </div>
                    <div>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>
                        AI-Generated Titles
                      </h4>
                      <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
                        Creative titles generated by AI based on your research
                      </p>
                    </div>
                    <span style={{ 
                      fontSize: '12px', 
                      backgroundColor: '#7b1fa2', 
                      color: 'white', 
                      padding: '4px 12px', 
                      borderRadius: '16px',
                      fontWeight: '500'
                    }}>
                      {aiGeneratedTitles.length}
                    </span>
                  </div>
                  <div style={{ display: 'grid', gap: '10px' }}>
                    {aiGeneratedTitles.map((title, index) => (
                      <button
                        key={`ai-${index}`}
                        onClick={() => handleTitleSelect(title)}
                        style={{
                          width: '100%',
                          padding: '16px 20px',
                          border: selectedTitle === title ? '2px solid #7b1fa2' : '1px solid #e5e7eb',
                          borderRadius: '12px',
                          backgroundColor: selectedTitle === title ? '#faf5ff' : 'white',
                          cursor: 'pointer',
                          textAlign: 'left',
                          fontSize: '15px',
                          color: '#1f2937',
                          transition: 'all 0.2s ease',
                          lineHeight: '1.4',
                          wordBreak: 'break-word'
                        }}
                        onMouseEnter={(e) => {
                          if (selectedTitle !== title) {
                            e.currentTarget.style.backgroundColor = '#f9fafb';
                            e.currentTarget.style.borderColor = '#d1d5db';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (selectedTitle !== title) {
                            e.currentTarget.style.backgroundColor = 'white';
                            e.currentTarget.style.borderColor = '#e5e7eb';
                          }
                        }}
                      >
                        {title}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Custom Title Input */}
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ 
                    width: '40px', 
                    height: '40px', 
                    backgroundColor: '#fef3c7', 
                    borderRadius: '10px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    fontSize: '18px'
                  }}>
                    ✏️
                  </div>
                  <div>
                    <h4 style={{ margin: '0 0 4px 0', fontSize: '18px', color: '#1f2937', fontWeight: '600' }}>
                      Custom Title
                    </h4>
                    <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>
                      Create your own unique title
                    </p>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <input
                    type="text"
                    value={customTitle}
                    onChange={(e) => setCustomTitle(e.target.value)}
                    placeholder="Enter your custom title..."
                    style={{
                      flex: 1,
                      padding: '16px 20px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '12px',
                      fontSize: '15px',
                      transition: 'all 0.2s ease'
                    }}
                    onKeyPress={(e) => e.key === 'Enter' && handleCustomTitleSubmit()}
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#1976d2';
                      e.currentTarget.style.boxShadow = '0 0 0 3px rgba(25, 118, 210, 0.1)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  />
                  <button
                    onClick={handleCustomTitleSubmit}
                    disabled={!customTitle.trim()}
                    style={{
                      padding: '16px 24px',
                      backgroundColor: customTitle.trim() ? '#1976d2' : '#d1d5db',
                      color: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      cursor: customTitle.trim() ? 'pointer' : 'not-allowed',
                      fontSize: '15px',
                      fontWeight: '600',
                      transition: 'all 0.2s ease',
                      minWidth: '120px'
                    }}
                    onMouseEnter={(e) => {
                      if (customTitle.trim()) {
                        e.currentTarget.style.backgroundColor = '#1565c0';
                        e.currentTarget.style.transform = 'translateY(-1px)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (customTitle.trim()) {
                        e.currentTarget.style.backgroundColor = '#1976d2';
                        e.currentTarget.style.transform = 'translateY(0)';
                      }
                    }}
                  >
                    Use Title
                  </button>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'flex-end', 
              gap: '12px', 
              marginTop: '24px',
              paddingTop: '16px',
              borderTop: '1px solid #e0e0e0'
            }}>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#f5f5f5',
                  color: '#666',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default EnhancedTitleSelector;
