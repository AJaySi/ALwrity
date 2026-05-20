import React, { useState, useCallback, useEffect } from 'react';
import { linkApi, LinkSearchResult } from '../../services/linkApi';

interface LinkSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  sectionHeading?: string;
  sectionText?: string;
  selectedText?: string;
  context?: {
    title?: string;
    section?: any;
    outline?: any;
    research?: any;
    sectionId?: string;
  };
  onRewordAccept?: (rewordedText: string, sectionId?: string) => void;
}

const SEO_TIPS = {
  internal: {
    title: 'Internal Links',
    icon: '🏠',
    color: '#10b981',
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    description: 'Link to other pages on your own website. This helps search engines understand your site structure and distributes page authority (link equity) across your pages.',
    benefits: [
      'Distributes page authority across your site',
      'Helps search engines discover and index your pages',
      'Reduces bounce rate by guiding readers to related content',
      'Builds topical clusters that boost keyword rankings',
    ],
    bestPractice: 'Use descriptive anchor text that includes relevant keywords. Aim for 2-4 internal links per 1,000 words.',
  },
  external: {
    title: 'External Links',
    icon: '🌐',
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
    description: 'Link to authoritative external sources. Search engines use outbound links as a trust signal — citing credible sources improves your content\'s E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness).',
    benefits: [
      'Signals topical authority to search engines',
      'Improves E-E-A-T (Experience, Expertise, Authoritativeness, Trust)',
      'Builds relationships with other content creators',
      'Provides readers with deeper, verified information',
    ],
    bestPractice: 'Link to high-DA (Domain Authority) sources like research papers, official docs, and industry leaders. Use 1-2 external links per section.',
  },
};

