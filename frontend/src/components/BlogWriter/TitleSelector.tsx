import React, { useState } from 'react';

interface TitleSelectorProps {
  titleOptions: string[];
  selectedTitle?: string;
  onTitleSelect: (title: string) => void;
  onCustomTitle?: (title: string) => void;
}

const TitleSelector: React.FC<TitleSelectorProps> = ({ 
  titleOptions, 
  selectedTitle, 
  onTitleSelect, 
  onCustomTitle 
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customTitle, setCustomTitle] = useState('');

  const handleCustomTitleSubmit = () => {
    if (customTitle.trim() && onCustomTitle) {
      onCustomTitle(customTitle.trim());
      setCustomTitle('');
      setShowCustomInput(false);
    }
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      border: '1px solid #e0e0e0',
      padding: '20px',
      marginBottom: '20px'
    }}>
      <h3 style={{ margin: '0 0 16px 0', color: '#333', fontSize: '18px' }}>
        📝 Choose Your Blog Title
      </h3>
      <p style={{ margin: '0 0 20px 0', color: '#666', fontSize: '14px' }}>
        Select from AI-generated options or create your own custom title.
      </p>

      {/* AI-Generated Title Options */}
      <div style={{ marginBottom: '20px' }}>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#333', fontWeight: '600' }}>
          AI-Generated Options
        </h4>
        <div style={{ display: 'grid', gap: '8px' }}>
          {titleOptions.map((title, index) => (
            <div
              key={index}
              onClick={() => onTitleSelect(title)}
              style={{
                padding: '12px 16px',
                border: selectedTitle === title ? '2px solid #1976d2' : '1px solid #e0e0e0',
                borderRadius: '8px',
                cursor: 'pointer',
                backgroundColor: selectedTitle === title ? '#f0f8ff' : 'white',
                transition: 'all 0.2s ease',
                fontSize: '14px',
                color: '#333'
              }}
              onMouseEnter={(e) => {
                if (selectedTitle !== title) {
                  e.currentTarget.style.backgroundColor = '#f8f9fa';
                  e.currentTarget.style.borderColor = '#1976d2';
                }
              }}
              onMouseLeave={(e) => {
                if (selectedTitle !== title) {
                  e.currentTarget.style.backgroundColor = 'white';
                  e.currentTarget.style.borderColor = '#e0e0e0';
                }
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {selectedTitle === title && (
                  <span style={{ color: '#1976d2', fontSize: '16px' }}>✓</span>
                )}
                <span style={{ fontWeight: selectedTitle === title ? '600' : '400' }}>
                  {title}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Custom Title Input */}
      <div>
        <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', color: '#333', fontWeight: '600' }}>
          Custom Title
        </h4>
        
        {!showCustomInput ? (
          <button
            onClick={() => setShowCustomInput(true)}
            style={{
              backgroundColor: 'transparent',
              border: '1px dashed #1976d2',
              borderRadius: '8px',
              padding: '12px 16px',
              cursor: 'pointer',
              fontSize: '14px',
              color: '#1976d2',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            ✏️ Create Custom Title
          </button>
        ) : (
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="Enter your custom title..."
              style={{
                flex: 1,
                padding: '12px 16px',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none'
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleCustomTitleSubmit();
                }
              }}
              autoFocus
            />
            <button
              onClick={handleCustomTitleSubmit}
              disabled={!customTitle.trim()}
              style={{
                backgroundColor: customTitle.trim() ? '#1976d2' : '#f5f5f5',
                color: customTitle.trim() ? 'white' : '#999',
                border: 'none',
                borderRadius: '8px',
                padding: '12px 16px',
                cursor: customTitle.trim() ? 'pointer' : 'not-allowed',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              Add
            </button>
            <button
              onClick={() => {
                setShowCustomInput(false);
                setCustomTitle('');
              }}
              style={{
                backgroundColor: 'transparent',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                padding: '12px 16px',
                cursor: 'pointer',
                fontSize: '14px',
                color: '#666'
              }}
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Title Tips */}
      <div style={{
        marginTop: '20px',
        padding: '12px 16px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        border: '1px solid #e0e0e0'
      }}>
        <h5 style={{ margin: '0 0 8px 0', fontSize: '13px', color: '#333', fontWeight: '600' }}>
          💡 Title Tips
        </h5>
        <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: '#666' }}>
          <li>Keep it under 60 characters for better SEO</li>
          <li>Include your primary keyword naturally</li>
          <li>Make it compelling and click-worthy</li>
          <li>Consider your target audience</li>
        </ul>
      </div>
    </div>
  );
};

export default TitleSelector;
