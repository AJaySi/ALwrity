import React, { useCallback, useEffect, useState } from 'react';
import { useBacklinkOutreachStore } from '../../stores/backlinkOutreachStore';

const BacklinkOutreachDashboard: React.FC = () => {
  const {
    campaigns, selectedCampaign, discoveredOpportunities,
    isLoading, isDiscovering, error,
    fetchCampaigns, createCampaign, selectCampaign,
    deepDiscover, clearDiscoveries,
  } = useBacklinkOutreachStore();

  const [activeTab, setActiveTab] = useState<'campaigns' | 'discover' | 'leads'>('campaigns');
  const [newCampaignName, setNewCampaignName] = useState('');
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    fetchCampaigns('default', 'default');
  }, [fetchCampaigns]);

  const handleCreateCampaign = useCallback(async () => {
    if (!newCampaignName.trim()) return;
    const id = await createCampaign('default', 'default', newCampaignName.trim());
    if (id) {
      setNewCampaignName('');
      setActiveTab('discover');
    }
  }, [newCampaignName, createCampaign]);

  const handleDiscover = useCallback(async () => {
    if (!keyword.trim()) return;
    await deepDiscover(keyword.trim(), 15);
  }, [keyword, deepDiscover]);

  const handleDiscoverAndSave = useCallback(async (campaignId: string) => {
    if (!keyword.trim()) return;
    await deepDiscover(keyword.trim(), 15, campaignId);
  }, [keyword, deepDiscover]);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Backlink Outreach</h1>
      <p style={{ color: '#666', marginBottom: '24px' }}>
        Discover guest post opportunities, manage campaigns, and track outreach.
      </p>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', borderBottom: '2px solid #eee', paddingBottom: '8px' }}>
        {(['campaigns', 'discover', 'leads'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 20px',
              border: 'none',
              background: activeTab === tab ? '#1976D2' : 'transparent',
              color: activeTab === tab ? '#fff' : '#666',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: activeTab === tab ? 600 : 400,
            }}
          >
            {tab === 'campaigns' ? 'Campaigns' : tab === 'discover' ? 'Discover' : 'Leads'}
          </button>
        ))}
      </div>

      {error && (
        <div style={{ padding: '12px', background: '#ffebee', color: '#c62828', borderRadius: '6px', marginBottom: '16px' }}>
          {error}
        </div>
      )}

      {/* Tab: Campaigns */}
      {activeTab === 'campaigns' && (
        <div>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
            <input
              type="text"
              value={newCampaignName}
              onChange={(e) => setNewCampaignName(e.target.value)}
              placeholder="Campaign name"
              style={{ flex: 1, padding: '10px 14px', border: '1px solid #ddd', borderRadius: '6px' }}
            />
            <button
              onClick={handleCreateCampaign}
              disabled={!newCampaignName.trim() || isLoading}
              style={{
                padding: '10px 24px', background: '#1976D2', color: '#fff',
                border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600,
              }}
            >
              {isLoading ? 'Creating...' : 'Create Campaign'}
            </button>
          </div>

          {campaigns.length === 0 && !isLoading && (
            <p style={{ color: '#999' }}>No campaigns yet. Create one to get started.</p>
          )}

          {campaigns.map((c) => (
            <div
              key={c.campaign_id}
              onClick={() => { selectCampaign(c.campaign_id, 'default'); setActiveTab('leads'); }}
              style={{
                padding: '16px', marginBottom: '8px', border: '1px solid #e0e0e0',
                borderRadius: '8px', cursor: 'pointer', background: '#fafafa',
              }}
            >
              <div style={{ fontWeight: 600 }}>{c.name}</div>
              <div style={{ fontSize: '13px', color: '#888', marginTop: '4px' }}>
                Status: {c.status}
                {c.created_at && <> &middot; Created: {new Date(c.created_at).toLocaleDateString()}</>}
              </div>
            </div>
          ))}
          {isLoading && <p style={{ color: '#999' }}>Loading campaigns...</p>}
        </div>
      )}

      {/* Tab: Discover */}
      {activeTab === 'discover' && (
        <div>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="Enter keyword (e.g. 'AI marketing')"
              style={{ flex: 1, padding: '10px 14px', border: '1px solid #ddd', borderRadius: '6px' }}
            />
            <button
              onClick={handleDiscover}
              disabled={!keyword.trim() || isDiscovering}
              style={{
                padding: '10px 24px', background: '#2e7d32', color: '#fff',
                border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 600,
              }}
            >
              {isDiscovering ? 'Searching...' : 'Discover'}
            </button>
          </div>

          {isDiscovering && <p style={{ color: '#666' }}>Searching for opportunities using Exa + DuckDuckGo...</p>}

          {discoveredOpportunities.length > 0 && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontWeight: 600 }}>Found {discoveredOpportunities.length} opportunities</span>
                <button
                  onClick={clearDiscoveries}
                  style={{ padding: '6px 16px', background: 'transparent', border: '1px solid #ccc', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Clear
                </button>
              </div>
              {discoveredOpportunities.map((opp, i) => (
                <div
                  key={`${opp.url}-${i}`}
                  style={{
                    padding: '14px', marginBottom: '8px', border: '1px solid #e0e0e0',
                    borderRadius: '8px', background: '#fff',
                  }}
                >
                  <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                    <a href={opp.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1976D2', textDecoration: 'none' }}>
                      {opp.page_title || opp.domain}
                    </a>
                  </div>
                  <div style={{ fontSize: '13px', color: '#666', marginBottom: '4px' }}>{opp.domain}</div>
                  {opp.snippet && (
                    <div style={{ fontSize: '13px', color: '#555', marginBottom: '6px' }}>{opp.snippet.slice(0, 200)}...</div>
                  )}
                  <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#888' }}>
                    <span>Quality: {(opp.quality_score * 100).toFixed(0)}%</span>
                    <span>Confidence: {(opp.confidence_score * 100).toFixed(0)}%</span>
                    <span>Words: {opp.word_count}</span>
                    {opp.has_guest_post_guidelines && <span style={{ color: '#2e7d32' }}>Has guidelines</span>}
                    {opp.email && <span style={{ color: '#1565c0' }}>Email found</span>}
                  </div>
                  <div style={{ marginTop: '8px' }}>
                    <button
                      onClick={() => campaigns.length > 0 && handleDiscoverAndSave(campaigns[0].campaign_id)}
                      disabled={campaigns.length === 0}
                      style={{
                        padding: '6px 14px', fontSize: '12px', background: '#f5f5f5',
                        border: '1px solid #ddd', borderRadius: '4px', cursor: campaigns.length > 0 ? 'pointer' : 'not-allowed',
                      }}
                    >
                      Save to first campaign
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: Leads */}
      {activeTab === 'leads' && (
        <div>
          {selectedCampaign ? (
            <div>
              <h3 style={{ marginBottom: '8px' }}>{selectedCampaign.name}</h3>
              <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
                Status: {selectedCampaign.status} &middot; {selectedCampaign.lead_count} leads
              </p>
              {selectedCampaign.leads.length === 0 && (
                <p style={{ color: '#999' }}>No leads yet. Go to Discover tab to find opportunities.</p>
              )}
              {selectedCampaign.leads.map((lead) => (
                <div
                  key={lead.lead_id}
                  style={{
                    padding: '14px', marginBottom: '8px', border: '1px solid #e0e0e0',
                    borderRadius: '8px', background: '#fff',
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{lead.page_title || lead.domain}</div>
                  <div style={{ fontSize: '13px', color: '#888', marginTop: '4px' }}>
                    {lead.url && <a href={lead.url} target="_blank" rel="noopener noreferrer" style={{ color: '#1976D2' }}>{lead.url}</a>}
                  </div>
                  <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#888', marginTop: '6px' }}>
                    <span>Status: <strong>{lead.status}</strong></span>
                    {lead.email && <span>Email: {lead.email}</span>}
                    <span>Source: {lead.discovery_source}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#999' }}>Select a campaign from the Campaigns tab to view its leads.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default BacklinkOutreachDashboard;