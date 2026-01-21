import { apiClient } from './client';

export interface Campaign {
  campaign_id: string;
  user_id: string;
  name: string;
  keywords: string[];
  status: string;
  created_at: string;
  email_stats: {
    sent: number;
    replied: number;
    bounced: number;
  };
}

export interface CreateCampaignRequest {
  name: string;
  keywords: string[];
  user_proposal: {
    user_name: string;
    user_email: string;
    topic: string;
    description?: string;
  };
}

export interface Opportunity {
  url: string;
  title: string;
  description: string;
  contact_email?: string;
  contact_name?: string;
  domain_authority?: number;
  content_topics: string[];
  submission_guidelines?: string;
  status: string;
}

export interface EmailConfig {
  server: string;
  port: number;
  user: string;
  password: string;
}

export interface CampaignAnalytics {
  total_opportunities: number;
  opportunities_by_status: Record<string, number>;
  email_stats: {
    sent: number;
    replied: number;
    bounced: number;
    open_rate: number;
    reply_rate: number;
  };
  top_performing_opportunities: any[];
  campaign_progress: {
    discovery_complete: boolean;
    emails_generated: boolean;
    emails_sent: boolean;
    responses_checked: boolean;
  };
}

// ====================
// CAMPAIGN MANAGEMENT
// ====================

export const createCampaign = async (data: CreateCampaignRequest): Promise<Campaign> => {
  const response = await apiClient.post('/backlinking/campaigns', data);
  return response.data;
};

export const getCampaigns = async (): Promise<Campaign[]> => {
  const response = await apiClient.get('/backlinking/campaigns');
  return response.data;
};

export const getCampaign = async (campaignId: string): Promise<Campaign> => {
  const response = await apiClient.get(`/backlinking/campaigns/${campaignId}`);
  return response.data;
};

export const pauseCampaign = async (campaignId: string): Promise<{ message: string }> => {
  const response = await apiClient.post(`/backlinking/campaigns/${campaignId}/pause`);
  return response.data;
};

export const resumeCampaign = async (campaignId: string): Promise<{ message: string }> => {
  const response = await apiClient.post(`/backlinking/campaigns/${campaignId}/resume`);
  return response.data;
};

export const deleteCampaign = async (campaignId: string): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/backlinking/campaigns/${campaignId}`);
  return response.data;
};

// ====================
// OPPORTUNITY DISCOVERY
// ====================

export const discoverOpportunities = async (
  campaignId: string,
  keywords: string[]
): Promise<Opportunity[]> => {
  const response = await apiClient.post(`/backlinking/campaigns/${campaignId}/discover`, {
    keywords
  });
  return response.data;
};

export const getCampaignOpportunities = async (campaignId: string): Promise<Opportunity[]> => {
  const response = await apiClient.get(`/backlinking/campaigns/${campaignId}/opportunities`);
  return response.data;
};

// ====================
// EMAIL OPERATIONS
// ====================

export interface EmailGenerationResponse {
  opportunity: Opportunity;
  email_subject: string;
  email_body: string;
  record_id: number;
}

export const generateOutreachEmails = async (
  campaignId: string,
  userProposal: any
): Promise<EmailGenerationResponse[]> => {
  const response = await apiClient.post(`/backlinking/campaigns/${campaignId}/generate-emails`, {
    user_proposal: userProposal
  });
  return response.data;
};

export const sendOutreachEmails = async (
  campaignId: string,
  emailRecords: any[],
  smtpConfig: EmailConfig
): Promise<{ message: string; campaign_id: string; emails_queued: number }> => {
  const response = await apiClient.post(`/backlinking/campaigns/${campaignId}/send-emails`, {
    email_records: emailRecords,
    smtp_config: smtpConfig
  });
  return response.data;
};

export const checkEmailResponses = async (
  campaignId: string,
  imapConfig: EmailConfig
): Promise<{ message: string; campaign_id: string }> => {
  const response = await apiClient.post(`/backlinking/campaigns/${campaignId}/check-responses`, {
    imap_config: imapConfig
  });
  return response.data;
};

// ====================
// ANALYTICS & REPORTING
// ====================

export const getCampaignAnalytics = async (campaignId: string): Promise<CampaignAnalytics> => {
  const response = await apiClient.get(`/backlinking/campaigns/${campaignId}/analytics`);
  return response.data;
};

// ====================
// UTILITY FUNCTIONS
// ====================

export const validateEmailConfig = (config: EmailConfig): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!config.server.trim()) {
    errors.push('SMTP server is required');
  }

  if (!config.port || config.port <= 0) {
    errors.push('Valid port number is required');
  }

  if (!config.user.trim()) {
    errors.push('Email address is required');
  } else if (!/\S+@\S+\.\S+/.test(config.user)) {
    errors.push('Valid email address is required');
  }

  if (!config.password.trim()) {
    errors.push('Password is required');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

export const getDefaultSmtpConfig = (): EmailConfig => ({
  server: 'smtp.gmail.com',
  port: 587,
  user: '',
  password: ''
});

export const getDefaultImapConfig = (): EmailConfig => ({
  server: 'imap.gmail.com',
  port: 993,
  user: '',
  password: ''
});