import type { ExampleVideo, AspectPreset } from '../types';
import type { ContentAsset } from '../../../../../hooks/useContentAssets';
import { aspectPresets } from '../constants';

export const handleExampleClick = (
  index: number,
  example: ExampleVideo,
  setPrompt: (value: string) => void,
  setAspect: (value: AspectPreset) => void,
  setSelectedExample: (index: number | null) => void,
  setSelectedAssetId: (id: number | null) => void
) => {
  setSelectedExample(index);
  setSelectedAssetId(null);
  setPrompt(example.prompt);
  // Set appropriate settings based on example
  if (example.platform === 'Instagram' || example.platform === 'YouTube') {
    setAspect('9:16');
  } else if (example.platform === 'LinkedIn') {
    setAspect('16:9');
  }
};

export const handleAssetClick = (
  asset: ContentAsset,
  setPrompt: (value: string) => void,
  setAspect: (value: AspectPreset) => void,
  setResolution: (value: '480p' | '720p' | '1080p') => void,
  setSelectedAssetId: (id: number | null) => void,
  setSelectedExample: (index: number | null) => void
) => {
  setSelectedAssetId(asset.id);
  setSelectedExample(null);
  // Use prompt from asset if available, otherwise use title or description
  if (asset.prompt) {
    setPrompt(asset.prompt);
  } else if (asset.title) {
    setPrompt(asset.title);
  } else if (asset.description) {
    setPrompt(asset.description);
  }
  // Try to extract settings from metadata
  if (asset.asset_metadata) {
    if (asset.asset_metadata.aspect_ratio || asset.asset_metadata.aspect) {
      const aspectValue = asset.asset_metadata.aspect_ratio || asset.asset_metadata.aspect;
      if (aspectPresets.includes(aspectValue as any)) {
        setAspect(aspectValue as AspectPreset);
      }
    }
    if (asset.asset_metadata.resolution) {
      const res = asset.asset_metadata.resolution.toLowerCase();
      if (res.includes('480')) setResolution('480p');
      else if (res.includes('720')) setResolution('720p');
      else if (res.includes('1080')) setResolution('1080p');
    }
  }
};
