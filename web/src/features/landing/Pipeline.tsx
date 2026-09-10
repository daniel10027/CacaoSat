import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import { FileCheck2, Layers, MapPinned, Radar, Satellite, Siren } from 'lucide-react';
import { Reveal } from '@/components/motion/Reveal';

const STEPS = [
  { icon: MapPinned, t: 'Cartographie participative', d: 'Les agents relèvent le contour GPS de chaque parcelle, hors‑ligne, depuis l’application mobile.' },
  { icon: Layers, t: 'Ingestion & structuration', d: 'Les polygones sont centralisés dans une base géospatiale unique, standardisée et interopérable.' },
  { icon: Satellite, t: 'Croisement satellite', d: 'Chaque parcelle est comparée à Sentinel‑2, Hansen/GFW et Digital Earth Africa depuis fin 2020.' },
  { icon: Radar, t: 'Scoring de conformité', d: 'Un score EUDR pondéré et explicable est calculé, avec identification des zones à risque.' },
  { icon: FileCheck2, t: 'Rapport de conformité', d: 'Un certificat exportable (PDF + GeoJSON) est généré en minutes plutôt qu’en semaines.' },
  { icon: Siren, t: 'Alerte précoce', d: 'Toute nouvelle activité de déforestation près des parcelles déclenche une alerte automatique.' },
];

export function Pipeline() {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start 0.8', 'end 0.4'] });
  const pathLength = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <section className="relative py-24">
      <div className="container-page">
        <Reveal>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-ci-orange">
            03 — La solution
          </p>
          <h2 className="mt-3 max-w-2xl text-3xl font-bold sm:text-4xl">
            Le pipeline CacaoSat, du terrain au certificat
          </h2>
        </Reveal>

        <div ref={ref} className="relative mt-16">
          {/* ligne orbitale tracée au scroll */}
          <svg
            aria-hidden
            className="pointer-events-none absolute left-1/2 top-0 hidden h-full w-24 -translate-x-1/2 lg:block"
            viewBox="0 0 100 1000"
            preserveAspectRatio="none"
          >
            <motion.path
              d="M50 0 C 90 160, 10 320, 50 480 S 90 800, 50 1000"
              fill="none"
              stroke="url(#pl-grad)"
              strokeWidth="2.5"
              style={reduce ? undefined : { pathLength }}
            />
            <defs>
              <linearGradient id="pl-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#FF7A00" />
                <stop offset="1" stopColor="#00A651" />
              </linearGradient>
            </defs>
          </svg>

          <div className="grid gap-5 lg:grid-cols-2">
            {STEPS.map((s, i) => {
              const Icon = s.icon;
              return (
                <Reveal key={s.t} delay={(i % 2) * 0.06} className={i % 2 ? 'lg:mt-16' : ''}>
                  <div className="card group flex gap-4 p-6 transition-colors hover:border-ci-orange/30">
                    <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-ci-orange/15 text-ci-orange ring-1 ring-inset ring-ci-orange/30">
                      <Icon size={20} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-display text-sm font-bold text-sand/40">
                          0{i + 1}
                        </span>
                        <h3 className="text-lg font-semibold">{s.t}</h3>
                      </div>
                      <p className="mt-1.5 text-sm text-sand/60">{s.d}</p>
                    </div>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