const LinkSearchModal: React.FC<LinkSearchModalProps> = ({
  isOpen,
  onClose,
  sectionHeading,
  sectionText,
  selectedText,
  context,
  onRewordAccept,
}) => {
  const [linkType, setLinkType] = useState<'internal' | 'external'>('external');
  const [siteUrl, setSiteUrl] = useState(() => localStorage.getItem('linkSearch_siteUrl') || '');
  const [searchQuery, setSearchQuery] = useState(sectionHeading || '');
  const [results, setResults] = useState<LinkSearchResult[]>([]);
  const [selectedLinks, setSelectedLinks] = useState<Set<number>>(new Set());
  const [warnings, setWarnings] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isRewording, setIsRewording] = useState(false);
  const [rewordedText, setRewordedText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showContext, setShowContext] = useState(false);
  const [showTips, setShowTips] = useState(false);

  const tipStyle = SEO_TIPS[linkType];

  useEffect(() => {
    if (isOpen) {
      setResults([]);
      setSelectedLinks(new Set());
      setWarnings([]);
      setRewordedText('');
      setError(null);
      setShowContext(false);
      setShowTips(false);
      const sec = context?.section;
      const heading = sectionHeading || sec?.heading || '';
      const keyPoints = sec?.key_points?.join(' ') || '';
      setSearchQuery(keyPoints ? `${heading} ${keyPoints}`.trim() : heading);
      setSiteUrl(localStorage.getItem('linkSearch_siteUrl') || '');
    }
  }, [isOpen, sectionHeading, context, selectedText]);

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;
    if (linkType === 'internal' && !siteUrl.trim()) {
      setError('Please enter your website URL for internal link search.');
      return;
    }
    if (siteUrl.trim()) {
      localStorage.setItem('linkSearch_siteUrl', siteUrl.trim());
    }
    setIsSearching(true);
    setError(null);
    setWarnings([]);
    setResults([]);
    setSelectedLinks(new Set());
    setRewordedText('');
    try {
      const response = await linkApi.searchLinks({
        query: searchQuery,
        link_type: linkType,
        site_url: linkType === 'internal' ? siteUrl.trim() : siteUrl.trim() || undefined,
        num_results: 8,
      });
      setResults(response.results || []);
      setWarnings(response.warnings || []);
      if ((response.results || []).length === 0) {
        setError(linkType === 'internal'
          ? 'No internal links found. Make sure your site URL is correct and publicly accessible.'
          : 'No external links found for this query. Try a different search term.');
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Search failed');
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery, linkType, siteUrl]);

  const toggleLink = useCallback((index: number) => {
    setSelectedLinks(prev => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index); else next.add(index);
      return next;
    });
  }, []);

  const handleReword = useCallback(async () => {
    if (selectedLinks.size === 0 || !sectionText) return;
    setIsRewording(true);
    setError(null);
    setRewordedText('');
    try {
      const linksToInclude = Array.from(selectedLinks).map(i => ({
        url: results[i].url,
        title: results[i].title,
      }));
      const response = await linkApi.rewordWithLinks({
        section_text: sectionText,
        selected_text: selectedText || undefined,
        section_heading: sectionHeading || undefined,
        links: linksToInclude,
      });
      setRewordedText(response.reworded_text);
      setWarnings(prev => [...prev, ...response.warnings]);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Reword failed');
    } finally {
      setIsRewording(false);
    }
  }, [selectedLinks, results, sectionText, selectedText, sectionHeading]);

  const handleAccept = useCallback(() => {
    if (rewordedText && onRewordAccept) {
      onRewordAccept(rewordedText, context?.sectionId);
    }
    onClose();
  }, [rewordedText, onRewordAccept, context, onClose]);

  if (!isOpen) return null;

  const contextSummary = [
    sectionHeading ? `Heading: "${sectionHeading}"` : null,
    selectedText ? `Selected text: "${selectedText.substring(0, 80)}${selectedText.length > 80 ? '...' : ''}"` : null,
    sectionText ? `Section text: ${sectionText.length} chars` : null,
    `Search query: "${searchQuery}"`,
    `Link type: ${linkType}`,
    siteUrl ? `Site URL: ${siteUrl}` : null,
  ].filter(Boolean).join('\n');

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.55)', zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center' }} onClick={onClose}>
      <div style={{ background: '#fff', width: '100%', maxWidth: '780px', borderRadius: 16, overflow: 'hidden', display: 'flex', flexDirection: 'column', maxHeight: '90vh', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }} onClick={e => e.stopPropagation()}>

        {/* Header with gradient */}
        <div style={{ background: tipStyle.gradient, padding: '20px 24px', color: 'white', position: 'relative' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: 'white', display: 'flex', alignItems: 'center', gap: 10 }}>
                <span style={{ fontSize: '24px' }}>{tipStyle.icon}</span>
                {sectionHeading || 'Find Links'}
              </h3>
              <p style={{ margin: '6px 0 0', fontSize: '13px', color: 'rgba(255,255,255,0.85)', lineHeight: 1.4 }}>
                {tipStyle.description}
              </p>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                onClick={() => setShowTips(!showTips)}
                style={{ background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: 6, padding: '6px 12px', color: 'white', fontSize: '12px', cursor: 'pointer', fontWeight: 500 }}
                title="SEO tips and best practices"
              >
                💡 SEO Tips
              </button>
              <button
                onClick={onClose}
                style={{ background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: 6, padding: '6px 12px', color: 'white', fontSize: '12px', cursor: 'pointer', fontWeight: 500 }}
              >
                ✕ Close
              </button>
            </div>
          </div>

          {/* SEO tips expandable */}
          {showTips && (
            <div style={{ marginTop: 12, padding: '12px 16px', background: 'rgba(255,255,255,0.15)', borderRadius: 8, backdropFilter: 'blur(4px)' }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'white', marginBottom: 6 }}>
                Why {linkType === 'internal' ? 'Internal' : 'External'} Links Matter for SEO:
              </div>
              <ul style={{ margin: 0, paddingLeft: 18, color: 'rgba(255,255,255,0.9)', fontSize: '12px', lineHeight: 1.6 }}>
                {tipStyle.benefits.map((b, i) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
              <div style={{ marginTop: 8, fontSize: '12px', color: 'rgba(255,255,255,0.8)', fontStyle: 'italic', background: 'rgba(0,0,0,0.15)', padding: '8px 12px', borderRadius: 6 }}>
                💡 Best practice: {tipStyle.bestPractice}
              </div>
            </div>
          )}
        </div>

        <div style={{ padding: 20, overflow: 'auto', flex: 1 }}>

          {/* Link Type Selector */}
          <div style={{ display: 'flex', gap: 0, marginBottom: 16, borderRadius: 10, overflow: 'hidden', border: '1px solid #e5e7eb' }}>
            <button
              onClick={() => { setLinkType('external'); setResults([]); setRewordedText(''); setSelectedLinks(new Set()); setError(null); }}
              style={{
                flex: 1, padding: '12px 16px', border: 'none',
                background: linkType === 'external' ? 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)' : '#fafafa',
                color: linkType === 'external' ? 'white' : '#666',
                fontWeight: 600, fontSize: '14px', cursor: 'pointer', transition: 'all 0.2s',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              }}
            >
              🌐 External Links
            </button>
            <button
              onClick={() => { setLinkType('internal'); setResults([]); setRewordedText(''); setSelectedLinks(new Set()); setError(null); }}
              style={{
                flex: 1, padding: '12px 16px', border: 'none',
                background: linkType === 'internal' ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : '#fafafa',
                color: linkType === 'internal' ? 'white' : '#666',
                fontWeight: 600, fontSize: '14px', cursor: 'pointer', transition: 'all 0.2s',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              }}
            >
              🏠 Internal Links
            </button>
          </div>

          {/* Site URL */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: 4 }}>
              {linkType === 'internal' ? '🔗 Your Website URL (required)' : '🔗 Your Website URL (optional — excludes your site from results)'}
              <span style={{ fontSize: '11px', color: '#9ca3af', fontWeight: 400 }}>(saved for next time)</span>
            </label>
            <input
              type="url"
              value={siteUrl}
              onChange={e => {
                setSiteUrl(e.target.value);
                if (e.target.value.trim()) localStorage.setItem('linkSearch_siteUrl', e.target.value.trim());
              }}
              placeholder="https://example.com"
              style={{ width: '100%', padding: '10px 14px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '14px', boxSizing: 'border-box', outline: 'none', transition: 'border-color 0.2s' }}
              onFocus={e => { e.currentTarget.style.borderColor = '#6366f1'; }}
              onBlur={e => { e.currentTarget.style.borderColor = '#d1d5db'; }}
            />
          </div>

          {/* Search Query */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: 4 }}>
              🔍 Search Query
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                placeholder="Topic or section heading..."
                style={{ flex: 1, padding: '10px 14px', border: '1px solid #d1d5db', borderRadius: 8, fontSize: '14px', outline: 'none' }}
              />
              <button
                onClick={handleSearch}
                disabled={isSearching || !searchQuery.trim()}
                style={{
                  padding: '10px 24px',
                  background: isSearching || !searchQuery.trim() ? '#d1d5db' : tipStyle.gradient,
                  color: 'white', border: 'none', borderRadius: 8, fontSize: '14px', fontWeight: 600,
                  cursor: isSearching ? 'not-allowed' : 'pointer',
                  boxShadow: isSearching || !searchQuery.trim() ? 'none' : '0 2px 8px rgba(99,102,241,0.3)',
                  transition: 'all 0.2s',
                }}
              >
                {isSearching ? '⏳ Searching...' : '🔍 Search'}
              </button>
            </div>
          </div>

          {/* Context toggle */}
          <div style={{ marginBottom: 12 }}>
            <button
              onClick={() => setShowContext(!showContext)}
              style={{ background: 'none', border: '1px solid #e5e7eb', borderRadius: 6, padding: '4px 10px', fontSize: '11px', color: '#6b7280', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4 }}
            >
              📋 {showContext ? 'Hide' : 'Show'} what we're sending to AI
            </button>
            {showContext && (
              <div style={{ marginTop: 6, padding: '10px 12px', background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 8, fontSize: '11px', color: '#6b7280', lineHeight: 1.6, whiteSpace: 'pre-wrap', maxHeight: 120, overflowY: 'auto' }}>
                {contextSummary}
              </div>
            )}
          </div>

          {/* Warnings */}
          {warnings.length > 0 && (
            <div style={{ padding: '10px 14px', background: '#fffbeb', border: '1px solid #fbbf24', borderRadius: 8, color: '#92400e', fontSize: '13px', marginBottom: 12 }}>
              <strong>⚠️ Note:</strong> {warnings.join(' ')}
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{ padding: '12px 16px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: 8, color: '#991b1b', fontSize: '13px', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '16px' }}>❌</span>
              {error}
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>
                  Found {results.length} link{results.length !== 1 ? 's' : ''} — select to include:
                </span>
                <button
                  onClick={() => {
                    if (selectedLinks.size === results.length) setSelectedLinks(new Set());
                    else setSelectedLinks(new Set(results.map((_, i) => i)));
                  }}
                  style={{ fontSize: '11px', color: '#6366f1', background: 'none', border: '1px solid #e0e7ff', borderRadius: 4, cursor: 'pointer', padding: '3px 8px', fontWeight: 500 }}
                >
                  {selectedLinks.size === results.length ? '✓ Deselect All' : `✓ Select All (${results.length})`}
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: '240px', overflowY: 'auto' }}>
                {results.map((result, index) => (
                  <label
                    key={index}
                    style={{
                      display: 'flex', alignItems: 'flex-start', gap: 10, padding: '10px 12px',
                      background: selectedLinks.has(index) ? 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)' : '#fafafa',
                      border: `1px solid ${selectedLinks.has(index) ? '#6366f1' : '#e5e7eb'}`,
                      borderRadius: 8, cursor: 'pointer', transition: 'all 0.15s',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedLinks.has(index)}
                      onChange={() => toggleLink(index)}
                      style={{ marginTop: 4, accentColor: '#6366f1' }}
                    />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: '14px', fontWeight: 500, color: '#1f2937', marginBottom: 2 }}>
                        {result.title || 'Untitled'}
                      </div>
                      <div style={{ fontSize: '12px', color: '#6366f1', marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        <a href={result.url} target="_blank" rel="noopener noreferrer" style={{ color: '#6366f1', textDecoration: 'none' }} onClick={e => e.stopPropagation()}>
                          {result.url} ↗
                        </a>
                      </div>
                      {result.text && (
                        <div style={{ fontSize: '12px', color: '#6b7280', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                          {result.text.substring(0, 200)}{result.text.length > 200 ? '...' : ''}
                        </div>
                      )}
                    </div>
                    {result.score > 0 && (
                      <span style={{ fontSize: '10px', color: '#9ca3af', whiteSpace: 'nowrap', background: '#f3f4f6', padding: '2px 6px', borderRadius: 4 }}>
                        relevance {result.score.toFixed(2)}
                      </span>
                    )}
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Reword Section */}
          {selectedLinks.size > 0 && !rewordedText && (
            sectionText ? (
              <button
                onClick={handleReword}
                disabled={isRewording}
                style={{
                  width: '100%', padding: '14px 24px',
                  background: isRewording ? '#d1d5db' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: 'white', border: 'none', borderRadius: 10, fontSize: '15px', fontWeight: 600,
                  cursor: isRewording ? 'not-allowed' : 'pointer', marginBottom: 12,
                  boxShadow: isRewording ? 'none' : '0 4px 12px rgba(16,185,129,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  transition: 'all 0.2s',
                }}
              >
                {isRewording ? '⏳ Rewording with AI...' : `✨ Reword with ${selectedLinks.size} Link${selectedLinks.size !== 1 ? 's' : ''}`}
              </button>
            ) : (
              <div style={{ padding: '14px 16px', background: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)', border: '1px solid #93c5fd', borderRadius: 10, color: '#1e40af', fontSize: '13px', marginBottom: 12, lineHeight: 1.5 }}>
                <strong>💡 Tip:</strong> Select links above and copy their URLs to insert manually. The "Reword with Links" feature requires section text context, which isn't available here — but works when you select text in the editor.
              </div>
            )
          )}

          {/* Reworded Result */}
          {rewordedText && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: '14px', fontWeight: 600, color: '#1f2937' }}>
                  ✨ Reworded Text
                </span>
                <span style={{ fontSize: '11px', color: '#6b7280' }}>
                  {selectedLinks.size} link{selectedLinks.size !== 1 ? 's' : ''} incorporated
                </span>
              </div>
              <div style={{
                padding: '14px 16px',
                background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                border: '1px solid #bbf7d0',
                borderRadius: 10, fontSize: '14px', lineHeight: 1.7, color: '#1f2937',
                maxHeight: '220px', overflowY: 'auto', whiteSpace: 'pre-wrap',
              }}>
                {rewordedText}
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button
                  onClick={handleAccept}
                  style={{
                    flex: 1, padding: '12px 24px',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white',
                    border: 'none', borderRadius: 10, fontSize: '14px', fontWeight: 600, cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(16,185,129,0.3)',
                  }}
                >
                  ✅ Use This Text
                </button>
                <button
                  onClick={() => { setRewordedText(''); }}
                  style={{
                    padding: '12px 20px', background: '#f9fafb', color: '#6b7280',
                    border: '1px solid #e5e7eb', borderRadius: 10, fontSize: '14px', cursor: 'pointer',
                  }}
                >
                  🔄 Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LinkSearchModal;