import { lazy, Suspense } from 'react';
import { ScrollProgress } from '@/components/motion/Parallax';
import { LandingNav } from '@/features/landing/LandingNav';
import { Hero } from '@/features/landing/Hero';
import { StatsBar } from '@/features/landing/StatsBar';
import { Footer } from '@/components/layout/Footer';

const EudrShock = lazy(() =>
  import('@/features/landing/EudrShock').then((m) => ({ default: m.EudrShock })),
);
const Pipeline = lazy(() =>
  import('@/features/landing/Pipeline').then((m) => ({ default: m.Pipeline })),
);
const NationalMap = lazy(() =>
  import('@/features/landing/NationalMap').then((m) => ({ default: m.NationalMap })),
);
const UnderHood = lazy(() =>
  import('@/features/landing/UnderHood').then((m) => ({ default: m.UnderHood })),
);
const ImpactTeam = lazy(() =>
  import('@/features/landing/ImpactTeam').then((m) => ({ default: m.ImpactTeam })),
);

const Gap = () => <div className="h-24" aria-hidden />;

export default function Landing() {
  return (
    <div id="top" className="relative bg-night text-sand/90">
      <ScrollProgress />
      <LandingNav />
      <main>
        <Hero />
        <StatsBar />
        <Suspense fallback={<Gap />}>
          <div id="pipeline">
            <EudrShock />
            <Pipeline />
          </div>
          <div id="regions">
            <NationalMap />
          </div>
          <UnderHood />
          <div id="equipe">
            <ImpactTeam />
          </div>
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
