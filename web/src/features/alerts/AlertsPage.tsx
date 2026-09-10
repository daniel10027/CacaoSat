import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, RadioTower } from 'lucide-react';
import { useAcknowledgeAlert, useAlerts } from '@/features/dashboard/queries';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { Card } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/misc';
import { toast } from '@/components/ui/Toast';
import { fmtDateTime, relativeTime } from '@/lib/format';

const TYPE_LABEL: Record<string, string> = {
  new_deforestation: 'Nouvelle déforestation',
  protected_encroachment: 'Empiètement aire protégée',
  data_gap: 'Dossier incomplet',
};
const SEV_STYLE: Record<string, string> = {
  low: 'border-white/10 text-sand/50',
  medium: 'border-risk-medium/40 text-risk-medium',
  high: 'border-risk-high/40 text-risk-high',
  critical: 'border-risk-high/60 text-risk-high',
};

export default function AlertsPage() {
  const [ackFilter, setAckFilter] = useState('false');
  const [type, setType] = useState('');
  const [severity, setSeverity] = useState('');
  const { data, isLoading, error, refetch } = useAlerts({
    acknowledged: ackFilter || undefined,
    type: type || undefined,
    severity: severity || undefined,
    per_page: 50,
  });
  const ack = useAcknowledgeAlert();

  return (
    <Page>
      <PageHeader
        title="Alertes précoces"
        subtitle="Déforestation, empiètement d'aires protégées, dossiers incomplets"
      />

      <Card className="mb-4 flex flex-wrap gap-3 p-4">
        <Select
          className="w-44"
          value={ackFilter}
          onChange={(e) => setAckFilter(e.target.value)}
          options={[
            { value: 'false', label: 'Non acquittées' },
            { value: 'true', label: 'Acquittées' },
            { value: '', label: 'Toutes' },
          ]}
        />
        <Select
          className="w-56"
          value={type}
          onChange={(e) => setType(e.target.value)}
          options={[
            { value: '', label: 'Tous types' },
            { value: 'new_deforestation', label: 'Déforestation' },
            { value: 'protected_encroachment', label: 'Aire protégée' },
            { value: 'data_gap', label: 'Dossier incomplet' },
          ]}
        />
        <Select
          className="w-44"
          value={severity}
          onChange={(e) => setSeverity(e.target.value)}
          options={[
            { value: '', label: 'Toutes sévérités' },
            { value: 'critical', label: 'Critique' },
            { value: 'high', label: 'Élevée' },
            { value: 'medium', label: 'Moyenne' },
            { value: 'low', label: 'Faible' },
          ]}
        />
      </Card>

      <QueryState isLoading={isLoading} error={error} onRetry={refetch}>
        {data?.items.length ? (
          <div className="grid gap-3">
            {data.items.map((a) => (
              <Card
                key={a.id}
                className={`flex flex-wrap items-center gap-4 border-l-4 p-4 ${SEV_STYLE[a.severity]}`}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-semibold uppercase tracking-wide">
                      {TYPE_LABEL[a.type] ?? a.type}
                    </span>
                    <Link
                      to={`/app/parcelles/${a.parcel_id}`}
                      className="text-ci-orange hover:underline"
                    >
                      {a.parcel_code}
                    </Link>
                    <span className="text-xs text-sand/35">· {a.severity}</span>
                  </div>
                  <p className="mt-1 text-sm text-sand/70">{a.message}</p>
                  <p className="mt-0.5 text-[11px] text-sand/35">
                    Détectée {relativeTime(a.detected_at)} ({fmtDateTime(a.detected_at)})
                  </p>
                </div>
                {a.acknowledged ? (
                  <span className="inline-flex items-center gap-1 text-xs text-risk-low">
                    <Check size={13} /> Acquittée
                  </span>
                ) : (
                  <Button
                    size="sm"
                    variant="ghost"
                    loading={ack.isPending && ack.variables === a.id}
                    onClick={() =>
                      ack.mutate(a.id, {
                        onSuccess: () => toast.success('Alerte acquittée'),
                      })
                    }
                  >
                    Acquitter
                  </Button>
                )}
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<RadioTower size={28} />}
            title="Aucune alerte"
            hint="Les alertes apparaissent lorsqu'une nouvelle analyse détecte un changement."
          />
        )}
      </QueryState>
    </Page>
  );
}
