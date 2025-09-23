import React from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { blogWriterApi, BlogSEOMetadataResponse } from '../../services/blogWriterApi';

interface PublisherProps {
  buildFullMarkdown: () => string;
  convertMarkdownToHTML: (md: string) => string;
  seoMetadata: BlogSEOMetadataResponse | null;
}

const useCopilotActionTyped = useCopilotAction as any;

export const Publisher: React.FC<PublisherProps> = ({
  buildFullMarkdown,
  convertMarkdownToHTML,
  seoMetadata
}) => {
  useCopilotActionTyped({
    name: 'publishToPlatform',
    description: 'Publish the blog to Wix or WordPress',
    parameters: [
      { name: 'platform', type: 'string', description: 'wix|wordpress', required: true },
      { name: 'schedule_time', type: 'string', description: 'Optional ISO datetime', required: false }
    ],
    handler: async ({ platform, schedule_time }: { platform: 'wix' | 'wordpress'; schedule_time?: string }) => {
      const md = buildFullMarkdown();
      const html = convertMarkdownToHTML(md);
      if (!seoMetadata) return { success: false, message: 'Generate SEO metadata first' };
      const res = await blogWriterApi.publish({ platform, html, metadata: seoMetadata, schedule_time });
      return { success: true, url: res.url };
    },
    render: ({ status, result }: any) => status === 'complete' ? (
      <div style={{ padding: 12 }}>Published: {result?.url || 'Success'}</div>
    ) : null
  });

  return null; // This component only provides the copilot action
};

export default Publisher;
