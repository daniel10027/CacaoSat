# Frontend Web — Landing immersive + Dashboards de conformité

**Rôle :** (1) une **landing page à couper le souffle** qui raconte le problème EUDR et met la Côte d'Ivoire en valeur ; (2) des **dashboards dignes d'un outil national** pour piloter la conformité des parcelles.

**Stack (100 % libre) :** React 18 · Vite · TypeScript · Tailwind CSS · **Motion** (ex‑Framer Motion) · **MapLibre GL JS** (fonds OpenStreetMap / Carto / ESA WorldCover — sans clé) · **Recharts** · TanStack Query · Zustand · React Router · react‑hook‑form + Zod · i18next (FR défaut, EN) · Lucide (icônes) · Vitest + Testing Library · Playwright (e2e) · ESLint + Prettier.

**Design system « Côte d'Ivoire » :**
- Couleurs drapeau : orange `#FF7A00` (Sassandra), blanc `#FFFFFF`, vert `#00A651` (canopée). Accents : nuit `#0B1F17`, or cacao `#7B3F00`, sable `#F4EAD5`.
- Typo : **Poppins** (titres) + **Inter** (texte) — Google Fonts (autorisé).
- Motif : orbite elliptique + fève de cacao (logo), lignes de latitude/longitude discrètes, dégradés verts profonds.
- Motion : `prefers-reduced-motion` respecté partout ; transitions douces (spring), parallax léger, apparition au scroll.

---

## Statut du lot : `[ ]` Lot 4 · `[ ]` Lot 5 · `[ ]` Lot 6

---

## Lot 4 — Socle & design system

### 4.1 Bootstrap projet
- [ ] `web/` : `npm create vite@latest` (react‑ts), Node 20, `package.json` scripts (`dev`, `build`, `preview`, `lint`, `test`, `test:e2e`, `typecheck`)
- [ ] Tailwind + `tailwind.config.ts` (tokens couleurs/typo/ombres/rayons ci‑dessus), `src/styles/index.css` (layers, variables CSS, `@media (prefers-reduced-motion)`)
- [ ] ESLint (flat config) + Prettier + `tsconfig` strict + `vite-tsconfig-paths` (alias `@/`)
- [ ] `.env.example` : `VITE_API_URL`, `VITE_MAP_STYLE_URL`, `VITE_APP_ENV`
- [ ] `web/Dockerfile` (multi‑stage : build Vite → **Nginx** statique) + `web/nginx.conf` (SPA fallback, gzip, cache assets, en‑têtes sécurité)
- [ ] `web/.dockerignore`

### 4.2 Fondations UI
- [ ] `src/assets/logo-cacaosat.svg` — **cacao en orbite** : fève stylisée + ellipse orbitale + petit satellite, versions mono/couleur, favicon `web/public/favicon.svg`
- [ ] `src/components/ui/` : `Button`, `Card`, `Badge` (statut EUDR), `Table`, `Tabs`, `Dialog`, `Drawer`, `Tooltip`, `Toast`, `Skeleton`, `Input`, `Select`, `Spinner`, `EmptyState`, `StatTile`, `KpiCard`, `ThemeToggle` (clair/sombre)
- [ ] `src/components/motion/` : `Reveal` (apparition au scroll `whileInView`), `Parallax`, `Stagger`, `CountUp`, `PageTransition` (via `AnimatePresence` sur le router)
- [ ] `src/components/brand/OrbitCacao.tsx` — animation SVG/Canvas du cacao en orbite (réutilisée hero + loader + favicon animé)
- [ ] `src/lib/cn.ts` (clsx+tailwind‑merge), `src/lib/format.ts` (nombres FR, ha, %, dates)

