import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { OrbitCacao } from '@/components/brand/OrbitCacao';
import { Wordmark, FlagRibbon } from '@/components/brand/Wordmark';

/**
 * Landing minimale (Lot 4). Version immersive complète au Lot 5.
 */
export default function Landing() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-night">
      <div className="pointer-events-none absolute inset-0 grid-dots opacity-60" />
      <div className="pointer-events-none absolute left-1/2 top-0 h-[600px] w-[900px] -translate-x-1/2 rounded-full bg-ci-green/10 blur-3xl" />

      <header className="container-page flex items-center justify-between py-6">
        <div className="flex items-center gap-2">
          <OrbitCacao size={40} />
          <Wordmark className="text-xl" />
        </div>
        <Link to="/login" className="btn-ghost">
          Espace coopérative
        </Link>
      </header>

      <section className="container-page grid items-center gap-12 py-16 md:grid-cols-2 md:py-24">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-ci-orange">
            Le spatial pour bâtir
          </p>
          <h1 className="mt-4 font-display text-5xl font-extrabold leading-[1.05] sm:text-6xl">
            <span className="text-ci-orange">CACAO</span>
            <span className="text-ci-green">SAT</span>
          </h1>
          <p className="mt-5 max-w-lg text-lg text-sand/70">
            Traçabilité géospatiale du cacao ivoirien : mettre les données satellites libres au
            service de la conformité EUDR et des coopératives locales.
          </p>
          <FlagRibbon className="mt-6 w-40" />
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/login" className="btn-primary">
              Voir le tableau de bord <ArrowRight size={16} />
            </Link>
            <a href="#pipeline" className="btn-ghost">
              Comprendre l'EUDR
            </a>
          </div>
        </div>

        <div className="relative grid place-items-center">
          <div className="absolute inset-0 rounded-full bg-ci-orange/10 blur-3xl" />
          <OrbitCacao size={340} />
        </div>
      </section>

      <section id="pipeline" className="container-page grid grid-cols-2 gap-4 pb-24 sm:grid-cols-4">
        {[
          ['N°1', 'Rang mondial de la Côte d’Ivoire'],
          ['82 %', 'Cacao traçable à la parcelle en 2023'],
          ['~30 %', 'Surface cacaoyère en zone protégée'],
          ['2M+', 'Foyers dépendants de la filière'],
        ].map(([n, label]) => (
          <div key={label} className="card p-5">
            <div className="font-display text-3xl font-bold text-ci-green">{n}</div>
            <div className="mt-1 text-sm text-sand/60">{label}</div>
          </div>
        ))}
      </section>
    </div>
  );
}
