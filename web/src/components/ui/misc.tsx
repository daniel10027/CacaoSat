import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/cn';

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-lg bg-white/5',
        'after:absolute after:inset-0 after:-translate-x-full after:animate-shimmer',
        'after:bg-gradient-to-r after:from-transparent after:via-white/10 after:to-transparent',
        className,
      )}
    />
  );
}

export function EmptyState({
  title,
  hint,
  icon,
  action,
}: {
  title: string;
  hint?: string;
  icon?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-white/10 p-10 text-center">
      {icon && <div className="text-sand/40">{icon}</div>}
      <p className="font-medium text-white">{title}</p>
      {hint && <p className="max-w-sm text-sm text-sand/50">{hint}</p>}
      {action}
    </div>
  );
}

export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-sand/80">{label}</span>
      {children}
      {error ? (
        <span className="mt-1 block text-xs text-risk-high">{error}</span>
      ) : hint ? (
        <span className="mt-1 block text-xs text-sand/45">{hint}</span>
      ) : null}
    </label>
  );
}

export function Divider({ className }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('h-px w-full bg-white/10', className)} />;
}
