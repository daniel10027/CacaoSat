import { Reveal } from '@/components/motion/Reveal';
import { CountUp } from '@/components/motion/CountUp';

const STATS: Array<{ value: number; decimals?: number; prefix?: string; suffix?: string; label: string }> = [
  { value: 1, prefix: 'N°', label: 'Rang mondial de la Côte d’Ivoire pour la production de cacao' },
  { value: 82, suffix: ' %', label: 'du cacao sourcé directement traçable à la parcelle en 2023' },
  { value: 30, prefix: '~', suffix: ' %', label: 'de la surface cacaoyère estimée en zone protégée' },
  { value: 2, suffix: 'M+', label: 'foyers dépendants de la filière en Afrique de l’Ouest' },
];

export function StatsBar() {
  return (
    <section className="border-y border-white/10 bg-night-2/40">
      <div className="container-page grid gap-6 py-14 sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map((s, i) => (
          <Reveal key={s.label} delay={i * 0.08}>
            <div className="font-display text-4xl font-extrabold text-ci-green sm:text-5xl">
              {s.prefix}
              <CountUp value={s.value} decimals={s.decimals ?? 0} />
              {s.suffix}
            </div>
            <p className="mt-2 text-sm text-sand/60">{s.label}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
