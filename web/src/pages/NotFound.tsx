import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { OrbitCacao } from '@/components/brand/OrbitCacao';

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <div className="grid min-h-screen place-items-center bg-night grid-dots px-4 text-center">
      <div>
        <OrbitCacao size={160} className="mx-auto" />
        <h1 className="mt-4 font-display text-4xl font-bold">404</h1>
        <p className="mt-2 text-lg text-white">{t('notFound.title')}</p>
        <p className="mt-1 text-sm text-sand/50">{t('notFound.text')}</p>
        <Link to="/" className="btn-primary mt-6 inline-flex">
          {t('notFound.home')}
        </Link>
      </div>
    </div>
  );
}
