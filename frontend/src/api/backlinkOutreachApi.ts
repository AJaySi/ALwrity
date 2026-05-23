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

// -- Deep Discovery --

export interface EnrichedOpportunity {
  url: string;
  domain: string;
  page_title: string;
  snippet: string;
  full_text: string;
  email: string | null;
  contact_page: string | null;
  confidence_score: number;
  quality_score: number;
  word_count: number;
  has_guest_post_guidelines: boolean;
  discovery_source: string;
}

export interface DeepDiscoveryRequest {
  keyword: string;
  max_results?: number;
  campaign_id?: string;
}

export interface DeepDiscoveryResponse {
  keyword: string;
  source: string;
  total_found: number;
  opportunities: EnrichedOpportunity[];
}

export const discoverDeepBacklinkOpportunities = async (payload: DeepDiscoveryRequest): Promise<DeepDiscoveryResponse> => (await apiClient.post('/api/backlink-outreach/discover/deep', payload)).data;

// -- Leads --

export interface LeadRecord {
  lead_id: string;
  campaign_id: string;
  url: string | null;
  domain: string;
  page_title: string;
  snippet: string;
  email: string | null;
  confidence_score: number;
  discovery_source: string;
  status: string;
  notes: string | null;
  created_at: string | null;
}

export interface LeadListResponse {
  leads: LeadRecord[];
  total: number;
}

export interface LeadCreateRequest {
  campaign_id: string;
  url: string;
  domain: string;
  email?: string;
  page_title?: string;
  snippet?: string;
  confidence_score?: number;
  notes?: string;
}

export interface LeadStatusUpdateRequest {
  status: string;
  notes?: string;
}

export interface CampaignDetailResponse {
  campaign_id: string;
  name: string;
  status: string;
  created_at: string | null;
  lead_count: number;
  leads: LeadRecord[];
}

export const fetchCampaignDetail = async (campaign_id: string, user_id: string): Promise<CampaignDetailResponse> => (await apiClient.get(`/api/backlink-outreach/campaigns/${campaign_id}`, { params: { user_id } })).data;
export const fetchCampaignLeads = async (campaign_id: string, user_id: string, status?: string): Promise<LeadListResponse> => (await apiClient.get(`/api/backlink-outreach/campaigns/${campaign_id}/leads`, { params: { user_id, status } })).data;
export const addLeadToCampaign = async (campaign_id: string, payload: LeadCreateRequest): Promise<LeadRecord> => (await apiClient.post(`/api/backlink-outreach/campaigns/${campaign_id}/leads`, payload)).data;
export const updateLeadStatus = async (lead_id: string, payload: LeadStatusUpdateRequest): Promise<LeadRecord> => (await apiClient.patch(`/api/backlink-outreach/leads/${lead_id}/status`, payload)).data;
