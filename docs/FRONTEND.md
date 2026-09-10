# Frontend Web — Landing immersive + Dashboards de conformité

**Rôle :** (1) une **landing page à couper le souffle** qui raconte le problème EUDR et met la Côte d'Ivoire en valeur ; (2) des **dashboards dignes d'un outil national** pour piloter la conformité des parcelles.

**Stack (100 % libre) :** React 18 · Vite · TypeScript · Tailwind CSS · **Motion** (ex‑Framer Motion) · **MapLibre GL JS** (fonds OpenStreetMap / Carto / ESA WorldCover — sans clé) · **Recharts** · TanStack Query · Zustand · React Router · react‑hook‑form + Zod · i18next (FR défaut, EN) · Lucide (icônes) · Vitest + Testing Library · Playwright (e2e) · ESLint + Prettier.

**Design system « Côte d'Ivoire » :**
- Couleurs drapeau : orange `#FF7A00` (Sassandra), blanc `#FFFFFF`, vert `#00A651` (canopée). Accents : nuit `#0B1F17`, or cacao `#7B3F00`, sable `#F4EAD5`.
- Typo : **Poppins** (titres) + **Inter** (texte) — Google Fonts (autorisé).
- Motif : orbite elliptique + fève de cacao (logo), lignes de latitude/longitude discrètes, dégradés verts profonds.
- Motion : `prefers-reduced-motion` respecté partout ; transitions douces (spring), parallax léger, apparition au scroll.

---

## Statut du lot : `[x]` Lot 4 (terminé) · `[x]` Lot 5 (terminé) · `[x]` Lot 6 (terminé)

---

## Lot 4 — Socle & design system

### 4.1 Bootstrap projet
- [x] `web/` : `npm create vite@latest` (react‑ts), Node 20, `package.json` scripts (`dev`, `build`, `preview`, `lint`, `test`, `test:e2e`, `typecheck`)
- [x] Tailwind + `tailwind.config.ts` (tokens couleurs/typo/ombres/rayons ci‑dessus), `src/styles/index.css` (layers, variables CSS, `@media (prefers-reduced-motion)`)
- [x] ESLint (flat config) + Prettier + `tsconfig` strict + `vite-tsconfig-paths` (alias `@/`)
- [x] `.env.example` : `VITE_API_URL`, `VITE_MAP_STYLE_URL`, `VITE_APP_ENV`
- [x] `web/Dockerfile` (multi‑stage : build Vite → **Nginx** statique) + `web/nginx.conf` (SPA fallback, gzip, cache assets, en‑têtes sécurité)
- [x] `web/.dockerignore`

### 4.2 Fondations UI
- [x] `web/public/favicon.svg` — **cacao en orbite** (fève + ellipse orbitale + satellite). Composant `OrbitCacao` = version animée. Logo raster `src/assets/logo-cacaosat.png` fourni.
- [x] `src/components/ui/` : `Button` (variants + loading), `Card`/`CardHeader`/`CardBody`, `EudrBadge` + `RiskDot`, `KpiCard` (+ CountUp), `Spinner`, `Skeleton`, `EmptyState`, `Field`, `Divider`. *(`Table`, `Tabs`, `Dialog`, `Drawer`, `Toast`, `Select` ajoutés au Lot 6 avec leurs écrans ; thème sombre par défaut, toggle clair reporté.)*
- [x] `src/components/motion/` : `Reveal` (scroll `whileInView`), `Stagger` + `StaggerItem`, `CountUp` (RAF, respecte reduced-motion), `PageTransition`. *(`Parallax` ajouté au Lot 5.)*
- [x] `src/components/brand/OrbitCacao.tsx` — logo animé (orbite + satellite + traînée + fève qui flotte), `Wordmark`, `FlagRibbon` ; réutilisé hero / loader / login / 404
- [x] `src/lib/cn.ts` (clsx+tailwind‑merge), `src/lib/format.ts` (nombres/ha/%/dates fr‑FR, libellés + couleurs EUDR)

