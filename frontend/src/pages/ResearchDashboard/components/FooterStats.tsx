import React from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';

interface FooterStatsProps {
  results: BlogResearchResponse;
}

export const FooterStats: React.FC<FooterStatsProps> = ({ results }) => {
  return (
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
  );
};
