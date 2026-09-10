import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Play } from 'lucide-react';
import { api } from '@/lib/api';
import { useAnalyzeParcel, useParcel } from '@/features/dashboard/queries';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { EudrBadge, RiskDot } from '@/components/ui/Badge';
import { MapView } from '@/components/map/MapView';
import { NdviSeries } from '@/components/charts/NdviSeries';
import { toast } from '@/components/ui/Toast';
import { fmtHa, fmtScore, fmtDate, fmtPct } from '@/lib/format';
import type { AnalysisRun, ComplianceScore, EudrStatus } from '@/types/api';

export default function ParcelDetailPage() {
  const { id } = useParams<{ id: string }>();
  const parcel = useParcel(id);
  const analyze = useAnalyzeParcel();

  const history = useQuery({
    queryKey: ['parcel', id, 'history'],
    queryFn: () =>
      api<{ analyses: AnalysisRun[]; scores: ComplianceScore[] }>(`/parcels/${id}/history`),
    enabled: !!id,
  });

  const latestScore = history.data?.scores[0];
  const latestRun = history.data?.analyses[0];

  const fc = useMemo<GeoJSON.FeatureCollection | undefined>(() => {
    if (!parcel.data) return undefined;
    return {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: parcel.data.geometry,
          properties: {
            code: parcel.data.code,
            producer: parcel.data.producer_name,
            area_ha: parcel.data.area_ha,
            score: parcel.data.latest_score?.score ?? null,
            eudr_status: parcel.data.latest_score?.eudr_status ?? 'unassessed',
          },
        },
      ],
    };
  }, [parcel.data]);

  const lossDate = latestRun?.loss_events?.find((e) => 'date' in e)?.['date'] as string | undefined;

  return (
    <Page>
      <Link
        to="/app/parcelles"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-sand/55 hover:text-white"
      >
        <ArrowLeft size={15} /> Toutes les parcelles
      </Link>

      <QueryState isLoading={parcel.isLoading} error={parcel.error} onRetry={parcel.refetch}>
        {parcel.data && (
          <>
            <PageHeader
              title={parcel.data.code}
              subtitle={`${parcel.data.producer_name ?? 'Producteur non rattaché'} · ${fmtHa(parcel.data.area_ha)} · planté ${parcel.data.planting_year ?? '?'}`}
              actions={
                <Button
                  loading={analyze.isPending}
                  onClick={() =>
                    id &&
                    analyze.mutate(id, {
                      onSuccess: (r) =>
                        toast.success(
                          `Analyse : ${r.compliance_score.score.toFixed(0)}/100 (${r.compliance_score.eudr_status})`,
                        ),
                      onError: () => toast.error("Échec de l'analyse"),
                    })
                  }
                >
                  <Play size={15} /> Relancer l'analyse
                </Button>
              }
            />

            <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
              <Card className="overflow-hidden">
                <CardHeader title="Localisation" />
                <CardBody>
                  <MapView parcels={fc} className="h-[360px] w-full rounded-xl" />
                </CardBody>
              </Card>

              <Card>
                <CardHeader title="Score de conformité EUDR" />
                <CardBody>
                  {latestScore ? (
                    <>
                      <div className="flex items-end gap-3">
                        <span className="font-display text-5xl font-bold text-white">
                          {fmtScore(latestScore.score)}
                        </span>
                        <span className="pb-2 text-sand/40">/ 100</span>
                        <div className="ml-auto flex flex-col items-end gap-1">
                          <EudrBadge status={latestScore.eudr_status as EudrStatus} />
                          <RiskDot level={latestScore.risk_level} />
                        </div>
                      </div>
                      <div className="mt-5 space-y-3">
                        {latestScore.factors.map((f) => (
                          <div key={f.key}>
                            <div className="flex justify-between text-xs">
                              <span className="text-sand/70">{f.label}</span>
                              <span className="font-semibold text-white">
                                {f.points.toFixed(1)} / {f.weight}
                              </span>
                            </div>
                            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/8">
                              <div
                                className="h-full rounded-full bg-ci-green"
                                style={{ width: `${(f.points / f.weight) * 100}%` }}
                              />
                            </div>
                            <p className="mt-1 text-[11px] text-sand/45">{f.explanation}</p>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <p className="py-8 text-center text-sm text-sand/45">
                      Aucune analyse. Lancez « Relancer l'analyse ».
                    </p>
                  )}
                </CardBody>
              </Card>
            </div>

            {latestRun && (
              <div className="mt-4 grid gap-4 lg:grid-cols-[1.4fr_1fr]">
                <Card>
                  <CardHeader
                    title="Série NDVI (Sentinel-2)"
                    subtitle="Indice de végétation — une chute nette signale une coupe"
                  />
                  <CardBody>
                    <NdviSeries series={latestRun.ndvi_series} lossDate={lossDate} />
                  </CardBody>
                </Card>
                <Card>
                  <CardHeader title="Analyse satellite" />
                  <CardBody className="space-y-2 text-sm">
                    <Row
                      label="Couvert forestier 2020"
                      value={fmtPct(latestRun.forest_cover_2020_pct ?? undefined)}
                    />
                    <Row
                      label="Couvert forestier actuel"
                      value={fmtPct(latestRun.forest_cover_current_pct ?? undefined)}
                    />
                    <Row label="Perte post-2020" value={fmtHa(latestRun.forest_loss_ha)} />
                    <Row
                      label="Recouvrement aire protégée"
                      value={fmtHa(latestRun.protected_area_overlap_ha)}
                    />
                    <Row
                      label="Déforestation détectée"
                      value={latestRun.deforestation_detected ? 'Oui' : 'Non'}
                    />
                    <Row label="Confiance" value={fmtPct(latestRun.confidence * 100)} />
                    <div className="pt-2 text-[11px] text-sand/35">
                      Sources : {Object.values(latestRun.provider_versions).slice(0, 3).join(' · ')}
                    </div>
                  </CardBody>
                </Card>
              </div>
            )}

            {history.data && history.data.scores.length > 1 && (
              <Card className="mt-4">
                <CardHeader title="Historique des analyses" />
                <CardBody className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs uppercase text-sand/40">
                        <th className="py-2">Date</th>
                        <th className="py-2 text-right">Score</th>
                        <th className="py-2">Statut</th>
                        <th className="py-2 text-right">Perte (ha)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {history.data.scores.map((s, i) => (
                        <tr key={s.id} className="border-t border-white/5">
                          <td className="py-2 text-sand/60">{fmtDate(s.computed_at)}</td>
                          <td className="py-2 text-right text-white">{fmtScore(s.score)}</td>
                          <td className="py-2">
                            <EudrBadge status={s.eudr_status as EudrStatus} />
                          </td>
                          <td className="py-2 text-right text-sand/60">
                            {history.data!.analyses[i]?.forest_loss_ha?.toFixed(2) ?? '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardBody>
              </Card>
            )}
          </>
        )}
      </QueryState>
    </Page>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-white/5 py-1.5">
      <span className="text-sand/55">{label}</span>
      <span className="font-medium text-white">{value}</span>
    </div>
  );
}
