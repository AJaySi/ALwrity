import React from 'react';
import { WASuggestion } from '../../services/writingAssistantService';

interface WritingAssistantCardProps {
  assistantOn: boolean;
  waSuggestion: WASuggestion | null;
  waError?: string | null;
  showContinuePrompt?: boolean;
  draft: string;
  onDraftChange: (value: string) => void;
  onDismissSuggestion: () => void;
  anchor?: { top: number; left: number } | null;
  caretIndex?: number;
  onInsertAtCaret?: (text: string, caretIndex: number) => void;
  onContinueWriting?: () => void;
}

const WritingAssistantCard: React.FC<WritingAssistantCardProps> = ({
  assistantOn,
  waSuggestion,
  waError,
  showContinuePrompt,
  draft,
  onDraftChange,
  onDismissSuggestion,
  anchor,
  caretIndex,
  onInsertAtCaret,
  onContinueWriting
}) => {
  if (!assistantOn || (!waSuggestion && !waError && !showContinuePrompt)) return null;

  return (
    <div style={{
      position: anchor ? 'absolute' : 'sticky',
      top: anchor ? `${anchor.top}px` : 0,
      left: anchor ? `${anchor.left}px` : undefined,
      width: anchor ? 'auto' : '100%',
      minWidth: anchor ? '320px' : 'auto',
      maxWidth: anchor ? '600px' : '100%',
      zIndex: 1000,
      background: '#fff',
      border: '1px solid #e0e0e0',
      borderRadius: 8,
      padding: 12,
      marginBottom: anchor ? 0 : 12,
      boxShadow: '0 6px 18px rgba(0,0,0,0.12)',
      wordWrap: 'break-word',
      overflowWrap: 'break-word'
    }}>
      {waError ? (
        // Error state
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <strong style={{ color: '#d32f2f' }}>⚠️ Assistive Writing Error</strong>
          </div>
          <div style={{ fontSize: 14, color: '#d32f2f', marginBottom: 8 }}>
            {waError}
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
            <button
              onClick={onDismissSuggestion}
              style={{ 
                padding: '8px 12px', 
                borderRadius: 6, 
                border: '1px solid #d32f2f', 
                background: '#d32f2f', 
                color: '#fff', 
                fontSize: 12,
                minWidth: '80px',
                whiteSpace: 'nowrap'
              }}
            >
              Dismiss
            </button>
          </div>
        </>
      ) : showContinuePrompt ? (
        // Continue CTA state
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <strong style={{ color: '#0a66c2' }}>Assistive Writing</strong>
          </div>
          <div style={{ fontSize: 14, color: '#333', marginBottom: 8 }}>
            ALwrity can contextually continue writing. Click Continue writing.
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
            <button
              onClick={() => onContinueWriting && onContinueWriting()}
              style={{ 
                padding: '8px 12px', 
                borderRadius: 6, 
                border: '1px solid #0a66c2', 
                background: '#0a66c2', 
                color: '#fff', 
                fontSize: 12,
                minWidth: '120px',
                whiteSpace: 'nowrap'
              }}
            >
              Continue writing
            </button>
            <button
              onClick={onDismissSuggestion}
              style={{ 
                padding: '8px 12px', 
                borderRadius: 6, 
                border: '1px solid #ddd', 
                background: '#fff', 
                color: '#555', 
                fontSize: 12,
                minWidth: '80px',
                whiteSpace: 'nowrap'
              }}
            >
              Dismiss
            </button>
          </div>
        </>
      ) : waSuggestion ? (
        // Suggestion state
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <strong style={{ color: '#0a66c2' }}>Assistive Writing Suggestion</strong>
            <span style={{ fontSize: 12, color: '#999' }}>Confidence: {Math.round((waSuggestion.confidence || 0) * 100)}%</span>
          </div>
          <div style={{ fontSize: 14, color: '#333', marginBottom: 8 }}>
            {waSuggestion.text}
          </div>
          {waSuggestion.sources?.length > 0 && (
            <div style={{ fontSize: 12, color: '#666', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {waSuggestion.sources.slice(0, 2).map((s, i) => (
                <a key={i} href={s.url} target="_blank" rel="noreferrer" style={{ color: '#0a66c2', textDecoration: 'none' }}>{s.title}</a>
              ))}
            </div>
          )}
          <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
            <button
              onClick={() => {
                if (!waSuggestion) return;
                
                // If we have caret position and insert function, insert at caret
                if (typeof caretIndex === 'number' && onInsertAtCaret) {
                  onInsertAtCaret(waSuggestion.text, caretIndex);
                } else {
                  // Fallback to appending at end
                  const newDraft = draft.endsWith(' ') ? draft + waSuggestion.text : draft + ' ' + waSuggestion.text;
                  onDraftChange(newDraft);
                }
                onDismissSuggestion();
              }}
              style={{ 
                padding: '8px 12px', 
                borderRadius: 6, 
                border: '1px solid #0a66c2', 
                background: '#0a66c2', 
                color: '#fff', 
                fontSize: 12,
                minWidth: '80px',
                whiteSpace: 'nowrap'
              }}
            >
              Accept
            </button>
            <button
              onClick={onDismissSuggestion}
              style={{ 
                padding: '8px 12px', 
                borderRadius: 6, 
                border: '1px solid #ddd', 
                background: '#fff', 
                color: '#555', 
                fontSize: 12,
                minWidth: '80px',
                whiteSpace: 'nowrap'
              }}
            >
              Dismiss
            </button>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default WritingAssistantCard;
