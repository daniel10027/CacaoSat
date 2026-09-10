# CacaoSat — Feuille de route & suivi d'exécution

Ce document est le **pilote central** du projet. Il découpe la livraison en **lots** ordonnés.
Chaque lot se termine par un **commit + push sur `develop`**. Les jalons déclenchent un merge `develop → preprod → prod`.

## Légende de statut

| Symbole | Sens |
|---------|------|
| `[ ]` | à faire |
| `[~]` | en cours |
| `[x]` | **terminé** — code réel, testé, exécutable, committé |
| 🔒 | bloqué (dépendance / décision externe) |

**Règle d'or :** une case n'est cochée que si le livrable tourne réellement (`make test` vert, service qui démarre, écran qui s'affiche). Pas de TODO, pas de pseudo‑code.

---

## Vue d'ensemble des lots

| Lot | Titre | Doc de détail | Statut | Push |
|-----|-------|---------------|--------|------|
| 0 | Fondations du dépôt | ce fichier | `[x]` | `chore: bootstrap monorepo + tracking docs` |
| 1 | Backend — socle (app factory, DB, auth, Docker) | [BACKEND.md](docs/BACKEND.md) | `[x]` | `feat(backend): socle Flask + PostGIS + auth JWT` |
| 2 | Backend — moteur satellite (mock) + scoring EUDR + API métier | [BACKEND.md](docs/BACKEND.md) | `[x]` | `feat(backend): moteur satellite mock + scoring EUDR + API métier` |
| 3 | Backend — rapports PDF/GeoJSON + alertes + sync mobile | [BACKEND.md](docs/BACKEND.md) | `[x]` | `feat(backend): rapports PDF/GeoJSON + alertes précoces + sync mobile` |
| 4 | Web — socle + design system Côte d'Ivoire + auth | [FRONTEND.md](docs/FRONTEND.md) | `[x]` | `feat(web): socle React + design system CI + auth` |
| 5 | Web — landing page immersive (cacao en orbite) | [FRONTEND.md](docs/FRONTEND.md) | `[x]` | `feat(web): landing immersive (cacao en orbite)` |
| 6 | Web — dashboards conformité (carte, KPIs, rapports, alertes) | [FRONTEND.md](docs/FRONTEND.md) | `[x]` | `feat(web): dashboards de conformité` |
| 7 | Mobile — socle Flutter (thème, DB locale, auth, nav) | [MOBILE.md](docs/MOBILE.md) | `[x]` | `feat(mobile): app Flutter de collecte terrain hors-ligne` |
| 8 | Mobile — collecte terrain hors‑ligne + sync différée | [MOBILE.md](docs/MOBILE.md) | `[x]` | (idem — Lots 7 & 8 livrés ensemble) |
| 9 | Infra — Docker Compose, CI/CD, `dev.sh`, observabilité | [INFRA.md](docs/INFRA.md) | `[ ]` | — |
| 10 | Pitch — deck 5 min PPTX + PDF | ce fichier | `[ ]` | — |
| 11 | Durcissement, seed démo, release preprod/prod | ce fichier | `[ ]` | — |

---

## Lot 0 — Fondations du dépôt  `[x]`

- [x] Arborescence monorepo (`backend/ web/ mobile/ infra/ scripts/ pitch/ docs/`)
- [x] `.gitignore` (Python, Node, Flutter, Docker, IDE)
- [x] `.editorconfig`
- [x] `LICENSE` (MIT)
- [x] `README.md` — présentation, architecture, quickstart, workflow Git
- [x] `ROADMAP.md` — ce fichier
- [x] `docs/BACKEND.md`, `docs/FRONTEND.md`, `docs/MOBILE.md`, `docs/INFRA.md` — listes de tâches détaillées
- [x] `git init`, commit initial sur `main`, création des branches `develop`, `preprod`, `prod`
- [x] `git remote add origin https://github.com/daniel10027/CacaoSat.git`
- [x] `git push` des 4 branches `main` / `develop` / `preprod` / `prod` (credential helper macOS actif)

**Definition of Done :** `git log` montre le commit de bootstrap, `git branch` liste `develop/preprod/prod`, les 6 docs existent. ✅ **Lot 0 terminé** — 4 branches sur `origin`, travail en cours sur `develop`.

---

## Lot 1 — Backend, socle  `[x]`

Détail des tâches : [docs/BACKEND.md § Lot 1](docs/BACKEND.md). Résumé livré :

- [x] Application factory Flask (`create_app`), configs Dev/Test/Prod, logs JSON, enveloppe d'erreurs uniforme
- [x] 10 modèles SQLAlchemy + PostGIS (`Cooperative, User, Producer, Parcel, AnalysisRun, ComplianceScore, ComplianceReport, Alert, SyncBatch, AuditLog`)
- [x] Migration Alembic initiale **réversible** (up/down testés), extension PostGIS activée, index GiST sur `parcels.geometry`
- [x] Auth : hachage **argon2**, JWT access/refresh, claims `role`/`cooperative_id`, `@roles_required`, rate‑limit login
- [x] Endpoints : `/health`, `/health/ready` (DB+Redis), `/metrics` (Prometheus), `/auth/login|refresh|me`, `/openapi.json`
- [x] `flask seed` (9 comptes, 2 coopératives) + `flask seed-demo` (24 producteurs, 41 parcelles géolocalisées)
- [x] `Dockerfile` multi‑stage non‑root + `entrypoint.sh` (attente DB → `db upgrade` → seed) + `gunicorn.conf.py`
- [x] `infra/docker-compose.dev.yml` (PostGIS, Redis, MailHog, MinIO) + `docker-compose.yml` racine (db, redis, backend, …)
- [x] Suite **pytest : 20 tests verts, couverture 85 %**, `ruff check` propre

**Definition of Done :** ✅ `make test` vert (85 %), `docker compose up --build backend db` opérationnel, `flask db upgrade`/`downgrade` réversibles, `/health/ready`=200, `/auth/login`→JWT.

---

## Lot 2 — Backend, moteur satellite + scoring EUDR + API métier  `[x]`

Détail : [docs/BACKEND.md § Lot 2](docs/BACKEND.md). Résumé livré :

- [x] **Mocks déterministes** (RNG NumPy seedé par `hash(parcel.id)`) : Sentinel‑2 (série NDVI mensuelle, chute simulable), Hansen/GFW (couvert 2000/2020, perte annuelle post‑2020), Digital Earth Africa (indice de dégradation), aires protégées (GeoJSON embarqué, recouvrement géométrique réel) + mocks e‑mail (MailHog)/SMS
- [x] **Moteur d'analyse** `run_analysis` : détection de rupture NDVI (moyenne glissante), `forest_loss_ha`, `loss_events`, recouvrement aire protégée, `confidence` (accord des signaux) → `AnalysisRun`
- [x] **Moteur de scoring EUDR** `compute_score` : 5 facteurs pondérés (45/20/15/10/10), `factors[]` explicable, `risk_level` + `eudr_status` dérivés
- [x] **API métier** : CRUD `/cooperatives` `/producers` `/parcels` (scoping par rôle, pagination, filtres `risk_level`/`eudr_status`/`bbox`/`q`, tri), `POST /parcels/{id}/analyze`, `POST /analysis/batch`, `GET /parcels/{id}/history`, `GET /parcels/{id}.geojson`
- [x] **Dashboard** : `/dashboard/summary` (KPIs, distribution de score, tendance mensuelle), `/dashboard/map` (FeatureCollection scorée), `/dashboard/regions` (agrégats nationaux, public)
- [x] **OpenAPI 3.0.3** `/openapi.json` (25 routes) + console `/docs`
- [x] **62 tests** pytest verts, couverture **86 %**, `ruff` propre

**Definition of Done :** ✅ validé en conteneur (`docker compose up`) — chaîne parcelle → analyse → score → dashboard opérationnelle de bout en bout ; batch 21/21 ; jeu de démo → 12 conformes / 4 à risque / 5 non‑conformes.

---

## Lot 3 — Backend, rapports + alertes + sync mobile  `[x]`

Détail : [docs/BACKEND.md § Lot 3](docs/BACKEND.md). Résumé livré :

- [x] **Rapport / certificat EUDR** (`app/services/report.py`) : PDF ReportLab (en‑tête, préambule légal, synthèse, **carte des parcelles** couleur = statut, tableau par producteur, annexe sources) + **export GeoJSON** au gabarit exportateurs + `content_hash` SHA‑256 stable
- [x] **Stockage** `app/storage.py` : MinIO/S3 (`boto3`) si joignable, repli disque local
- [x] `POST/GET /reports`, `GET /reports/{id}`, `GET /reports/{id}/download?format=pdf|geojson`
- [x] **Alertes précoces** (`app/services/alerts.py`) : `scan_for_alerts` compare dernière/précédente analyse → `new_deforestation` / `protected_encroachment` / `data_gap`, dédup tant que non acquittée, notif MailHog + SMS (mock) aux managers
- [x] `GET /alerts` (filtres + pagination), `GET /alerts/{id}`, `POST /alerts/{id}/acknowledge`, `POST /alerts/scan`, `GET /alerts/stream` (SSE)
- [x] **Sync mobile** (`app/services/sync.py`) : `GET /sync/bootstrap` (coopérative, producteurs, parcelles, aires protégées, barème), `POST /sync/batch` (idempotent via `client_batch_id`, LWW horodaté, `id_map` client→serveur, analyse déclenchée), `GET /sync/status/{id}`
- [x] **Job planifié** `app/tasks/scheduler.py` (APScheduler, `SCHEDULER_ENABLED=1`) + CLI `flask reanalyze|scan-alerts|make-report`
- [x] `app/audit.py` (journal d'audit), **76 tests** (couverture **83 %**), `ruff` propre

**Definition of Done :** ✅ validé en conteneur — rapport PDF+GeoJSON téléchargeables, alertes créées + notifiées, batch mobile simulé (producteur+parcelle, rejeu idempotent, analyse auto). **Backend complet → jalon M1 (merge `develop → preprod`).**

---

## Lot 10 — Pitch (5 minutes)  `[ ]`

- [ ] `pitch/build_deck.py` — génération du `.pptx` via **python-pptx** (aucun outil payant)
- [ ] Charte : drapeau CI (orange `#FF8200`, blanc, vert `#009A44`), logo cacao en orbite, typo libre (Poppins/Inter)
- [ ] Trame 5 min / ~12 slides :
  1. Titre — *CacaoSat, le spatial pour bâtir*
  2. Le choc réglementaire EUDR (chiffres : N°1 mondial, 82 %, 30 %, 2M+ foyers)
  3. Qui porte le poids : les petites coopératives
  4. Insight — *la donnée existe déjà, gratuite ; ce qui manque, c'est le pipeline*
  5. La solution CacaoSat — le pipeline en 6 étapes
  6. Démo 1 — app mobile : relevé GPS hors‑ligne d'une parcelle
  7. Démo 2 — dashboard : carte des parcelles scorées, zone à risque
  8. Démo 3 — certificat de conformité EUDR généré en 1 clic (PDF)
  9. Sous le capot — Sentinel‑2 + Hansen/GFW + Digital Earth Africa, 100 % open data
  10. Impact — économique / social / environnemental / institutionnel
  11. Au‑delà du hackathon — pilote coopérative + Conseil du Café‑Cacao
  12. L'équipe + appel à soutien
- [ ] Export **PDF** (`libreoffice --headless --convert-to pdf`) → `pitch/CacaoSat-Pitch.pdf`
- [ ] `pitch/SCRIPT.md` — texte minuté du pitch (chrono par slide)
- [ ] `make pitch` régénère `.pptx` + `.pdf`

**Definition of Done :** `pitch/CacaoSat-Pitch.pptx` et `.pdf` présents, régénérables, cohérents avec la démo.

---

## Lot 11 — Durcissement & release  `[ ]`

- [ ] Seed de démo réaliste : 1 zone pilote (région du Cavally/Guémon), 2 coopératives, ~40 producteurs, ~60 parcelles dont plusieurs en zone à risque et 1 cas de déforestation post‑2020 net
- [ ] Smoke test e2e : `scripts/smoke.sh` (login → créer parcelle → analyser → générer rapport → télécharger PDF)
- [ ] `docker compose up` à froid : stack complète verte en < 3 min
- [ ] Revue accessibilité web (contraste AA, navigation clavier, `prefers-reduced-motion`)
- [ ] Relecture des 6 docs : toutes les cases pertinentes cochées
- [ ] Merge `develop → preprod` (CI verte) puis `preprod → prod` ; tags `v1.0.0-preprod`, `v1.0.0`
- [ ] README : badges CI, captures d'écran, lien démo

**Definition of Done :** les 3 branches à jour, tag `v1.0.0` sur `prod`, `scripts/smoke.sh` vert.

---

## Jalons Git

| Jalon | Contenu | Action |
|-------|---------|--------|
| **M1** | Lots 1–3 (backend complet) | push `develop` → merge `preprod` |
| **M2** | Lots 4–6 (web complet) | push `develop` → merge `preprod` |
| **M3** | Lots 7–8 (mobile complet) | push `develop` → merge `preprod` |
| **M4** | Lot 9 (infra/CI) | push `develop` → merge `preprod` |
| **M5** | Lots 10–11 (pitch + release) | merge `preprod` → `prod`, tag `v1.0.0` |

## Convention de commits

`type(scope): sujet` — types : `feat`, `fix`, `chore`, `docs`, `test`, `ci`, `refactor`, `perf`.
Scopes : `backend`, `web`, `mobile`, `infra`, `pitch`, `repo`.
Chaque commit de fin de lot met aussi à jour les cases `[x]` des docs concernés **dans le même commit**.

## Accès GitHub (action requise de l'utilisateur)

Le push nécessite une authentification. Dans ce terminal, lancer :

```
! gh auth login
```

(ou fournir un *Personal Access Token* avec scope `repo`). Une fois authentifié, l'agent poussera `main`, `develop`, `preprod`, `prod` sur `https://github.com/daniel10027/CacaoSat.git` et poursuivra les lots.
