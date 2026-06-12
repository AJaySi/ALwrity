import { useCopilotAction } from '@copilotkit/react-core';

interface ParameterDescriptor {
  name: string;
  type: string;
  required?: boolean;
  description?: string;
  enum?: string[];
  attributes?: ParameterDescriptor[];
}

interface CopilotActionConfig<TArgs = Record<string, any>> {
  name: string;
  description: string;
  parameters?: ParameterDescriptor[];
  handler: (args: TArgs) => Promise<any>;
}

export function useCopilotActionTyped<TArgs = Record<string, any>>(
  config: CopilotActionConfig<TArgs>
): void {
  (useCopilotAction as (config: unknown) => void)(config);
}
