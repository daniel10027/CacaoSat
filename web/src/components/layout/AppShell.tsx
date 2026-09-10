import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  BarChart3,
  Bell,
  Building2,
  FileText,
  Leaf,
  LogOut,
  Map,
  Menu,
  TriangleAlert,
  Users,
  X,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/cn';
import { useAuth } from '@/features/auth/useAuth';
import { OrbitCacao } from '@/components/brand/OrbitCacao';
import { Wordmark } from '@/components/brand/Wordmark';
import { LanguageToggle } from '@/components/layout/LanguageToggle';
import { AlertBell } from '@/components/layout/AlertBell';
import type { Role } from '@/types/api';

interface NavItem {
  to: string;
  key: string;
  icon: typeof Map;
  roles?: Role[];
}

const NAV: NavItem[] = [
  { to: '/app/dashboard', key: 'dashboard', icon: BarChart3 },
  { to: '/app/parcelles', key: 'parcels', icon: Map },
  { to: '/app/producteurs', key: 'producers', icon: Users },
  { to: '/app/rapports', key: 'reports', icon: FileText, roles: ['manager', 'regulator'] },
  { to: '/app/alertes', key: 'alerts', icon: TriangleAlert, roles: ['manager', 'regulator', 'agent'] },
  { to: '/app/cooperatives', key: 'cooperatives', icon: Building2, roles: ['regulator', 'admin'] },
  { to: '/app/methodo', key: 'methodology', icon: Leaf },
];

export function AppShell() {
  const { t } = useTranslation();
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const items = NAV.filter((i) => !i.roles || hasRole(...i.roles));

  const SideContent = (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 px-5 py-5">
        <OrbitCacao size={38} />
        <Wordmark className="text-lg" />
      </div>
      <nav className="flex-1 space-y-1 px-3" aria-label="Navigation principale">
        {items.map(({ to, key, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-ci-orange/15 text-white ring-1 ring-inset ring-ci-orange/30'
                  : 'text-sand/60 hover:bg-white/5 hover:text-white',
              )
            }
          >
            <Icon size={18} />
            {t(`nav.${key}`)}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-white/10 p-4">
        <div className="mb-2 truncate text-xs text-sand/50">
          {user?.full_name} · {user?.role}
        </div>
        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm text-sand/70 hover:bg-white/5 hover:text-white"
        >
          <LogOut size={16} /> {t('nav.logout')}
        </button>
      </div>
    </div>
  );

  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[264px_1fr] bg-night grid-dots">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-[70] focus:rounded-lg focus:bg-ci-orange focus:px-3 focus:py-2 focus:text-sm focus:font-semibold focus:text-white">Aller au contenu</a>
      <aside className="hidden border-r border-white/10 bg-night-2/60 lg:block">{SideContent}</aside>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-black/60 lg:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
            />
            <motion.aside
              className="fixed inset-y-0 left-0 z-50 w-72 border-r border-white/10 bg-night-2 lg:hidden"
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 26, stiffness: 240 }}
            >
              <button
                className="absolute right-3 top-4 text-sand/60"
                onClick={() => setOpen(false)}
                aria-label={t('common.close')}
              >
                <X size={20} />
              </button>
              {SideContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-3 border-b border-white/10 bg-night/80 px-4 py-3 backdrop-blur sm:px-6">
          <button
            className="rounded-lg p-1.5 text-sand/70 hover:bg-white/5 lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Menu"
          >
            <Menu size={20} />
          </button>
          <div className="hidden text-sm text-sand/50 sm:block">
            Coopérative ·{' '}
            <span className="font-medium text-sand/80">
              {user?.cooperative_id ? user.cooperative_id.slice(0, 8) : 'Portée nationale'}
            </span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <AlertBell />
            <LanguageToggle />
          </div>
        </header>
        <main id="main" className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export { Bell };
