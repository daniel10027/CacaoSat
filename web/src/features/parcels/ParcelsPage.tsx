import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useSearchParams } from 'react-router-dom';
import { Play, Search } from 'lucide-react';
import { useAnalyzeParcel, useParcels, type ParcelFilters } from '@/features/dashboard/queries';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { Card } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { EudrBadge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/misc';
import { toast } from '@/components/ui/Toast';
import { fmtHa, fmtScore, fmtDate } from '@/lib/format';
import type { EudrStatus } from '@/types/api';

const RISK_OPTS = [
  { value: '', label: 'Tous risques' },
  { value: 'low', label: 'Risque faible' },
  { value: 'medium', label: 'Risque moyen' },
  { value: 'high', label: 'Risque élevé' },
];
const EUDR_OPTS = [
  { value: '', label: 'Tous statuts' },
  { value: 'compliant', label: 'Conforme' },
  { value: 'at_risk', label: 'À vérifier' },
  { value: 'non_compliant', label: 'Non conforme' },
];

export default function ParcelsPage() {
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get('q') ?? '');

  const filters: ParcelFilters = {
    page: Number(params.get('page') ?? 1),
    per_page: 20,
    q: params.get('q') ?? undefined,
    risk_level: params.get('risk_level') ?? undefined,
    eudr_status: params.get('eudr_status') ?? undefined,
    sort: params.get('sort') ?? 'code',
    order: params.get('order') ?? 'asc',
  };

  const set = (patch: Record<string, string>) => {
    const next = new URLSearchParams(params);
    for (const [k, v] of Object.entries(patch)) {
      if (v) next.set(k, v);
      else next.delete(k);
    }
    if (!('page' in patch)) next.set('page', '1');
    setParams(next);
  };

  const { data, isLoading, error, refetch, isFetching } = useParcels(filters);
  const analyze = useAnalyzeParcel();

  return (
    <Page>
      <PageHeader
        title="Parcelles"
        subtitle="Relevés terrain et statut de conformité EUDR"
      />

      <Card className="mb-4 flex flex-wrap items-center gap-3 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            set({ q });
          }}
          className="relative flex-1 min-w-52"
        >
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-sand/40" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Rechercher un code de parcelle…"
            className="field pl-9"
          />
        </form>
        <Select
          options={RISK_OPTS}
          value={filters.risk_level ?? ''}
          onChange={(e) => set({ risk_level: e.target.value })}
          className="w-44"
        />
        <Select
          options={EUDR_OPTS}
          value={filters.eudr_status ?? ''}
          onChange={(e) => set({ eudr_status: e.target.value })}
          className="w-44"
        />
      </Card>

      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left text-xs uppercase tracking-wide text-sand/45">
                  <th className="px-4 py-3">Code</th>
                  <th className="px-4 py-3">Producteur</th>
                  <th className="px-4 py-3 text-right">Surface</th>
                  <th className="px-4 py-3 text-right">Score</th>
                  <th className="px-4 py-3">Statut EUDR</th>
                  <th className="px-4 py-3">Dernière analyse</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className={isFetching ? 'opacity-60' : ''}>
                {data?.items.map((p) => (
                  <tr key={p.id} className="border-b border-white/5 hover:bg-white/[0.03]">
                    <td className="px-4 py-3">
                      <Link
                        to={`/app/parcelles/${p.id}`}
                        className="font-medium text-white hover:text-ci-orange"
                      >
                        {p.code}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sand/70">{p.producer_name ?? '—'}</td>
                    <td className="px-4 py-3 text-right text-sand/70">{fmtHa(p.area_ha)}</td>
                    <td className="px-4 py-3 text-right font-semibold text-white">
                      {fmtScore(p.latest_score?.score ?? null)}
                    </td>
                    <td className="px-4 py-3">
                      <EudrBadge status={(p.latest_score?.eudr_status ?? 'unassessed') as EudrStatus} />
                    </td>
                    <td className="px-4 py-3 text-xs text-sand/50">
                      {fmtDate(p.latest_analysis?.created_at ?? null)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        loading={analyze.isPending && analyze.variables === p.id}
                        onClick={() =>
                          analyze.mutate(p.id, {
                            onSuccess: (r) =>
                              toast.success(
                                `${p.code} : ${r.compliance_score.score.toFixed(0)}/100 — ${r.compliance_score.eudr_status}`,
                              ),
                            onError: () => toast.error(`Échec de l'analyse de ${p.code}`),
                          })
                        }
                      >
                        <Play size={13} /> Analyser
                      </Button>
                    </td>
                  </tr>
                ))}
                {isLoading &&
                  Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i}>
                      <td colSpan={7} className="px-4 py-3">
                        <Skeleton className="h-5 w-full" />
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {data && (
            <div className="flex items-center justify-between border-t border-white/10 px-4 py-3 text-sm text-sand/55">
              <span>
                {data.pagination.total} parcelles · page {data.pagination.page}/
                {data.pagination.pages}
              </span>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!data.pagination.has_prev}
                  onClick={() => set({ page: String(data.pagination.page - 1) })}
                >
                  Précédent
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!data.pagination.has_next}
                  onClick={() => set({ page: String(data.pagination.page + 1) })}
                >
                  Suivant
                </Button>
              </div>
            </div>
          )}
        </Card>
      </QueryState>
    </Page>
  );
}
