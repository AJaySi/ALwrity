/**
 * IntentResultsDisplay Component
 * 
 * Displays intent-driven research results organized by deliverable type.
 * Shows statistics, quotes, case studies, trends, etc. in a structured format.
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Grid,
  Link,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  TrendingUp as TrendIcon,
  FormatQuote as QuoteIcon,
  BarChart as StatsIcon,
  School as CaseStudyIcon,
  Lightbulb as IdeaIcon,
  OpenInNew as OpenIcon,
  ExpandMore as ExpandMoreIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import {
  IntentDrivenResearchResponse,
  DELIVERABLE_DISPLAY,
} from '../../types/intent.types';

interface IntentResultsDisplayProps {
  result: IntentDrivenResearchResponse;
}

export const IntentResultsDisplay: React.FC<IntentResultsDisplayProps> = ({ result }) => {
  const [tabIndex, setTabIndex] = useState(0);

  // Build available tabs based on what we have
  const tabs = [
    { id: 'summary', label: 'Summary', icon: <IdeaIcon />, count: 0 },
    ...(result.statistics.length > 0 ? [{ id: 'statistics', label: 'Statistics', icon: <StatsIcon />, count: result.statistics.length }] : []),
    ...(result.expert_quotes.length > 0 ? [{ id: 'quotes', label: 'Expert Quotes', icon: <QuoteIcon />, count: result.expert_quotes.length }] : []),
    ...(result.case_studies.length > 0 ? [{ id: 'case_studies', label: 'Case Studies', icon: <CaseStudyIcon />, count: result.case_studies.length }] : []),
    ...(result.trends.length > 0 ? [{ id: 'trends', label: 'Trends', icon: <TrendIcon />, count: result.trends.length }] : []),
    { id: 'sources', label: 'Sources', icon: <OpenIcon />, count: result.sources.length },
  ];

  const currentTab = tabs[tabIndex]?.id || 'summary';

  return (
    <Box>
      {/* Executive Summary Banner */}
      {result.executive_summary && (
        <Alert 
          severity="success" 
          icon={<CheckIcon />}
          sx={{ mb: 3, borderRadius: 2 }}
        >
          <Typography variant="body1">{result.executive_summary}</Typography>
        </Alert>
      )}

      {/* Primary Answer */}
      {result.primary_answer && (
        <Paper elevation={0} sx={{ p: 3, mb: 3, borderRadius: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <Typography variant="subtitle2" gutterBottom>
            Answer to Your Question:
          </Typography>
          <Typography variant="body1" fontWeight={500}>
            {result.primary_answer}
          </Typography>
        </Paper>
      )}

      {/* Tabs */}
      <Tabs
        value={tabIndex}
        onChange={(_, v) => setTabIndex(v)}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ mb: 2, borderBottom: 1, borderColor: 'divider' }}
      >
        {tabs.map((tab, idx) => (
          <Tab
            key={tab.id}
            icon={tab.icon}
            iconPosition="start"
            label={
              <Box display="flex" alignItems="center" gap={0.5}>
                {tab.label}
                {tab.count > 0 && (
                  <Chip size="small" label={tab.count} color="primary" sx={{ height: 20, fontSize: '0.7rem' }} />
                )}
              </Box>
            }
            sx={{ minHeight: 48, textTransform: 'none' }}
          />
        ))}
      </Tabs>

      {/* Tab Content */}
      <Box sx={{ minHeight: 300 }}>
        {/* Summary Tab */}
        {currentTab === 'summary' && (
          <Box>
            {/* Key Takeaways */}
            {result.key_takeaways.length > 0 && (
              <Box mb={3}>
                <Typography variant="h6" gutterBottom color="primary">
                  ✨ Key Takeaways
                </Typography>
                <List>
                  {result.key_takeaways.map((takeaway, idx) => (
                    <ListItem key={idx} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckIcon color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={takeaway} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Best Practices */}
            {result.best_practices.length > 0 && (
              <Box mb={3}>
                <Typography variant="h6" gutterBottom color="primary">
                  📋 Best Practices
                </Typography>
                <List>
                  {result.best_practices.map((practice, idx) => (
                    <ListItem key={idx} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <IdeaIcon color="info" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={practice} />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Suggested Content Outline */}
            {result.suggested_outline.length > 0 && (
              <Box mb={3}>
                <Typography variant="h6" gutterBottom color="primary">
                  📝 Suggested Content Outline
                </Typography>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <List dense>
                    {result.suggested_outline.map((item, idx) => (
                      <ListItem key={idx}>
                        <ListItemText primary={item} />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Box>
            )}

            {/* Definitions */}
            {Object.keys(result.definitions).length > 0 && (
              <Box mb={3}>
                <Typography variant="h6" gutterBottom color="primary">
                  📖 Key Definitions
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(result.definitions).map(([term, definition], idx) => (
                    <Grid item xs={12} md={6} key={idx}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle2" color="primary" gutterBottom>
                            {term}
                          </Typography>
                          <Typography variant="body2">{definition}</Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </Box>
        )}

        {/* Statistics Tab */}
        {currentTab === 'statistics' && (
          <Grid container spacing={2}>
            {result.statistics.map((stat, idx) => (
              <Grid item xs={12} md={6} key={idx}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="flex-start" gap={1}>
                      <StatsIcon color="primary" />
                      <Box flex={1}>
                        <Typography variant="body1" fontWeight={500}>
                          {stat.statistic}
                        </Typography>
                        {stat.value && (
                          <Chip label={stat.value} color="primary" size="small" sx={{ mt: 0.5 }} />
                        )}
                        <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                          {stat.context}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                          <Link href={stat.url} target="_blank" rel="noopener" variant="caption">
                            {stat.source} <OpenIcon sx={{ fontSize: 12 }} />
                          </Link>
                          <Chip
                            size="small"
                            label={`${Math.round(stat.credibility * 100)}% credible`}
                            color={stat.credibility > 0.8 ? 'success' : 'warning'}
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Expert Quotes Tab */}
        {currentTab === 'quotes' && (
          <Box>
            {result.expert_quotes.map((quote, idx) => (
              <Card key={idx} variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Box display="flex" gap={2}>
                    <QuoteIcon color="primary" sx={{ fontSize: 40, opacity: 0.5 }} />
                    <Box>
                      <Typography variant="body1" fontStyle="italic" mb={1}>
                        "{quote.quote}"
                      </Typography>
                      <Typography variant="subtitle2" color="primary">
                        — {quote.speaker}
                        {quote.title && `, ${quote.title}`}
                        {quote.organization && ` at ${quote.organization}`}
                      </Typography>
                      <Link href={quote.url} target="_blank" rel="noopener" variant="caption">
                        Source: {quote.source} <OpenIcon sx={{ fontSize: 12 }} />
                      </Link>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}

        {/* Case Studies Tab */}
        {currentTab === 'case_studies' && (
          <Box>
            {result.case_studies.map((cs, idx) => (
              <Accordion key={idx} defaultExpanded={idx === 0}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box>
                    <Typography variant="subtitle1" fontWeight={600}>
                      {cs.title}
                    </Typography>
                    <Typography variant="caption" color="primary">
                      {cs.organization}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="caption" color="text.secondary">Challenge</Typography>
                      <Typography variant="body2">{cs.challenge}</Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="caption" color="text.secondary">Solution</Typography>
                      <Typography variant="body2">{cs.solution}</Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="caption" color="text.secondary">Outcome</Typography>
                      <Typography variant="body2">{cs.outcome}</Typography>
                    </Grid>
                  </Grid>
                  {cs.key_metrics.length > 0 && (
                    <Box mt={2} display="flex" gap={1} flexWrap="wrap">
                      {cs.key_metrics.map((metric, i) => (
                        <Chip key={i} label={metric} size="small" color="success" variant="outlined" />
                      ))}
                    </Box>
                  )}
                  <Box mt={2}>
                    <Link href={cs.url} target="_blank" rel="noopener" variant="caption">
                      Read full case study <OpenIcon sx={{ fontSize: 12 }} />
                    </Link>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}

        {/* Trends Tab */}
        {currentTab === 'trends' && (
          <Grid container spacing={2}>
            {result.trends.map((trend, idx) => (
              <Grid item xs={12} md={6} key={idx}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <TrendIcon
                        color={trend.direction === 'growing' ? 'success' : trend.direction === 'declining' ? 'error' : 'info'}
                      />
                      <Typography variant="subtitle1" fontWeight={500}>
                        {trend.trend}
                      </Typography>
                      <Chip
                        size="small"
                        label={trend.direction}
                        color={trend.direction === 'growing' ? 'success' : trend.direction === 'declining' ? 'error' : 'info'}
                      />
                    </Box>
                    {trend.impact && (
                      <Typography variant="body2" color="text.secondary" mb={1}>
                        Impact: {trend.impact}
                      </Typography>
                    )}
                    {trend.timeline && (
                      <Typography variant="caption" color="text.secondary">
                        Timeline: {trend.timeline}
                      </Typography>
                    )}
                    <Box mt={1}>
                      <Typography variant="caption" color="text.secondary">Evidence:</Typography>
                      <List dense>
                        {trend.evidence.slice(0, 3).map((e, i) => (
                          <ListItem key={i} sx={{ py: 0, pl: 1 }}>
                            <ListItemText primary={`• ${e}`} primaryTypographyProps={{ variant: 'caption' }} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Sources Tab */}
        {currentTab === 'sources' && (
          <List>
            {result.sources.map((source, idx) => (
              <ListItem
                key={idx}
                component="a"
                href={source.url}
                target="_blank"
                rel="noopener"
                sx={{ 
                  borderBottom: '1px solid', 
                  borderColor: 'divider',
                  '&:hover': { bgcolor: 'action.hover' }
                }}
              >
                <ListItemText
                  primary={source.title}
                  secondary={
                    <Box>
                      {source.excerpt && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          {source.excerpt}
                        </Typography>
                      )}
                      <Box display="flex" gap={1} mt={0.5}>
                        {source.content_type && (
                          <Chip size="small" label={source.content_type} variant="outlined" />
                        )}
                        <Chip
                          size="small"
                          label={`${Math.round(source.relevance_score * 100)}% relevant`}
                          color="primary"
                          variant="outlined"
                        />
                        <Chip
                          size="small"
                          label={`${Math.round(source.credibility_score * 100)}% credible`}
                          color={source.credibility_score > 0.8 ? 'success' : 'warning'}
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  }
                />
                <OpenIcon color="action" />
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      {/* Gaps Identified */}
      {result.gaps_identified.length > 0 && (
        <Alert severity="warning" icon={<WarningIcon />} sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Gaps Identified:
          </Typography>
          <List dense>
            {result.gaps_identified.map((gap, idx) => (
              <ListItem key={idx} sx={{ py: 0 }}>
                <ListItemText primary={`• ${gap}`} />
              </ListItem>
            ))}
          </List>
          {result.follow_up_queries.length > 0 && (
            <Box mt={1}>
              <Typography variant="caption" color="text.secondary">
                Suggested follow-up: {result.follow_up_queries.slice(0, 2).join(', ')}
              </Typography>
            </Box>
          )}
        </Alert>
      )}

      {/* Confidence */}
      <Box mt={2} display="flex" justifyContent="flex-end">
        <Chip
          label={`Research confidence: ${Math.round(result.confidence * 100)}%`}
          color={result.confidence > 0.8 ? 'success' : result.confidence > 0.6 ? 'warning' : 'error'}
          variant="outlined"
        />
      </Box>
    </Box>
  );
};

export default IntentResultsDisplay;
