import { cn } from '@/lib/cn';
import { EUDR_LABEL, RISK_LABEL } from '@/lib/format';
import type { EudrStatus, RiskLevel } from '@/types/api';

const EUDR_STYLE: Record<EudrStatus, string> = {
  compliant: 'bg-risk-low/15 text-risk-low ring-1 ring-inset ring-risk-low/30',
  at_risk: 'bg-risk-medium/15 text-risk-medium ring-1 ring-inset ring-risk-medium/30',
  non_compliant: 'bg-risk-high/15 text-risk-high ring-1 ring-inset ring-risk-high/30',
  unassessed: 'bg-white/5 text-sand/60 ring-1 ring-inset ring-white/10',
};

export function EudrBadge({ status, className }: { status: EudrStatus; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold',
        EUDR_STYLE[status] ?? EUDR_STYLE.unassessed,
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {EUDR_LABEL[status] ?? status}
    </span>
  );
}

const RISK_STYLE: Record<RiskLevel, string> = {
  low: 'text-risk-low',
  medium: 'text-risk-medium',
  high: 'text-risk-high',
};

export function RiskDot({ level }: { level: RiskLevel }) {
  return (
    <span className={cn('inline-flex items-center gap-1.5 text-xs font-medium', RISK_STYLE[level])}>
      <span className="h-2 w-2 rounded-full bg-current" />
      {RISK_LABEL[level] ?? level}
    </span>
  );
}
