import { useState } from 'react';
import { Copy, Download, FileText, Plus } from 'lucide-react';
import { useCooperatives, useCreateReport, useReports } from '@/features/dashboard/queries';
import { useAuth } from '@/features/auth/useAuth';
import { Page, PageHeader, QueryState } from '@/components/ui/Page';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import { Dialog } from '@/components/ui/Dialog';
import { Field } from '@/components/ui/misc';
import { EmptyState } from '@/components/ui/misc';
import { toast } from '@/components/ui/Toast';
import { fmtDate, fmtDateTime } from '@/lib/format';

export default function ReportsPage() {
  const reports = useReports();
  const create = useCreateReport();
  const user = useAuth((s) => s.user);
  const coops = useCooperatives();
  const [open, setOpen] = useState(false);
  const year = new Date().getFullYear();
  const [start, setStart] = useState(`${year}-01-01`);
  const [end, setEnd] = useState(new Date().toISOString().slice(0, 10));
  const [title, setTitle] = useState('');
  const [coopId, setCoopId] = useState('');

  // Un manager porte sa coopérative dans son token et l'API la déduit seule.
  // Un rôle national (admin, régulateur) n'en a aucune : sans choix explicite,
  // la génération échoue en 422. On lui demande donc la coopérative.
  const needsCoop = !user?.cooperative_id;
  const selectedCoop = needsCoop ? coopId || coops.data?.[0]?.id || '' : '';

  async function tokenizedDownload(reportId: string, format: 'pdf' | 'geojson') {
    // Le téléchargement passe par fetch (Authorization) puis un Blob local.
    const { api } = await import('@/lib/api');
    try {
      const res = await api<Response>(`/reports/${reportId}/download?format=${format}`, {
        raw: true,
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = format === 'pdf' ? 'rapport-conformite-eudr.pdf' : 'parcelles.geojson';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error('Téléchargement impossible');
    }
  }

  return (
    <Page>
      <PageHeader
        title="Rapports de conformité"
        subtitle="Certificats EUDR (PDF + GeoJSON) exploitables par les exportateurs"
        actions={
          <Button onClick={() => setOpen(true)}>
            <Plus size={15} /> Générer un rapport
          </Button>
        }
      />

      <QueryState isLoading={reports.isLoading} error={reports.error} onRetry={reports.refetch}>
        {reports.data?.items.length ? (
          <div className="grid gap-4">
            {reports.data.items.map((r) => (
              <Card key={r.id}>
                <CardHeader
                  title={r.title}
                  subtitle={`Période ${fmtDate(r.period_start)} → ${fmtDate(r.period_end)} · généré le ${fmtDateTime(r.generated_at)}`}
                  action={
                    <div className="flex gap-2">
                      <Button size="sm" variant="ghost" onClick={() => tokenizedDownload(r.id, 'pdf')}>
                        <Download size={13} /> PDF
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => tokenizedDownload(r.id, 'geojson')}
                      >
                        <Download size={13} /> GeoJSON
                      </Button>
                    </div>
                  }
                />
                <CardBody className="flex flex-wrap items-center gap-4 text-sm text-sand/60">
                  <span>
                    <b className="text-white">{r.parcel_ids.length}</b> parcelles
                  </span>
                  {typeof r.summary.compliant === 'number' && (
                    <>
                      <span className="text-risk-low">{String(r.summary.compliant)} conformes</span>
                      <span className="text-risk-medium">
                        {String(r.summary.at_risk ?? 0)} à vérifier
                      </span>
                      <span className="text-risk-high">
                        {String(r.summary.non_compliant ?? 0)} non conformes
                      </span>
                    </>
                  )}
                  <button
                    onClick={() => {
                      void navigator.clipboard.writeText(r.content_hash);
                      toast.info('Empreinte copiée');
                    }}
                    className="ml-auto inline-flex items-center gap-1 font-mono text-xs text-sand/40 hover:text-sand/70"
                  >
                    <Copy size={12} /> {r.content_hash.slice(0, 16)}…
                  </button>
                </CardBody>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<FileText size={28} />}
            title="Aucun rapport généré"
            hint="Générez un certificat de conformité EUDR pour la période de votre choix."
          />
        )}
      </QueryState>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title="Générer un rapport de conformité"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Annuler
            </Button>
            {/* `Button` résout `disabled ?? loading` : isPending est réintégré
                ici, sinon un disabled={false} lèverait le verrou anti-double-clic. */}
            <Button
              size="sm"
              loading={create.isPending}
              disabled={(needsCoop && !selectedCoop) || create.isPending}
              onClick={() =>
                create.mutate(
                  {
                    period_start: start,
                    period_end: end,
                    title: title || undefined,
                    ...(needsCoop ? { cooperative_id: selectedCoop } : {}),
                  },
                  {
                    onSuccess: () => {
                      toast.success('Rapport généré');
                      setOpen(false);
                    },
                    onError: (e) =>
                      toast.error(e instanceof Error ? e.message : 'Échec de la génération'),
                  },
                )
              }
            >
              Générer
            </Button>
          </>
        }
      >
        {needsCoop && (
          <Field
            label="Coopérative"
            hint={
              coops.isLoading
                ? 'Chargement des coopératives…'
                : coops.data?.length
                  ? undefined
                  : 'Aucune coopérative disponible.'
            }
          >
            <Select
              options={(coops.data ?? []).map((c) => ({
                value: c.id,
                label: `${c.name} (${c.code})`,
              }))}
              value={selectedCoop}
              onChange={(e) => setCoopId(e.target.value)}
            />
          </Field>
        )}
        <Field label="Titre (optionnel)">
          <input value={title} onChange={(e) => setTitle(e.target.value)} className="field" />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Début de période">
            <input type="date" value={start} onChange={(e) => setStart(e.target.value)} className="field" />
          </Field>
          <Field label="Fin de période">
            <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} className="field" />
          </Field>
        </div>
        <p className="text-xs text-sand/45">
          Le rapport couvre toutes les parcelles de la coopérative ayant une analyse.
        </p>
      </Dialog>
    </Page>
  );
}
