import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type {
  Alert,
  AnalyzeResult,
  ComplianceReport,
  Cooperative,
  DashboardSummary,
  Paginated,
  Parcel,
  Producer,
} from '@/types/api';

type FC = GeoJSON.FeatureCollection;

const qs = (params: Record<string, string | number | undefined | null>) => {
  const s = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') s.set(k, String(v));
  }
  const out = s.toString();
  return out ? `?${out}` : '';
};

export const useSummary = (coopId?: string) =>
  useQuery({
    queryKey: ['dashboard', 'summary', coopId ?? 'scope'],
    queryFn: () => api<DashboardSummary>(`/dashboard/summary${qs({ cooperative_id: coopId })}`),
  });

export const useDashboardMap = (coopId?: string) =>
  useQuery({
    queryKey: ['dashboard', 'map', coopId ?? 'scope'],
    queryFn: () => api<FC>(`/dashboard/map${qs({ cooperative_id: coopId })}`),
  });

export interface ParcelFilters {
  page?: number;
  per_page?: number;
  q?: string;
  risk_level?: string;
  eudr_status?: string;
  producer_id?: string;
  cooperative_id?: string;
  sort?: string;
  order?: string;
}

export const useParcels = (filters: ParcelFilters) =>
  useQuery({
    queryKey: ['parcels', filters],
    queryFn: () => api<Paginated<Parcel>>(`/parcels${qs(filters as Record<string, string>)}`),
  });

export const useParcel = (id: string | undefined) =>
  useQuery({
    queryKey: ['parcel', id],
    queryFn: () => api<Parcel>(`/parcels/${id}`),
    enabled: !!id,
  });

export const useParcelHistory = (id: string | undefined) =>
  useQuery({
    queryKey: ['parcel', id, 'history'],
    queryFn: () =>
      api<{ analyses: unknown[]; scores: unknown[] }>(`/parcels/${id}/history`),
    enabled: !!id,
  });

export const useAnalyzeParcel = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api<AnalyzeResult>(`/parcels/${id}/analyze`, { method: 'POST' }),
    onSuccess: (_data, id) => {
      void qc.invalidateQueries({ queryKey: ['parcel', id] });
      void qc.invalidateQueries({ queryKey: ['parcels'] });
      void qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export const useProducers = (filters: ParcelFilters) =>
  useQuery({
    queryKey: ['producers', filters],
    queryFn: () => api<Paginated<Producer>>(`/producers${qs(filters as Record<string, string>)}`),
  });

export const useCooperatives = () =>
  useQuery({
    queryKey: ['cooperatives'],
    queryFn: () => api<Cooperative[]>('/cooperatives'),
  });

export const useAlerts = (filters: {
  page?: number;
  per_page?: number;
  severity?: string;
  type?: string;
  acknowledged?: string;
}) =>
  useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => api<Paginated<Alert>>(`/alerts${qs(filters)}`),
  });

export const useAcknowledgeAlert = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api<Alert>(`/alerts/${id}/acknowledge`, { method: 'POST' }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

export const useReports = () =>
  useQuery({
    queryKey: ['reports'],
    queryFn: () => api<Paginated<ComplianceReport>>('/reports?per_page=50'),
  });

export const useCreateReport = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      period_start: string;
      period_end: string;
      title?: string;
      // Obligatoire pour les rôles à portée nationale : leur token ne porte
      // aucune coopérative, l'API ne peut donc pas la déduire.
      cooperative_id?: string;
    }) => api<ComplianceReport>('/reports', { method: 'POST', body }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['reports'] });
    },
  });
};
