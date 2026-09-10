import type { Page } from '@playwright/test';

const polygon = (lon: number, lat: number, d = 0.0009) => ({
  type: 'Polygon',
  coordinates: [
    [
      [lon - d, lat - d],
      [lon + d, lat - d],
      [lon + d, lat + d],
      [lon - d, lat + d],
      [lon - d, lat - d],
    ],
  ],
});

const parcel = (i: number, status: string, score: number) => ({
  id: `p-${i}`,
  code: `COOPCA-GUIGLO-${String(i).padStart(4, '0')}`,
  producer_id: `pr-${i}`,
  producer_name: ['Kouassi Traoré', 'Affoué Gnagne', "N'Guessan Bamba"][i % 3],
  cooperative_id: 'coop-1',
  geometry: polygon(-7.49 + i * 0.001, 6.54),
  area_ha: 1.2 + i * 0.4,
  planting_year: 2014,
  crop: 'cocoa',
  gps_accuracy_m: 4.3,
  collection_method: 'walk',
  collected_at: '2026-09-01T09:00:00Z',
  source: 'mobile',
  status: 'active',
  created_at: '2026-09-01T09:00:00Z',
  latest_score: { score, risk_level: score >= 80 ? 'low' : score >= 50 ? 'medium' : 'high', eudr_status: status, computed_at: '2026-09-10T10:00:00Z' },
  latest_analysis: {
    id: `a-${i}`,
    deforestation_detected: status === 'non_compliant',
    forest_loss_ha: status === 'non_compliant' ? 0.6 : 0,
    forest_cover_2020_pct: 88,
    forest_cover_current_pct: 84,
    protected_area_overlap_ha: 0,
    confidence: 0.7,
    created_at: '2026-09-10T10:00:00Z',
  },
});

const PARCELS = [
  parcel(1, 'compliant', 95),
  parcel(2, 'compliant', 92),
  parcel(3, 'at_risk', 61),
  parcel(4, 'non_compliant', 38),
  parcel(5, 'compliant', 88),
];

