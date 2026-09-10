import type { ReactNode } from 'react';
import { PageTransition } from '@/components/motion/PageTransition';
import { Spinner } from './Spinner';
import { Button } from './Button';

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="font-display text-2xl font-bold text-white sm:text-3xl">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-sand/55">{subtitle}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function Page({ children }: { children: ReactNode }) {
  return <PageTransition>{children}</PageTransition>;
}

export function QueryState({
  isLoading,
  error,
  onRetry,
  children,
}: {
  isLoading: boolean;
  error: unknown;
  onRetry?: () => void;
  children: ReactNode;
}) {
  if (isLoading) {
    return (
      <div className="grid min-h-64 place-items-center">
        <Spinner label="Chargement des données…" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="grid min-h-64 place-items-center gap-3 text-center">
        <p className="text-sm text-risk-high">
          {error instanceof Error ? error.message : 'Erreur de chargement'}
        </p>
        {onRetry && (
          <Button variant="ghost" size="sm" onClick={onRetry}>
            Réessayer
          </Button>
        )}
      </div>
    );
  }
  return <>{children}</>;
}
