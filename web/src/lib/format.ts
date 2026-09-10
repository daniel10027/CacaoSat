const nf = new Intl.NumberFormat('fr-FR');
const nf1 = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 1 });
const nf2 = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });

export const fmtInt = (n: number | null | undefined): string => (n == null ? '—' : nf.format(n));
export const fmtHa = (n: number | null | undefined): string =>
  n == null ? '—' : `${nf2.format(n)} ha`;
export const fmtPct = (n: number | null | undefined): string =>
  n == null ? '—' : `${nf1.format(n)} %`;
export const fmtScore = (n: number | null | undefined): string =>
  n == null ? '—' : nf1.format(n);

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

export function fmtDateTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function relativeTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.round(diff / 60000);
  if (min < 1) return "à l'instant";
  if (min < 60) return `il y a ${min} min`;
  const h = Math.round(min / 60);
  if (h < 24) return `il y a ${h} h`;
  const j = Math.round(h / 24);
  return `il y a ${j} j`;
}

export const EUDR_LABEL: Record<string, string> = {
  compliant: 'Conforme',
  at_risk: 'À vérifier',
  non_compliant: 'Non conforme',
  unassessed: 'Non évaluée',
};

export const RISK_LABEL: Record<string, string> = {
  low: 'Faible',
  medium: 'Moyen',
  high: 'Élevé',
};

export const EUDR_COLOR: Record<string, string> = {
  compliant: '#00A651',
  at_risk: '#E8A33D',
  non_compliant: '#C0392B',
  unassessed: '#9AA0A6',
};
