# Web — CacaoSat

Landing immersive + dashboards de conformité EUDR. React 18 · Vite · TypeScript · Tailwind ·
Framer Motion · MapLibre · Recharts · TanStack Query · Zustand · i18next.

Toutes les tâches : [../docs/FRONTEND.md](../docs/FRONTEND.md).

## Démarrage

```bash
npm install
cp .env.example .env          # VITE_API_URL -> API CacaoSat
npm run dev                   # http://localhost:5173
```

## Scripts

| Commande | Rôle |
|----------|------|
| `npm run dev` | serveur de dev (host 0.0.0.0:5173) |
| `npm run build` | `tsc -b && vite build` → `dist/` |
| `npm run preview` | sert le build |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run test` | Vitest |

## Structure

```
src/
  components/
    ui/        primitives (Button, Card, Badge, KpiCard, Spinner, misc…)
    motion/    Reveal, Stagger, CountUp, PageTransition
    brand/     OrbitCacao (logo animé), Wordmark, FlagRibbon
    layout/    AppShell, LanguageToggle, AlertBell
  features/auth/   useAuth (zustand), guards (RequireAuth / RequireRole)
  lib/       api.ts (client + refresh), queryClient, cn, format
  i18n/      fr (défaut) + en
  pages/     Landing, Login, NotFound, Placeholder
  types/     api.ts (contrat)
  routes.tsx  App.tsx  main.tsx
```

## Design system

Palette drapeau de Côte d'Ivoire — orange `#FF7A00`, blanc, vert `#00A651` ; accents nuit /
or cacao / sable. Typo Poppins (titres) + Inter (texte). Toutes les animations respectent
`prefers-reduced-motion`.
