import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RequireAuth, RequireRole } from '@/features/auth/guards';
import { AppShell } from '@/components/layout/AppShell';
import { Spinner } from '@/components/ui/Spinner';
import { Placeholder } from '@/pages/Placeholder';

const Landing = lazy(() => import('@/pages/Landing'));
const Login = lazy(() => import('@/pages/Login'));
const NotFound = lazy(() => import('@/pages/NotFound'));

const fallback = (
  <div className="grid min-h-screen place-items-center bg-night">
    <Spinner label="Chargement…" />
  </div>
);

const page = (node: React.ReactNode) => <Suspense fallback={fallback}>{node}</Suspense>;

export const router = createBrowserRouter([
  { path: '/', element: page(<Landing />) },
  { path: '/login', element: page(<Login />) },
  {
    path: '/app',
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/app/dashboard" replace /> },
      { path: 'dashboard', element: <Placeholder title="Tableau de bord" /> },
      { path: 'parcelles', element: <Placeholder title="Parcelles" /> },
      { path: 'parcelles/:id', element: <Placeholder title="Détail parcelle" /> },
      { path: 'producteurs', element: <Placeholder title="Producteurs" /> },
      {
        path: 'rapports',
        element: (
          <RequireRole roles={['manager', 'regulator']}>
            <Placeholder title="Rapports" />
          </RequireRole>
        ),
      },
      { path: 'alertes', element: <Placeholder title="Alertes" /> },
      {
        path: 'cooperatives',
        element: (
          <RequireRole roles={['regulator', 'admin']}>
            <Placeholder title="Coopératives" />
          </RequireRole>
        ),
      },
      { path: 'methodo', element: <Placeholder title="Méthodologie" /> },
    ],
  },
  { path: '*', element: page(<NotFound />) },
]);
