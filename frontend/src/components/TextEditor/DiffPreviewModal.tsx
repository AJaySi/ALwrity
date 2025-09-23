import React from 'react';
import { diffMarkup } from '../LinkedInWriter/utils/contentFormatters';

interface DiffPreviewModalProps {
  isPreviewing: boolean;
  pendingEdit: { src: string; target: string } | null;
  livePreviewHtml: string;
  onConfirmChanges: () => void;
  onDiscardChanges: () => void;
}

const DiffPreviewModal: React.FC<DiffPreviewModalProps> = ({
  isPreviewing,
  pendingEdit,
  livePreviewHtml,
  onConfirmChanges,
  onDiscardChanges
}) => {
  if (!isPreviewing || !pendingEdit) return null;

  return (
    <div style={{
      margin: '24px',
      border: '1px solid #e0e0e0',
      borderRadius: 8,
      background: '#fff',
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
    }}>
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid #eee',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <strong style={{ color: '#0a66c2' }}>Preview Changes</strong>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={onConfirmChanges}
            style={{
              padding: '6px 12px',
              background: '#0a66c2',
              color: '#fff',
              border: '1px solid #0a66c2',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 14,
              fontWeight: 600
            }}
          >
            Confirm Changes
          </button>
          <button
            onClick={onDiscardChanges}
            style={{
              padding: '6px 12px',
              background: '#fff',
              color: '#444',
              border: '1px solid #ddd',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 14,
              fontWeight: 500
            }}
          >
            Discard
          </button>
        </div>
      </div>
      <div style={{ padding: 16 }}>
        <div
          style={{ fontFamily: 'inherit', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}
          dangerouslySetInnerHTML={{ __html: livePreviewHtml || diffMarkup(pendingEdit.src, pendingEdit.target) }}
        />
        <style>{`
          .liw-add { background: rgba(46, 204, 113, 0.18); font-style: normal; }
          .liw-del { color: #c0392b; text-decoration: line-through; opacity: 0.8; }
          .liw-more { color: #999; }
        `}</style>
      </div>
    </div>
  );
};

export default DiffPreviewModal;