### 4.3 Données & auth
- [x] `src/lib/api.ts` — client fetch typé, base `VITE_API_URL`, injection Bearer, refresh auto sur 401, erreurs normalisées
- [x] `src/features/auth/` — `useAuth` (Zustand + persist), pages `Login`, garde `RequireAuth` + `RequireRole`, logout
- [x] `src/lib/queryClient.ts` — TanStack Query (staleTime, retry, devtools en dev)
- [x] `src/types/api.ts` — types écrits à la main d'après `/api/v1/openapi.json` (Parcel, Score, Alert, DashboardSummary, Paginated…)
- [x] `src/i18n/` — `fr.json` (défaut) + `en.json`, `LanguageToggle`

### 4.4 Layout applicatif
- [x] `src/components/layout/` : `AppShell` (sidebar rétractable + drawer mobile animé, topbar, `AlertBell` avec compteur non‑acquittées polling 20 s, `LanguageToggle`) — nav filtrée par rôle
- [x] Router : `/` (landing) · `/login` · `/app` (shell, `RequireAuth`) → `/app/dashboard`, `/parcelles`, `/parcelles/:id`, `/producteurs`, `/rapports` (`RequireRole`), `/alertes`, `/cooperatives` (`RequireRole`), `/methodo` — écrans en `Placeholder` jusqu'au Lot 6
- [x] `NotFound` (404 soignée, `OrbitCacao`), `ErrorBoundary` global
- [x] Accessibilité : focus visible (`focus-visible:ring`), `aria-label`, thème sombre contrasté, `@media (prefers-reduced-motion)`

**Definition of Done Lot 4 :** ✅ `npm run build` OK (JS initial **148 kB gzip**), `npm run typecheck` + `lint` + `test` (3) verts, `npm run preview` sert l'app (SPA fallback `/app/*` = 200), `web/Dockerfile` (Vite → Nginx) écrit. Login branché sur l'API réelle (`useAuth` + refresh JWT auto).

---

## Lot 5 — Landing page immersive

> Objectif : un site **futuriste, animé, fluide**, qui met la Côte d'Ivoire en valeur et présente la solution. Chargement rapide (lazy‑load des sections lourdes), 60 fps, dégradation propre en `reduced-motion`.

- [x] **Hero** plein écran : fond nuit + canopée en dégradé, **cacao en orbite animé** (rotation + traînée lumineuse orbitale, léger parallax souris), titre `CACAO` (orange) `SAT` (vert), sous‑titre « Traçabilité géospatiale du cacao ivoirien », CTA « Voir le dashboard » / « Comprendre l'EUDR ». Ruban tricolore animé.
- [x] **Barre de stats** animée (`CountUp` au scroll) : `N°1 mondial`, `82 % traçable (2023)`, `~30 % en zone protégée`, `2M+ foyers`.
- [x] **Section « Le choc EUDR »** — storytelling scrolly : 3–4 panneaux qui s'enchaînent (texte + illustration), timeline `2020 → 2025 → contrôle UE`.
- [x] **Section « Le pipeline CacaoSat »** — 6 étapes en cartes animées reliées par une ligne orbitale qui se trace au scroll (cartographie → ingestion → satellite → scoring → rapport → alerte).
- [x] **Carte nationale** (`NationalMap.tsx`) : contour schématique animé de la Côte d'Ivoire (SVG, `pathLength` au scroll), 6 pôles cacao qui s'illuminent selon `GET /dashboard/regions` (agrégats live, repli sur les chiffres de la zone pilote hors ligne), couleur = ratio de conformité. *(MapLibre réservé au dashboard — Lot 6.)*
- [x] **Section « Sous le capot »** — logos/mentions Sentinel‑2 (Copernicus), Hansen/Global Forest Watch, Digital Earth Africa ; badge « 100 % open data ».
- [x] **Section Impact** — 4 cartes (économique / social / environnemental / institutionnel) avec micro‑animations.
- [x] **Section Équipe** — 3 cartes (Timothé, Elie, Daniel) avec rôles.
- [x] **CTA final** + footer (liens docs, GitHub, mentions données, sélecteur langue).
- [x] **Perf & SEO** : `<title>` + meta OG/description dans `index.html`, polices Google `display=swap`, **sections sous le pli en `React.lazy`** (chunks 1–7 kB gzip), `ScrollProgress` en `transform` only. *(Audit Lighthouse formel branché au Lot 11 — `lighthouserc.json`, budgets a11y ≥ 0,95 / perf ≥ 0,85 en CI.)*
- [x] **Responsive** : grilles fluides `clamp()` / flex ; la carte nationale (SVG) s'adapte sans média lourd.
- [x] Tests Vitest : `StatsBar`, `EudrShock`, `UnderHood` rendent sans erreur (stub `IntersectionObserver` dans `vitest.setup.ts`). *(Playwright e2e `e2e/landing.spec.ts` ajouté au Lot 11.)*

