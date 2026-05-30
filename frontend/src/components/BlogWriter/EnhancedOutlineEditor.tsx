import React, { useState } from 'react';
import { BlogOutlineSection, SourceMappingStats, GroundingInsights, ResearchCoverage } from '../../services/blogWriterApi';
import OutlineIntelligenceChips from './OutlineIntelligenceChips';
import ImageGeneratorModal from '../ImageGen/ImageGeneratorModal';
import ChartGeneratorModal from '../Chart/ChartGeneratorModal';
import LinkSearchModal from '../Link/LinkSearchModal';
import { ChartGenerateResponse } from '../../services/chartApi';
import chartApi from '../../services/chartApi';
import { OperationButton } from '../shared/OperationButton';

interface Props {
  outline: BlogOutlineSection[];
  onRefine: (operation: string, sectionId?: string, payload?: any) => void;
  research?: any;
  sourceMappingStats?: SourceMappingStats | null;
  groundingInsights?: GroundingInsights | null;
  researchCoverage?: ResearchCoverage | null;
  sectionImages?: Record<string, string>;
  setSectionImages?: (images: Record<string, string> | ((prev: Record<string, string>) => Record<string, string>)) => void;
}

// ==================== STYLE CONSTANTS ====================
const styles = {
  container: {
    borderRadius: 16,
    overflow: 'hidden',
    border: '1px solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  } as React.CSSProperties,
  
  header: {
    padding: '12px 20px',
    background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
    color: 'white',
  } as React.CSSProperties,
  
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as React.CSSProperties,
  
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  } as React.CSSProperties,
  
  headerTitle: {
    margin: 0,
    fontSize: '16px',
    fontWeight: 700,
    color: 'white',
    letterSpacing: '-0.01em',
  } as React.CSSProperties,
  
  headerSubtitle: {
    margin: 0,
    color: 'rgba(255,255,255,0.7)',
    fontSize: '12px',
  } as React.CSSProperties,
  
  infoChip: {
    background: 'rgba(255,255,255,0.15)',
    color: 'white',
    padding: '3px 8px',
    borderRadius: 12,
    fontSize: '11px',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,
  
  buttonGroup: {
    display: 'flex',
    gap: 8,
  } as React.CSSProperties,
  
  buttonRefine: {
    background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    boxShadow: '0 2px 8px rgba(124,58,237,0.3)',
  } as React.CSSProperties,
  
  buttonAdd: {
    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    boxShadow: '0 2px 8px rgba(37,99,235,0.3)',
  } as React.CSSProperties,
  
  buttonToc: {
    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    color: 'white',
    border: 'none',
    padding: '8px 14px',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    boxShadow: '0 2px 8px rgba(245,158,11,0.3)',
  } as React.CSSProperties,
  
  addSectionForm: {
    padding: '16px 24px',
    background: '#f0f4ff',
    borderBottom: '1px solid #e5e7eb',
  } as React.CSSProperties,
  
  addSectionTitle: {
    margin: '0 0 12px',
    fontSize: '15px',
    fontWeight: 600,
    color: '#1e293b',
  } as React.CSSProperties,
  
  formColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  } as React.CSSProperties,
  
  inputFull: {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    fontSize: '14px',
    boxSizing: 'border-box',
  } as React.CSSProperties,
  
  formRow: {
    display: 'flex',
    gap: 10,
  } as React.CSSProperties,
  
  textarea: {
    flex: 1,
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    fontSize: '14px',
    resize: 'vertical',
    boxSizing: 'border-box',
  } as React.CSSProperties,
  
  formActions: {
    display: 'flex',
    gap: 8,
    alignItems: 'center',
  } as React.CSSProperties,
  
  inputNumber: {
    width: 80,
    padding: '6px 10px',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    fontSize: '14px',
  } as React.CSSProperties,
  
  labelSmall: {
    fontSize: '13px',
    color: '#6b7280',
  } as React.CSSProperties,
  
  spacer: {
    flex: 1,
  } as React.CSSProperties,
  
  buttonCancel: {
    padding: '8px 16px',
    background: '#f1f5f9',
    border: '1px solid #e2e8f0',
    borderRadius: 6,
    fontSize: '13px',
    color: '#64748b',
    cursor: 'pointer',
  } as React.CSSProperties,
  
  buttonPrimary: {
    padding: '8px 16px',
    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
    border: 'none',
    borderRadius: 6,
    fontSize: '13px',
    color: 'white',
    cursor: 'pointer',
    fontWeight: 500,
  } as React.CSSProperties,
  
  sectionRow: {
    borderBottom: '1px solid #e2e8f0',
    background: 'white',
    borderTop: '2px solid transparent',
    borderLeft: '3px solid transparent',
    borderRight: '3px solid transparent',
    transition: 'border-color 0.2s, box-shadow 0.2s',
  } as React.CSSProperties,
  
  sectionHeader: {
    padding: '12px 16px',
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    cursor: 'pointer',
    transition: 'background 0.15s, transform 0.15s',
    minHeight: 44,
  } as React.CSSProperties,
  
  sectionNumberBadge: {
    minWidth: 24,
    height: 24,
    borderRadius: 6,
    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '11px',
    fontWeight: 700,
    flexShrink: 0,
    boxShadow: '0 1px 3px rgba(37,99,235,0.3)',
  } as React.CSSProperties,
  
  sectionLabel: {
    fontSize: '10px',
    fontWeight: 700,
    color: '#94a3b8',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    flexShrink: 0,
  } as React.CSSProperties,
  
  sectionTitle: {
    flex: 1,
    minWidth: 0,
    maxWidth: '100%',
  } as React.CSSProperties,
  
  inputEdit: {
    fontSize: '14px',
    fontWeight: 600,
    border: '1px solid #3b82f6',
    borderRadius: 4,
    padding: '4px 8px',
    width: '100%',
    outline: 'none',
  } as React.CSSProperties,
  
  spanTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1e293b',
    display: 'block',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  } as React.CSSProperties,
  
  tagsContainer: {
    display: 'flex',
    gap: 6,
    flexShrink: 0,
  } as React.CSSProperties,
  
  tagWordCount: {
    background: '#eff6ff',
    color: '#2563eb',
    padding: '3px 8px',
    borderRadius: 12,
    fontSize: '11px',
    fontWeight: 600,
    whiteSpace: 'nowrap',
    border: '1px solid #dbeafe',
  } as React.CSSProperties,
  
  tagSources: {
    background: '#f0fdf4',
    color: '#16a34a',
    padding: '3px 8px',
    borderRadius: 12,
    fontSize: '11px',
    fontWeight: 600,
    whiteSpace: 'nowrap',
    border: '1px solid #dcfce7',
  } as React.CSSProperties,
  
  actionButtons: {
    display: 'flex',
    gap: 4,
    flexShrink: 0,
  } as React.CSSProperties,
  
  buttonIcon: {
    background: 'transparent',
    border: '1px solid #e2e8f0',
    borderRadius: 4,
    padding: '3px 6px',
    cursor: 'pointer',
    fontSize: '11px',
    color: '#64748b',
  } as React.CSSProperties,
  
  buttonImage: {
    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
    border: 'none',
    borderRadius: 6,
    padding: '5px 10px',
    cursor: 'pointer',
    fontSize: '11px',
    color: 'white',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,
  
  buttonChart: {
    background: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
    border: 'none',
    borderRadius: 6,
    padding: '5px 10px',
    cursor: 'pointer',
    fontSize: '11px',
    color: 'white',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,
  
  buttonLink: {
    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    border: 'none',
    borderRadius: 6,
    padding: '5px 10px',
    cursor: 'pointer',
    fontSize: '11px',
    color: 'white',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    whiteSpace: 'nowrap',
  } as React.CSSProperties,
  
  buttonMove: {
    background: 'transparent',
    border: '1px solid #e2e8f0',
    borderRadius: 4,
    padding: '3px 5px',
    fontSize: '10px',
  } as React.CSSProperties,
  
  buttonRemove: {
    background: 'transparent',
    border: '1px solid #fecaca',
    borderRadius: 4,
    padding: '3px 5px',
    cursor: 'pointer',
    fontSize: '10px',
    color: '#ef4444',
  } as React.CSSProperties,
  
  expandArrow: {
    transition: 'transform 0.2s',
    fontSize: '12px',
    color: '#94a3b8',
    flexShrink: 0,
  } as React.CSSProperties,
  
  expandedContent: {
    padding: '0 16px 12px 52px',
    background: '#fafbfc',
    borderTop: '1px solid #f1f5f9',
  } as React.CSSProperties,
  
  contentSection: {
    marginBottom: 10,
    paddingTop: 8,
  } as React.CSSProperties,
  
  contentLabel: {
    fontSize: '10px',
    fontWeight: 700,
    color: '#64748b',
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: '0.8px',
  } as React.CSSProperties,
  
  chipsContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 6,
  } as React.CSSProperties,
  
  chipKeyPoint: {
    background: '#f8fafc',
    color: '#334155',
    padding: '6px 10px',
    borderRadius: 8,
    fontSize: '12px',
    lineHeight: 1.5,
    maxWidth: '100%',
    border: '1px solid #e2e8f0',
  } as React.CSSProperties,
  
  chipSubheading: {
    background: '#eff6ff',
    color: '#1e40af',
    padding: '6px 10px',
    borderRadius: 8,
    fontSize: '12px',
    fontWeight: 500,
    border: '1px solid #dbeafe',
  } as React.CSSProperties,
  
  chipKeyword: {
    background: '#fef3c7',
    color: '#92400e',
    padding: '4px 8px',
    borderRadius: 8,
    fontSize: '11px',
    fontWeight: 600,
    border: '1px solid #fde68a',
  } as React.CSSProperties,
  
  chipSource: {
    background: 'white',
    border: '1px solid #e2e8f0',
    padding: '4px 10px',
    borderRadius: 8,
    fontSize: '11px',
    color: '#475569',
    maxWidth: 200,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
  } as React.CSSProperties,
  
  chipMore: {
    background: '#f1f5f9',
    padding: '4px 10px',
    borderRadius: 8,
    fontSize: '11px',
    color: '#64748b',
    border: '1px solid #e2e8f0',
  } as React.CSSProperties,
  
  imageContainer: {
    border: '1px solid #e2e8f0',
    borderRadius: 8,
    overflow: 'hidden',
    maxWidth: 480,
    backgroundColor: 'white',
  } as React.CSSProperties,
  
  image: {
    width: '100%',
    height: 'auto',
    display: 'block',
  } as React.CSSProperties,
  
  actionButtonsRow: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: 6,
    paddingTop: 4,
  } as React.CSSProperties,
  
  buttonLinksRow: {
    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    color: '#fff',
    border: 'none',
    padding: '6px 12px',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    boxShadow: '0 1px 4px rgba(16,185,129,0.3)',
  } as React.CSSProperties,
  
  buttonImageRow: {
    background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
    color: '#fff',
    border: 'none',
    padding: '6px 12px',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: 4,
    boxShadow: '0 1px 4px rgba(37,99,235,0.3)',
  } as React.CSSProperties,
  
  footer: {
    padding: '14px 24px',
    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    borderTop: '1px solid #a78bfa',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    boxShadow: '0 -2px 8px rgba(99,102,241,0.2)',
  } as React.CSSProperties,
  
  footerText: {
    fontSize: '13px',
    color: 'white',
    fontWeight: 600,
    letterSpacing: '0.3px',
    textShadow: '0 1px 2px rgba(0,0,0,0.2)',
  } as React.CSSProperties,
  
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  } as React.CSSProperties,
  
  modalContent: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 28,
    maxWidth: 560,
    width: '90%',
    boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
    border: '1px solid #e5e7eb',
  } as React.CSSProperties,
  
  modalTitle: {
    margin: '0 0 8px',
    fontSize: '18px',
    fontWeight: 700,
    color: '#1e293b',
  } as React.CSSProperties,
  
  modalSubtitle: {
    margin: '0 0 20px',
    color: '#64748b',
    fontSize: '13px',
  } as React.CSSProperties,
  
  modalTextarea: {
    width: '100%',
    minHeight: 100,
    padding: 12,
    border: '1px solid #e2e8f0',
    borderRadius: 8,
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
    boxSizing: 'border-box',
  } as React.CSSProperties,
  
  tocModalContent: {
    backgroundColor: 'white',
    borderRadius: 16,
    padding: 0,
    maxWidth: 640,
    width: '90%',
    maxHeight: '80vh',
    overflow: 'hidden',
    boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
    border: '1px solid #e5e7eb',
  } as React.CSSProperties,
  
  tocHeader: {
    padding: '20px 24px',
    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    color: 'white',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as React.CSSProperties,
  
  tocTitle: {
    margin: 0,
    fontSize: '18px',
    fontWeight: 700,
    color: 'white',
  } as React.CSSProperties,
  
  tocCloseButton: {
    background: 'rgba(255,255,255,0.2)',
    border: 'none',
    borderRadius: 8,
    width: 32,
    height: 32,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    fontSize: '18px',
    color: 'white',
    transition: 'background 0.2s',
  } as React.CSSProperties,
  
  tocList: {
    padding: '24px',
    maxHeight: '60vh',
    overflowY: 'auto',
  } as React.CSSProperties,
  
  tocItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 12,
    padding: '12px 0',
    borderBottom: '1px solid #f1f5f9',
  } as React.CSSProperties,
  
  tocItemNumber: {
    minWidth: 28,
    height: 28,
    borderRadius: 8,
    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: 700,
    flexShrink: 0,
  } as React.CSSProperties,
  
  tocItemContent: {
    flex: 1,
    minWidth: 0,
  } as React.CSSProperties,
  
  tocItemHeading: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#1e293b',
    marginBottom: 4,
  } as React.CSSProperties,
  
  tocItemMeta: {
    fontSize: '12px',
    color: '#64748b',
    display: 'flex',
    gap: 8,
    alignItems: 'center',
  } as React.CSSProperties,
  
  tocMetaChip: {
    background: '#f3f4f6',
    padding: '2px 6px',
    borderRadius: 8,
    fontSize: '11px',
    fontWeight: 500,
    color: '#4b5563',
  } as React.CSSProperties,
  
  modalActions: {
    display: 'flex',
    gap: 8,
    justifyContent: 'flex-end',
    marginTop: 16,
  } as React.CSSProperties,
  
  buttonModalCancel: {
    padding: '8px 16px',
    background: '#f1f5f9',
    color: '#64748b',
    border: '1px solid #e2e8f0',
    borderRadius: 8,
    fontSize: '13px',
    cursor: 'pointer',
  } as React.CSSProperties,
  
  buttonModalPrimary: {
    padding: '8px 16px',
    color: 'white',
    border: 'none',
    borderRadius: 8,
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(124,58,237,0.3)',
  } as React.CSSProperties,
} as const;

