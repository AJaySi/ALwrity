import React from 'react';

interface QuickEditToolbarProps {
  draft: string;
  isPreviewing: boolean;
}

const QuickEditToolbar: React.FC<QuickEditToolbarProps> = ({ draft, isPreviewing }) => {
  if (!draft || isPreviewing) return null;

  return (
    <div style={{
      display: 'flex',
      gap: 8,
      padding: '10px 16px',
      borderBottom: '1px solid #eee',
      background: '#fafafa'
    }}>
      <span style={{ fontSize: 12, color: '#666', alignSelf: 'center' }}>
        Quick edits (preview):
      </span>
      <button
        onClick={() => {
          const lines = draft.split('\n');
          if (lines.length > 0) {
            const first = lines[0].trim();
            lines[0] = first.replace(/^(.*?)([\.!?])?$/, '👉 $1$2');
          }
          const target = lines.join('\n');
          window.dispatchEvent(new CustomEvent('linkedinwriter:applyEdit', { detail: { target } }));
        }}
        style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, background: '#fff', cursor: 'pointer' }}
      >
        Tighten Hook
      </button>
      <button
        onClick={() => {
          const target = draft + '\n\nWhat are your thoughts on this? Share your experience in the comments below!';
          window.dispatchEvent(new CustomEvent('linkedinwriter:applyEdit', { detail: { target } }));
        }}
        style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, background: '#fff', cursor: 'pointer' }}
      >
        Add CTA
      </button>
      <button
        onClick={() => {
          const target = draft.length > 200 ? draft.substring(0, 200) + '...' : draft;
          window.dispatchEvent(new CustomEvent('linkedinwriter:applyEdit', { detail: { target } }));
        }}
        style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, background: '#fff', cursor: 'pointer' }}
      >
        Shorten
      </button>
      <button
        onClick={() => {
          const target = draft + '\n\nThis approach has shown strong results. The key is to maintain consistency while adapting to changing conditions.';
          window.dispatchEvent(new CustomEvent('linkedinwriter:applyEdit', { detail: { target } }));
        }}
        style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, background: '#fff', cursor: 'pointer' }}
      >
        Lengthen
      </button>
      <button
        onClick={() => {
          const target = `[Professionalized]` + '\n\n' + draft;
          window.dispatchEvent(new CustomEvent('linkedinwriter:applyEdit', { detail: { target } }));
        }}
        style={{ padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, background: '#fff', cursor: 'pointer' }}
      >
        Professionalize
      </button>
    </div>
  );
};

export default QuickEditToolbar;
