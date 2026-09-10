// Types du contrat API CacaoSat (alignés sur /api/v1/openapi.json).

export type Role = 'agent' | 'manager' | 'exporter' | 'regulator' | 'admin';
export type RiskLevel = 'low' | 'medium' | 'high';
export type EudrStatus = 'compliant' | 'at_risk' | 'non_compliant' | 'unassessed';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  cooperative_id: string | null;
  created_at: string;
}

export interface Cooperative {
  id: string;
  name: string;
  code: string;
  region: string | null;
  department: string | null;
  contact_name: string | null;
  contact_phone: string | null;
  contact_email: string | null;
  created_at: string;
}

export interface Producer {
  id: string;
  cooperative_id: string;
  full_name: string;
  national_id: string | null;
  gender: string;
  village: string | null;
  phone: string | null;
  registered_at: string | null;
  created_at: string;
  parcels_count?: number;
}

export interface ScoreBrief {
  score: number;
  risk_level: RiskLevel;
  eudr_status: EudrStatus;
  computed_at: string;
}

export interface AnalysisBrief {
  id: string;
  deforestation_detected: boolean;
  forest_loss_ha: number;
  forest_cover_2020_pct: number | null;
  forest_cover_current_pct: number | null;
  protected_area_overlap_ha: number;
  confidence: number;
  created_at: string;
}

export interface Parcel {
  id: string;
  code: string;
  producer_id: string | null;
  producer_name: string | null;
  cooperative_id: string;
  geometry: GeoJSON.Polygon | GeoJSON.MultiPolygon;
  area_ha: number;
  planting_year: number | null;
  crop: string;
  gps_accuracy_m: number | null;
  collection_method: string;
  collected_at: string | null;
  source: string;
  status: string;
  created_at: string;
  latest_score: ScoreBrief | null;
  latest_analysis: AnalysisBrief | null;
}

export interface ScoreFactor {
  key: string;
  label: string;
  weight: number;
  raw_value: unknown;
  points: number;
  explanation: string;
}

export interface ComplianceScore {
  id: string;
  parcel_id: string;
  analysis_run_id: string;
  score: number;
  risk_level: RiskLevel;
  eudr_status: EudrStatus;
  factors: ScoreFactor[];
  computed_at: string;
}

export interface AnalysisRun {
  id: string;
  parcel_id: string;
  provider_versions: Record<string, string>;
  forest_cover_2020_pct: number | null;
  forest_cover_current_pct: number | null;
  forest_loss_ha: number;
  loss_events: Array<Record<string, unknown>>;
  ndvi_series: Array<{ date: string; ndvi: number }>;
  protected_area_overlap_ha: number;
  deforestation_detected: boolean;
  confidence: number;
  created_at: string;
}

export interface AnalyzeResult {
  analysis_run: AnalysisRun;
  compliance_score: ComplianceScore;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface Paginated<T> {
  items: T[];
  pagination: Pagination;
}

export interface DashboardSummary {
  cooperative_id: string | null;
  parcels_total: number;
  area_ha_total: number;
  assessed: number;
  coverage_pct: number;
  compliant: number;
  at_risk: number;
  non_compliant: number;
  unassessed: number;
  deforestation_events: number;
  high_risk_area_ha: number;
  risk_distribution: { low: number; medium: number; high: number };
  score_distribution: Array<{ range: string; count: number }>;
  trend: Array<{ month: string; assessed: number; compliant_pct: number }>;
}

export interface RegionsResponse {
  generated_at: string;
  regions: Array<{
    region: string;
    parcels: number;
    area_ha: number;
    compliant: number;
    at_risk: number;
    non_compliant: number;
  }>;
}

export interface Alert {
  id: string;
  parcel_id: string;
  parcel_code: string | null;
  cooperative_id: string | null;
  type: 'new_deforestation' | 'protected_encroachment' | 'data_gap';
  severity: 'low' | 'medium' | 'high' | 'critical';
  detected_at: string;
  area_ha: number;
  message: string;
  acknowledged: boolean;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  created_at: string;
}

export interface ComplianceReport {
  id: string;
  cooperative_id: string;
  title: string;
  period_start: string;
  period_end: string;
  parcel_ids: string[];
  summary: Record<string, unknown>;
  content_hash: string;
  pdf_key: string;
  geojson_key: string;
  generated_by: string | null;
  generated_at: string;
}