### 4.3 Données & auth
- [ ] `src/lib/api.ts` — client fetch typé, base `VITE_API_URL`, injection Bearer, refresh auto sur 401, erreurs normalisées
- [ ] `src/features/auth/` — `useAuth` (Zustand + persist), pages `Login`, garde `RequireAuth` + `RequireRole`, logout
- [ ] `src/lib/queryClient.ts` — TanStack Query (staleTime, retry, devtools en dev)
- [ ] `src/types/api.ts` — types générés/écrits d'après `openapi.json` du backend (script `npm run gen:api`)
- [ ] `src/i18n/` — `fr.json` (défaut) + `en.json`, sélecteur de langue

### 4.4 Layout applicatif
- [ ] `src/components/layout/` : `AppShell` (sidebar rétractable, topbar, fil d'ariane, sélecteur de coopérative, cloche d'alertes SSE), `Footer`
- [ ] Router : `/` (landing) · `/login` · `/app` (shell) → `/app/dashboard`, `/app/parcelles`, `/app/parcelles/:id`, `/app/producteurs`, `/app/rapports`, `/app/alertes`, `/app/cooperatives` (admin), `/app/methodo`
- [ ] `NotFound` (404 soignée, motif orbite), `ErrorBoundary` global
- [ ] Accessibilité : focus visible, `aria-*`, contrastes AA, navigation clavier de la sidebar et de la carte

**Definition of Done Lot 4 :** `npm run dev` sert l'app, login réel contre l'API, shell navigable, `npm run build` + image Docker OK, `npm run typecheck` + `lint` verts.

---

## Lot 5 — Landing page immersive

> Objectif : un site **futuriste, animé, fluide**, qui met la Côte d'Ivoire en valeur et présente la solution. Chargement rapide (lazy‑load des sections lourdes), 60 fps, dégradation propre en `reduced-motion`.

- [ ] **Hero** plein écran : fond nuit + canopée en dégradé, **cacao en orbite animé** (rotation + traînée lumineuse orbitale, léger parallax souris), titre `CACAO` (orange) `SAT` (vert), sous‑titre « Traçabilité géospatiale du cacao ivoirien », CTA « Voir le dashboard » / « Comprendre l'EUDR ». Ruban tricolore animé.
- [ ] **Barre de stats** animée (`CountUp` au scroll) : `N°1 mondial`, `82 % traçable (2023)`, `~30 % en zone protégée`, `2M+ foyers`.
- [ ] **Section « Le choc EUDR »** — storytelling scrolly : 3–4 panneaux qui s'enchaînent (texte + illustration), timeline `2020 → 2025 → contrôle UE`.
- [ ] **Section « Le pipeline CacaoSat »** — 6 étapes en cartes animées reliées par une ligne orbitale qui se trace au scroll (cartographie → ingestion → satellite → scoring → rapport → alerte).
- [ ] **Carte nationale interactive** (MapLibre) : contour Côte d'Ivoire, régions cacao qui s'illuminent, données depuis `GET /dashboard/regions` (agrégats), légende statut EUDR. Bascule « zones protégées ».
- [ ] **Section « Sous le capot »** — logos/mentions Sentinel‑2 (Copernicus), Hansen/Global Forest Watch, Digital Earth Africa ; badge « 100 % open data ».
- [ ] **Section Impact** — 4 cartes (économique / social / environnemental / institutionnel) avec micro‑animations.
- [ ] **Section Équipe** — 3 cartes (Timothé, Elie, Daniel) avec rôles.
- [ ] **CTA final** + footer (liens docs, GitHub, mentions données, sélecteur langue).
- [ ] **Perf & SEO** : `<title>`, meta OG (image = hero rendu), `lighthouse` mobile ≥ 90 perf / 100 a11y visé ; images en `webp`/SVG ; polices `display=swap` ; sections sous le pli en `React.lazy`.
- [ ] **Responsive** : mobile (360) → 4K ; menu burger animé ; la carte devient statique/simplifiée sur très petit écran.
- [ ] Tests : `Reveal`/`CountUp` rendent sans erreur, la landing monte en < X ms (Vitest + RTL), Playwright : scroll complet sans exception console.

