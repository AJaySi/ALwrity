import { useCopilotAction } from '@copilotkit/react-core';

const useCopilotActionTyped = useCopilotAction as any;

export const RegisterBlogWriterActions: React.FC = () => {
  useCopilotActionTyped({
    name: 'Generate All Sections of Outline',
    description: 'Generate content for every section in the current outline',
    parameters: [],
    handler: async () => {
      // Frontend-only placeholder; generation handled via individual actions in UI for now
      return { success: true };
    },
  });

  return null;
};

export default RegisterBlogWriterActions;


