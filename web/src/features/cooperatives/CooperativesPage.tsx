import { useCooperatives } from '@/features/dashboard/queries';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';

export default function CooperativesPage() {
  const { data, isLoading, error, refetch } = useCooperatives();

  return (
    <Page>
      <PageHeader title="Coopératives" subtitle="Réseau de coopératives suivies" />
      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.map((c) => (
            <Card key={c.id}>
              <CardHeader title={c.name} subtitle={`${c.code} · ${c.region ?? '—'}`} />
              <CardBody className="space-y-1 text-sm text-sand/60">
                <div>Département : {c.department ?? '—'}</div>
                <div>Contact : {c.contact_name ?? '—'}</div>
                <div>{c.contact_phone ?? '—'}</div>
                <div className="text-ci-orange">{c.contact_email ?? ''}</div>
              </CardBody>
            </Card>
          ))}
        </div>
      </QueryState>
    </Page>
  );
}