**Definition of Done Lot 5 :** landing complète, animée, responsive, `reduced-motion` OK, build < budget (JS initial < 200 kB gzip hors carte), Playwright vert.

---

## Lot 6 — Dashboards de conformité

### 6.1 Tableau de bord coopérative (`/app/dashboard`)
- [ ] Ligne de **KPIs** (`KpiCard` + `CountUp`) : parcelles totales, surface (ha), % conformes, nb à risque, nb non‑conformes, événements de déforestation, surface à haut risque.
- [ ] **Carte des parcelles** (MapLibre) : polygones colorés par `eudr_status` (vert/ambre/rouge), popup (code, producteur, score, surface, motifs), fond satellite ESA WorldCover + OSM, contrôle de couches (parcelles / aires protégées / pertes de couvert), zoom sur bbox coopérative, clustering des centroïdes à petit zoom.
- [ ] **Graphes Recharts** : distribution des scores (histogramme), tendance mensuelle du % conforme (aire), répartition par risque (donut), top producteurs à risque (barres).
- [ ] **File d'alertes** (temps réel SSE) : liste, badge sévérité, bouton « Acquitter », lien vers la parcelle.
- [ ] Filtres globaux : coopérative (si multi), risque, statut, période ; état persillé dans l'URL (query params).

### 6.2 Parcelles (`/app/parcelles`, `/app/parcelles/:id`)
- [ ] Table serveur (tri, filtres, pagination, recherche) : code, producteur, surface, score, statut, dernière analyse.
- [ ] Actions : « Analyser » (une / sélection), export GeoJSON, création manuelle d'une parcelle (dessin de polygone sur la carte avec Mapbox Draw / maplibre‑gl‑draw + formulaire producteur).
- [ ] **Détail parcelle** : carte zoomée + polygone, fiche producteur, **jauge de score** avec ventilation des `factors` (barres pondérées + explications), **série temporelle NDVI** (Recharts, marqueur sur l'événement de perte), historique des analyses, aires protégées à proximité, bouton « Générer un extrait de rapport ».
- [ ] États : chargement (skeleton), vide, erreur.

### 6.3 Rapports (`/app/rapports`)
- [ ] Formulaire de génération : coopérative, période, sélection de parcelles (ou toutes), aperçu du périmètre sur carte.
- [ ] Liste des rapports : titre, période, nb parcelles, statut, `content_hash` (copiable), **télécharger PDF / GeoJSON**.
- [ ] Aperçu PDF intégré (`<iframe>` sur l'URL de download) + résumé (compteurs, motifs dominants).

### 6.4 Autres écrans
- [ ] **Producteurs** : table + fiche (parcelles liées, statut agrégé).
- [ ] **Alertes** (`/app/alertes`) : vue complète, filtres (type, sévérité, acquittées), carte des points d'alerte, acquittement en masse.
- [ ] **Coopératives** (admin) : CRUD, comptes utilisateurs, quotas.
- [ ] **Méthodologie** (`/app/methodo`) : barème de scoring lisible (depuis l'API), sources de données, définitions EUDR — sert aussi de contenu pour la landing.

### 6.5 Qualité
- [ ] Skeletons + optimistic UI sur acquittement/analyse.
- [ ] Gestion fine des erreurs API (toast + retry).
- [ ] Tests Vitest : hooks data, rendu KPIs, formatage ; Playwright e2e : login → dashboard → analyser une parcelle → générer un rapport → télécharger.
- [ ] Lighthouse app ≥ 90 perf, 100 a11y sur `/app/dashboard`.

**Definition of Done Lot 6 :** tous les écrans branchés sur l'API réelle, carte + graphes fonctionnels, génération/téléchargement de rapport depuis l'UI, SSE d'alertes visible, e2e Playwright vert ; **push `develop` + merge `preprod` (jalon M2)**.

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
