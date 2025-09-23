import React, { useState } from 'react';
import { BlogOutlineSection, SourceMappingStats, GroundingInsights, OptimizationResults, ResearchCoverage } from '../../services/blogWriterApi';
import EnhancedOutlineInsights from './EnhancedOutlineInsights';
import OutlineIntelligenceChips from './OutlineIntelligenceChips';

interface Props {
  outline: BlogOutlineSection[];
  onRefine: (operation: string, sectionId?: string, payload?: any) => void;
  research?: any; // Research data for context
  sourceMappingStats?: SourceMappingStats | null;
  groundingInsights?: GroundingInsights | null;
  optimizationResults?: OptimizationResults | null;
  researchCoverage?: ResearchCoverage | null;
}

const EnhancedOutlineEditor: React.FC<Props> = ({ 
  outline, 
  onRefine, 
  research, 
  sourceMappingStats, 
  groundingInsights, 
  optimizationResults, 
  researchCoverage 
}) => {
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [showAddSection, setShowAddSection] = useState(false);
  const [newSectionData, setNewSectionData] = useState({
    heading: '',
    subheadings: '',
    key_points: '',
    target_words: 300
  });

  const toggleExpanded = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const handleRename = (sectionId: string, newHeading: string) => {
    if (newHeading.trim()) {
      onRefine('rename', sectionId, { heading: newHeading.trim() });
    }
    setEditingSection(null);
  };

  const handleMove = (sectionId: string, direction: 'up' | 'down') => {
    onRefine('move', sectionId, { direction });
  };

  const handleAddSection = () => {
    if (newSectionData.heading.trim()) {
      const subheadings = newSectionData.subheadings
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      const keyPoints = newSectionData.key_points
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      onRefine('add', undefined, {
        heading: newSectionData.heading.trim(),
        subheadings,
        key_points: keyPoints,
        target_words: newSectionData.target_words
      });

      setNewSectionData({
        heading: '',
        subheadings: '',
        key_points: '',
        target_words: 300
      });
      setShowAddSection(false);
    }
  };

  const getTotalWords = () => {
    return outline.reduce((total, section) => total + (section.target_words || 0), 0);
  };


  return (
    <div style={{ 
      backgroundColor: 'white', 
      borderRadius: '12px', 
      border: '1px solid #e0e0e0',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{ 
        padding: '20px', 
        backgroundColor: '#f8f9fa',
        borderBottom: '1px solid #e0e0e0'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div>
              <h2 style={{ margin: 0, color: '#333', fontSize: '20px' }}>
                📋 Blog Outline
              </h2>
              <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
                {outline.length} sections • {getTotalWords()} words total
              </p>
            </div>
            {/* Intelligence Chips inline with title */}
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <OutlineIntelligenceChips
                sections={outline}
                sourceMappingStats={sourceMappingStats}
                groundingInsights={groundingInsights}
                optimizationResults={optimizationResults}
                researchCoverage={researchCoverage}
              />
            </div>
          </div>
          <button
            onClick={() => setShowAddSection(!showAddSection)}
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
            ➕ Add Section
          </button>
        </div>
      </div>


      {/* Add Section Form */}
      {showAddSection && (
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#f0f8ff',
          borderBottom: '1px solid #e0e0e0'
        }}>
          <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>Add New Section</h3>
          <div style={{ display: 'grid', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
                Section Title
              </label>
              <input
                type="text"
                value={newSectionData.heading}
                onChange={(e) => setNewSectionData({...newSectionData, heading: e.target.value})}
                placeholder="Enter section title..."
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
                  Subheadings (one per line)
                </label>
                <textarea
                  value={newSectionData.subheadings}
                  onChange={(e) => setNewSectionData({...newSectionData, subheadings: e.target.value})}
                  placeholder="Subheading 1&#10;Subheading 2&#10;Subheading 3"
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
                  Key Points (one per line)
                </label>
                <textarea
                  value={newSectionData.key_points}
                  onChange={(e) => setNewSectionData({...newSectionData, key_points: e.target.value})}
                  placeholder="Key point 1&#10;Key point 2&#10;Key point 3"
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
              </div>
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '4px', fontSize: '14px', fontWeight: '500' }}>
                Target Words
              </label>
              <input
                type="number"
                value={newSectionData.target_words}
                onChange={(e) => setNewSectionData({...newSectionData, target_words: parseInt(e.target.value) || 300})}
                min="100"
                max="2000"
                style={{
                  width: '120px',
                  padding: '8px 12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={handleAddSection}
                style={{
                  backgroundColor: '#1976d2',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Add Section
              </button>
              <button
                onClick={() => setShowAddSection(false)}
                style={{
                  backgroundColor: '#f5f5f5',
                  color: '#666',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Outline Sections */}
      <div style={{ padding: '0' }}>
        {outline.map((section, index) => (
          <div key={section.id} style={{
            borderBottom: index < outline.length - 1 ? '1px solid #f0f0f0' : 'none',
            transition: 'all 0.2s ease'
          }}>
            {/* Section Header */}
            <div style={{
              padding: '16px 20px',
              backgroundColor: expandedSections.has(section.id) ? '#f8f9fa' : 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
            onClick={() => toggleExpanded(section.id)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  backgroundColor: '#1976d2',
                  color: 'white',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {index + 1}
                </div>
                
                {editingSection === section.id ? (
                  <input
                    type="text"
                    defaultValue={section.heading}
                    onBlur={(e) => handleRename(section.id, e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleRename(section.id, e.currentTarget.value);
                      }
                    }}
                    autoFocus
                    style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      border: '1px solid #1976d2',
                      borderRadius: '4px',
                      padding: '4px 8px',
                      backgroundColor: 'white'
                    }}
                  />
                ) : (
                  <h3 style={{ 
                    margin: 0, 
                    fontSize: '16px', 
                    fontWeight: '600', 
                    color: '#333',
                    flex: 1
                  }}>
                    {section.heading}
                  </h3>
                )}
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    backgroundColor: '#e3f2fd',
                    color: '#1976d2',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '500'
                  }}>
                    {section.target_words || 300} words
                  </span>
                  
                  {section.references && section.references.length > 0 && (
                    <span style={{
                      backgroundColor: '#e8f5e8',
                      color: '#388e3c',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: '500'
                    }}>
                      {section.references.length} sources
                    </span>
                  )}
                </div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingSection(section.id);
                  }}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    color: '#666'
                  }}
                >
                  ✏️
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMove(section.id, 'up');
                  }}
                  disabled={index === 0}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    cursor: index === 0 ? 'not-allowed' : 'pointer',
                    fontSize: '12px',
                    color: index === 0 ? '#ccc' : '#666',
                    opacity: index === 0 ? 0.5 : 1
                  }}
                >
                  ⬆️
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMove(section.id, 'down');
                  }}
                  disabled={index === outline.length - 1}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    cursor: index === outline.length - 1 ? 'not-allowed' : 'pointer',
                    fontSize: '12px',
                    color: index === outline.length - 1 ? '#ccc' : '#666',
                    opacity: index === outline.length - 1 ? 0.5 : 1
                  }}
                >
                  ⬇️
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm(`Are you sure you want to remove "${section.heading}"?`)) {
                      onRefine('remove', section.id);
                    }
                  }}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #f44336',
                    borderRadius: '4px',
                    padding: '4px 8px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    color: '#f44336'
                  }}
                >
                  🗑️
                </button>
                
                <div style={{
                  transform: expandedSections.has(section.id) ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s ease',
                  fontSize: '14px',
                  color: '#666'
                }}>
                  ▼
                </div>
              </div>
            </div>

            {/* Expanded Section Content */}
            {expandedSections.has(section.id) && (
              <div style={{ padding: '0 20px 20px 52px', backgroundColor: '#fafafa' }}>
                {/* Subheadings */}
                {section.subheadings && section.subheadings.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>
                      📝 Subheadings
                    </h4>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      {section.subheadings.map((subheading, i) => (
                        <li key={i} style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>
                          {subheading}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Key Points */}
                {section.key_points && section.key_points.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>
                      🎯 Key Points
                    </h4>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      {section.key_points.map((point, i) => (
                        <li key={i} style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Keywords */}
                {section.keywords && section.keywords.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>
                      🎯 SEO Keywords
                    </h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {section.keywords.map((keyword, i) => (
                        <span key={i} style={{
                          backgroundColor: '#e3f2fd',
                          color: '#1976d2',
                          padding: '4px 8px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }}>
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* References */}
                {section.references && section.references.length > 0 && (
                  <div>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#333' }}>
                      📚 Sources ({section.references.length})
                    </h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {section.references.map((ref, i) => (
                        <div key={i} style={{
                          backgroundColor: 'white',
                          border: '1px solid #e0e0e0',
                          borderRadius: '6px',
                          padding: '8px 12px',
                          fontSize: '12px',
                          color: '#666',
                          maxWidth: '200px'
                        }}>
                          <div style={{ fontWeight: '500', marginBottom: '2px' }}>
                            {ref.title}
                          </div>
                          <div style={{ color: '#999' }}>
                            Credibility: {Math.round((ref.credibility_score || 0.8) * 100)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div style={{ 
        padding: '16px 20px', 
        backgroundColor: '#f8f9fa',
        borderTop: '1px solid #e0e0e0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ fontSize: '14px', color: '#666' }}>
          💡 Tip: Click on any section to expand and see details. Use the controls to reorder, edit, or remove sections.
        </div>
        <div style={{ fontSize: '14px', color: '#666' }}>
          Total: {getTotalWords()} words
        </div>
      </div>
    </div>
  );
};

export default EnhancedOutlineEditor;
