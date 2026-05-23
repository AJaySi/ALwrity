import React, { useCallback, useEffect, useState } from 'react';

import { fetchBacklinkQueryTemplates } from '../../api/backlinkOutreachApi';
import { useBacklinkOutreachStore } from '../../stores/backlinkOutreachStore';

const BacklinkOutreachModuleList: React.FC = () => {
  const { modules, coverage, campaigns, isLoading, error, refreshBacklinkRegistry, fetchCampaigns, createCampaign } = useBacklinkOutreachStore();
  const [queryPreview, setQueryPreview] = useState<string[]>([]);
  const [newCampaignName, setNewCampaignName] = useState('');

  useEffect(() => {
    refreshBacklinkRegistry();
  }, [refreshBacklinkRegistry]);

  useEffect(() => {
    const loadPreview = async () => {
      const response = await fetchBacklinkQueryTemplates('seo');
      setQueryPreview(response.queries.slice(0, 3));
    };
    loadPreview().catch(() => setQueryPreview([]));
  }, []);

  useEffect(() => {
    fetchCampaigns('default', 'default').catch(() => {});
  }, [fetchCampaigns]);

  const handleCreateCampaign = useCallback(async () => {
    if (!newCampaignName.trim()) return;
    await createCampaign('default', 'default', newCampaignName.trim());
    setNewCampaignName('');
  }, [newCampaignName, createCampaign]);

  return (
    <section>
      <h3>Backlink Outreach Modules</h3>
      {isLoading && <p>Loading backlink module registry…</p>}
      {error && <p>{error}</p>}
      {!isLoading && !error && (
        <>
          <ul>
            {modules.map((module) => (
              <li key={`${module.identifier}:${module.module_path}`}>
                <strong>{module.identifier}</strong>: {module.module_path}
              </li>
            ))}
          </ul>
          {coverage && (
            <>
              <p>
                Legacy parity: {coverage.implemented_count} implemented / {coverage.planned_count} planned
              </p>
              <p>Legacy reference: {coverage.legacy_reference}</p>
            </>
          )}
          {queryPreview.length > 0 && (
            <>
              <h4>Legacy query template preview (keyword: seo)</h4>
              <ul>
                {queryPreview.map((query) => (
                  <li key={query}>{query}</li>
                ))}
              </ul>
            </>
          )}

          <h4>Campaigns</h4>
          {campaigns.length === 0 ? (
            <p>No campaigns yet. Create one below.</p>
          ) : (
            <ul>
              {campaigns.map((c) => (
                <li key={c.campaign_id}>
                  <strong>{c.name}</strong> ({c.status})
                  {c.created_at && <span> — {new Date(c.created_at).toLocaleDateString()}</span>}
                </li>
              ))}
            </ul>
          )}
          <div>
            <input
              type="text"
              value={newCampaignName}
              onChange={(e) => setNewCampaignName(e.target.value)}
              placeholder="Campaign name"
            />
            <button onClick={handleCreateCampaign} disabled={!newCampaignName.trim()}>
              Create Campaign
            </button>
          </div>
        </>
      )}
    </section>
  );
};

export default BacklinkOutreachModuleList;
