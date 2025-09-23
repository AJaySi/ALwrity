import React from 'react';

interface Props {
  original: string;
  updated: string;
  onApply: () => void;
  onDiscard: () => void;
}

function highlightDiff(a: string, b: string) {
  // Simple common prefix/suffix highlighting
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i++;
  let j = 0;
  while (j < a.length - i && j < b.length - i && a[a.length - 1 - j] === b[b.length - 1 - j]) j++;
  const aMid = a.substring(i, a.length - j);
  const bMid = b.substring(i, b.length - j);
  const aHtml = `${escapeHtml(a.substring(0, i))}<span style="background:#ffe5e5;text-decoration:line-through;">${escapeHtml(aMid)}</span>${escapeHtml(a.substring(a.length - j))}`;
  const bHtml = `${escapeHtml(b.substring(0, i))}<span style="background:#e6ffed;">${escapeHtml(bMid)}</span>${escapeHtml(b.substring(b.length - j))}`;
  return { aHtml, bHtml };
}

function escapeHtml(s: string) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

const DiffPreview: React.FC<Props> = ({ original, updated, onApply, onDiscard }) => {
  const { aHtml, bHtml } = highlightDiff(original, updated);
  return (
    <div style={{ border: '1px solid #ddd', padding: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>Preview Changes</div>
      <div style={{ display: 'flex', gap: 8 }}>
        <div style={{ flex: 1, background: '#fafafa', padding: 8 }} dangerouslySetInnerHTML={{ __html: aHtml }} />
        <div style={{ flex: 1, background: '#f5fff5', padding: 8 }} dangerouslySetInnerHTML={{ __html: bHtml }} />
      </div>
      <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
        <button onClick={onApply}>Apply</button>
        <button onClick={onDiscard}>Discard</button>
      </div>
    </div>
  );
};

export default DiffPreview;


