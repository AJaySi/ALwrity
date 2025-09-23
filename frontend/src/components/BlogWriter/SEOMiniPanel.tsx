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
      <div>Score: {analysis.seo_score}</div>
      {!!analysis.recommendations?.length && (
        <ul>
          {analysis.recommendations.slice(0, 3).map((r, i) => (<li key={i}>{r}</li>))}
        </ul>
      )}
    </div>
  );
};

export default SEOMiniPanel;


