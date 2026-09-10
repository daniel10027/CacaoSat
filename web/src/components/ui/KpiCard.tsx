import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';
import { CountUp } from '@/components/motion/CountUp';

export function KpiCard({
  label,
  value,
  suffix,
  icon,
  tone = 'neutral',
  hint,
}: {
  label: string;
  value: number;
  suffix?: string;
  icon?: ReactNode;
  tone?: 'neutral' | 'good' | 'warn' | 'bad';
  hint?: string;
}) {
  const toneRing = {
    neutral: 'ring-white/10',
    good: 'ring-risk-low/30',
    warn: 'ring-risk-medium/30',
    bad: 'ring-risk-high/30',
  }[tone];
  const toneText = {
    neutral: 'text-white',
    good: 'text-risk-low',
    warn: 'text-risk-medium',
    bad: 'text-risk-high',
  }[tone];

  return (
    <div className={cn('rounded-2xl border border-white/10 bg-night-2/70 p-5 ring-1', toneRing)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-sand/50">{label}</span>
        {icon && <span className="text-sand/40">{icon}</span>}
      </div>
      <div className={cn('mt-2 font-display text-3xl font-bold', toneText)}>
        <CountUp value={value} />
        {suffix && <span className="ml-1 text-lg font-semibold text-sand/60">{suffix}</span>}
      </div>
      {hint && <p className="mt-1 text-xs text-sand/45">{hint}</p>}
    </div>
  );
}
