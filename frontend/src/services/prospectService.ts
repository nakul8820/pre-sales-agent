import apiClient from './api';

export interface ManualIntakePayload {
  company_name: string;
  website_url: string;
  contact_name?: string;
  contact_email?: string;
  contact_title?: string;
  contact_phone?: string;
  notes?: string;
}

export interface PageSpeedOpportunities {
  id: string;
  title: string;
  display_value?: string;
  severity?: string;
}

export interface PageSpeedTelemetry {
  status: string;
  performance_score: number;
  core_web_vitals: {
    fcp_ms: number;
    lcp_ms: number;
    cls: number;
    tbt_ms: number;
    speed_index_ms: number;
  };
  opportunities: PageSpeedOpportunities[];
  is_cached?: boolean;
}

export interface TopKeyword {
  keyword: string;
  position: number;
  search_volume: number;
  cpc: number;
  traffic_percent: number;
}

export interface SEMrushTelemetry {
  status: string;
  domain_rank: number;
  organic_traffic: number;
  organic_keywords: number;
  organic_cost: number;
  adwords_keywords: number;
  top_keywords?: TopKeyword[];
  is_cached?: boolean;
}

export interface CrawlerTelemetry {
  domain: string;
  pages_crawled_count: number;
  crawl_duration_seconds: number;
  lead_gen?: {
    lead_gen_score: number;
    has_contact_form: boolean;
    has_phone_number: boolean;
    has_email_address: boolean;
    has_live_chat: boolean;
    has_booking_widget: boolean;
    has_newsletter: boolean;
    detected_phones?: string[];
    detected_emails?: string[];
    detected_ctas?: string[];
  };
  broken_links?: {
    broken_links_score: number;
    total_links_checked: number;
    broken_links_count: number;
    internal_broken_count: number;
    external_broken_count: number;
  };
  ui_ux?: {
    ui_ux_score: number;
    mobile_responsive: boolean;
    total_images: number;
    missing_alt_tags_count: number;
    alt_coverage_percent: number;
    has_ssl: boolean;
    mixed_content_count: number;
    has_title_tag: boolean;
    has_meta_description: boolean;
    has_h1: boolean;
  };
}

export interface ModerationFlagItem {
  category: string;
  severity: string;
  confidence_score: number;
  flagged_keywords: string[];
  snippet: string;
  description: string;
}

export interface ContentModerationTelemetry {
  domain: string;
  is_safe: boolean;
  has_critical_flag: boolean;
  flags_count: number;
  status_label: string;
  flags: ModerationFlagItem[];
}

export interface CriticalFocusAreaItem {
  category: string;
  severity: string;
  title: string;
  description: string;
  impact: string;
  pitch_angle?: string;
}

export interface ProspectWebFormResponse {
  prospect_id: string;
  company_name: string;
  domain: string;
  website_url: string;
  source: string;
  status: string;
  message: string;
  created_at: string;
  logo_url?: string;
  
  overall_score?: number;
  letter_grade?: string;
  grade_label?: string;
  grade_color?: string;
  
  performance_score?: number;
  seo_score?: number;
  lead_gen_score?: number;
  ui_ux_score?: number;
  broken_links_score?: number;
  category_weights?: Record<string, number>;

  moderation?: ContentModerationTelemetry;
  pagespeed_data?: PageSpeedTelemetry;
  semrush_data?: SEMrushTelemetry;
  crawler_data?: CrawlerTelemetry;
  critical_focus_areas?: CriticalFocusAreaItem[];
}

export interface ProspectItem {
  id: string;
  company_name: string;
  domain: string;
  website_url: string;
  contact_name?: string;
  contact_email?: string;
  contact_title?: string;
  contact_phone?: string;
  source: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ProspectListResponse {
  items: ProspectItem[];
  total: number;
  page: number;
  page_size: number;
}

export const prospectService = {
  submitWebForm: async (data: ManualIntakePayload): Promise<ProspectWebFormResponse> => {
    const response = await apiClient.post<ProspectWebFormResponse>('/prospects/web-form', data);
    return response.data;
  },

  analyzeProspect: async (prospectId: string): Promise<ProspectWebFormResponse> => {
    const response = await apiClient.post<ProspectWebFormResponse>(`/prospects/${prospectId}/analyze`);
    return response.data;
  },

  getProspects: async (page: number = 1, limit: number = 20): Promise<ProspectListResponse> => {
    const response = await apiClient.get<ProspectListResponse>('/prospects', {
      params: { page, limit },
    });
    return response.data;
  },

  getProspectById: async (prospectId: string): Promise<ProspectItem> => {
    const response = await apiClient.get<ProspectItem>(`/prospects/${prospectId}`);
    return response.data;
  },
};

export default prospectService;