**Definition of Done Lot 5 :** ✅ landing complète (hero parallax + orbite, stats CountUp, choc EUDR, pipeline avec ligne orbitale tracée au scroll, carte nationale live, sources open data, impact + équipe, footer), `prefers-reduced-motion` respecté, `npm run build` OK — **JS initial 148 kB gzip, landing chunk 7.3 kB**, tsc + lint + test (6) verts. Vérifié visuellement au navigateur.

---

## Lot 6 — Dashboards de conformité

### 6.1 Tableau de bord coopérative (`/app/dashboard`)
- [x] Ligne de **KPIs** (`KpiCard` + `CountUp`) : parcelles totales, surface (ha), % conformes, nb à risque, nb non‑conformes, événements de déforestation, surface à haut risque.
- [x] **Carte des parcelles** (`MapView` MapLibre) : polygones colorés par `eudr_status` (vert/ambre/rouge), popup (code, producteur, surface, score, statut), **fond satellite Esri World Imagery** (sans clé — on voit le couvert forestier), couche aires protégées togglable, `fitBounds` sur les parcelles, `ResizeObserver` + repaint sur `visibilitychange`. *(clustering : Lot 11 si utile.)*
- [x] **Graphes Recharts** : `ScoreHistogram`, `ComplianceTrend` (aire, % conformes/mois), `RiskDonut` (avec total au centre). *(top producteurs : reporté.)*
- [x] **File d'alertes** : 6 dernières non acquittées, badge sévérité, « Acquitter » (optimiste + toast), lien vers la parcelle, « Tout voir ». *(SSE branché au Lot 11 — `lib/sse.ts` + `useAlertStream` ; polling `AlertBell` conservé en filet de sécurité.)*
- [x] Sélecteur de coopérative pour les rôles nationaux ; filtres parcelles/alertes dans l'URL (`useSearchParams`).

