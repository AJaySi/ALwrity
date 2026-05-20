import React from 'react';
import { Dialog, DialogContent, IconButton, Typography, Box, Tooltip } from '@mui/material';
import { Close as CloseIcon, Print as PrintIcon } from '@mui/icons-material';

interface BlogPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  introduction: string;
  sections: Array<{
    title: string;
    content: string;
  }>;
  convertMarkdownToHTML: (md: string) => string;
}

export const BlogPreviewModal: React.FC<BlogPreviewModalProps> = ({
  isOpen,
  onClose,
  title,
  introduction,
  sections,
  convertMarkdownToHTML,
}) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <>
      <Dialog
        open={isOpen}
        onClose={onClose}
        maxWidth="md"
        fullWidth
        fullScreen
        sx={{
          '& .MuiDialog-paper': {
            bgcolor: '#fafbfc',
          },
        }}
      >
        {/* Header */}
        <Box
          sx={{
            position: 'sticky',
            top: 0,
            bgcolor: 'white',
            borderBottom: '1px solid #e2e8f0',
            px: 3,
            py: 2,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            zIndex: 1000,
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#1e293b' }}>
            👁️ Blog Preview
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Print or Save as PDF">
              <IconButton onClick={handlePrint} sx={{ color: '#4f46e5' }}>
                <PrintIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Return to Editing">
              <IconButton onClick={onClose} sx={{ color: '#64748b' }}>
                <CloseIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Content */}
        <DialogContent
          sx={{
            px: { xs: 2, md: 4 },
            py: 4,
            maxWidth: '800px',
            mx: 'auto',
            bgcolor: 'white',
            borderRadius: 2,
            my: 2,
            boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
          }}
        >
          {/* Blog Title */}
          <Typography
            variant="h1"
            sx={{
              fontSize: { xs: '2rem', md: '2.5rem' },
              fontWeight: 800,
              color: '#1e293b',
              mb: 3,
              lineHeight: 1.2,
              fontFamily: 'Georgia, serif',
            }}
          >
            {title}
          </Typography>

          {/* Introduction */}
          {introduction && introduction.trim() && (
            <Box
              sx={{
                mb: 4,
                pb: 4,
                borderBottom: '2px solid #e5e7eb',
              }}
            >
              <div
                style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: '1.125rem',
                  lineHeight: 1.8,
                  color: '#475569',
                }}
                dangerouslySetInnerHTML={{ __html: convertMarkdownToHTML(introduction) }}
              />
            </Box>
          )}

          {/* Sections */}
          {sections.map((section, index) => (
            <Box
              key={section.title || index}
              sx={{
                mb: 4,
                pb: 4,
                borderBottom: index < sections.length - 1 ? '1px solid #f1f5f9' : 'none',
              }}
            >
              {/* Section Title */}
              <Typography
                variant="h2"
                sx={{
                  fontSize: { xs: '1.5rem', md: '1.75rem' },
                  fontWeight: 700,
                  color: '#1e293b',
                  mb: 2,
                  mt: 3,
                  fontFamily: 'Georgia, serif',
                  borderBottom: '1px solid #e5e7eb',
                  pb: 1,
                }}
              >
                {section.title}
              </Typography>

              {/* Section Content */}
              <div
                style={{
                  fontFamily: 'Georgia, serif',
                  fontSize: '1rem',
                  lineHeight: 1.8,
                  color: '#334155',
                }}
                dangerouslySetInnerHTML={{ __html: convertMarkdownToHTML(section.content) }}
              />
            </Box>
          ))}
        </DialogContent>

        {/* Footer */}
        <Box
          sx={{
            position: 'sticky',
            bottom: 0,
            bgcolor: 'white',
            borderTop: '1px solid #e2e8f0',
            px: 3,
            py: 2,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            zIndex: 1000,
          }}
        >
          <Typography variant="body2" sx={{ color: '#64748b', fontSize: '0.875rem' }}>
            {sections.length} sections &bull; Preview Mode
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography variant="body2" sx={{ color: '#94a3b8', fontSize: '0.75rem' }}>
              Press Ctrl+P to print
            </Typography>
          </Box>
        </Box>
      </Dialog>

      {/* Print Styles */}
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          .MuiDialogContent-root, .MuiDialogContent-root * {
            visibility: visible;
          }
          .MuiDialogContent-root {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            box-shadow: none !important;
            margin: 0 !important;
            padding: 20px !important;
          }
          /* Hide UI elements */
          .MuiDialog-paper > div:first-child,
          .MuiDialog-paper > div:last-child {
            display: none !important;
          }
          /* Optimize for print */
          h1, h2, h3 {
            page-break-after: avoid;
          }
          img {
            max-width: 100% !important;
            page-break-inside: avoid;
          }
        }
      `}</style>
    </>
  );
};

export default BlogPreviewModal;
