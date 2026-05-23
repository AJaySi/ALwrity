import { apiClient } from './client';

export interface BacklinkModuleRecord {
  identifier: 'backlink' | 'outreach' | 'guest_post' | string;
  module_path: string;
  purpose: string;
}

export interface BacklinkModuleRegistryResponse {
  feature: string;
  modules: BacklinkModuleRecord[];
}

export interface BacklinkCoverageResponse {
  legacy_reference: string;
  implemented_count: number;
  planned_count: number;
  implemented: string[];
  planned: string[];
}

export interface BacklinkQueryTemplatesResponse {
  keyword: string;
  queries: string[];
}

export interface BacklinkDiscoveryRequest {
  keyword: string;
  max_results?: number;
}

export interface BacklinkOpportunity {
  url: string;
  title: string;
  snippet: string;
  confidence_score: number;
}



export interface BacklinkPolicyValidationRequest {
  user_id: string;
  workspace_id: string;
  campaign_id: string;
  recipient_email: string;
  recipient_domain: string;
  recipient_region: string;
  legal_basis: string;
  approved_by_human: boolean;
  unsubscribe_url?: string;
  sender_identity: string;
  idempotency_key: string;
}

export interface BacklinkPolicyValidationResponse {
  allowed: boolean;
  reasons: string[];
  final_status: string;
}

export interface BacklinkReportingSnapshot {
  send_volume: number;
  decision_events: number;
  response_rate: number;
  placement_conversion: number;
}

export interface BacklinkDiscoveryResponse {
  keyword: string;
  queries: string[];
  opportunities: BacklinkOpportunity[];
}

export interface BacklinkCampaignRecord {
  campaign_id: string;
  name: string;
  status: string;
  created_at?: string;
}

export interface BacklinkCampaignCreateRequest {
  user_id: string;
  workspace_id: string;
  name: string;
}

export interface BacklinkCampaignCreateResponse {
  campaign_id: string;
  name: string;
  status: string;
}

export interface BacklinkCampaignListResponse {
  campaigns: BacklinkCampaignRecord[];
}

export const fetchBacklinkModuleRegistry = async (): Promise<BacklinkModuleRegistryResponse> => (await apiClient.get('/api/backlink-outreach/modules')).data;
export const fetchBacklinkMigrationCoverage = async (): Promise<BacklinkCoverageResponse> => (await apiClient.get('/api/backlink-outreach/migration-coverage')).data;
export const fetchBacklinkQueryTemplates = async (keyword: string): Promise<BacklinkQueryTemplatesResponse> => (await apiClient.get('/api/backlink-outreach/query-templates', { params: { keyword } })).data;
export const discoverBacklinkOpportunities = async (payload: BacklinkDiscoveryRequest): Promise<BacklinkDiscoveryResponse> => (await apiClient.post('/api/backlink-outreach/discover', payload)).data;

export const validateBacklinkPolicy = async (payload: BacklinkPolicyValidationRequest): Promise<BacklinkPolicyValidationResponse> => (await apiClient.post('/api/backlink-outreach/policy-validate', payload)).data;
export const fetchBacklinkReportingSnapshot = async (): Promise<BacklinkReportingSnapshot> => (await apiClient.get('/api/backlink-outreach/reporting')).data;

export const createBacklinkCampaign = async (payload: BacklinkCampaignCreateRequest): Promise<BacklinkCampaignCreateResponse> => (await apiClient.post('/api/backlink-outreach/campaigns', payload)).data;
export const listBacklinkCampaigns = async (user_id: string, workspace_id: string): Promise<BacklinkCampaignListResponse> => (await apiClient.get('/api/backlink-outreach/campaigns', { params: { user_id, workspace_id } })).data;
