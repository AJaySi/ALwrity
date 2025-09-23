import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogOutlineSection } from '../../services/blogWriterApi';

interface OutlineRefinerProps {
  outline: BlogOutlineSection[];
  onOutlineUpdated: (outline: BlogOutlineSection[]) => void;
}

const useCopilotActionTyped = useCopilotAction as any;

export const OutlineRefiner: React.FC<OutlineRefinerProps> = ({
  outline,
  onOutlineUpdated
}) => {
  useCopilotActionTyped({
    name: 'refineOutline',
    description: 'Refine the outline (add/remove/move/merge)',
    parameters: [
      { name: 'operation', type: 'string', description: 'add|remove|move|merge|rename', required: true },
      { name: 'sectionId', type: 'string', description: 'Target section ID', required: false },
      { name: 'payload', type: 'string', description: 'JSON payload for operation', required: false },
    ],
    handler: async ({ operation, sectionId, payload }: { operation: string; sectionId?: string; payload?: string }) => {
      const payloadObj = payload ? (() => { try { return JSON.parse(payload); } catch { return {}; } })() : undefined;
      const res = await blogWriterApi.refineOutline({ outline, operation, section_id: sectionId, payload: payloadObj });
      if (res?.outline) onOutlineUpdated(res.outline);
      return { success: true };
    }
  });

  return null; // This component only provides the copilot action
};

export default OutlineRefiner;
