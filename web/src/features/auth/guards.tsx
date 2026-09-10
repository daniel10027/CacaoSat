import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';
import type { Role } from '@/types/api';
import { Spinner } from '@/components/ui/Spinner';

export function RequireAuth({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  const location = useLocation();

  if (status === 'idle' || status === 'loading') {
    return (
      <div className="grid min-h-screen place-items-center">
        <Spinner label="Vérification de la session…" />
      </div>
    );
  }
  if (status === 'anon') {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <>{children}</>;
}

export function RequireRole({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const hasRole = useAuth((s) => s.hasRole);
  if (!hasRole(...roles)) {
    return <Navigate to="/app/dashboard" replace />;
  }
  return <>{children}</>;
}