export async function mockApi(page: Page): Promise<void> {
  await page.route('**/api/v1/**', async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname.replace('/api/v1', '');
    const method = route.request().method();
    const json = (body: unknown, status = 200) =>
      route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) });

    if (path === '/auth/login' && method === 'POST') {
      return json({ access_token: 'tok', refresh_token: 'ref', token_type: 'Bearer', expires_in: 900 });
    }
    if (path === '/auth/me') {
      return json({
        id: 'u1',
        email: 'manager1@cacaosat.ci',
        full_name: 'Responsable',
        role: 'manager',
        is_active: true,
        cooperative_id: 'coop-1',
        created_at: '2026-01-01T00:00:00Z',
      });
    }
    if (path === '/dashboard/regions') {
      return json({
        generated_at: '2026-09-10',
        regions: [{ region: 'Cavally', parcels: 41, area_ha: 135.3, compliant: 20, at_risk: 12, non_compliant: 9 }],
      });
    }
    if (path === '/dashboard/summary') {
      return json({
        cooperative_id: 'coop-1',
        parcels_total: 5,
        area_ha_total: 12.4,
        assessed: 5,
        coverage_pct: 100,
        compliant: 3,
        at_risk: 1,
        non_compliant: 1,
        unassessed: 0,
        deforestation_events: 1,
        high_risk_area_ha: 2.8,
        risk_distribution: { low: 3, medium: 1, high: 1 },
        score_distribution: [
          { range: '0-20', count: 0 },
          { range: '20-40', count: 1 },
          { range: '40-60', count: 0 },
          { range: '60-80', count: 1 },
          { range: '80-100', count: 3 },
        ],
        trend: [{ month: '2026-09', assessed: 5, compliant_pct: 60 }],
      });
    }
    if (path === '/dashboard/map') {
      return json({
        type: 'FeatureCollection',
        features: PARCELS.map((p) => ({
          type: 'Feature',
          geometry: p.geometry,
          properties: {
            id: p.id,
            code: p.code,
            producer: p.producer_name,
            area_ha: p.area_ha,
            score: p.latest_score.score,
            risk_level: p.latest_score.risk_level,
            eudr_status: p.latest_score.eudr_status,
            deforestation_detected: p.latest_analysis.deforestation_detected,
            protected_area_overlap_ha: 0,
          },
        })),
      });
    }
    if (path === '/sync/bootstrap') {
      return json({ protected_areas: { type: 'FeatureCollection', features: [] } });
    }
    if (path === '/parcels' && method === 'GET') {
      return json({
        items: PARCELS,
        pagination: { page: 1, per_page: 20, total: PARCELS.length, pages: 1, has_next: false, has_prev: false },
      });
    }
    if (/^\/parcels\/[^/]+\/analyze$/.test(path) && method === 'POST') {
      return json(
        {
          analysis_run: { ...PARCELS[0].latest_analysis, ndvi_series: [{ date: '2022-01-15', ndvi: 0.8 }], loss_events: [], provider_versions: {} },
          compliance_score: { ...PARCELS[0].latest_score, id: 's1', parcel_id: 'p-1', analysis_run_id: 'a-1', factors: [] },
        },
        201,
      );
    }
    if (path === '/parcels/p-1') {
      return json(PARCELS[0]);
    }
    if (path === '/parcels/p-1/history') {
      return json({
        analyses: [{ ...PARCELS[0].latest_analysis, ndvi_series: [{ date: '2022-01-15', ndvi: 0.8 }, { date: '2022-02-15', ndvi: 0.79 }], loss_events: [], provider_versions: { sentinel2: 'mock' } }],
        scores: [{ ...PARCELS[0].latest_score, id: 's1', parcel_id: 'p-1', analysis_run_id: 'a-1', factors: [
          { key: 'deforestation_post_2020', label: 'Déforestation post-2020', weight: 45, raw_value: 0, points: 45, explanation: 'Aucune perte détectée.' },
          { key: 'protected_area_overlap', label: 'Aire protégée', weight: 20, raw_value: 0, points: 20, explanation: 'Hors aire protégée.' },
          { key: 'ndvi_degradation_trend', label: 'Tendance NDVI', weight: 15, raw_value: 0.1, points: 13, explanation: 'Stable.' },
          { key: 'data_completeness', label: 'Complétude', weight: 10, raw_value: 'complète', points: 10, explanation: 'Dossier complet.' },
          { key: 'gps_quality_freshness', label: 'GPS', weight: 10, raw_value: {}, points: 9, explanation: 'Précision 4 m.' },
        ] }],
      });
    }
    if (path === '/reports' && method === 'GET') {
      return json({ items: [], pagination: { page: 1, per_page: 50, total: 0, pages: 0, has_next: false, has_prev: false } });
    }
    if (path === '/reports' && method === 'POST') {
      return json(
        {
          id: 'r1',
          cooperative_id: 'coop-1',
          title: 'Conformité EUDR',
          period_start: '2026-01-01',
          period_end: '2026-12-31',
          parcel_ids: ['p-1', 'p-2'],
          summary: { parcels_total: 5, compliant: 3, at_risk: 1, non_compliant: 1 },
          content_hash: 'a'.repeat(64),
          pdf_key: 'reports/r1/x.pdf',
          geojson_key: 'reports/r1/x.geojson',
          generated_by: 'u1',
          generated_at: '2026-09-10T12:00:00Z',
        },
        201,
      );
    }
    if (path === '/alerts') {
      return json({ items: [], pagination: { page: 1, per_page: 6, total: 0, pages: 0, has_next: false, has_prev: false } });
    }
    if (path === '/cooperatives') {
      return json([{ id: 'coop-1', name: 'Coopérative de Guiglo', code: 'COOPCA-GUIGLO', region: 'Cavally', department: 'Guiglo', contact_name: null, contact_phone: null, contact_email: null, created_at: '2026-01-01T00:00:00Z' }]);
    }
    return json({ error: { code: 'not_mocked', message: path, details: {} } }, 404);
  });
}
