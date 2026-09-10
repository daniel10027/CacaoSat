import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Building2, Leaf, TrendingUp, Users } from 'lucide-react';
import { Reveal, Stagger, StaggerItem } from '@/components/motion/Reveal';
import { OrbitCacao } from '@/components/brand/OrbitCacao';

const IMPACT = [
  { icon: TrendingUp, t: 'Économique', d: 'Sécuriser l’accès des coopératives au marché européen en réduisant délai et coût de mise en conformité.' },
  { icon: Users, t: 'Social', d: 'Un outil simple et accessible pour les petites coopératives, sans dépendre d’intermédiaires coûteux.' },
  { icon: Leaf, t: 'Environnemental', d: 'Renforcer le suivi continu du couvert forestier autour des zones de production.' },
  { icon: Building2, t: 'Institutionnel', d: 'Fournir au Conseil du Café‑Cacao une base nationale consolidée pour le pilotage des politiques.' },
];

const TEAM = [
  { initials: 'AT', name: 'Akandji Timothé', role: 'Chef de projet & Data Engineering' },
  { initials: 'EK', name: 'Elie Konan', role: 'Traitement géospatial' },
  { initials: 'DG', name: 'Daniel Guedegbe', role: 'Application mobile & terrain' },
];

export function ImpactTeam() {
  return (
    <section className="py-24">
      <div className="container-page">
        <Reveal>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-ci-orange">
            06 — Impact attendu
          </p>
          <h2 className="mt-3 text-3xl font-bold sm:text-4xl">Une réponse à un défi national concret</h2>
        </Reveal>

        <Stagger className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {IMPACT.map((it) => {
            const Icon = it.icon;
            return (
              <StaggerItem key={it.t}>
                <motion.div whileHover={{ y: -6 }} className="card h-full p-6">
                  <Icon className="text-ci-green" size={22} />
                  <h3 className="mt-3 font-semibold">{it.t}</h3>
                  <p className="mt-1.5 text-sm text-sand/60">{it.d}</p>
                </motion.div>
              </StaggerItem>
            );
          })}
        </Stagger>

        <Reveal delay={0.1}>
          <h3 className="mt-20 text-2xl font-bold">Notre équipe</h3>
        </Reveal>
        <Stagger className="mt-6 grid gap-5 sm:grid-cols-3">
          {TEAM.map((m) => (
            <StaggerItem key={m.name}>
              <div className="card flex items-center gap-4 p-5">
                <div className="grid h-12 w-12 place-items-center rounded-xl bg-ci-green/15 font-display font-bold text-ci-green ring-1 ring-inset ring-ci-green/30">
                  {m.initials}
                </div>
                <div>
                  <div className="font-semibold text-white">{m.name}</div>
                  <div className="text-xs text-sand/55">{m.role}</div>
                </div>
              </div>
            </StaggerItem>
          ))}
        </Stagger>

        <Reveal delay={0.1}>
          <div className="mt-20 grid items-center gap-8 rounded-2xl border border-white/10 bg-gradient-to-br from-night-2 to-canopy p-8 md:grid-cols-[1fr_auto] md:p-12">
            <div>
              <h3 className="text-2xl font-bold sm:text-3xl">
                Le spatial, entre les mains de la jeunesse ivoirienne.
              </h3>
              <p className="mt-3 max-w-xl text-sand/65">
                CacaoSat n’est pas un projet théorique : c’est une réponse directe à une exigence déjà
                en vigueur, qui touche des millions de foyers.
              </p>
              <Link to="/login" className="btn-primary mt-6 inline-flex">
                Explorer le tableau de bord
              </Link>
            </div>
            <OrbitCacao size={160} className="mx-auto hidden md:block" />
          </div>
        </Reveal>
      </div>
    </section>
  );
}
