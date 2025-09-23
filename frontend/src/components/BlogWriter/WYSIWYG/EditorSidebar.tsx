import React from 'react';
import { Paper, Button, Chip } from '@mui/material';
import {
  Add as AddIcon,
  AutoAwesome as AutoAwesomeIcon,
  BarChart as BarChartIcon,
  Hub as HubIcon,
  GpsFixed as GpsFixedIcon,
} from '@mui/icons-material';

interface EditorSidebarProps {
  sections: any[];
  totalWords: number;
}

const EditorSidebar: React.FC<EditorSidebarProps> = ({ sections, totalWords }) => {
  return (
    <div className="sticky top-24 hidden lg:block">
      <Paper elevation={2} className="p-4 rounded-xl shadow-lg border border-gray-100">
        <h3 className="font-bold text-lg mb-4 text-gray-700">Editor's Toolkit</h3>
        <div className="space-y-3 mb-6">
          <Button 
            fullWidth 
            variant="contained" 
            startIcon={<AutoAwesomeIcon />} 
            className="!bg-gradient-to-r !from-indigo-500 !to-purple-500 !capitalize !font-semibold !rounded-lg"
          >
            ALwrity it
          </Button>
          <Button 
            fullWidth 
            variant="outlined" 
            startIcon={<AddIcon />} 
            className="!capitalize !rounded-lg"
          >
            Add Section
          </Button>
        </div>
        <div className="mb-6">
          <h4 className="font-semibold text-sm text-gray-600 mb-3">Outline</h4>
          <ul className="space-y-2">
            {sections.map(section => (
              <li key={section.id}>
                <a 
                  href={`#section-${section.id}`} 
                  className="text-sm text-gray-500 hover:text-indigo-600 transition-colors flex items-start"
                >
                  <span className="mr-2 font-semibold">{section.id}.</span>
                  <span className="flex-1">{section.title}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
        <div className="border-t pt-4">
          <h4 className="font-semibold text-sm text-gray-600 mb-3">SuperPowers</h4>
          <div className="flex flex-wrap gap-2">
            <Chip 
              icon={<BarChartIcon />} 
              label="Research" 
              size="small" 
              clickable 
              variant="outlined" 
            />
            <Chip 
              icon={<HubIcon />} 
              label="Source Mapping" 
              size="small" 
              clickable 
              variant="outlined" 
            />
            <Chip 
              icon={<GpsFixedIcon />} 
              label="Grounding" 
              size="small" 
              clickable 
              variant="outlined" 
            />
          </div>
        </div>
      </Paper>
      <div className="text-center text-xs text-gray-400 mt-4">
        <span>{sections.length} sections</span> &bull; <span>{totalWords} words total</span>
      </div>
    </div>
  );
};

export default EditorSidebar;
