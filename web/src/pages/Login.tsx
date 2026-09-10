import { useState, type FormEvent } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { useAuth } from '@/features/auth/useAuth';
import { ApiError } from '@/lib/api';
import { OrbitCacao } from '@/components/brand/OrbitCacao';
import { Wordmark, FlagRibbon } from '@/components/brand/Wordmark';
import { Button } from '@/components/ui/Button';
import { Field } from '@/components/ui/misc';

const DEMO = [
  { label: 'Manager', email: 'manager1@cacaosat.ci' },
  { label: 'Agent', email: 'agent1a@cacaosat.ci' },
  { label: 'Régulateur', email: 'regulateur@conseilcafecacao.ci' },
];

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuth((s) => s.login);
  const [email, setEmail] = useState('manager1@cacaosat.ci');
  const [password, setPassword] = useState('cacaosat');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as { from?: string } | null)?.from ?? '/app/dashboard';

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('auth.error'));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative grid min-h-screen place-items-center overflow-hidden bg-night grid-dots px-4">
      <div className="pointer-events-none absolute -left-40 top-1/2 h-[520px] w-[520px] -translate-y-1/2 rounded-full bg-ci-green/10 blur-3xl" />
      <div className="pointer-events-none absolute -right-40 top-10 h-[420px] w-[420px] rounded-full bg-ci-orange/10 blur-3xl" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md rounded-2xl2 border border-white/10 bg-night-2/80 p-8 shadow-card backdrop-blur"
      >
        <div className="mb-6 flex flex-col items-center text-center">
          <OrbitCacao size={120} />
          <Wordmark className="mt-3 text-2xl" />
          <FlagRibbon className="mt-3 w-24" />
          <p className="mt-4 text-sm text-sand/60">{t('auth.subtitle')}</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <Field label={t('auth.email')}>
            <input
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="field"
            />
          </Field>
          <Field label={t('auth.password')} error={error ?? undefined}>
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="field"
            />
          </Field>
          <Button type="submit" loading={loading} className="w-full">
            {loading ? t('auth.loading') : t('auth.submit')}
            {!loading && <ArrowRight size={16} />}
          </Button>
        </form>

        <div className="mt-6 border-t border-white/10 pt-4">
          <p className="mb-2 text-xs uppercase tracking-wide text-sand/40">{t('auth.demo')}</p>
          <div className="flex flex-wrap gap-2">
            {DEMO.map((d) => (
              <button
                key={d.email}
                onClick={() => {
                  setEmail(d.email);
                  setPassword('cacaosat');
                }}
                className="rounded-lg border border-white/10 px-2.5 py-1 text-xs text-sand/70 hover:border-ci-orange/40 hover:text-white"
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>

        <Link
          to="/"
          className="mt-6 block text-center text-xs text-sand/40 hover:text-sand/70"
        >
          ← Retour au site
        </Link>
      </motion.div>
    </div>
  );
}
