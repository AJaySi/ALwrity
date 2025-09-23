import React from 'react';

interface OutlineProgressModalProps {
  isVisible: boolean;
  status: string;
  progressMessages: string[];
  latestMessage: string;
  error: string | null;
  titleOverride?: string;
}

export const OutlineProgressModal: React.FC<OutlineProgressModalProps> = ({
  isVisible,
  status,
  progressMessages,
  latestMessage,
  error,
  titleOverride
}) => {
  if (!isVisible) return null;

  const getUserFriendlyMessage = (message: string): string => {
    // Map technical backend messages to user-friendly ones
    if (message.includes('Starting outline generation')) {
      return '🧩 Starting to create your blog outline...';
    }
    if (message.includes('Analyzing research data and building content strategy')) {
      return '📊 Analyzing your research data to build the perfect content strategy...';
    }
    if (message.includes('Generating AI-powered outline with research insights')) {
      return '🤖 Creating an intelligent outline using AI and your research insights...';
    }
    if (message.includes('Making AI request to generate structured outline')) {
      return '🔄 Generating your structured blog outline...';
    }
    if (message.includes('Calling Gemini API for outline generation')) {
      return '🤖 AI is crafting your personalized blog structure...';
    }
    if (message.includes('Processing outline structure and validating sections')) {
      return '📝 Processing and validating your outline sections...';
    }
    if (message.includes('Running parallel processing for maximum speed')) {
      return '⚡ Optimizing processing speed for faster results...';
    }
    if (message.includes('Applying intelligent source-to-section mapping')) {
      return '🔗 Intelligently matching your research sources to outline sections...';
    }
    if (message.includes('Extracting grounding metadata insights')) {
      return '🧠 Extracting valuable insights from your research data...';
    }
    if (message.includes('Enhancing sections with grounding insights')) {
      return '✨ Enhancing your outline sections with research-backed insights...';
    }
    if (message.includes('Optimizing outline for better flow and engagement')) {
      return '🎯 Optimizing your outline for maximum reader engagement...';
    }
    if (message.includes('Rebalancing word count distribution')) {
      return '⚖️ Balancing content distribution across sections...';
    }
    if (message.includes('Outline generation and optimization completed successfully')) {
      return '✅ Your blog outline has been successfully created and optimized!';
    }
    if (message.includes('Outline generated successfully')) {
      return '🎉 Success! Your personalized blog outline is ready!';
    }
    
    // Return the original message if no mapping found
    return message;
  };

  const getProgressPercentage = (): number => {
    if (status === 'complete') return 100;
    if (status === 'error') return 0;
    
    // Estimate progress based on common message patterns
    const messageCount = progressMessages.length;
    if (messageCount === 0) return 0;
    if (messageCount >= 10) return 90;
    return Math.min(messageCount * 10, 90);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '0',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'hidden',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        border: '1px solid #e5e7eb'
      }}>
        {/* Header with background image */}
        <div style={{
          backgroundImage: 'url(/blog-writer-bg.png)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          padding: '32px',
          color: 'white',
          textAlign: 'center',
          position: 'relative'
        }}>
          {/* Dark overlay */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            borderRadius: '16px 16px 0 0'
          }} />
          
          <div style={{ position: 'relative', zIndex: 1 }}>
            <h2 style={{ 
              margin: '0 0 16px 0', 
              fontSize: '24px', 
              fontWeight: '700',
              textShadow: '2px 2px 4px rgba(0, 0, 0, 0.3)'
            }}>
              {titleOverride || (status === 'complete' ? '🎉 Outline Ready!' : status === 'error' ? '❌ Generation Failed' : '🧩 Creating Your Blog Outline')}
            </h2>
            
            {/* Progress Bar */}
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
              height: '8px',
              overflow: 'hidden',
              marginBottom: '16px'
            }}>
              <div style={{
                backgroundColor: status === 'error' ? '#ef4444' : '#10b981',
                height: '100%',
                width: `${getProgressPercentage()}%`,
                transition: 'width 0.3s ease',
                borderRadius: '12px'
              }} />
            </div>
            
            <p style={{ 
              margin: 0, 
              fontSize: '16px', 
              opacity: 0.9,
              textShadow: '1px 1px 2px rgba(0, 0, 0, 0.3)'
            }}>
              {titleOverride
                ? (status === 'complete' 
                    ? 'Your AI-generated blog content is ready!'
                    : status === 'error'
                      ? 'Something went wrong during generation'
                      : 'AI is generating your blog content...')
                : (status === 'complete' 
                    ? 'Your AI-powered blog outline is ready to use!'
                    : status === 'error' 
                      ? 'Something went wrong during outline generation'
                      : 'AI is analyzing your research and creating the perfect blog structure...')}
            </p>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '24px' }}>
          {error ? (
            <div style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              padding: '16px',
              color: '#dc2626'
            }}>
              <strong>Error:</strong> {error}
            </div>
          ) : (
            <>
              {/* Current Status */}
              <div style={{
                backgroundColor: '#f0f9ff',
                border: '1px solid #bae6fd',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <div style={{ 
                  fontSize: '14px', 
                  fontWeight: '600', 
                  color: '#0369a1', 
                  marginBottom: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ 
                    display: 'inline-block',
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: status === 'complete' ? '#10b981' : '#3b82f6',
                    animation: status === 'executing' ? 'pulse 2s infinite' : 'none'
                  }} />
                  Current Status
                </div>
                <div style={{ 
                  fontSize: '15px', 
                  color: '#1e40af',
                  lineHeight: '1.5'
                }}>
                  {latestMessage ? getUserFriendlyMessage(latestMessage) : 'Preparing to generate your outline...'}
                </div>
              </div>

              {/* Progress Messages */}
              {progressMessages.length > 0 && (
                <div>
                  <h4 style={{ 
                    margin: '0 0 12px 0', 
                    fontSize: '14px', 
                    fontWeight: '600', 
                    color: '#374151' 
                  }}>
                    Progress Timeline
                  </h4>
                  <div style={{
                    maxHeight: '200px',
                    overflowY: 'auto',
                    backgroundColor: '#f9fafb',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '12px'
                  }}>
                    {progressMessages.slice().reverse().slice(0, 8).map((message, index) => (
                      <div key={index} style={{
                        fontSize: '13px',
                        color: '#6b7280',
                        marginBottom: index < Math.min(progressMessages.length - 1, 7) ? '8px' : '0',
                        paddingLeft: '20px',
                        position: 'relative',
                        lineHeight: '1.4'
                      }}>
                        <span style={{
                          position: 'absolute',
                          left: '0',
                          top: '2px',
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: index === 0 ? '#10b981' : '#d1d5db'
                        }} />
                        {getUserFriendlyMessage(message)}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* CSS for pulse animation */}
        <style>
          {`
            @keyframes pulse {
              0%, 100% {
                opacity: 1;
                transform: scale(1);
              }
              50% {
                opacity: 0.7;
                transform: scale(1.1);
              }
            }
          `}
        </style>
      </div>
    </div>
  );
};
