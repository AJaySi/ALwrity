import React, { useState, useEffect } from 'react';
import PersonaEditorModal from './PersonaEditorModal';

interface PersonaData {
  id?: number;
  user_id?: number;
  persona_name: string;
  archetype: string;
  core_belief: string;
  brand_voice_description: string;
  linguistic_fingerprint: any;
  platform_adaptations: any;
  confidence_score: number;
  ai_analysis_version: string;
  platform_type: string;
  sentence_metrics: any;
  lexical_features: any;
  rhetorical_devices: any;
  tonal_range: any;
  stylistic_constraints: any;
  content_format_rules: any;
  engagement_patterns: any;
  posting_frequency: any;
  content_types: any;
  platform_best_practices: any;
  algorithm_considerations: any;
}

interface PersonaChipProps {
  platform: string;
  userId?: number;
  onPersonaUpdate?: (personaData: PersonaData) => void;
}

const PersonaChip: React.FC<PersonaChipProps> = ({
  platform,
  userId = 1,
  onPersonaUpdate
}) => {
  const [personaData, setPersonaData] = useState<PersonaData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showEditor, setShowEditor] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch persona data
  const fetchPersonaData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch core persona list (take most recent active) and platform-specific details
      const [coreRes, platformRes] = await Promise.all([
        fetch(`/api/personas/user/${userId}`),
        fetch(`/api/personas/platform/${platform}?user_id=${userId}`)
      ]);

      if (coreRes.ok && platformRes.ok) {
        const coreList = await coreRes.json();
        const platformData = await platformRes.json();
        const core = (coreList?.personas && coreList.personas.length > 0) ? coreList.personas[0] : {};

        // Merge core + platform fields for editor convenience
        setPersonaData({
          id: core.id,
          user_id: core.user_id,
          persona_name: core.persona_name,
          archetype: core.archetype,
          core_belief: core.core_belief,
          brand_voice_description: core.brand_voice_description,
          linguistic_fingerprint: core.linguistic_fingerprint,
          platform_adaptations: core.platform_adaptations,
          confidence_score: core.confidence_score,
          ai_analysis_version: core.ai_analysis_version,
          platform_type: platform,
          sentence_metrics: platformData?.sentence_metrics,
          lexical_features: platformData?.lexical_features,
          rhetorical_devices: platformData?.rhetorical_devices,
          tonal_range: platformData?.tonal_range,
          stylistic_constraints: platformData?.stylistic_constraints,
          content_format_rules: platformData?.content_format_rules,
          engagement_patterns: platformData?.engagement_patterns,
          posting_frequency: platformData?.posting_frequency,
          content_types: platformData?.content_types,
          platform_best_practices: platformData?.platform_best_practices,
          algorithm_considerations: platformData?.algorithm_considerations,
        } as any);
      } else {
        setError('No persona found for this platform');
      }
    } catch (err) {
      setError('Failed to load persona data');
      console.error('Error fetching persona:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPersonaData();
  }, [platform, userId]);

  const handleSavePersona = async (data: PersonaData, saveToDatabase: boolean) => {
    try {
      if (saveToDatabase) {
        // Save core persona simple fields
        if (data.id) {
          const corePayload: any = {
            persona_name: data.persona_name,
            archetype: data.archetype,
            core_belief: data.core_belief,
            brand_voice_description: data.brand_voice_description,
            linguistic_fingerprint: data.linguistic_fingerprint,
            platform_adaptations: data.platform_adaptations,
          };

          const coreRes = await fetch(`/api/personas/${data.id}?user_id=${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(corePayload)
          });
          if (!coreRes.ok) throw new Error('Failed to update core persona');
        }

        // Save platform persona fields
        const platformPayload: any = {
          sentence_metrics: data.sentence_metrics,
          lexical_features: data.lexical_features,
          rhetorical_devices: data.rhetorical_devices,
          tonal_range: data.tonal_range,
          stylistic_constraints: data.stylistic_constraints,
          content_format_rules: data.content_format_rules,
          engagement_patterns: data.engagement_patterns,
          posting_frequency: data.posting_frequency,
          content_types: data.content_types,
          platform_best_practices: data.platform_best_practices,
          algorithm_considerations: data.algorithm_considerations,
        };

        const platRes = await fetch(`/api/personas/platform/${platform}?user_id=${userId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(platformPayload)
        });
        if (!platRes.ok) throw new Error('Failed to update platform persona');
      }

      // Update local state
      setPersonaData(data);
      
      // Notify parent component
      if (onPersonaUpdate) {
        onPersonaUpdate(data);
      }

      console.log('Persona updated:', saveToDatabase ? 'saved to database' : 'session only');
    } catch (err) {
      console.error('Error saving persona:', err);
      setError('Failed to save persona changes');
    }
  };

  const getPersonaColor = (confidence?: number) => {
    if (!confidence) return '#6b7280';
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const getPersonaIcon = (archetype?: string) => {
    if (!archetype) return '👤';
    
    const archetypeIcons: Record<string, string> = {
      'pragmatic futurist': '🔮',
      'thoughtful educator': '📚',
      'innovative leader': '🚀',
      'analytical expert': '🔍',
      'creative storyteller': '✨',
      'strategic advisor': '🎯',
      'authentic connector': '🤝',
      'data-driven optimist': '📊'
    };

    const lowerArchetype = archetype.toLowerCase();
    for (const [key, icon] of Object.entries(archetypeIcons)) {
      if (lowerArchetype.includes(key)) {
        return icon;
      }
    }
    
    return '👤';
  };

  if (isLoading) {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)',
        border: '1px solid #d1d5db',
        borderRadius: '999px',
        padding: '6px 14px',
        fontSize: '11px',
        fontWeight: '700',
        color: '#6b7280',
        display: 'flex',
        alignItems: 'center',
        gap: '6px'
      }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: '#9ca3af',
          animation: 'pulse 2s infinite'
        }} />
        Loading Persona...
      </div>
    );
  }

  if (error || !personaData) {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)',
        border: '1px solid #fca5a5',
        borderRadius: '999px',
        padding: '6px 14px',
        fontSize: '11px',
        fontWeight: '700',
        color: '#dc2626',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        cursor: 'pointer'
      }}
      onClick={() => fetchPersonaData()}
      title="Click to retry loading persona data"
      >
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: '#ef4444'
        }} />
        No Persona
      </div>
    );
  }

  const confidence = personaData.confidence_score || 0;
  const confidenceColor = getPersonaColor(confidence);
  
  // Debug: Log the confidence score to see what's being stored
  console.log('PersonaChip confidence_score:', personaData.confidence_score, 'processed:', confidence);
  const personaIcon = getPersonaIcon(personaData.archetype);

  return (
    <>
      <div
        style={{
          background: `linear-gradient(135deg, ${confidenceColor} 0%, ${confidenceColor}dd 100%)`,
          border: `1px solid ${confidenceColor}`,
          borderRadius: '999px',
          padding: '6px 14px',
          fontSize: '11px',
          fontWeight: '700',
          color: 'white',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          boxShadow: `0 2px 8px ${confidenceColor}40`,
          transform: 'translateZ(0)',
          userSelect: 'none'
        }}
        title={`${personaData.persona_name} - ${personaData.archetype || 'No archetype'} (${Math.round(confidence * 100)}% confidence). Click to edit.`}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)';
          e.currentTarget.style.boxShadow = `0 4px 16px ${confidenceColor}60`;
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0) scale(1)';
          e.currentTarget.style.boxShadow = `0 2px 8px ${confidenceColor}40`;
        }}
        onClick={() => setShowEditor(true)}
      >
        <div style={{
          fontSize: '12px',
          flexShrink: 0
        }}>
          {personaIcon}
        </div>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.9)',
          flexShrink: 0,
          boxShadow: '0 0 6px rgba(255, 255, 255, 0.5)'
        }} />
        <span style={{ whiteSpace: 'nowrap' }}>
          {personaData.persona_name || 'Untitled Persona'}
        </span>
        <div style={{
          fontSize: '10px',
          opacity: 0.8,
          marginLeft: '4px'
        }}>
          {Math.round(confidence * 100)}%
        </div>
      </div>

      <PersonaEditorModal
        isOpen={showEditor}
        onClose={() => setShowEditor(false)}
        personaData={personaData}
        onSave={(data, saveToDatabase) => handleSavePersona(data, saveToDatabase)}
        platform={platform}
      />
    </>
  );
};

export default PersonaChip;