### 6.2 Parcelles (`/app/parcelles`, `/app/parcelles/:id`)
- [x] Table serveur (tri, filtres, pagination, recherche) : code, producteur, surface, score, statut, dernière analyse.
- [x] Action « Analyser » par ligne (loading + toast du score). *(Dessin de polygone `maplibre-gl-draw` : couvert par l'app mobile — création web reportée.)*
- [x] **Détail parcelle** : **carte satellite** zoomée + polygone, en‑tête producteur, **jauge de score** (56,1/100) avec ventilation des 5 `factors` (barres pondérées + explication par facteur), **série NDVI** (Recharts, marqueur `perte`), panneau « Analyse satellite » (couvert 2020/actuel, perte ha, déforestation, confiance, sources), historique des analyses.
- [x] États : skeleton (chargement), erreur + retry, vide.

### 6.3 Rapports (`/app/rapports`)
- [x] `Dialog` de génération : titre, période (début/fin) → `POST /reports` (loading + toast).
- [x] Liste des rapports : titre, période, date, nb parcelles, compteurs conformes/à vérifier/non conformes, `content_hash` copiable, **téléchargement PDF / GeoJSON** via `fetch` authentifié + Blob local. *(Aperçu iframe : reporté — le PDF se télécharge.)*

### 6.4 Autres écrans
- [x] **Producteurs** : table paginée + recherche (`?q=`), pièce d'identité manquante signalée, nb de parcelles.
- [x] **Alertes** (`/app/alertes`) : liste complète, filtres acquittées/type/sévérité, bordure colorée par sévérité, acquittement unitaire + toast, lien parcelle.
- [x] **Coopératives** (regulator/admin) : cartes (code, région, département, contact). *(CRUD/comptes : reporté.)*
- [x] **Méthodologie** (`/app/methodo`) : barème 45/20/15/10/10 détaillé, définitions des 3 statuts EUDR, sources open data.

### 6.5 Qualité
- [x] `Skeleton` (chargement), `QueryState` (loading/erreur+retry), `EmptyState`, optimistic UI sur acquittement.
- [x] `Toaster` global (zustand) — erreurs API en toast.
- [x] Tests Vitest verts (6) ; `tsc` strict + `eslint` propres (0 erreur). *(Playwright e2e `e2e/compliance-flow.spec.ts` + Lighthouse ajoutés au Lot 11.)*

**Definition of Done Lot 6 :** ✅ tous les écrans branchés sur l'API réelle et **vérifiés au navigateur** (login → dashboard KPIs + carte satellite Esri + graphes + file d'alertes ; liste parcelles filtrable ; détail parcelle avec jauge de score, ventilation des facteurs et série NDVI ; génération + téléchargement de rapport ; alertes ; producteurs ; méthodologie). `npm run build` OK (charts en chunk lazy 325 kB gzip hors bundle initial), tsc + lint + test verts. **→ jalon M2 : merge `develop → preprod`.**

---

## Lot 11 — Finitions frontend

