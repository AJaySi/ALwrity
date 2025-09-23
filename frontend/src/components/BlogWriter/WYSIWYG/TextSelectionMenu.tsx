import React from 'react';
import { HallucinationDetectionResponse } from '../../../services/hallucinationDetectorService';
import FactCheckResults from '../../LinkedInWriter/components/FactCheckResults';

interface TextSelectionMenuProps {
  selectionMenu: { x: number; y: number; text: string } | null;
  factCheckResults: HallucinationDetectionResponse | null;
  isFactChecking: boolean;
  factCheckProgress: { step: string; progress: number } | null;
  smartSuggestion: {
    text: string;
    position: { x: number; y: number };
    confidence?: number;
    sources?: Array<{
      title: string;
      url: string;
      text?: string;
      author?: string;
      published_date?: string;
      score: number;
    }>;
  } | null;
  isGeneratingSuggestion: boolean;
  allSuggestions: Array<{
    text: string;
    confidence?: number;
    sources?: Array<{
      title: string;
      url: string;
      text?: string;
      author?: string;
      published_date?: string;
      score: number;
    }>;
  }>;
  suggestionIndex: number;
  onCheckFacts: (text: string) => void;
  onCloseFactCheckResults: () => void;
  onQuickEdit: (editType: string, selectedText: string) => void;
  onAcceptSuggestion: () => void;
  onRejectSuggestion: () => void;
  onNextSuggestion: () => void;
}

const TextSelectionMenu: React.FC<TextSelectionMenuProps> = ({
  selectionMenu,
  factCheckResults,
  isFactChecking,
  factCheckProgress,
  smartSuggestion,
  isGeneratingSuggestion,
  allSuggestions,
  suggestionIndex,
  onCheckFacts,
  onCloseFactCheckResults,
  onQuickEdit,
  onAcceptSuggestion,
  onRejectSuggestion,
  onNextSuggestion
}) => {
  return (
    <>
      {/* Text Selection Menu */}
      {selectionMenu && (
        <div
          onClick={(e) => {
            console.log('🔍 [TextSelectionMenu] Selection menu clicked!', e.target);
            e.stopPropagation();
          }}
          style={{
            position: 'fixed',
            top: selectionMenu.y - 60,
            left: Math.max(8, selectionMenu.x - 140),
            background: 'rgba(79, 70, 229, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.25)',
            borderRadius: '12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            padding: '12px 16px',
            boxShadow: '0 12px 28px rgba(0, 0, 0, 0.35)',
            backdropFilter: 'blur(12px)',
            zIndex: 10000,
            minWidth: '240px',
            maxWidth: '280px'
          }}
        >
          {/* Fact Check Button */}
          <button
            onClick={(e) => {
              console.log('🔍 [TextSelectionMenu] Check Facts button clicked!', selectionMenu.text);
              e.preventDefault();
              e.stopPropagation();
              onCheckFacts(selectionMenu.text);
            }}
            disabled={isFactChecking}
            style={{
              background: isFactChecking ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.2)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '8px',
              padding: '8px 16px',
              color: 'white',
              fontSize: '13px',
              fontWeight: '600',
              cursor: isFactChecking ? 'not-allowed' : 'pointer',
              opacity: isFactChecking ? 0.6 : 1,
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              width: '100%',
              justifyContent: 'center'
            }}
            onMouseEnter={(e) => {
              if (!isFactChecking) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isFactChecking) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
              }
            }}
          >
            {isFactChecking ? (
              <>
                <div style={{
                  width: '14px',
                  height: '14px',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }} />
                Fact-checking...
              </>
            ) : (
              <>
                🔍 Fact Check
              </>
            )}
          </button>

          {/* Quick Edit Options */}
          <div style={{
            borderTop: '1px solid rgba(255, 255, 255, 0.2)',
            paddingTop: '10px',
            marginTop: '6px'
          }}>
            <div style={{
              color: 'rgba(255, 255, 255, 0.9)',
              fontSize: '11px',
              fontWeight: '600',
              marginBottom: '8px',
              textAlign: 'center',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              ✨ Assistive Writing
            </div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '6px'
            }}>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onQuickEdit('improve', selectionMenu.text);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                ✏️ Improve
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onQuickEdit('add-transition', selectionMenu.text);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                🔗 Transition
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onQuickEdit('shorten', selectionMenu.text);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                ✂️ Shorten
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onQuickEdit('expand', selectionMenu.text);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                📝 Expand
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onQuickEdit('professionalize', selectionMenu.text);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                🎓 Professional
              </button>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  onQuickEdit('add-data', selectionMenu.text);
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 10px',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                📊 Add Data
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Fact Check Progress */}
      {factCheckProgress && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: 'rgba(79, 70, 229, 0.95)',
          color: 'white',
          padding: '12px 20px',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.25)',
          backdropFilter: 'blur(10px)',
          zIndex: 10001,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          minWidth: '280px'
        }}>
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            borderTop: '2px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: '600' }}>
              Fact-checking content...
            </div>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>
              {factCheckProgress.step}
            </div>
          </div>
        </div>
      )}

      {/* Fact Check Results */}
      {factCheckResults && (
        <FactCheckResults
          results={factCheckResults}
          onClose={onCloseFactCheckResults}
        />
      )}

      {/* Smart Typing Suggestion */}
      {smartSuggestion && (
        <div
          onClick={(e) => {
            console.log('🔍 [TextSelectionMenu] Smart suggestion modal clicked!', smartSuggestion);
            e.stopPropagation();
          }}
          style={{
            position: 'fixed',
            top: smartSuggestion.position.y,
            left: smartSuggestion.position.x,
            background: 'rgba(34, 197, 94, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.25)',
            borderRadius: '12px',
            padding: '16px 20px',
            boxShadow: '0 12px 28px rgba(0, 0, 0, 0.25)',
            backdropFilter: 'blur(12px)',
            zIndex: 10002,
            maxWidth: '400px',
            minWidth: '320px',
            color: 'white'
          }}
        >
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            marginBottom: '8px',
            opacity: 0.9,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>✨ Smart Writing Suggestion</span>
            {allSuggestions.length > 1 && (
              <span style={{ fontSize: '10px', opacity: 0.7 }}>
                {suggestionIndex + 1} of {allSuggestions.length}
              </span>
            )}
          </div>
          
          <div style={{
            fontSize: '14px',
            lineHeight: '1.4',
            marginBottom: '16px',
            fontStyle: 'italic'
          }}>
            "{smartSuggestion.text}"
          </div>
          
          <div style={{
            display: 'flex',
            gap: '8px',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              {allSuggestions.length > 1 && suggestionIndex < allSuggestions.length - 1 && (
                <button
                  onClick={onNextSuggestion}
                  style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                  }}
                >
                  ↻ Next
                </button>
              )}
            </div>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={onRejectSuggestion}
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  color: 'white',
                  fontSize: '12px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.25)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
                }}
              >
                ✕ Dismiss
              </button>
              <button
                onClick={onAcceptSuggestion}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  color: 'white',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                }}
              >
                ✓ Accept
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Smart Suggestion Loading Indicator */}
      {isGeneratingSuggestion && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          background: 'rgba(34, 197, 94, 0.95)',
          color: 'white',
          padding: '12px 20px',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.25)',
          backdropFilter: 'blur(10px)',
          zIndex: 10001,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          minWidth: '240px'
        }}>
          <div style={{
            width: '20px',
            height: '20px',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            borderTop: '2px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: '600' }}>
              Generating suggestion...
            </div>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>
              AI is crafting helpful content
            </div>
          </div>
        </div>
      )}

      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

export default TextSelectionMenu;
