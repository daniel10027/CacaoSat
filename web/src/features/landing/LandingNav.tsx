import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useScroll, useMotionValueEvent } from 'framer-motion';
import { cn } from '@/lib/cn';
import { OrbitCacao } from '@/components/brand/OrbitCacao';
import { Wordmark } from '@/components/brand/Wordmark';

const LINKS = [
  { href: '#eudr', label: 'EUDR' },
  { href: '#pipeline', label: 'Pipeline' },
  { href: '#regions', label: 'National' },
  { href: '#equipe', label: 'Équipe' },
];

export function LandingNav() {
  const { scrollY } = useScroll();
  const [solid, setSolid] = useState(false);
  useMotionValueEvent(scrollY, 'change', (v) => setSolid(v > 40));

  return (
    <header
      className={cn(
        'fixed inset-x-0 top-0 z-40 transition-colors duration-300',
        solid ? 'border-b border-white/10 bg-night/90 backdrop-blur' : 'bg-transparent',
      )}
    >
      <div className="container-page flex items-center justify-between py-4">
        <a href="#top" className="flex items-center gap-2">
          <OrbitCacao size={34} spin={!solid} />
          <Wordmark className="text-lg" />
        </a>
        <nav className="hidden items-center gap-6 text-sm text-sand/60 md:flex">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="transition-colors hover:text-white">
              {l.label}
            </a>
          ))}
        </nav>
        <Link
          to="/login"
          className="rounded-xl border border-white/15 px-4 py-2 text-sm font-semibold text-sand/90 transition-colors hover:border-ci-orange/50 hover:text-white"
        >
          Espace coopérative
        </Link>
      </div>
    </header>
  );
}
