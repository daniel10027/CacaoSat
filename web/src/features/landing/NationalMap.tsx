import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import type { RegionsResponse } from '@/types/api';
import { Reveal } from '@/components/motion/Reveal';
import { fmtHa, fmtInt } from '@/lib/format';

// Contour schématique de la Côte d'Ivoire (stylisé, viewBox 0 0 400 360).
const CI_PATH =
  'M64 96 L150 60 L214 40 L300 66 L338 120 L356 210 L326 300 L300 330 L210 336 L150 322 L96 300 L70 226 L58 160 Z';

// Pôles cacao approximatifs (x,y dans le viewBox) + région correspondante.
const POLES = [
  { key: 'Cavally', x: 96, y: 236 },
  { key: 'Nawa', x: 150, y: 262 },
  { key: 'Gôh', x: 196, y: 232 },
  { key: 'Indénié-Djuablin', x: 292, y: 190 },
  { key: 'Sud-Comoé', x: 300, y: 292 },
  { key: 'Marahoué', x: 206, y: 168 },
];

export function NationalMap() {
  const { data } = useQuery({
    queryKey: ['regions'],
    queryFn: () => api<RegionsResponse>('/dashboard/regions', { auth: false }),
    staleTime: 5 * 60_000,
    retry: 1,
  });

  const regions = data?.regions ?? [];
  const byRegion = new Map(regions.map((r) => [r.region, r]));
  const live = regions.reduce(
    (acc, r) => ({
      parcels: acc.parcels + r.parcels,
      area: acc.area + r.area_ha,
      compliant: acc.compliant + r.compliant,
    }),
    { parcels: 0, area: 0, compliant: 0 },
  );
  // Repli si l'API n'est pas jointe : chiffres de référence de la zone pilote.
  const totals = live.parcels > 0 ? live : { parcels: 41, area: 135.3, compliant: 21 };

  return (
    <section className="relative overflow-hidden py-24">
      <div className="absolute left-1/2 top-1/2 h-[70vh] w-[70vh] -translate-x-1/2 -translate-y-1/2 rounded-full bg-ci-green/10 blur-[120px]" />
      <div className="container-page relative grid items-center gap-12 lg:grid-cols-2">
        <Reveal>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-ci-orange">
            04 — À l’échelle nationale
          </p>
          <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
            Une base consolidée, région par région
          </h2>
          <p className="mt-4 max-w-lg text-sand/65">
            Les agrégats proviennent directement de l’API CacaoSat. Chaque pôle de production
            s’illumine selon le volume de parcelles cartographiées et leur statut de conformité.
          </p>
          <div className="mt-8 grid grid-cols-3 gap-4">
            {[
              ['Parcelles', fmtInt(totals.parcels)],
              ['Surface suivie', fmtHa(totals.area)],
              ['Conformes', fmtInt(totals.compliant)],
            ].map(([l, v]) => (
              <div key={l} className="card p-4">
                <div className="font-display text-2xl font-bold text-white">{v}</div>
                <div className="mt-1 text-xs text-sand/50">{l}</div>
              </div>
            ))}
          </div>
          <p className="mt-4 text-xs text-sand/40">Vue schématique — zone pilote : région du Cavally.</p>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="relative mx-auto max-w-md">
            <svg viewBox="0 0 400 360" className="w-full">
              <defs>
                <linearGradient id="ci-fill" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stopColor="#0E211A" />
                  <stop offset="1" stopColor="#08130E" />
                </linearGradient>
              </defs>
              <motion.path
                d={CI_PATH}
                fill="url(#ci-fill)"
                stroke="#00A651"
                strokeWidth="1.5"
                strokeOpacity="0.5"
                initial={{ pathLength: 0, opacity: 0 }}
                whileInView={{ pathLength: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.4, ease: 'easeInOut' }}
              />
              {POLES.map((p, i) => {
                const r = byRegion.get(p.key);
                const active = (r?.parcels ?? 0) > 0;
                const total = r ? r.compliant + r.at_risk + r.non_compliant : 0;
                const compRatio = total ? r!.compliant / total : 0;
                const color = !active
                  ? '#9AA0A6'
                  : compRatio > 0.66
                    ? '#00A651'
                    : compRatio > 0.33
                      ? '#E8A33D'
                      : '#C0392B';
                return (
                  <g key={p.key}>
                    {active && (
                      <motion.circle
                        cx={p.x}
                        cy={p.y}
                        r={14}
                        fill={color}
                        opacity={0.25}
                        animate={{ r: [10, 20, 10], opacity: [0.3, 0, 0.3] }}
                        transition={{ duration: 3, repeat: Infinity, delay: i * 0.3 }}
                      />
                    )}
                    <motion.circle
                      cx={p.x}
                      cy={p.y}
                      r={active ? 5.5 : 3}
                      fill={color}
                      initial={{ scale: 0 }}
                      whileInView={{ scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: 0.6 + i * 0.1, type: 'spring', stiffness: 300 }}
                    />
                    <text x={p.x + 10} y={p.y + 4} fontSize="9" fill="#F4EAD5" opacity={0.75}>
                      {p.key}
                      {active ? ` · ${r!.parcels}` : ''}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
