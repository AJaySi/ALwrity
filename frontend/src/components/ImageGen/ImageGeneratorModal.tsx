import React, { useMemo, useRef } from 'react';
import { Tooltip } from '@mui/material';
import ImageGenerator, { ImageGeneratorHandle } from './ImageGenerator';

interface ImageGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultPrompt?: string;
  context?: any;
  onImageGenerated?: (imageBase64: string, sectionId?: string) => void;
}

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0,0,0,0.5)',
  zIndex: 2000,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'stretch'
};

const modalStyle: React.CSSProperties = {
  background: '#fff',
  width: '100%',
  maxWidth: '1200px',
  margin: '24px',
  borderRadius: 12,
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column'
};

const headerStyle: React.CSSProperties = {
  padding: '16px 20px',
  borderBottom: '1px solid #e0e0e0',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  color: '#202124'
};

const bodyStyle: React.CSSProperties = {
  padding: 20,
  overflow: 'auto',
  flex: 1
};

const ImageGeneratorModal: React.FC<ImageGeneratorModalProps> = ({ isOpen, onClose, defaultPrompt, context, onImageGenerated }) => {
  const handleImageReady = (base64: string) => {
    if (onImageGenerated) {
      onImageGenerated(base64, context?.section?.id || context?.sectionId);
    }
  };

  const imageRef = useRef<ImageGeneratorHandle>(null);
  const sectionTitle = useMemo(() => context?.section?.heading || context?.title || 'Generate Blog Section Image', [context]);

  if (!isOpen) return null;
  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#202124' }}>{sectionTitle}</h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Tooltip title="Close the image generator modal. Any generated images are saved and will appear in your blog section." placement="bottom" arrow>
              <button 
                onClick={onClose} 
                style={{ 
                  border: 'none', 
                  background: 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)', 
                  color: '#5f6368',
                  borderRadius: 8, 
                  padding: '8px 20px', 
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 500,
                  transition: 'all 0.2s ease',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(135deg, #e8eaed 0%, #dadce0 100%)';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                }}
              >
                Close
              </button>
            </Tooltip>
          </div>
        </div>
        <div style={bodyStyle}>
          <ImageGenerator ref={imageRef} defaultPrompt={defaultPrompt || ''} context={context} onImageReady={handleImageReady} />
        </div>
      </div>
    </div>
  );
};

export default ImageGeneratorModal;


