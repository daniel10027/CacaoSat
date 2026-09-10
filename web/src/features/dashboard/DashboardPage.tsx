import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart,
  FileWarning,
  Leaf,
  MapPin,
  ShieldAlert,
  ShieldCheck,
  TriangleAlert,
} from 'lucide-react';
import { api } from '@/lib/api';
import { useAuth } from '@/features/auth/useAuth';
import {
  useAcknowledgeAlert,
  useAlerts,
  useCooperatives,
  useDashboardMap,
  useSummary,
} from '@/features/dashboard/queries';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { KpiCard } from '@/components/ui/KpiCard';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { MapView } from '@/components/map/MapView';
import { ComplianceTrend, RiskDonut, ScoreHistogram } from '@/components/charts/Charts';
import { fmtHa, fmtInt, fmtPct, relativeTime } from '@/lib/format';
import type { Cooperative } from '@/types/api';

const SEV_COLOR: Record<string, string> = {
  low: 'text-sand/50',
  medium: 'text-risk-medium',
  high: 'text-risk-high',
  critical: 'text-risk-high',
};

export default function DashboardPage() {
  const { user, hasRole } = useAuth();
  const national = hasRole('regulator', 'admin', 'exporter');
  const [coopId, setCoopId] = useState<string>('');
  const [showProtected, setShowProtected] = useState(true);

  const coops = useCooperatives();
  const scope = national ? coopId || undefined : (user?.cooperative_id ?? undefined);

  const summary = useSummary(scope);
  const map = useDashboardMap(scope);
  const alerts = useAlerts({ acknowledged: 'false', per_page: 6 });
  const ack = useAcknowledgeAlert();

  const protectedAreas = useQuery({
    queryKey: ['protected-areas'],
    queryFn: () => api<{ protected_areas: GeoJSON.FeatureCollection }>('/sync/bootstrap'),
    staleTime: 10 * 60_000,
  });

  const coopOptions = useMemo(
    () => [
      { value: '', label: national ? 'Toutes les coopératives' : 'Ma coopérative' },
      ...((coops.data as Cooperative[] | undefined)?.map((c) => ({
        value: c.id,
        label: c.name,
      })) ?? []),
    ],
    [coops.data, national],
  );

  return (
    <Page>
      <PageHeader
        title="Tableau de bord"
        subtitle="Conformité EUDR des parcelles cartographiées"
        actions={
          national ? (
            <Select
              options={coopOptions}
              value={coopId}
              onChange={(e) => setCoopId(e.target.value)}
              className="min-w-52"
            />
          ) : null
        }
      />

      <QueryState isLoading={summary.isLoading} error={summary.error} onRetry={summary.refetch}>
        {summary.data && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <KpiCard label="Parcelles" value={summary.data.parcels_total} icon={<MapPin size={16} />} />
              <KpiCard
                label="Surface suivie"
                value={summary.data.area_ha_total}
                suffix="ha"
                icon={<Leaf size={16} />}
              />
              <KpiCard
                label="Conformes"
                value={summary.data.compliant}
                tone="good"
                icon={<ShieldCheck size={16} />}
                hint={fmtPct(
                  summary.data.assessed
                    ? (summary.data.compliant / summary.data.assessed) * 100
                    : 0,
                )}
              />
              <KpiCard
                label="Non conformes"
                value={summary.data.non_compliant}
                tone="bad"
                icon={<ShieldAlert size={16} />}
              />
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <KpiCard
                label="À vérifier"
                value={summary.data.at_risk}
                tone="warn"
                icon={<TriangleAlert size={16} />}
              />
              <KpiCard
                label="Déforestation"
                value={summary.data.deforestation_events}
                tone="bad"
                icon={<FileWarning size={16} />}
                hint="événements post-2020"
              />
              <KpiCard
                label="Surface à haut risque"
                value={summary.data.high_risk_area_ha}
                suffix="ha"
                tone="bad"
              />
              <KpiCard
                label="Couverture d'analyse"
                value={summary.data.coverage_pct}
                suffix="%"
                icon={<AreaChart size={16} />}
              />
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-[1.6fr_1fr]">
              <Card className="overflow-hidden">
                <CardHeader
                  title="Carte des parcelles"
                  subtitle="Vert : conforme · Ambre : à vérifier · Rouge : non conforme"
                  action={
                    <Button
                      variant={showProtected ? 'primary' : 'ghost'}
                      size="sm"
                      onClick={() => setShowProtected((v) => !v)}
                    >
                      Aires protégées
                    </Button>
                  }
                />
                <CardBody>
                  <MapView
                    parcels={map.data ?? undefined}
                    protectedAreas={protectedAreas.data?.protected_areas}
                    showProtected={showProtected}
                    className="h-[440px] w-full rounded-xl"
                  />
                </CardBody>
              </Card>

              <Card>
                <CardHeader
                  title="Alertes récentes"
                  subtitle="Non acquittées"
                  action={
                    <Link to="/app/alertes" className="text-xs text-ci-orange hover:underline">
                      Tout voir
                    </Link>
                  }
                />
                <CardBody className="space-y-2">
                  {alerts.data?.items.length ? (
                    alerts.data.items.map((a) => (
                      <div
                        key={a.id}
                        className="rounded-xl border border-white/10 bg-night/60 p-3 text-sm"
                      >
                        <div className="flex items-center justify-between">
                          <span className={`font-semibold ${SEV_COLOR[a.severity]}`}>
                            {a.parcel_code}
                          </span>
                          <span className="text-[11px] text-sand/40">
                            {relativeTime(a.detected_at)}
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-sand/60">{a.message}</p>
                        <button
                          onClick={() => ack.mutate(a.id)}
                          disabled={ack.isPending}
                          className="mt-2 text-[11px] font-semibold text-ci-green hover:underline"
                        >
                          Acquitter
                        </button>
                      </div>
                    ))
                  ) : (
                    <p className="py-8 text-center text-sm text-sand/45">Aucune alerte en attente.</p>
                  )}
                </CardBody>
              </Card>
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-3">
              <Card>
                <CardHeader title="Distribution des scores" />
                <CardBody>
                  <ScoreHistogram data={summary.data.score_distribution} />
                </CardBody>
              </Card>
              <Card>
                <CardHeader title="Tendance de conformité" subtitle="% conformes par mois" />
                <CardBody>
                  <ComplianceTrend data={summary.data.trend} />
                </CardBody>
              </Card>
              <Card>
                <CardHeader title="Répartition par risque" />
                <CardBody>
                  <RiskDonut data={summary.data.risk_distribution} />
                  <div className="mt-3 flex justify-center gap-4 text-xs text-sand/55">
                    <span>
                      <b className="text-risk-low">{fmtInt(summary.data.risk_distribution.low)}</b>{' '}
                      faible
                    </span>
                    <span>
                      <b className="text-risk-medium">
                        {fmtInt(summary.data.risk_distribution.medium)}
                      </b>{' '}
                      moyen
                    </span>
                    <span>
                      <b className="text-risk-high">{fmtInt(summary.data.risk_distribution.high)}</b>{' '}
                      élevé
                    </span>
                  </div>
                </CardBody>
              </Card>
            </div>
            <p className="mt-4 text-xs text-sand/35">
              Surface totale suivie : {fmtHa(summary.data.area_ha_total)} ·{' '}
              {fmtInt(summary.data.assessed)} parcelles analysées sur{' '}
              {fmtInt(summary.data.parcels_total)}.
            </p>
          </>
        )}
      </QueryState>
    </Page>
  );
}
