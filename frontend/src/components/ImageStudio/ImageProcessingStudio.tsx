import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Stack,
} from '@mui/material';
import CompressIcon from '@mui/icons-material/Compress';
import TransformIcon from '@mui/icons-material/Transform';
import AspectRatioIcon from '@mui/icons-material/AspectRatio';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import { ImageStudioLayout } from './ImageStudioLayout';
import { FormatConverterTab } from './ImageProcessingStudio/FormatConverterTab';
import { CompressionTab } from './ImageProcessingStudio/CompressionTab';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`processing-tabpanel-${index}`}
      aria-labelledby={`processing-tab-${index}`}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
};

export const ImageProcessingStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <ImageStudioLayout>
      <Paper
        elevation={0}
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          background: 'rgba(15,23,42,0.7)',
          borderRadius: 4,
          border: '1px solid rgba(255,255,255,0.08)',
          p: { xs: 2, md: 3 },
          backdropFilter: 'blur(20px)',
        }}
      >
        <Stack spacing={2} mb={2}>
          <Typography
            variant="h4"
            fontWeight={800}
            sx={{
              background: 'linear-gradient(90deg, #ede9fe, #c7d2fe)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Image Processing Studio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            All-in-one toolkit for compression and format conversion, with resizing and watermarking on the roadmap.
          </Typography>
        </Stack>

        <Box sx={{ borderBottom: 1, borderColor: 'rgba(255,255,255,0.1)' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            sx={{
              '& .MuiTab-root': {
                color: 'rgba(255,255,255,0.6)',
                textTransform: 'none',
                fontWeight: 600,
                minHeight: 64,
                '&.Mui-selected': {
                  color: '#667eea',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: '#667eea',
              },
            }}
          >
            <Tab
              icon={<CompressIcon />}
              iconPosition="start"
              label="Compression"
              id="processing-tab-0"
              aria-controls="processing-tabpanel-0"
            />
            <Tab
              icon={<TransformIcon />}
              iconPosition="start"
              label="Format Converter"
              id="processing-tab-1"
              aria-controls="processing-tabpanel-1"
            />
            <Tab
              icon={<AspectRatioIcon />}
              iconPosition="start"
              label="Resizer"
              id="processing-tab-2"
              aria-controls="processing-tabpanel-2"
              disabled
            />
            <Tab
              icon={<WaterDropIcon />}
              iconPosition="start"
              label="Watermark"
              id="processing-tab-3"
              aria-controls="processing-tabpanel-3"
              disabled
            />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <CompressionTab />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <FormatConverterTab />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              Resizer & Cropper - Roadmap
            </Typography>
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary">
              Watermark Studio - Roadmap
            </Typography>
          </Box>
        </TabPanel>
      </Paper>
    </ImageStudioLayout>
  );
};
