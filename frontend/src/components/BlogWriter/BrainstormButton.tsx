import React, { useState, useEffect, useRef } from 'react';
import { useGSCBrainstorm } from '../../hooks/useGSCBrainstorm';
import { GSCBrainstormModal } from './GSCBrainstormModal';

interface BrainstormButtonProps {
  keywords: string;
  onKeywordsChange: (val: string) => void;
  onBrainstormResult?: (result: import('../../api/gscBrainstorm').BrainstormResult) => void;
  disabled?: boolean;
}

export const BrainstormButton: React.FC<BrainstormButtonProps> = ({
  keywords,
  onKeywordsChange,
  onBrainstormResult,
  disabled = false,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [showConnectOverlay, setShowConnectOverlay] = useState(false);
  const pendingBrainstormRef = useRef(false);
  const {
    gscConnected,
    isConnecting,
    connectError,
    isBrainstorming,
    brainstormError,
    contentOpportunities,
    keywordGaps,
    quickWins,
    pageOpportunities,
    aiRecommendations,
    summary,
    progressMessage,
    connectGSC,
    brainstorm,
    reset,
  } = useGSCBrainstorm();

  const wordCount = keywords.trim().split(/\s+/).filter(Boolean).length;
  const isVisible = wordCount >= 3;

  useEffect(() => {
    if (gscConnected && pendingBrainstormRef.current && !isConnecting) {
      pendingBrainstormRef.current = false;
      brainstorm(keywords).then((result) => {
        if (result && onBrainstormResult) {
          onBrainstormResult(result);
        }
      });
    }
  }, [gscConnected, isConnecting]);

  const handleClick = async () => {
    if (!gscConnected) {
      setShowConnectOverlay(true);
      return;
    }

    setShowModal(true);
    const result = await brainstorm(keywords);
    if (result && onBrainstormResult) {
      onBrainstormResult(result);
    }
  };

  const handleSelectSuggestion = (suggestion: string) => {
    onKeywordsChange(suggestion);
    setShowModal(false);
    reset();
  };

  const handleConnectGSC = async () => {
    pendingBrainstormRef.current = true;
    await connectGSC();
  };

  const handleConnectSuccess = async () => {
    setShowConnectOverlay(false);
    setShowModal(true);
    const result = await brainstorm(keywords);
    if (result && onBrainstormResult) {
      onBrainstormResult(result);
    }
  };

  const handleConnectCancel = () => {
    setShowConnectOverlay(false);
    pendingBrainstormRef.current = false;
  };

  const handleReRun = async (newKeywords: string) => {
    if (newKeywords !== keywords) {
      onKeywordsChange(newKeywords);
    }
    const result = await brainstorm(newKeywords, undefined, true);
    if (result && onBrainstormResult) {
      onBrainstormResult(result);
    }
  };

  if (!isVisible) return null;

  return (
    <>
      <button
        onClick={handleClick}
        disabled={disabled || isBrainstorming}
        title={
          wordCount < 3
            ? 'Enter at least 3 words to enable brainstorming'
            : 'Brainstorm topics using your Google Search Console data'
        }
        style={{
          padding: '12px 20px',
          backgroundColor: disabled || isBrainstorming ? '#999' : '#4caf50',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          fontSize: '14px',
          fontWeight: 500,
          cursor: disabled || isBrainstorming ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.7 : 1,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          whiteSpace: 'nowrap',
          transition: 'background-color 0.15s',
        }}
      >
        {isBrainstorming ? (
          <>
            <span
              style={{
                display: 'inline-block',
                width: '14px',
                height: '14px',
                border: '2px solid #fff',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'brainstormSpin 0.8s linear infinite',
              }}
            />
            <style>{`@keyframes brainstormSpin { to { transform: rotate(360deg); } }`}</style>
            Analyzing...
          </>
        ) : (
          'Brainstorm Topics'
        )}
      </button>

      {gscConnected && (
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            padding: '4px 10px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 500,
            color: '#2e7d32',
            background: '#e8f5e9',
            border: '1px solid #a5d6a7',
            whiteSpace: 'nowrap',
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#4caf50',
              boxShadow: '0 0 6px #4caf50',
            }}
          />
          GSC
        </span>
      )}

      <GSCBrainstormModal
        open={showModal}
        onClose={() => {
          setShowModal(false);
          reset();
        }}
        contentOpportunities={contentOpportunities}
        keywordGaps={keywordGaps}
        quickWins={quickWins}
        pageOpportunities={pageOpportunities}
        aiRecommendations={aiRecommendations}
        summary={summary}
        error={brainstormError}
        isBrainstorming={isBrainstorming}
        progressMessage={progressMessage}
        onSelectSuggestion={handleSelectSuggestion}
        initialKeywords={keywords}
        onReRun={handleReRun}
      />

      {showConnectOverlay && (
        <GSConnectOverlay
          isConnecting={isConnecting}
          connectError={connectError}
          gscConnected={gscConnected}
          onConnect={handleConnectGSC}
          onSuccess={handleConnectSuccess}
          onCancel={handleConnectCancel}
        />
      )}
    </>
  );
};

const GSConnectOverlay: React.FC<{
  isConnecting: boolean;
  connectError: string | null;
  gscConnected: boolean;
  onConnect: () => void;
  onSuccess: () => void;
  onCancel: () => void;
}> = ({ isConnecting, connectError, gscConnected, onConnect, onSuccess, onCancel }) => {
  if (gscConnected && !isConnecting) {
    onSuccess();
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 10000,
      }}
    >
      <div
        style={{
          backgroundColor: '#fff',
          borderRadius: '12px',
          padding: '32px',
          maxWidth: '440px',
          textAlign: 'center',
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
        }}
      >
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
        <h3 style={{ margin: '0 0 8px', fontSize: '18px', color: '#333' }}>
          Connect Google Search Console
        </h3>
        <p style={{ margin: '0 0 20px', fontSize: '14px', color: '#666', lineHeight: 1.5 }}>
          Brainstorm Topics uses your Google Search Console data to suggest blog topics
          based on what your audience is actually searching for.
        </p>

        {connectError && (
          <p style={{ color: '#d32f2f', fontSize: '13px', margin: '0 0 16px' }}>{connectError}</p>
        )}

        {isConnecting ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <div
              style={{
                width: '20px',
                height: '20px',
                border: '2px solid #e0e0e0',
                borderTopColor: '#4caf50',
                borderRadius: '50%',
                animation: 'gscSpin 0.8s linear infinite',
              }}
            />
            <style>{`@keyframes gscSpin { to { transform: rotate(360deg); } }`}</style>
            <span style={{ fontSize: '14px', color: '#666' }}>Opening Google sign-in...</span>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              onClick={onConnect}
              style={{
                padding: '12px 24px',
                backgroundColor: '#4caf50',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Connect Google Search Console
            </button>
            <button
              onClick={onCancel}
              style={{
                padding: '8px 24px',
                backgroundColor: 'transparent',
                color: '#888',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '13px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <p style={{ fontSize: '12px', color: '#999', margin: '4px 0 0' }}>
              You'll be redirected to Google to authorize access. Your data stays private.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BrainstormButton;