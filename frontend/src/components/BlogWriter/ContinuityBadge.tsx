import React, { useEffect, useState } from 'react';
import { blogWriterApi } from '../../services/blogWriterApi';

interface Props { 
  sectionId: string; 
  refreshToken?: number;
  disabled?: boolean;
  flowAnalysisResults?: any;
}

export const ContinuityBadge: React.FC<Props> = ({ sectionId, refreshToken, disabled = false, flowAnalysisResults }) => {
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);
  const [hover, setHover] = useState(false);

  useEffect(() => {
    let mounted = true;
    
    // If we have flow analysis results, use them instead of API call
    if (flowAnalysisResults && flowAnalysisResults.sections) {
      console.log('🔍 [ContinuityBadge] Flow analysis results available:', flowAnalysisResults);
      console.log('🔍 [ContinuityBadge] Looking for section ID:', sectionId);
      console.log('🔍 [ContinuityBadge] Available section IDs:', flowAnalysisResults.sections.map((s: any) => s.section_id));
      
      const sectionAnalysis = flowAnalysisResults.sections.find((s: any) => s.section_id === sectionId);
      if (sectionAnalysis) {
        console.log('🔍 [ContinuityBadge] Found section analysis:', sectionAnalysis);
        if (mounted) {
          setMetrics({
            flow: sectionAnalysis.flow_score, // Already in decimal format (0.0-1.0)
            consistency: sectionAnalysis.consistency_score,
            progression: sectionAnalysis.progression_score
          });
        }
        return;
      } else {
        console.log('🔍 [ContinuityBadge] No matching section found for ID:', sectionId);
      }
    }
    
    // Fallback to API call if no flow analysis results
    console.log('🔍 [ContinuityBadge] Fetching continuity for section:', sectionId);
    blogWriterApi.getContinuity(sectionId)
      .then(res => { 
        console.log('🔍 [ContinuityBadge] Received continuity data:', res);
        if (mounted) setMetrics(res.continuity_metrics || null); 
      })
      .catch((error) => { 
        console.log('🔍 [ContinuityBadge] Error fetching continuity:', error);
        /* ignore */ 
      });
    return () => { mounted = false; };
  }, [sectionId, refreshToken, flowAnalysisResults]);

  // Show badge even if metrics are null (for debugging)
  const flow = metrics ? Math.round(((metrics.flow || 0) * 100)) : 0;
  const consistency = metrics ? Math.round(((metrics.consistency || 0) * 100)) : 0;
  const progression = metrics ? Math.round(((metrics.progression || 0) * 100)) : 0;
  
  // Enable badge if we have flow analysis results or metrics
  const isEnabled = !disabled || (flowAnalysisResults && flowAnalysisResults.sections) || metrics;
  
  // Enhanced color coding with actionable feedback
  const getFlowColor = (score: number) => {
    if (score >= 80) return '#2e7d32'; // Green - Excellent
    if (score >= 60) return '#f9a825'; // Yellow - Good
    return '#c62828'; // Red - Needs improvement
  };
  
  const getFlowSuggestion = (score: number) => {
    if (score >= 80) return "🎉 Excellent narrative flow!";
    if (score >= 60) return "💡 Good flow - try connecting ideas more smoothly";
    return "🔧 Consider adding transitions between paragraphs";
  };
  
  const getConsistencySuggestion = (score: number) => {
    if (score >= 80) return "✨ Consistent tone and style";
    if (score >= 60) return "📝 Good consistency - maintain your voice";
    return "🎯 Work on maintaining consistent tone throughout";
  };
  
  const getProgressionSuggestion = (score: number) => {
    if (score >= 80) return "🚀 Great logical progression!";
    if (score >= 60) return "📈 Good progression - build on previous points";
    return "🔗 Strengthen connections between ideas";
  };
  
  const color = getFlowColor(flow);

  return (
    <span
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <span
        title={!isEnabled ? 'Flow analysis disabled - use Copilot to enable' : (metrics ? `Flow ${flow}%` : 'Flow metrics not available')}
        style={{
          display: 'inline-block',
          fontSize: 12,
          color: !isEnabled ? '#999' : (metrics ? color : '#666'),
          border: `1px solid ${!isEnabled ? '#ddd' : (metrics ? color : '#ccc')}`,
          padding: '2px 6px',
          borderRadius: 10,
          background: !isEnabled ? '#f5f5f5' : 'transparent',
          cursor: !isEnabled ? 'not-allowed' : 'default',
          opacity: !isEnabled ? 0.6 : 1
        }}
      >
        {!isEnabled ? 'Flow --' : (metrics ? `Flow ${flow}%` : 'Flow --')}
      </span>

      {hover && isEnabled && (
        <div
          style={{
            position: 'absolute',
            top: '150%',
            left: 0,
            zIndex: 10,
            background: '#fff',
            color: '#333',
            border: '1px solid #e0e0e0',
            borderRadius: 12,
            padding: '12px 16px',
            minWidth: 280,
            maxWidth: 320,
            boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
            backdropFilter: 'blur(8px)'
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 12, color: '#1a1a1a' }}>
            📊 Content Quality Analysis
          </div>
          
          {/* Flow Analysis */}
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 12, display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontWeight: 600 }}>Flow</span>
              <span style={{ color: getFlowColor(flow), fontWeight: 600 }}>{flow}%</span>
            </div>
            <div style={{ fontSize: 11, color: '#666', lineHeight: '1.4' }}>
              {getFlowSuggestion(flow)}
            </div>
          </div>
          
          {/* Consistency Analysis */}
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 12, display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontWeight: 600 }}>Consistency</span>
              <span style={{ color: getFlowColor(consistency), fontWeight: 600 }}>{consistency}%</span>
            </div>
            <div style={{ fontSize: 11, color: '#666', lineHeight: '1.4' }}>
              {getConsistencySuggestion(consistency)}
            </div>
          </div>
          
          {/* Progression Analysis */}
          <div style={{ marginBottom: 8 }}>
            <div style={{ fontSize: 12, display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontWeight: 600 }}>Progression</span>
              <span style={{ color: getFlowColor(progression), fontWeight: 600 }}>{progression}%</span>
            </div>
            <div style={{ fontSize: 11, color: '#666', lineHeight: '1.4' }}>
              {getProgressionSuggestion(progression)}
            </div>
          </div>
          
          {/* Overall Quality Indicator */}
          <div style={{ 
            borderTop: '1px solid #f0f0f0', 
            paddingTop: 8, 
            marginTop: 8,
            fontSize: 11,
            color: '#888',
            fontStyle: 'italic'
          }}>
            💡 Hover over other sections to compare quality metrics
          </div>
        </div>
      )}
    </span>
  );
};

export default ContinuityBadge;


