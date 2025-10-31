import React from 'react';
import { BlogSEOAnalyzeResponse } from '../../services/blogWriterApi';

interface Props {
  analysis?: BlogSEOAnalyzeResponse | null;
}

const SEOMiniPanel: React.FC<Props> = ({ analysis }) => {
  if (!analysis) return null;
  return (
    <div style={{ border: '1px solid #eee', padding: 8, marginTop: 8 }}>
      <div style={{ fontWeight: 600 }}>SEO Mini Panel</div>
      <div>Score: {analysis.overall_score}</div>
      {!!analysis.analysis_summary && (
        <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>
          Grade {analysis.analysis_summary.overall_grade} · {analysis.analysis_summary.status}
        </div>
      )}
      {!!analysis.actionable_recommendations?.length && (
        <ul>
          {analysis.actionable_recommendations.slice(0, 3).map((rec, index) => (
            <li key={index}>
              <strong>{rec.category}:</strong> {rec.recommendation}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SEOMiniPanel;


