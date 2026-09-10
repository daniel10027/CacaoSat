import { OrbitCacao } from '@/components/brand/OrbitCacao';
import { Wordmark } from '@/components/brand/Wordmark';
import { LanguageToggle } from '@/components/layout/LanguageToggle';

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-night-2/50">
      <div className="container-page flex flex-col gap-6 py-10 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <OrbitCacao size={32} spin={false} />
          <Wordmark className="text-base" />
          <span className="ml-2 text-xs text-sand/40">Ivoire Spacehack 2026 · Abidjan</span>
        </div>
        <div className="flex flex-wrap items-center gap-4 text-sm text-sand/55">
          <a
            href="https://github.com/daniel10027/CacaoSat"
            className="hover:text-white"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
          <span className="text-sand/25">·</span>
          <span>Données : Copernicus / GFW / Digital Earth Africa</span>
          <LanguageToggle />
        </div>
      </div>
    </footer>
  );
}
