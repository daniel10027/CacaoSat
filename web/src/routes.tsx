import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RequireAuth, RequireRole } from '@/features/auth/guards';
import { AppShell } from '@/components/layout/AppShell';
import { Spinner } from '@/components/ui/Spinner';

const Landing = lazy(() => import('@/pages/Landing'));
const Login = lazy(() => import('@/pages/Login'));
const NotFound = lazy(() => import('@/pages/NotFound'));
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage'));
const ParcelsPage = lazy(() => import('@/features/parcels/ParcelsPage'));
const ParcelDetailPage = lazy(() => import('@/features/parcels/ParcelDetailPage'));
const ProducersPage = lazy(() => import('@/features/producers/ProducersPage'));
const ReportsPage = lazy(() => import('@/features/reports/ReportsPage'));
const AlertsPage = lazy(() => import('@/features/alerts/AlertsPage'));
const CooperativesPage = lazy(() => import('@/features/cooperatives/CooperativesPage'));
const Methodology = lazy(() => import('@/pages/Methodology'));

const fallback = (
  <div className="grid min-h-screen place-items-center bg-night">
    <Spinner label="Chargement…" />
  </div>
);
const P = (node: React.ReactNode) => <Suspense fallback={fallback}>{node}</Suspense>;

export const router = createBrowserRouter([
  { path: '/', element: P(<Landing />) },
  { path: '/login', element: P(<Login />) },
  {
    path: '/app',
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/app/dashboard" replace /> },
      { path: 'dashboard', element: P(<DashboardPage />) },
      { path: 'parcelles', element: P(<ParcelsPage />) },
      { path: 'parcelles/:id', element: P(<ParcelDetailPage />) },
      { path: 'producteurs', element: P(<ProducersPage />) },
      {
        path: 'rapports',
        element: (
          <RequireRole roles={['manager', 'regulator']}>{P(<ReportsPage />)}</RequireRole>
        ),
      },
      { path: 'alertes', element: P(<AlertsPage />) },
      {
        path: 'cooperatives',
        element: (
          <RequireRole roles={['regulator', 'admin']}>{P(<CooperativesPage />)}</RequireRole>
        ),
      },
      { path: 'methodo', element: P(<Methodology />) },
    ],
  },
  { path: '*', element: P(<NotFound />) },
]);
