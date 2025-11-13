import React from 'react';
import { TextField, Tooltip, IconButton, InputAdornment, Box, Typography } from '@mui/material';
import { InfoOutlined } from '@mui/icons-material';

interface TooltipContent {
  title: string;
  description: string;
  examples?: string[];
}

interface FormFieldWithTooltipProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  placeholder?: string;
  helperText?: string;
  required?: boolean;
  multiline?: boolean;
  rows?: number;
  type?: string;
  tooltip: TooltipContent;
  sx?: any;
  inputProps?: any;
}

export const FormFieldWithTooltip: React.FC<FormFieldWithTooltipProps> = ({
  label,
  value,
  onChange,
  placeholder,
  helperText,
  required = false,
  multiline = false,
  rows,
  type,
  tooltip,
  sx,
  inputProps,
}) => {
  return (
    <TextField
      fullWidth
      label={label}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      helperText={helperText}
      required={required}
      multiline={multiline}
      rows={rows}
      type={type}
      sx={sx}
      InputProps={{
        ...inputProps,
        endAdornment: (
          <InputAdornment position="end">
            <Tooltip
              title={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    {tooltip.title}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    {tooltip.description}
                  </Typography>
                  {tooltip.examples && tooltip.examples.length > 0 && (
                    <>
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                        Examples:
                      </Typography>
                      <Typography variant="body2" component="div">
                        {tooltip.examples.map((example, index) => (
                          <React.Fragment key={index}>
                            • {example}
                            {index < tooltip.examples!.length - 1 && <br />}
                          </React.Fragment>
                        ))}
                      </Typography>
                    </>
                  )}
                </Box>
              }
              arrow
              placement="top"
            >
              <IconButton size="small" edge="end">
                <InfoOutlined fontSize="small" />
              </IconButton>
            </Tooltip>
          </InputAdornment>
        ),
      }}
    />
  );
};

