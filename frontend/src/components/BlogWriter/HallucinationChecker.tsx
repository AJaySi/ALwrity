import React, { useState } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import DiffPreview from './DiffPreview';

interface HallucinationCheckerProps {
  buildFullMarkdown: () => string;
  buildUpdatedMarkdownForClaim: (claimText: string, supportingUrl?: string) => {
    original: string;
    updated: string;
    updatedMarkdown: string;
  };
  applyClaimFix: (claimText: string, supportingUrl?: string) => void;
}

const useCopilotActionTyped = useCopilotAction as any;

export const HallucinationChecker: React.FC<HallucinationCheckerProps> = ({
  buildFullMarkdown,
  buildUpdatedMarkdownForClaim,
  applyClaimFix
}) => {
  const [hallucinationResult, setHallucinationResult] = useState<any>(null);

  useCopilotActionTyped({
    name: 'runHallucinationCheck',
    description: 'Run hallucination detector on full draft and view claims',
    parameters: [],
    handler: async () => {
      const content = buildFullMarkdown();
      const res = await fetch('/api/blog/quality/hallucination-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: content })
      });
      const data = await res.json();
      setHallucinationResult(data);
      return { success: true, total_claims: data?.total_claims };
    },
    renderAndWaitForResponse: ({ respond, result }: any) => {
      if (!result) return null;
      const claims = hallucinationResult?.claims || [];
      return (
        <div style={{ padding: 12 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Hallucination Check</div>
          <div>Total claims: {hallucinationResult?.total_claims ?? 0}</div>
          <ul>
            {claims.slice(0, 5).map((c: any, i: number) => {
              const supporting = (c.supporting_sources && c.supporting_sources[0]?.url) || undefined;
              const { original, updated } = buildUpdatedMarkdownForClaim(c.text, supporting);
              return (
                <li key={i} style={{ marginBottom: 10 }}>
                  <div style={{ marginBottom: 4 }}>[{c.assessment}] {c.text} (conf: {Math.round((c.confidence || 0)*100)/100})</div>
                  {original && updated ? (
                    <DiffPreview
                      original={original}
                      updated={updated}
                      onApply={() => { applyClaimFix(c.text, supporting); respond?.('applied'); }}
                      onDiscard={() => { respond?.('discarded'); }}
                    />
                  ) : (
                    <div style={{ fontStyle: 'italic', color: '#666' }}>No matching sentence found for preview.</div>
                  )}
                </li>
              );
            })}
          </ul>
          <button onClick={() => respond?.('ack')}>Close</button>
        </div>
      );
    }
  });

  return null; // This component only provides the copilot action
};

export default HallucinationChecker;
