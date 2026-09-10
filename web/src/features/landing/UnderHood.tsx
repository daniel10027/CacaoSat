import { Reveal, Stagger, StaggerItem } from '@/components/motion/Reveal';
import { BadgeCheck } from 'lucide-react';

const SOURCES = [
  { name: 'Sentinel‑2', org: 'Copernicus (ESA)', use: 'Imagerie optique 10 m — séries temporelles NDVI' },
  { name: 'Hansen / Global Forest Watch', org: 'University of Maryland', use: 'Couvert arboré et perte annuelle, référence fin 2020' },
  { name: 'Digital Earth Africa', org: 'DE Africa', use: 'Suivi de la dégradation des terres' },
];

export function UnderHood() {
  return (
    <section className="py-24">
      <div className="container-page">
        <Reveal>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-ci-orange">
            05 — Sous le capot
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <h2 className="text-3xl font-bold sm:text-4xl">100 % open data, coût d’infrastructure minimal</h2>
            <span className="chip bg-ci-green/15 text-ci-green ring-1 ring-inset ring-ci-green/30">
              <BadgeCheck size={14} /> Sources libres
            </span>
          </div>
        </Reveal>

        <Stagger className="mt-12 grid gap-5 md:grid-cols-3">
          {SOURCES.map((s) => (
            <StaggerItem key={s.name}>
              <div className="card h-full p-6">
                <div className="font-display text-lg font-semibold text-white">{s.name}</div>
                <div className="mt-0.5 text-xs uppercase tracking-wide text-ci-green">{s.org}</div>
                <p className="mt-3 text-sm text-sand/60">{s.use}</p>
              </div>
            </StaggerItem>
          ))}
        </Stagger>

        <Reveal delay={0.1}>
          <p className="mt-10 max-w-3xl text-sand/55">
            Pour la démonstration du hackathon, ces fournisseurs sont simulés de façon déterministe.
            L’architecture — application mobile de collecte, base géospatiale PostGIS, moteur de
            traitement Python, tableau de bord web — est conçue pour brancher les flux réels sans
            changement de contrat d’API.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
