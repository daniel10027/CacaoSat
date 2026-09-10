import { Reveal } from '@/components/motion/Reveal';
import { motion } from 'framer-motion';

const STEPS = [
  {
    year: '2020',
    title: 'La date de référence',
    text: 'Le 31 décembre 2020 devient la ligne rouge : toute parcelle déboisée après cette date rend le cacao non conforme.',
  },
  {
    year: '2024 / 2025',
    title: 'L’EUDR entre en vigueur',
    text: 'Chaque cargaison exportée vers l’UE doit fournir les coordonnées GPS de chaque parcelle et prouver l’absence de déforestation.',
  },
  {
    year: 'Contrôle UE',
    title: 'Vérification par satellite',
    text: 'Les autorités européennes recroisent les parcelles déclarées avec l’imagerie satellite. Sans preuve, l’accès au marché est bloqué.',
  },
];

export function EudrShock() {
  return (
    <section id="eudr" className="relative py-24">
      <div className="container-page">
        <Reveal>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-ci-orange">
            02 — Le choc réglementaire
          </p>
          <h2 className="mt-3 max-w-2xl text-3xl font-bold sm:text-4xl">
            Un nouveau cadre européen qui change tout pour la filière
          </h2>
          <p className="mt-4 max-w-2xl text-sand/65">
            Premier producteur mondial, la Côte d’Ivoire fait face depuis 2024/2025 à une exigence
            inédite. Ce sont les <span className="text-white">petites coopératives</span> qui portent
            le poids de cette mise en conformité — sans outils numériques ni ressources juridiques.
          </p>
        </Reveal>

        <div className="relative mt-14 grid gap-6 md:grid-cols-3">
          <div className="pointer-events-none absolute left-0 right-0 top-8 hidden h-px bg-gradient-to-r from-transparent via-ci-green/40 to-transparent md:block" />
          {STEPS.map((s, i) => (
            <Reveal key={s.year} delay={i * 0.12}>
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="card relative h-full p-6"
              >
                <span className="absolute -top-3 left-6 rounded-full border border-ci-green/40 bg-night px-3 py-0.5 text-xs font-bold text-ci-green">
                  {s.year}
                </span>
                <h3 className="mt-3 text-lg font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-sand/60">{s.text}</p>
              </motion.div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.1}>
          <div className="mt-14 rounded-2xl border-l-4 border-ci-orange bg-night-2/60 p-6">
            <p className="text-sm font-bold uppercase tracking-wide text-ci-orange">Notre conviction</p>
            <p className="mt-2 max-w-3xl text-lg text-sand/80">
              Les données satellites nécessaires existent déjà, gratuitement, en open data. Ce qui
              manque, ce n’est pas la donnée — c’est le <span className="text-white">pipeline</span>{' '}
              qui la relie aux réalités concrètes de chaque coopérative sur le terrain.
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
