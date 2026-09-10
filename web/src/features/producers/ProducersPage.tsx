import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search } from 'lucide-react';
import { useProducers } from '@/features/dashboard/queries';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { fmtDate } from '@/lib/format';

export default function ProducersPage() {
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get('q') ?? '');
  const page = Number(params.get('page') ?? 1);

  const { data, isLoading, error, refetch } = useProducers({
    page,
    per_page: 25,
    q: params.get('q') ?? undefined,
    sort: 'full_name',
  });

  const setPage = (p: number) => {
    const n = new URLSearchParams(params);
    n.set('page', String(p));
    setParams(n);
  };

  return (
    <Page>
      <PageHeader title="Producteurs" subtitle="Registre des producteurs de la coopérative" />

      <Card className="mb-4 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            const n = new URLSearchParams(params);
            if (q) n.set('q', q);
            else n.delete('q');
            n.set('page', '1');
            setParams(n);
          }}
          className="relative max-w-md"
        >
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-sand/40" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Nom, pièce d'identité, village…"
            className="field pl-9"
          />
        </form>
      </Card>

      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left text-xs uppercase text-sand/45">
                  <th className="px-4 py-3">Nom</th>
                  <th className="px-4 py-3">Pièce d'identité</th>
                  <th className="px-4 py-3">Village</th>
                  <th className="px-4 py-3 text-right">Parcelles</th>
                  <th className="px-4 py-3">Enregistré</th>
                </tr>
              </thead>
              <tbody>
                {data?.items.map((p) => (
                  <tr key={p.id} className="border-b border-white/5 hover:bg-white/[0.03]">
                    <td className="px-4 py-3 font-medium text-white">{p.full_name}</td>
                    <td className="px-4 py-3 font-mono text-xs text-sand/55">
                      {p.national_id ?? (
                        <span className="text-risk-medium">manquante</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sand/60">{p.village ?? '—'}</td>
                    <td className="px-4 py-3 text-right text-sand/70">{p.parcels_count ?? 0}</td>
                    <td className="px-4 py-3 text-xs text-sand/45">{fmtDate(p.registered_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data && (
            <div className="flex items-center justify-between border-t border-white/10 px-4 py-3 text-sm text-sand/55">
              <span>
                {data.pagination.total} producteurs · page {data.pagination.page}/
                {data.pagination.pages}
              </span>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!data.pagination.has_prev}
                  onClick={() => setPage(page - 1)}
                >
                  Précédent
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!data.pagination.has_next}
                  onClick={() => setPage(page + 1)}
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
