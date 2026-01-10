import React from 'react';
import { useNavigate } from 'react-router-dom';
import UserBadge from '../../../components/shared/UserBadge';

interface HeaderProps {
  onMyProjectsClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMyProjectsClick }) => {
  const navigate = useNavigate();

  const handleMyProjectsClick = () => {
    if (onMyProjectsClick) {
      onMyProjectsClick();
    } else {
      navigate('/asset-library?source_module=research_tools&asset_type=text');
    }
  };

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.7)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(14, 165, 233, 0.15)',
      padding: '16px 24px',
      marginBottom: '20px',
      position: 'relative',
      zIndex: 10,
      boxShadow: '0 1px 3px rgba(14, 165, 233, 0.1)',
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.25)',
          }}>
            🔬
          </div>
          <div style={{ flex: 1 }}>
            <h1 style={{
              margin: 0,
              fontSize: '24px',
              fontWeight: '700',
              color: '#0c4a6e',
              letterSpacing: '-0.01em',
            }}>
              AI-Powered Research Lab
            </h1>
            <p style={{
              margin: '2px 0 0 0',
              fontSize: '13px',
              color: '#0369a1',
              fontWeight: '400',
            }}>
              Enterprise-grade research intelligence at your fingertips
            </p>
          </div>
          <button
            onClick={handleMyProjectsClick}
            style={{
              padding: '10px 20px',
              backgroundColor: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 2px 8px rgba(102, 126, 234, 0.2)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#5568d3';
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#667eea';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.2)';
            }}
            title="View all saved research projects in Asset Library"
          >
            <span>📁</span>
            <span>My Projects</span>
          </button>
        </div>
        
        {/* User Badge - Using existing shared component */}
        <UserBadge colorMode="light" />
      </div>
    </div>
  );
};
