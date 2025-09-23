import React from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface ResearchGroundingProps {
  research: BlogResearchResponse;
}

export const ResearchGrounding: React.FC<ResearchGroundingProps> = ({ research }) => {
  const renderConfidenceScore = (score: number | undefined) => {
    const safeScore = score ?? 0.5;
    const percentage = Math.round(safeScore * 100);
    const color = safeScore >= 0.8 ? '#4CAF50' : safeScore >= 0.6 ? '#FF9800' : '#F44336';
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ 
          width: '50px', 
          height: '6px', 
          backgroundColor: '#e0e0e0', 
          borderRadius: '3px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${percentage}%`,
            height: '100%',
            backgroundColor: color,
            transition: 'width 0.3s ease'
          }} />
        </div>
        <span style={{ fontSize: '11px', color: '#666' }}>{percentage}%</span>
      </div>
    );
  };

  if (!research.grounding_metadata) {
    return (
      <div style={{ padding: '16px', textAlign: 'center', color: '#666' }}>
        No grounding metadata available
      </div>
    );
  }

  const { grounding_chunks, grounding_supports, citations, web_search_queries } = research.grounding_metadata;

  return (
    <div style={{ padding: '16px' }}>
      <h3 style={{ margin: '0 0 16px 0', color: '#333' }}>🔗 Google Grounding Metadata</h3>
      
      {/* Grounding Chunks */}
      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#555', fontSize: '16px' }}>
          📚 Grounding Chunks ({grounding_chunks.length})
        </h4>
      <div style={{ display: 'grid', gap: '8px' }}>
          {grounding_chunks.map((chunk, index) => (
          <div key={index} style={{
            border: '1px solid #e0e0e0',
            borderRadius: '6px',
            padding: '12px',
              backgroundColor: '#fafafa'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <h5 style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: '#333' }}>
                  {chunk.title}
                </h5>
                {chunk.confidence_score && renderConfidenceScore(chunk.confidence_score)}
              </div>
              <a 
                href={chunk.url} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ 
                  fontSize: '12px', 
                  color: '#1976d2', 
                  textDecoration: 'none',
                  wordBreak: 'break-all'
                }}
              >
                {chunk.url}
              </a>
          </div>
        ))}
      </div>
    </div>

      {/* Grounding Supports */}
      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#555', fontSize: '16px' }}>
          🎯 Grounding Supports ({grounding_supports.length})
        </h4>
        <div style={{ display: 'grid', gap: '8px' }}>
          {grounding_supports.map((support, index) => (
            <div key={index} style={{
              border: '1px solid #e0e0e0',
            borderRadius: '6px',
              padding: '12px',
              backgroundColor: '#fafafa'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', color: '#666' }}>
                  Chunks: {support.grounding_chunk_indices.join(', ')}
                </span>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {support.confidence_scores.map((score, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span style={{ fontSize: '10px', color: '#666' }}>C{i+1}:</span>
                      {renderConfidenceScore(score)}
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ 
                fontSize: '13px', 
                color: '#555', 
                fontStyle: 'italic',
                backgroundColor: '#f0f0f0',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #e0e0e0'
              }}>
                "{support.segment_text}"
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Citations */}
      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#555', fontSize: '16px' }}>
          📝 Inline Citations ({citations.length})
        </h4>
        <div style={{ display: 'grid', gap: '8px' }}>
          {citations.map((citation, index) => (
            <div key={index} style={{
              border: '1px solid #e0e0e0',
              borderRadius: '6px',
              padding: '12px',
              backgroundColor: '#fafafa'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ 
                    backgroundColor: '#e8f5e8', 
                    color: '#2e7d32', 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontSize: '10px', 
                    fontWeight: '600' 
                  }}>
                    {citation.citation_type}
                  </span>
                  <span style={{ fontSize: '12px', color: '#666' }}>
                    {citation.reference}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '4px' }}>
                  {citation.source_indices.map((sourceIdx, i) => (
                    <span key={i} style={{
                      backgroundColor: '#e3f2fd',
                      color: '#1976d2',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '10px',
                      fontWeight: '600'
                    }}>
                      S{sourceIdx + 1}
                    </span>
                  ))}
                </div>
              </div>
        <div style={{
                fontSize: '13px', 
                color: '#555', 
                backgroundColor: '#f0f0f0',
                padding: '8px',
                borderRadius: '4px',
          border: '1px solid #e0e0e0',
                fontStyle: 'italic'
              }}>
                "{citation.text}"
              </div>
              <div style={{ 
                fontSize: '10px', 
                color: '#999', 
                marginTop: '4px',
                fontFamily: 'monospace'
              }}>
                Position: {citation.start_index}-{citation.end_index}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default ResearchGrounding;
