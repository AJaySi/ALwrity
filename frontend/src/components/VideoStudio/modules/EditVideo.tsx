import React from 'react';
import ModulePlaceholder from '../ModulePlaceholder';

export const EditVideo: React.FC = () => {
  return (
    <ModulePlaceholder
      title="Edit Studio"
      subtitle="Trim, replace, captions"
      status="coming soon"
      description="Non-destructive trims, speed changes, stabilization, background replace, object/face swap, captions/subtitles."
      bullets={[
        'Use cases: polish social clips, remove sections, localize with captions',
        'Planned: timeline editor, region/face selection, auto-captions',
        'Guardrails: duration caps per tier, cost shown before edits run',
      ]}
    />
  );
};

export default EditVideo;