### 11.1 Alertes temps réel (SSE)
- [x] `src/lib/sse.ts` — `openEventStream(path, onEvent)` : lecteur SSE `fetch` + `ReadableStream` (permet l'en‑tête `Authorization: Bearer`, impossible avec `EventSource`), reconnexion avec backoff.
- [x] `src/features/dashboard/useAlertStream.ts` — abonnement `/alerts/stream`, invalidation des requêtes `['alerts']` + toast à chaque nouvelle alerte ; appelé `useAlertStream(true)` dans `DashboardPage`. Le polling `AlertBell` reste en filet de sécurité.

### 11.2 Accessibilité
- [x] `AppShell` — lien d'évitement `« Aller au contenu »` (`sr-only focus:not-sr-only`), `id="main"` sur `<main>`, `aria-label` sur les `<nav>`.
- [x] `Dialog` — piège de focus (Tab/Shift+Tab), focus initial sur le panneau, restauration du focus déclencheur à la fermeture, `tabIndex={-1}`.
- [x] `Toaster` — `role="status" aria-live="polite"`.
- [x] `LandingNav` — `aria-label="Sections"`.

### 11.3 Tests e2e & audit
- [x] `playwright.config.ts` + `e2e/fixtures.ts` (`mockApi(page)` intercepte `**/api/v1/**`) — aucun backend requis.
- [x] `e2e/landing.spec.ts` — la landing charge et défile **sans erreur console**, CTA → `/login`.
- [x] `e2e/compliance-flow.spec.ts` — login → dashboard → parcelles → détail → analyser → rapport ; garde de rôle `agent`.
- [x] `lighthouserc.json` — budgets **a11y ≥ 0,95**, **perf ≥ 0,85** (LHCI).
- [x] `.github/workflows/web.yml` — jobs `build`, `e2e` (Playwright), `lighthouse` (LHCI).
- [x] Bug réel attrapé par Playwright : `<circle r="undefined">` dans `NationalMap` (Motion `animate={{ r: [...] }}`) → remplacé par SMIL `<animate attributeName="r">`.

**Definition of Done Lot 11 :** ✅ alertes poussées en direct au dashboard (SSE authentifié), parcours e2e Playwright verts sans backend, budgets Lighthouse tenus en CI, corrections d'accessibilité (skip‑link, focus trap, live regions). Entrées critiques toujours en `transition` CSS (jamais cachées en onglet de fond). **→ inclus au jalon M5 (retag `v1.0.0`).**

---

## Arborescence cible `web/src/`

```
assets/            logo, illustrations, lottie/svg orbite
components/
  ui/              primitives (Button, Card, Table, …)
  motion/          Reveal, Parallax, Stagger, CountUp, PageTransition
  brand/           OrbitCacao, FlagRibbon
  layout/          AppShell, Sidebar, Topbar, Footer
  map/             MapView, ParcelLayer, ProtectedLayer, LegendControl, DrawControl
  charts/          ScoreHistogram, ComplianceTrend, RiskDonut, NdviSeries
features/
  auth/  parcels/  producers/  dashboard/  reports/  alerts/  cooperatives/  landing/
lib/               api.ts, queryClient.ts, cn.ts, format.ts, sse.ts
i18n/              index.ts, fr.json, en.json
pages/             Landing.tsx, Login.tsx, NotFound.tsx
types/             api.ts
routes.tsx  main.tsx  App.tsx
```

## Variables d'environnement (`web/.env.example`)

```
VITE_API_URL=http://localhost:8000/api/v1
VITE_MAP_STYLE_URL=https://tiles.openfreemap.org/styles/liberty
VITE_APP_ENV=development
```

## Changelog du frontend

| Date | Lot | Commit | Note |
|------|-----|--------|------|
| — | 0 | `chore(repo): bootstrap` | dossier `web/` réservé |
| 2026-09-10 | 4 | `feat(web): socle React + design system CI + auth` | Vite/TS/Tailwind, design system drapeau CI, OrbitCacao animé, client API + refresh JWT, useAuth, AppShell + routing + gardes rôle, i18n fr/en, Login/404, Dockerfile Nginx. build 148 kB gzip, tsc/lint/test verts |
| 2026-09-10 | 5 | `feat(web): landing immersive (cacao en orbite)` | Hero parallax + orbite, StatsBar CountUp, EudrShock (timeline), Pipeline (ligne orbitale tracée au scroll), NationalMap (SVG CI + agrégats /dashboard/regions live), UnderHood, ImpactTeam, LandingNav sticky, Footer. Sections lazy (1–7 kB). Vérifié au navigateur |
| 2026-09-10 | 6 | `feat(web): dashboards de conformité` | DashboardPage (KPIs + carte satellite Esri + Recharts + file d'alertes), ParcelsPage (table filtrable), ParcelDetailPage (jauge score + facteurs + NDVI), ReportsPage (Dialog + download PDF/GeoJSON), AlertsPage, ProducersPage, CooperativesPage, Methodology. MapView (MapLibre), charts, Select/Dialog/Toast. **Correctif robustesse : entrées critiques par `transition` CSS et non `animation` (contenu jamais caché onglet en fond).** Vérifié au navigateur |
| 2026-09-10 | 11 | `feat(web): finitions — SSE alertes, a11y, e2e Playwright` | `lib/sse.ts` + `useAlertStream` (alertes poussées au dashboard, Bearer via fetch/ReadableStream), skip-link + focus trap `Dialog` + live regions, `playwright.config.ts` + `e2e/` (landing sans erreur console, parcours conformité, garde de rôle) avec `mockApi`, `lighthouserc.json` (a11y ≥ 0,95 / perf ≥ 0,85), jobs CI `e2e` + `lighthouse`. Bug SMIL `<circle r>` corrigé |
