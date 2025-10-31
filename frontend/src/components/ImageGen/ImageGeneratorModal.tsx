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
            <h3 style={{ margin: 0 }}>{sectionTitle}</h3>
            <span style={{ fontSize: 12, color: '#5f6368' }}>Generate Blog Section Image</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Tooltip title="Toggle advanced image generation settings. Opens provider selection (Hugging Face, Gemini, Stability AI), model specification, and image dimensions (width/height). Hover or click to show/hide these options." placement="bottom" arrow>
              <button
                onMouseEnter={() => imageRef.current?.openAdvanced()}
                onClick={() => {
                  // toggle
                  if (imageRef.current) {
                    imageRef.current.openAdvanced();
                  }
                }}
                style={{ border: '1px solid #cbd5e1', background: '#ffffff', color: '#334155', borderRadius: 20, padding: '6px 12px', cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.04)' }}
              >
                Advanced Image Options
              </button>
            </Tooltip>
            <Tooltip title="Get AI-powered prompt suggestions tailored to your blog section. Uses section title, subheadings, key points, keywords, and research data to generate multiple hyper-personalized prompts. Suggestions appear as tabs below." placement="bottom" arrow>
              <button
                onClick={() => imageRef.current?.suggest()}
                style={{ border: '1px solid #1976d2', background: '#fff', color: '#1976d2', borderRadius: 20, padding: '6px 12px', cursor: 'pointer' }}
              >
                Suggest Prompt
              </button>
            </Tooltip>
            <Tooltip title="Close the image generator modal. Any generated images are saved and will appear in your blog section." placement="bottom" arrow>
              <button onClick={onClose} style={{ border: '1px solid #ddd', background: '#f5f5f5', borderRadius: 6, padding: '6px 10px', cursor: 'pointer' }}>Close</button>
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


