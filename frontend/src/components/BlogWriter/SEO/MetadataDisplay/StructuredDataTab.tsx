/**
 * Structured Data Tab Component
 * 
 * Displays and allows editing of JSON-LD structured data including:
 * - Article schema
 * - Author information
 * - Publisher details
 * - Publication dates
 * - Keywords and categories
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Paper,
  Grid,
  IconButton,
  Tooltip,
  InputAdornment,
  Alert,
  Card,
  CardContent,
  Divider,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Check as CheckIcon,
  Code as CodeIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  CalendarToday as CalendarIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon
} from '@mui/icons-material';

interface StructuredDataTabProps {
  metadata: any;
  onMetadataEdit: (field: string, value: any) => void;
  onCopyToClipboard: (text: string, itemId: string) => void;
  copiedItems: Set<string>;
}

export const StructuredDataTab: React.FC<StructuredDataTabProps> = ({
  metadata,
  onMetadataEdit,
  onCopyToClipboard,
  copiedItems
}) => {
  const [showRawJson, setShowRawJson] = useState(false);
  
  const handleTextFieldChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    onMetadataEdit(field, event.target.value);
  };

  const handleNestedFieldChange = (parentField: string, childField: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const currentValue = metadata[parentField] || {};
    onMetadataEdit(parentField, {
      ...currentValue,
      [childField]: event.target.value
    });
  };

  const handleAuthorFieldChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const currentSchema = metadata.json_ld_schema || {};
    const currentAuthor = currentSchema.author || {};
    onMetadataEdit('json_ld_schema', {
      ...currentSchema,
      author: {
        ...currentAuthor,
        [field]: event.target.value
      }
    });
  };

  const handlePublisherFieldChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const currentSchema = metadata.json_ld_schema || {};
    const currentPublisher = currentSchema.publisher || {};
    onMetadataEdit('json_ld_schema', {
      ...currentSchema,
      publisher: {
        ...currentPublisher,
        [field]: event.target.value
      }
    });
  };

  const handleSchemaFieldChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const currentSchema = metadata.json_ld_schema || {};
    onMetadataEdit('json_ld_schema', {
      ...currentSchema,
      [field]: event.target.value
    });
  };

  const getJsonLdSchema = () => {
    const schema = metadata.json_ld_schema || {};
    return JSON.stringify(schema, null, 2);
  };

  const copyJsonLdSchema = () => {
    onCopyToClipboard(getJsonLdSchema(), 'json_ld_schema');
  };

  const jsonLdSchema = metadata.json_ld_schema || {};
  const author = jsonLdSchema.author || {};
  const publisher = jsonLdSchema.publisher || {};

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <CodeIcon sx={{ color: 'primary.main' }} />
        Structured Data (JSON-LD)
      </Typography>

      <Grid container spacing={3}>
        {/* Article Information */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <CodeIcon />
              Article Schema
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Headline
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(jsonLdSchema.headline || '', 'schema_headline')}
                    >
                      {copiedItems.has('schema_headline') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  value={jsonLdSchema.headline || ''}
                  onChange={handleSchemaFieldChange('headline')}
                  placeholder="Article headline"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Description
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(jsonLdSchema.description || '', 'schema_description')}
                    >
                      {copiedItems.has('schema_description') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={jsonLdSchema.description || ''}
                  onChange={handleSchemaFieldChange('description')}
                  placeholder="Article description"
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Main Entity URL
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(jsonLdSchema.mainEntityOfPage || '', 'schema_url')}
                    >
                      {copiedItems.has('schema_url') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  value={jsonLdSchema.mainEntityOfPage || ''}
                  onChange={handleSchemaFieldChange('mainEntityOfPage')}
                  placeholder="https://example.com/blog-post"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <CodeIcon />
                      </InputAdornment>
                    )
                  }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Word Count
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(jsonLdSchema.wordCount?.toString() || '', 'schema_wordcount')}
                    >
                      {copiedItems.has('schema_wordcount') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  type="number"
                  value={jsonLdSchema.wordCount || ''}
                  onChange={handleSchemaFieldChange('wordCount')}
                  placeholder="1500"
                  InputProps={{
                    endAdornment: <InputAdornment position="end">words</InputAdornment>
                  }}
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Author Information */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PersonIcon />
              Author Information
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Author Name
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(author.name || '', 'author_name')}
                    >
                      {copiedItems.has('author_name') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  value={author.name || ''}
                  onChange={handleAuthorFieldChange('name')}
                  placeholder="Author Name"
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Author Type
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(author['@type'] || '', 'author_type')}
                    >
                      {copiedItems.has('author_type') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  value={author['@type'] || ''}
                  onChange={handleAuthorFieldChange('@type')}
                  placeholder="Person"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Publisher Information */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <BusinessIcon />
              Publisher Information
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Publisher Name
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(publisher.name || '', 'publisher_name')}
                    >
                      {copiedItems.has('publisher_name') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  value={publisher.name || ''}
                  onChange={handlePublisherFieldChange('name')}
                  placeholder="Publisher Name"
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Publisher Logo
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(publisher.logo || '', 'publisher_logo')}
                    >
                      {copiedItems.has('publisher_logo') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  value={publisher.logo || ''}
                  onChange={handlePublisherFieldChange('logo')}
                  placeholder="https://example.com/logo.png"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Publication Dates */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <CalendarIcon />
              Publication Dates
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Date Published
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(jsonLdSchema.datePublished || '', 'date_published')}
                    >
                      {copiedItems.has('date_published') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  type="datetime-local"
                  value={jsonLdSchema.datePublished || ''}
                  onChange={handleSchemaFieldChange('datePublished')}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Date Modified
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard(jsonLdSchema.dateModified || '', 'date_modified')}
                    >
                      {copiedItems.has('date_modified') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  type="datetime-local"
                  value={jsonLdSchema.dateModified || ''}
                  onChange={handleSchemaFieldChange('dateModified')}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Keywords */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
              <CodeIcon />
              Keywords & Categories
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Keywords
                  </Typography>
                  <Tooltip title="Copy to clipboard">
                    <IconButton
                      size="small"
                      onClick={() => onCopyToClipboard((jsonLdSchema.keywords || []).join(', '), 'schema_keywords')}
                    >
                      {copiedItems.has('schema_keywords') ? <CheckIcon color="success" /> : <CopyIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={(jsonLdSchema.keywords || []).join(', ')}
                  onChange={(e) => {
                    const keywords = e.target.value.split(',').map(k => k.trim()).filter(k => k);
                    handleSchemaFieldChange('keywords')({ target: { value: keywords } } as any);
                  }}
                  placeholder="keyword1, keyword2, keyword3"
                  helperText="Separate keywords with commas"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Raw JSON View */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CodeIcon />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Raw JSON-LD Schema
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ position: 'relative' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Complete JSON-LD Schema
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={copiedItems.has('json_ld_schema') ? <CheckIcon /> : <CopyIcon />}
                    onClick={copyJsonLdSchema}
                  >
                    {copiedItems.has('json_ld_schema') ? 'Copied!' : 'Copy JSON'}
                  </Button>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={15}
                  value={getJsonLdSchema()}
                  InputProps={{
                    readOnly: true,
                    sx: {
                      fontFamily: 'monospace',
                      fontSize: '0.875rem'
                    }
                  }}
                  sx={{
                    '& .MuiInputBase-input': {
                      fontFamily: 'monospace',
                      fontSize: '0.875rem'
                    }
                  }}
                />
              </Box>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Information Alert */}
        <Grid item xs={12}>
          <Alert severity="info">
            <Typography variant="body2">
              <strong>JSON-LD Structured Data:</strong> This schema helps search engines understand your content 
              and may enable rich snippets in search results. The data follows Schema.org Article guidelines.
            </Typography>
          </Alert>
        </Grid>
      </Grid>
    </Box>
  );
};