const EnhancedOutlineEditor: React.FC<Props> = ({
  outline,
  onRefine,
  research,
  sourceMappingStats,
  groundingInsights,
  researchCoverage,
  sectionImages = {},
  setSectionImages
}) => {
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [hoveredSection, setHoveredSection] = useState<string | null>(null);
  const [showAddSection, setShowAddSection] = useState(false);
  const [imageModalState, setImageModalState] = useState<{ open: boolean; sectionId?: string }>(() => ({ open: false }));
  const [chartModalState, setChartModalState] = useState<{ open: boolean; sectionId?: string }>(() => ({ open: false }));
  const [linkModalState, setLinkModalState] = useState<{ open: boolean; sectionId?: string }>(() => ({ open: false }));
  const [tocModalOpen, setTocModalOpen] = useState(false);
  const [newSectionData, setNewSectionData] = useState({
    heading: '',
    subheadings: '',
    key_points: '',
    target_words: 300
  });
  const [showRefineModal, setShowRefineModal] = useState(false);
  const [refineFeedback, setRefineFeedback] = useState('');
  const [isRefining, setIsRefining] = useState(false);

  const toggleExpanded = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const handleRename = (sectionId: string, newHeading: string) => {
    if (newHeading.trim()) {
      onRefine('rename', sectionId, { heading: newHeading.trim() });
    }
    setEditingSection(null);
  };

  const handleMove = (sectionId: string, direction: 'up' | 'down') => {
    onRefine('move', sectionId, { direction });
  };

  const handleAddSection = () => {
    if (newSectionData.heading.trim()) {
      const subheadings = newSectionData.subheadings
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      const keyPoints = newSectionData.key_points
        .split('\n')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      onRefine('add', undefined, {
        heading: newSectionData.heading.trim(),
        subheadings,
        key_points: keyPoints,
        target_words: newSectionData.target_words
      });

      setNewSectionData({ heading: '', subheadings: '', key_points: '', target_words: 300 });
      setShowAddSection(false);
    }
  };

  const handleRefineOutline = async () => {
    if (!refineFeedback.trim()) {
      alert('Please provide feedback on how you would like to refine the outline.');
      return;
    }
    setIsRefining(true);
    try {
      await onRefine('refine', undefined, { feedback: refineFeedback.trim() });
      setRefineFeedback('');
      setShowRefineModal(false);
      const toast = document.createElement('div');
      toast.style.cssText = 'position:fixed;top:20px;right:20px;padding:16px 24px;border-radius:8px;background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:white;font-weight:500;z-index:10000;box-shadow:0 4px 12px rgba(0,0,0,0.15);';
      toast.textContent = 'Outline refined successfully!';
      document.body.appendChild(toast);
      setTimeout(() => document.body.removeChild(toast), 3000);
    } catch (error) {
      console.error('Failed to refine outline:', error);
      alert('Failed to refine outline. Please try again.');
    } finally {
      setIsRefining(false);
    }
  };

  const getTotalWords = () => outline.reduce((total, section) => total + (section.target_words || 0), 0);

  const getSectionBackground = (sectionId: string) => {
    const isExpanded = expandedSections.has(sectionId);
    const isHovered = hoveredSection === sectionId;
    if (isExpanded) return '#f8fafc';
    if (isHovered) return '#fafbfc';
    return 'white';
  };

  const getSectionBorderStyle = (sectionId: string) => {
    const isExpanded = expandedSections.has(sectionId);
    const isHovered = hoveredSection === sectionId;
    if (isExpanded) {
      return {
        borderTopColor: '#8b5cf6',
        borderLeftColor: '#8b5cf6',
        borderRightColor: '#8b5cf6',
        boxShadow: '0 2px 8px rgba(139,92,246,0.15)',
      };
    }
    if (isHovered) {
      return {
        borderTopColor: '#a78bfa',
        borderLeftColor: '#a78bfa',
        borderRightColor: '#a78bfa',
        boxShadow: '0 1px 4px rgba(167,139,250,0.1)',
      };
    }
    return {
      borderTopColor: 'transparent',
      borderLeftColor: 'transparent',
      borderRightColor: 'transparent',
      boxShadow: 'none',
    };
  };

  const getMoveButtonStyle = (disabled: boolean) => ({
    ...styles.buttonMove,
    cursor: disabled ? 'not-allowed' : 'pointer',
    color: disabled ? '#cbd5e1' : '#64748b',
    opacity: disabled ? 0.4 : 1,
  });

  const getModalButtonStyle = (disabled: boolean) => ({
    ...styles.buttonModalPrimary,
    background: disabled ? '#94a3b8' : 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
    boxShadow: disabled ? 'none' : '0 2px 8px rgba(124,58,237,0.3)',
    cursor: disabled ? 'not-allowed' : 'pointer',
  });

  const getImageSrc = (imageData: string) => {
    if (!imageData) return '';
    if (imageData.startsWith('http') || imageData.startsWith('/api/') || imageData.startsWith('data:')) {
      return imageData;
    }
    return `data:image/png;base64,${imageData}`;
  };

  const getSectionContext = (sectionId?: string) => {
    if (!sectionId) return undefined;
    const sec = outline.find(s => s.id === sectionId);
    if (!sec) return undefined;
    return { title: sec.heading, section: sec, outline, research, sectionId };
  };

  const getSectionText = (sectionId?: string) => {
    if (!sectionId) return '';
    const sec = outline.find(s => s.id === sectionId);
    if (!sec) return '';
    const points = sec.key_points?.join('\n') || '';
    return points ? `${sec.heading}\n${points}` : sec.heading || '';
  };

  const getSectionDefaultText = (sectionId?: string) => {
    if (!sectionId) return '';
    const sec = outline.find(s => s.id === sectionId);
    if (!sec) return '';
    const points = sec.key_points?.join('. ') || '';
    return `${sec.heading}. ${points}`;
  };

  const getSectionHeading = (sectionId?: string) => {
    if (!sectionId) return '';
    const sec = outline.find(s => s.id === sectionId);
    return sec?.heading || '';
  };

  return (
    <>
    <div style={styles.container}>
      {imageModalState.open && (
        <ImageGeneratorModal
          isOpen={imageModalState.open}
          onClose={() => setImageModalState({ open: false })}
          defaultPrompt={getSectionHeading(imageModalState.sectionId)}
          context={getSectionContext(imageModalState.sectionId)}
          onImageGenerated={(imageBase64, sectionId) => { 
            if (sectionId && setSectionImages) { 
              setSectionImages((prev: Record<string, string>) => ({ ...prev, [sectionId]: imageBase64 })); 
            } 
          }}
        />
      )}
      {linkModalState.open && (
        <LinkSearchModal
          isOpen={linkModalState.open}
          onClose={() => setLinkModalState({ open: false })}
          sectionHeading={getSectionHeading(linkModalState.sectionId)}
          sectionText={getSectionText(linkModalState.sectionId)}
          context={getSectionContext(linkModalState.sectionId)}
          onRewordAccept={(rewordedText, sectionId) => { 
            if (sectionId) { 
              onRefine('update-section-content', sectionId, { content: rewordedText }); 
            } 
          }}
        />
      )}
      {chartModalState.open && (
        <ChartGeneratorModal
          isOpen={chartModalState.open}
          onClose={() => setChartModalState({ open: false })}
          defaultText={getSectionDefaultText(chartModalState.sectionId)}
          context={getSectionContext(chartModalState.sectionId)}
          onChartGenerated={async (result: ChartGenerateResponse & { sectionId?: string }) => { 
            if (result.sectionId && setSectionImages && result.preview_url) { 
              const authUrl = await chartApi.getPreviewUrl(result.preview_url); 
              setSectionImages((prev: Record<string, string>) => ({ ...prev, [result.sectionId!]: authUrl })); 
            } 
          }}
        />
      )}

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.headerLeft}>
            <h2 style={styles.headerTitle}>Blog Outline</h2>
            <span style={styles.infoChip}>{outline.length} sections</span>
            <span style={styles.infoChip}>{getTotalWords()} words</span>
            <OutlineIntelligenceChips sections={outline} sourceMappingStats={sourceMappingStats} groundingInsights={groundingInsights} researchCoverage={researchCoverage} />
          </div>
          <div style={styles.buttonGroup}>
            <button onClick={() => setTocModalOpen(true)} style={styles.buttonToc} title="View Table of Contents">
              📋 ToC
            </button>
            <button onClick={() => setShowRefineModal(true)} style={styles.buttonRefine}>
              Refine
            </button>
            <button onClick={() => setShowAddSection(!showAddSection)} style={styles.buttonAdd}>
              + Add Section
            </button>
          </div>
        </div>
      </div>

      {/* Add Section Form */}
      {showAddSection && (
        <div style={styles.addSectionForm}>
          <h3 style={styles.addSectionTitle}>Add New Section</h3>
          <div style={styles.formColumn}>
            <input 
              type="text" 
              value={newSectionData.heading} 
              onChange={e => setNewSectionData({...newSectionData, heading: e.target.value})} 
              placeholder="Section title..." 
              style={styles.inputFull} 
            />
            <div style={styles.formRow}>
              <textarea 
                value={newSectionData.subheadings} 
                onChange={e => setNewSectionData({...newSectionData, subheadings: e.target.value})} 
                placeholder="Subheadings (one per line)" 
                rows={2} 
                style={styles.textarea} 
              />
              <textarea 
                value={newSectionData.key_points} 
                onChange={e => setNewSectionData({...newSectionData, key_points: e.target.value})} 
                placeholder="Key points (one per line)" 
                rows={2} 
                style={styles.textarea} 
              />
            </div>
            <div style={styles.formActions}>
              <input 
                type="number" 
                value={newSectionData.target_words} 
                onChange={e => setNewSectionData({...newSectionData, target_words: parseInt(e.target.value) || 300})} 
                min={100} 
                max={2000} 
                style={styles.inputNumber} 
              />
              <span style={styles.labelSmall}>target words</span>
              <div style={styles.spacer} />
              <button 
                onClick={() => setShowAddSection(false)} 
                style={styles.buttonCancel}
              >
                Cancel
              </button>
              <button 
                onClick={handleAddSection} 
                style={styles.buttonPrimary}
              >
                Add Section
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Outline Sections */}
      <div>
        {outline.map((section, index) => {
          const isExpanded = expandedSections.has(section.id);
          const sectionBg = getSectionBackground(section.id);
          const sectionBorder = getSectionBorderStyle(section.id);
          
          return (
            <div key={section.id} style={{...styles.sectionRow, ...sectionBorder}}>
              {/* Section Header Row */}
              <div
                style={{
                  ...styles.sectionHeader,
                  background: sectionBg,
                }}
                onMouseEnter={() => setHoveredSection(section.id)}
                onMouseLeave={() => setHoveredSection(null)}
                onClick={() => toggleExpanded(section.id)}
              >
                {/* Section Number Badge */}
                <div style={styles.sectionNumberBadge}>
                  {index + 1}
                </div>

                {/* Section Label */}
                <span style={styles.sectionLabel}>SECTION</span>

                {/* Section Title */}
                <div style={styles.sectionTitle}>
                  {editingSection === section.id ? (
                    <input
                      type="text"
                      defaultValue={section.heading}
                      onBlur={e => handleRename(section.id, e.target.value)}
                      onKeyDown={e => { if (e.key === 'Enter') handleRename(section.id, e.currentTarget.value); }}
                      autoFocus
                      onClick={e => e.stopPropagation()}
                      style={styles.inputEdit}
                    />
                  ) : (
                    <span style={styles.spanTitle} title={section.heading}>
                      {section.heading}
                    </span>
                  )}
                </div>

                {/* Tags */}
                <div style={styles.tagsContainer}>
                  <span style={styles.tagWordCount}>
                    {section.target_words || 300}w
                  </span>
                  {section.references && section.references.length > 0 && (
                    <span style={styles.tagSources}>
                      {section.references.length} src
                    </span>
                  )}
                </div>

                {/* Action Buttons */}
                <div style={styles.actionButtons} onClick={e => e.stopPropagation()}>
                  <button 
                    onClick={() => setEditingSection(section.id)} 
                    title="Rename section" 
                    style={styles.buttonIcon}
                  >
                    ✏️
                  </button>
                  <OperationButton
                    operation={{
                      provider: "stability",
                      operation_type: "image_generation",
                    }}
                    label="🖼️ Image"
                    size="small"
                    variant="contained"
                    showCost={true}
                    checkOnHover={true}
                    checkOnMount={false}
                    onClick={() => setImageModalState({ open: true, sectionId: section.id })}
                    sx={{
                      background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                      color: 'white',
                      fontSize: '11px',
                      fontWeight: 500,
                      textTransform: 'none',
                      minWidth: 'auto',
                      minHeight: 'auto',
                      padding: '5px 10px',
                      borderRadius: '6px',
                      boxShadow: 'none',
                      lineHeight: 1.4,
                      '&:hover': {
                        background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                      },
                    }}
                  />
                  <button 
                    onClick={() => setChartModalState({ open: true, sectionId: section.id })} 
                    title="Generate chart from section data" 
                    style={styles.buttonChart}
                  >
                    📊 Chart
                  </button>
                  <button 
                    onClick={() => setLinkModalState({ open: true, sectionId: section.id })} 
                    title="Find internal and external links for SEO" 
                    style={styles.buttonLink}
                  >
                    🔗 Links
                  </button>
                  <button 
                    onClick={() => handleMove(section.id, 'up')} 
                    disabled={index === 0} 
                    style={getMoveButtonStyle(index === 0)}
                    title="Move section up"
                  >
                    ▲
                  </button>
                  <button 
                    onClick={() => handleMove(section.id, 'down')} 
                    disabled={index === outline.length - 1} 
                    style={getMoveButtonStyle(index === outline.length - 1)}
                    title="Move section down"
                  >
                    ▼
                  </button>
                  <button 
                    onClick={() => { if (window.confirm(`Remove "${section.heading}"?`)) onRefine('remove', section.id); }} 
                    style={styles.buttonRemove}
                  >
                    ✕
                  </button>
                </div>

                {/* Expand Arrow */}
                <div style={{
                  ...styles.expandArrow,
                  transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                }}>
                  ▼
                </div>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div style={styles.expandedContent}>
                  {/* Key Points as compact chips */}
                  {section.key_points && section.key_points.length > 0 && (
                    <div style={styles.contentSection}>
                      <div style={styles.contentLabel}>Key Points</div>
                      <div style={styles.chipsContainer}>
                        {section.key_points.map((point, i) => (
                          <span key={i} style={styles.chipKeyPoint}>
                            {point}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Subheadings */}
                  {section.subheadings && section.subheadings.length > 0 && (
                    <div style={styles.contentSection}>
                      <div style={styles.contentLabel}>Subheadings</div>
                      <div style={styles.chipsContainer}>
                        {section.subheadings.map((sub, i) => (
                          <span key={i} style={styles.chipSubheading}>
                            {sub}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Keywords */}
                  {section.keywords && section.keywords.length > 0 && (
                    <div style={styles.contentSection}>
                      <div style={styles.contentLabel}>SEO Keywords</div>
                      <div style={styles.chipsContainer}>
                        {section.keywords.map((kw, i) => (
                          <span key={i} style={styles.chipKeyword}>
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* References */}
                  {section.references && section.references.length > 0 && (
                    <div style={styles.contentSection}>
                      <div style={styles.contentLabel}>
                        Sources ({section.references.length})
                      </div>
                      <div style={styles.chipsContainer}>
                        {section.references.slice(0, 4).map((ref, i) => (
                          <span key={i} style={styles.chipSource}>
                            {ref.title || `Source ${i + 1}`}
                          </span>
                        ))}
                        {section.references.length > 4 && (
                          <span style={styles.chipMore}>
                            +{section.references.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Generated Image */}
                  {sectionImages[section.id] && (
                    <div style={styles.contentSection}>
                      <div style={styles.contentLabel}>Generated Image</div>
                      <div style={styles.imageContainer}>
                        <img
                          src={getImageSrc(sectionImages[section.id])}
                          alt={section.heading}
                          style={styles.image}
                        />
                      </div>
                    </div>
                  )}

                  {/* Action buttons row */}
                  <div style={styles.actionButtonsRow}>
                    <button 
                      onClick={e => { e.stopPropagation(); setLinkModalState({ open: true, sectionId: section.id }); }} 
                      title="Find internal & external links for SEO" 
                      style={styles.buttonLinksRow}
                    >
                      🔗 Links
                    </button>
                    <span onClick={e => e.stopPropagation()}>
                      <OperationButton
                        operation={{
                          provider: "stability",
                          operation_type: "image_generation",
                        }}
                        label="🖼️ Image"
                        size="small"
                        variant="contained"
                        showCost={true}
                        checkOnHover={true}
                        checkOnMount={false}
                        onClick={() => setImageModalState({ open: true, sectionId: section.id })}
                        sx={{
                          background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                          color: '#fff',
                          fontSize: '12px',
                          fontWeight: 500,
                          textTransform: 'none',
                          minWidth: 'auto',
                          minHeight: 'auto',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          boxShadow: '0 1px 4px rgba(37,99,235,0.3)',
                          lineHeight: 1.4,
                          '&:hover': {
                            background: 'linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%)',
                          },
                        }}
                      />
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <span style={styles.footerText}>💡 Click a section to expand and view details</span>
      </div>
    </div>

    {/* Table of Contents Modal */}
    {tocModalOpen && (
      <div 
        style={styles.modalOverlay} 
        onClick={() => setTocModalOpen(false)}
      >
        <div 
          style={styles.tocModalContent} 
          onClick={e => e.stopPropagation()}
        >
          <div style={styles.tocHeader}>
            <h2 style={styles.tocTitle}>📋 Table of Contents</h2>
            <button 
              onClick={() => setTocModalOpen(false)} 
              style={styles.tocCloseButton}
              title="Close"
            >
              ✕
            </button>
          </div>
          <div style={styles.tocList}>
            {outline.map((section, index) => (
              <div key={section.id} style={styles.tocItem}>
                <div style={styles.tocItemNumber}>
                  {index + 1}
                </div>
                <div style={styles.tocItemContent}>
                  <div style={styles.tocItemHeading}>
                    {section.heading}
                  </div>
                  <div style={styles.tocItemMeta}>
                    <span style={styles.tocMetaChip}>{section.target_words || 300} words</span>
                    {section.references && section.references.length > 0 && (
                      <span style={styles.tocMetaChip}>{section.references.length} sources</span>
                    )}
                    {section.key_points && section.key_points.length > 0 && (
                      <span style={styles.tocMetaChip}>{section.key_points.length} key points</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )}

    {/* Refine Outline Modal */}
    {showRefineModal && (
      <div 
        style={styles.modalOverlay} 
        onClick={() => !isRefining && setShowRefineModal(false)}
      >
        <div 
          style={styles.modalContent} 
          onClick={e => e.stopPropagation()}
        >
          <h2 style={styles.modalTitle}>Refine Outline</h2>
          <p style={styles.modalSubtitle}>Describe how you want to improve the outline structure</p>
          <textarea 
            value={refineFeedback} 
            onChange={e => setRefineFeedback(e.target.value)} 
            placeholder="E.g., Add a section about best practices, merge sections 2 and 3, expand the introduction..." 
            style={styles.modalTextarea} 
          />
          <div style={styles.modalActions}>
            <button 
              onClick={() => { setShowRefineModal(false); setRefineFeedback(''); }} 
              disabled={isRefining} 
              style={{
                ...styles.buttonModalCancel,
                cursor: isRefining ? 'not-allowed' : 'pointer',
              }}
            >
              Cancel
            </button>
            <button 
              onClick={handleRefineOutline} 
              disabled={isRefining || !refineFeedback.trim()} 
              style={getModalButtonStyle(isRefining || !refineFeedback.trim())}
            >
              {isRefining ? '⏳ Refining...' : '✨ Refine Outline'}
            </button>
          </div>
        </div>
      </div>
    )}
    </>
  );
};

export default EnhancedOutlineEditor;
