import { useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useScroll,
  useSpring,
  useTransform,
} from 'framer-motion';
import { ArrowRight, Radar } from 'lucide-react';
import { OrbitCacao } from '@/components/brand/OrbitCacao';
import { FlagRibbon } from '@/components/brand/Wordmark';

export function Hero() {
  const ref = useRef<HTMLElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const lift = useTransform(scrollYProgress, [0, 1], [0, -80]);

  const mx = useSpring(useMotionValue(0), { stiffness: 60, damping: 20 });
  const my = useSpring(useMotionValue(0), { stiffness: 60, damping: 20 });
  const podX = useTransform(mx, [-0.5, 0.5], [-22, 22]);
  const podY = useTransform(my, [-0.5, 0.5], [-14, 14]);

  function onMove(e: React.MouseEvent) {
    if (reduce) return;
    const r = (e.currentTarget as HTMLElement).getBoundingClientRect();
    mx.set((e.clientX - r.left) / r.width - 0.5);
    my.set((e.clientY - r.top) / r.height - 0.5);
  }

  return (
    <section
      ref={ref}
      onMouseMove={onMove}
      className="relative flex min-h-[100svh] items-center overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-b from-night via-canopy to-night" />
      <div className="absolute inset-0 grid-dots opacity-40" />
      <motion.div
        aria-hidden
        className="absolute left-1/2 top-[-10%] h-[70vh] w-[70vw] -translate-x-1/2 rounded-full bg-ci-green/12 blur-[120px]"
        style={reduce ? undefined : { y: lift }}
      />
      <div className="absolute -right-40 bottom-0 h-[50vh] w-[50vh] rounded-full bg-ci-orange/12 blur-[120px]" />

      <div className="container-page relative grid items-center gap-10 py-24 md:grid-cols-[1.05fr_0.95fr]">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-ci-orange">
            <Radar size={13} /> Le spatial pour bâtir
          </p>

          <h1
            className="mt-5 font-display text-[clamp(3rem,9vw,6.5rem)] font-extrabold leading-[0.95]"
          >
            <span className="text-ci-orange">CACAO</span>
            <span className="text-ci-green">SAT</span>
          </h1>

          <p
            className="mt-6 max-w-xl text-lg text-sand/75 sm:text-xl"
          >
            Traçabilité géospatiale du cacao ivoirien : mettre les données satellites libres au
            service de la <span className="text-white">conformité EUDR</span> et des coopératives
            locales.
          </p>

          <div>
            <FlagRibbon className="mt-7 w-44" />
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/login"
                className="group inline-flex items-center gap-2 rounded-xl bg-ci-orange px-5 py-3 font-semibold text-white transition-all hover:bg-ci-orange-600 hover:shadow-glow"
              >
                Voir le tableau de bord
                <ArrowRight size={16} className="transition-transform group-hover:translate-x-1" />
              </Link>
              <a
                href="#eudr"
                className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-5 py-3 font-semibold text-sand/90 transition-colors hover:border-ci-green/50 hover:text-white"
              >
                Comprendre l'EUDR
              </a>
            </div>
          </div>
        </div>

        <motion.div
          className="relative grid place-items-center"
          style={reduce ? undefined : { x: podX, y: podY }}
        >
          <div className="absolute inset-0 rounded-full bg-ci-orange/10 blur-3xl" />
          <OrbitCacao size={420} className="max-w-full" />
        </motion.div>
      </div>

      <div
        aria-hidden
        className="absolute bottom-6 left-1/2 -translate-x-1/2 text-sand/40 motion-safe:animate-float-y"
      >
        <div className="h-9 w-5 rounded-full border border-white/20 p-1">
          <div className="h-2 w-full rounded-full bg-white/40" />
        </div>
      </div>
    </section>
  );
}
