import React, { useEffect } from 'react';
import { WizardStepProps } from '../types/research.types';

const industries = [
  'General',
  'Technology',
  'Business',
  'Marketing',
  'Finance',
  'Healthcare',
  'Education',
  'Real Estate',
  'Entertainment',
  'Food & Beverage',
  'Travel',
  'Fashion',
  'Sports',
  'Science',
  'Law',
  'Other',
];

export const StepKeyword: React.FC<WizardStepProps> = ({ state, onUpdate }) => {
  const handleKeywordsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const keywords = value.split(',').map(k => k.trim()).filter(Boolean);
    onUpdate({ keywords });
  };

  const handleIndustryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onUpdate({ industry: e.target.value });
  };

  const handleAudienceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onUpdate({ targetAudience: e.target.value });
  };

  const keywordText = state.keywords.join(', ');

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '8px', color: '#333' }}>🔍 Research Setup</h2>
      <p style={{ marginBottom: '24px', color: '#666', fontSize: '15px' }}>
        Enter your keywords, industry, and target audience to start research.
      </p>

      {/* Keywords Input */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#555' }}>
          Keywords *
        </label>
        <textarea
          value={keywordText}
          onChange={handleKeywordsChange}
          placeholder="e.g., AI in marketing, automation tools, customer engagement"
          rows={4}
          style={{
            width: '100%',
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            fontSize: '14px',
            fontFamily: 'inherit',
            resize: 'vertical',
            boxSizing: 'border-box',
          }}
        />
        <p style={{ marginTop: '4px', fontSize: '12px', color: '#888' }}>
          Separate multiple keywords with commas
        </p>
      </div>

      {/* Industry Selection */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#555' }}>
          Industry
        </label>
        <select
          value={state.industry}
          onChange={handleIndustryChange}
          style={{
            width: '100%',
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            fontSize: '14px',
            fontFamily: 'inherit',
            backgroundColor: 'white',
            cursor: 'pointer',
          }}
        >
          {industries.map(ind => (
            <option key={ind} value={ind}>{ind}</option>
          ))}
        </select>
      </div>

      {/* Target Audience */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#555' }}>
          Target Audience
        </label>
        <input
          type="text"
          value={state.targetAudience}
          onChange={handleAudienceChange}
          placeholder="e.g., Digital marketers, Small business owners"
          style={{
            width: '100%',
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            fontSize: '14px',
            fontFamily: 'inherit',
            boxSizing: 'border-box',
          }}
        />
      </div>

      <div style={{
        padding: '12px',
        backgroundColor: '#f0f7ff',
        borderRadius: '8px',
        border: '1px solid #b3d9ff',
        fontSize: '13px',
        color: '#004085',
      }}>
        💡 <strong>Tip:</strong> Be specific with your keywords. The more precise your keywords, the better your research results.
      </div>
    </div>
  );
};

