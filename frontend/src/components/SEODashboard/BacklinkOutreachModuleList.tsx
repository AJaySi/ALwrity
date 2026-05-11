import React, { useEffect, useState } from 'react';

import { fetchBacklinkQueryTemplates } from '../../api/backlinkOutreachApi';
import { useBacklinkOutreachStore } from '../../stores/backlinkOutreachStore';

const BacklinkOutreachModuleList: React.FC = () => {
  const { modules, coverage, isLoading, error, refreshBacklinkRegistry } = useBacklinkOutreachStore();
  const [queryPreview, setQueryPreview] = useState<string[]>([]);

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
        </>
      )}
    </section>
  );
};

export default BacklinkOutreachModuleList;
