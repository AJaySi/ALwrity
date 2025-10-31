import React from 'react';

interface OutlineCtaBannerProps {
  onGenerate: () => void;
}

const OutlineCtaBanner: React.FC<OutlineCtaBannerProps> = ({ onGenerate }) => {
  return (
    <div style={{ padding: '12px 16px', background: '#fff8e1', borderBottom: '1px solid #ffe0b2', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ color: '#8d6e63' }}>Next step: generate your outline from research.</span>
      <button
        onClick={onGenerate}
        style={{ padding: '6px 10px', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}
      >
        Next: Create Outline
      </button>
    </div>
  );
};

export default OutlineCtaBanner;
