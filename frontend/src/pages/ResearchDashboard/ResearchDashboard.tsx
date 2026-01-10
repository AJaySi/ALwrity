import React, { useState } from 'react';
import { ResearchWizard } from '../../components/Research';
import { BlogResearchResponse } from '../../services/blogWriterApi';
import { ResearchPersonaModal } from '../../components/Research/ResearchPersonaModal';
import { OnboardingCompetitorModal } from '../../components/Research/OnboardingCompetitorModal';
import { useProjectRestoration } from './hooks/useProjectRestoration';
import { usePersonaManagement } from './hooks/usePersonaManagement';
import { useCompetitorManagement } from './hooks/useCompetitorManagement';
import { Header } from './components/Header';
import { LeftPanel } from './components/LeftPanel';
import { FooterStats } from './components/FooterStats';
import { PersonaDetailsModal } from './components/PersonaDetailsModal';
import { ResearchPreset } from './types';
import { dashboardStyles } from './styles';

export const ResearchDashboard: React.FC = () => {
  const [results, setResults] = useState<BlogResearchResponse | null>(null);
  const [showDebug, setShowDebug] = useState(false);
  const [showPersonaDetailsModal, setShowPersonaDetailsModal] = useState(false);

  // Custom hooks for state management
  const projectRestoration = useProjectRestoration();
  const personaManagement = usePersonaManagement();
  const competitorManagement = useCompetitorManagement();

  const handleComplete = (researchResults: BlogResearchResponse) => {
    setResults(researchResults);
  };

  const handlePresetClick = (preset: ResearchPreset) => {
    projectRestoration.setPresetKeywords([preset.keywords]);
    projectRestoration.setPresetIndustry(preset.industry);
    projectRestoration.setPresetTargetAudience(preset.targetAudience);
    projectRestoration.setPresetMode(preset.researchMode);
    projectRestoration.setPresetConfig(preset.config);
    setResults(null);
  };

  const handleOpenPersonaDetails = async () => {
    setShowPersonaDetailsModal(true);
    await personaManagement.handleOpenPersonaDetails();
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Elements */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '5%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 20s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '10%',
        right: '5%',
        width: '300px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 15s ease-in-out infinite reverse',
      }} />
      
      <style>{dashboardStyles}</style>

      {/* Header */}
      <Header />

      {/* Main Content */}
      <div style={{ 
        maxWidth: '1400px', 
        margin: '0 auto', 
        padding: '0 24px', 
        display: 'flex', 
        gap: '20px', 
        flexWrap: 'wrap', 
        position: 'relative', 
        zIndex: 10 
      }}>
        {/* Left Panel */}
        <LeftPanel
          presets={personaManagement.displayPresets}
          personaExists={personaManagement.personaExists}
          showDebug={showDebug}
          results={results}
          onPresetClick={handlePresetClick}
          onReset={projectRestoration.handleReset}
          onToggleDebug={setShowDebug}
        />

        {/* Main Content - Wizard */}
        <div style={{ flex: '2 1 800px', animation: 'fadeInUp 0.4s ease-out' }}>
          <ResearchWizard
            initialKeywords={projectRestoration.presetKeywords}
            initialIndustry={projectRestoration.presetIndustry}
            initialResults={
              projectRestoration.restoredProject?.intent_result || 
              projectRestoration.restoredProject?.legacy_result || 
              results
            }
            initialTargetAudience={projectRestoration.presetTargetAudience}
            initialResearchMode={projectRestoration.presetMode}
            initialConfig={projectRestoration.presetConfig}
            onComplete={handleComplete}
            headerActions={{
              onOpenPersona: handleOpenPersonaDetails,
              onOpenCompetitors: competitorManagement.handleOpenCompetitorModal,
              personaExists: personaManagement.personaExists,
            }}
          />
        </div>
      </div>

      {/* Footer Stats */}
      {results && <FooterStats results={results} />}

      {/* Research Persona Generation Modal */}
      <ResearchPersonaModal
        open={personaManagement.showPersonaModal}
        onClose={() => personaManagement.setShowPersonaModal(false)}
        onGenerate={personaManagement.handleGeneratePersona}
        onCancel={personaManagement.handleCancelPersona}
      />

      {/* Competitor Analysis Modal */}
      <OnboardingCompetitorModal
        open={competitorManagement.showCompetitorModal}
        onClose={() => competitorManagement.setShowCompetitorModal(false)}
        data={competitorManagement.competitorData}
        loading={competitorManagement.loadingCompetitors}
        error={competitorManagement.competitorError}
        onRefresh={competitorManagement.handleRefreshCompetitors}
      />

      {/* Research Persona Details Modal */}
      <PersonaDetailsModal
        open={showPersonaDetailsModal}
        loading={personaManagement.loadingPersonaDetails}
        researchPersona={personaManagement.researchPersona}
        onClose={() => setShowPersonaDetailsModal(false)}
      />
    </div>
  );
};

export default ResearchDashboard;
