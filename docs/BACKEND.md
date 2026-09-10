# Backend — API Flask, base géospatiale, moteur satellite & scoring EUDR

**Rôle :** exposer l'API REST qui reçoit les relevés terrain, les structure dans PostGIS, les croise avec les données satellites (mockées), calcule le score de conformité EUDR, génère les rapports/certificats et les alertes.

**Stack (100 % libre) :** Flask 3 · Flask‑SQLAlchemy 3 · GeoAlchemy2 · PostgreSQL 16 + PostGIS 3 · Flask‑Migrate (Alembic) · Flask‑JWT‑Extended · Marshmallow · Shapely / pyproj · NumPy · ReportLab (PDF) · APScheduler (jobs) · Redis (file d'attente légère) · Gunicorn (prod) · pytest + coverage · Ruff (lint) · MailHog (mock e‑mail) · MinIO (mock stockage objet S3).

**Base URL :** `/api/v1` · **Auth :** Bearer JWT · **Format géo :** GeoJSON (EPSG:4326).

---

## Statut du lot : `[x]` Lot 1 (terminé) · `[x]` Lot 2 (terminé) · `[x]` Lot 3 (terminé)

---

## Lot 1 — Socle backend

### 1.1 Projet & configuration
- [x] `backend/pyproject.toml` — métadonnées, dépendances, config Ruff + pytest
- [x] `backend/requirements.txt` + `requirements-dev.txt` (versions épinglées)
- [x] `backend/app/__init__.py` — **application factory** `create_app(config_name)`
- [x] `backend/app/config.py` — classes `BaseConfig / DevConfig / TestConfig / ProdConfig`, lecture `.env` via `python-dotenv`
- [x] `backend/.env.example` — `FLASK_ENV`, `DATABASE_URL`, `JWT_SECRET_KEY`, `REDIS_URL`, `CORS_ORIGINS`, `MAIL_*`, `S3_*`, `MOCK_SEED`
- [x] `backend/app/extensions.py` — instances `db`, `migrate`, `jwt`, `ma`, `cors`, `scheduler`
- [x] `backend/wsgi.py` — point d'entrée Gunicorn
- [x] `backend/app/errors.py` — handlers JSON uniformes (`400/401/403/404/409/422/500`), enveloppe `{error: {code, message, details}}`
- [x] `backend/app/logging.py` — logs structurés JSON (stdout), niveau par env

### 1.2 Base de données géospatiale
- [x] Connexion PostGIS + activation extension `postgis` via migration Alembic
- [x] `backend/app/models/base.py` — `TimestampMixin`, `UUIDMixin`, `SoftDeleteMixin`
- [x] `models/cooperative.py` — `Cooperative(id, name, code, region, department, contact_name, contact_phone, contact_email, created_at)`
- [x] `models/user.py` — `User(id, email, password_hash, full_name, role, cooperative_id, is_active)` ; rôles : `agent | manager | exporter | regulator | admin`
- [x] `models/producer.py` — `Producer(id, cooperative_id, external_ref, full_name, national_id, gender, village, phone, registered_at)`
- [x] `models/parcel.py` — `Parcel(id, code, producer_id, cooperative_id, geometry: Geometry(POLYGON,4326), area_ha, centroid, planting_year, crop, gps_accuracy_m, collection_method, collected_by, collected_at, source, status)` ; index GIST sur `geometry`
- [x] `models/analysis_run.py` — `AnalysisRun(id, parcel_id, provider_versions: JSONB, forest_cover_2020_pct, forest_cover_current_pct, forest_loss_ha, loss_events: JSONB, ndvi_series: JSONB, protected_area_overlap_ha, deforestation_detected: bool, confidence, created_at)`
- [x] `models/compliance_score.py` — `ComplianceScore(id, parcel_id, analysis_run_id, score, risk_level, eudr_status, factors: JSONB, computed_at)` ; `risk_level: low|medium|high` ; `eudr_status: compliant|at_risk|non_compliant`
- [x] `models/compliance_report.py` — `ComplianceReport(id, cooperative_id, title, period_start, period_end, parcel_ids: JSONB, summary: JSONB, pdf_key, geojson_key, content_hash, generated_by, generated_at)`
- [x] `models/alert.py` — `Alert(id, parcel_id, type, severity, detected_at, area_ha, geometry, message, acknowledged, acknowledged_by, acknowledged_at)` ; `type: new_deforestation|protected_encroachment|data_gap`
- [x] `models/sync_batch.py` — `SyncBatch(id, device_id, user_id, received_at, item_count, accepted, rejected, errors: JSONB, status)`
- [x] `models/audit_log.py` — `AuditLog(id, actor_id, action, entity_type, entity_id, payload: JSONB, created_at, ip)`
- [x] `backend/migrations/` — migration initiale générée + relue (types géo, index, FK, enums)

### 1.3 Authentification & autorisation
- [x] `app/api/auth.py` — `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`
- [x] Hash mots de passe `argon2` (via `argon2-cffi`)
- [x] JWT access (15 min) + refresh (7 j), claims `role`, `cooperative_id`
- [x] `app/security.py` — décorateurs `@roles_required(...)`, helper `scope_cooperative_id()` (portée coopérative / nationale)
- [x] Rate‑limit `POST /auth/login` (Flask‑Limiter, backend mémoire en dev / Redis en prod)

### 1.4 Schémas & validation
- [x] `app/schemas/` amorcé — Marshmallow `auth` (login/token/user). Les schémas par ressource (cooperative, producer, parcel, …) sont créés au **Lot 2** avec leurs endpoints.
- [x] Helper `app/geo.py` — parse/valide GeoJSON (polygone valide, non auto‑intersectant, dans l'emprise CI, surface plausible), calcul `area_ha` (repro EPSG:32630), `centroid`, `WKTElement`, `FeatureCollection`, `parse_bbox`

### 1.5 Santé, seed, outillage
- [x] `GET /health` (liveness) + `GET /health/ready` (DB + Redis) + `GET /metrics` (compteurs Prometheus texte)
- [x] `backend/seeds/seed.py` + `flask seed` (CLI) — 1 admin, 1 régulateur, 2 coopératives, 1 manager + 2 agents chacune, données mock chargées
- [x] `flask seed-demo` — zone pilote (Cavally/Guiglo) : 24 producteurs + 41 parcelles géolocalisées générées de façon déterministe (le GeoJSON figé arrive au Lot 11)
- [x] `backend/README.md` (run local, migrations, seed, tests, comptes de démo)

### 1.6 Conteneurisation
- [x] `backend/Dockerfile` — multi‑stage (builder deps → runtime slim), user non‑root, `HEALTHCHECK`, `CMD gunicorn -c gunicorn.conf.py wsgi:app`
- [x] `backend/gunicorn.conf.py` — workers = `2*cpu+1`, timeout, access log JSON
- [x] `backend/.dockerignore`
- [x] `backend/entrypoint.sh` — attend la DB, applique `flask db upgrade`, (option) `flask seed`, puis exec CMD

### 1.7 Tests (Lot 1)
- [x] `backend/tests/conftest.py` — app de test, base `cacaosat_test` auto‑créée (+ extension PostGIS), nettoyage par test, fixtures `seeded` / `auth_header`
- [x] `tests/test_auth.py`, `tests/test_health.py`, `tests/test_models_geo.py` (round‑trip polygone, area_ha, index GiST), `tests/test_config.py`
- [x] `make test` → `pytest --cov=app --cov-fail-under=80` — **20 tests verts, couverture 85 %**

**Definition of Done Lot 1 :** ✅ `docker compose up --build backend db` démarre, migrations Alembic appliquées (up + down réversibles), `flask seed` + `flask seed-demo` peuplent la base, `GET /health/ready` = 200, `POST /auth/login` renvoie un JWT, `make test` vert (85 %), `ruff check` propre.

---

## Lot 2 — Moteur satellite (mock) + scoring EUDR + API métier

### 2.1 Mocks des services externes (déterministes)
- [x] `app/mocks/__init__.py` — registre, seed global `MOCK_SEED`
- [x] `app/mocks/sentinel2.py` — pour une géométrie + intervalle de dates, renvoie une **série temporelle NDVI** (12–36 points) générée de façon déterministe (hash(parcel_id) → RNG NumPy) : saisonnalité + tendance + bruit ; capable de simuler une **chute nette de NDVI** (coupe forestière) à une date donnée
- [x] `app/mocks/gfw_hansen.py` — renvoie `tree_cover_2000_pct`, `lossyear` (0 = pas de perte, sinon année 2001‑2025) échantillonné sur une grille dans le polygone → `forest_cover_2020_pct`, `forest_loss_ha` post‑2020
- [x] `app/mocks/digital_earth_africa.py` — indice de dégradation des terres 0‑1 + tendance (utile zones frontalières)
- [x] `app/mocks/protected_areas.py` — jeu de polygones d'aires protégées / forêts classées de la zone pilote (GeoJSON embarqué) + fonction `overlap_ha(geom)`
- [x] `app/mocks/fixtures/protected_areas.geojson` — aires protégées (Forêt classée du Cavally, du Goin‑Débé, tampon Parc de Taï). Scénarios `compliant`/`at_risk`/`deforested` attribués de façon déterministe par `hash(parcel.id)` (+ `scenarios.SCENARIO_OVERRIDES` par code pour scénariser la démo)
- [x] Chaque mock expose `provider_version` (pour `AnalysisRun.provider_versions`) et est **remplaçable** par une vraie implémentation (interface `SatelliteProvider`)

### 2.2 Moteur d'analyse
- [x] `app/services/analysis.py` — `run_analysis(parcel) -> AnalysisRun` :
  - récupère NDVI (Sentinel‑2 mock), couvert forestier (GFW mock), dégradation (DEA mock), recouvrement aire protégée
  - détecte une rupture dans la série NDVI (méthode : moyenne glissante + seuil d'écart + `lossyear > 2020`)
  - calcule `forest_loss_ha`, `loss_events` (liste `{date, area_ha, ndvi_drop}`), `confidence`
  - persiste `AnalysisRun`
- [x] `app/services/analysis.py::analyze_many(parcel_ids)` — traitement par lot, rollback + rapport d'échec par parcelle
- [ ] Job planifié APScheduler : ré‑analyse quotidienne des parcelles `at_risk` — **déplacé au Lot 3** (branché avec le moteur d'alertes)

### 2.3 Moteur de scoring EUDR
- [x] `app/services/scoring.py` — `compute_score(analysis_run, parcel, context) -> ComplianceScore`, **logique réelle, pondérée, explicable** :

  | Facteur | Poids | Règle |
  |--------|------:|------|
  | Déforestation post‑2020 sur la parcelle | 45 | `forest_loss_ha` vs surface : 0 perte → 45 pts ; dégressif ; > 5 % surface → 0 |
  | Recouvrement aire protégée / forêt classée | 20 | 0 recouvrement → 20 ; proportionnel au % recouvert |
  | Tendance NDVI / dégradation (DEA) | 15 | stable/positif → 15 ; déclin marqué → 0 |
  | Complétude de la donnée (producteur lié, `national_id`, géométrie valide) | 10 | tout présent → 10 |
  | Qualité du relevé GPS (`gps_accuracy_m`) + fraîcheur (`collected_at`) | 10 | ≤ 5 m & < 12 mois → 10 ; dégressif |

  - `score` = somme (0‑100)
  - `risk_level` : `score ≥ 80 → low` · `50‑79 → medium` · `< 50 → high`
  - `eudr_status` : `low & 0 déforestation & 0 recouvrement → compliant` · `medium → at_risk` · `high → non_compliant`
  - `factors` : liste `{key, label, weight, raw_value, points, explanation}` (traçable dans le rapport)
- [x] `tests/test_scoring.py` — cas limites : parcelle propre → `compliant` ~95 ; perte 3 % surface → `at_risk` ; coupe nette + aire protégée → `non_compliant` ; barème documenté figé par snapshot

### 2.4 Endpoints CRUD & métier
- [x] `app/api/cooperatives.py` — `GET/POST /cooperatives`, `GET/PATCH /cooperatives/{id}` (admin/régulateur ; manager lecture de la sienne)
- [x] `app/api/producers.py` — `GET/POST /producers`, `GET/PATCH/DELETE /producers/{id}` (scopé coopérative), recherche `?q=`
- [x] `app/api/parcels.py` — `GET /parcels` (filtres : `cooperative_id, producer_id, risk_level, eudr_status, bbox`, pagination, tri), `POST /parcels` (GeoJSON), `GET/PATCH/DELETE /parcels/{id}`, `GET /parcels/{id}.geojson`
- [x] `POST /parcels/{id}/analyze` — lance analyse + scoring, renvoie `{analysis_run, compliance_score}`
- [x] `POST /analysis/batch` — `{parcel_ids | cooperative_id}` → lot, renvoie résumé
- [x] `GET /parcels/{id}/history` — analyses + scores triés
- [x] `app/api/dashboard.py` :
  - `GET /dashboard/summary?cooperative_id=` → `{parcels_total, area_ha_total, compliant, at_risk, non_compliant, deforestation_events, high_risk_area_ha, coverage_pct, score_distribution, trend: [{month, compliant_pct}]}`
  - `GET /dashboard/map?cooperative_id=&bbox=` → `FeatureCollection` parcelles + `properties {code, producer, score, risk_level, eudr_status, area_ha}`
  - `GET /dashboard/regions` → agrégats par région (pour la carte nationale de la landing)
- [x] Pagination/tri/filtre factorisés (`app/api/_helpers.py`)
- [x] OpenAPI : `app/openapi.py` sert `/api/v1/openapi.json` (spec 3.0.3 maintenue à la main, zéro dépendance, couvre les 25 routes) + console Swagger UI sur `/api/v1/docs` (assets via CDN unpkg — outil de dev)

### 2.5 Tests (Lot 2)
- [x] `tests/test_mocks.py` — déterminisme (même seed → même sortie), scénarios `compliant/at_risk/deforested`
- [x] `tests/test_analysis.py` — détection de rupture NDVI, `forest_loss_ha`, recouvrement aire protégée
- [x] `tests/test_parcels_api.py`, `tests/test_dashboard_api.py`, `tests/test_cooperatives_api.py`, `tests/test_producers_api.py` — auth, scoping coopérative, filtres, bbox, pagination, formes de réponse
- [x] Couverture **86 %** (62 tests)

**Definition of Done Lot 2 :** ✅ validé en conteneur — `POST /parcels` (GeoJSON) → `POST /{id}/analyze` → score EUDR explicable (5 facteurs) cohérent avec le scénario ; `POST /analysis/batch` (21/21) ; `GET /dashboard/summary` (KPIs + distribution + tendance), `/dashboard/map` (FeatureCollection scorée), `/dashboard/regions` (public) exploitables ; `/openapi.json` + `/docs` servis ; `make test` vert (62 tests, 86 %), `ruff` propre.

---

## Lot 3 — Rapports, alertes, synchronisation mobile

### 3.1 Génération de rapport / certificat de conformité
- [x] `app/services/report.py` — `generate_report(cooperative_id, period, parcel_ids=None) -> ComplianceReport` :
  - agrège scores + analyses des parcelles retenues
  - **PDF** (ReportLab platypus) : en‑tête `CACAOSAT` + « Certificat de conformité EUDR », bloc coopérative/période/empreinte SHA‑256, préambule légal EUDR (coordonnées GPS + absence de déforestation depuis le 31/12/2020), synthèse, **carte des parcelles** (`reportlab.graphics` — polygones projetés, couleur = statut, aucune dépendance image), tableau par producteur/parcelle (code, producteur, surface, score, statut, motif principal), annexe méthodologie & sources
  - **GeoJSON** export : `FeatureCollection` au gabarit exportateurs (`PlotId`, `ProducerName`, `ProducerId`, `NationalId`, `Area`, `ProductionPlace`, `ProductionDate`, `Commodity`, `eudr_status`, `risk_level`, `score`, `deforestation_after_2020`)
  - `content_hash` = SHA‑256 du contenu normalisé (JSON trié — anti‑falsification, stable entre deux générations identiques)
  - stockage : `app/storage.py` → MinIO/S3 (`boto3`) si joignable, **repli disque local** (`instance/storage/`) sinon
- [x] `app/api/reports.py` — `POST /reports`, `GET /reports` (scopé, paginé), `GET /reports/{id}`, `GET /reports/{id}/download?format=pdf|geojson` (stream + `Content-Disposition`)
- [x] `tests/test_report.py` — le PDF se génère (> 0 octet, en‑tête `%PDF`), le GeoJSON valide le schéma, `content_hash` stable

### 3.2 Alertes précoces
- [x] `app/services/alerts.py` — `scan_for_alerts()` : compare la dernière analyse à la précédente ; crée `Alert` si nouvelle perte de couvert, nouveau recouvrement d'aire protégée, ou `data_gap` (parcelle sans producteur/national_id)
- [x] Job APScheduler quotidien (`app/tasks/scheduler.py`, activé par `SCHEDULER_ENABLED=1`) → ré‑analyse des parcelles `at_risk`/`non_compliant` puis `scan_for_alerts()` ; notification e‑mail MailHog + log SMS (`app/mocks/notifications.py`) aux managers de la coopérative
- [x] `app/api/alerts.py` — `GET /alerts` (filtres `cooperative_id, severity, acknowledged, type`), `GET /alerts/{id}`, `POST /alerts/{id}/acknowledge`
- [x] `GET /alerts/stream` — SSE (Server‑Sent Events) pour le temps réel dans le dashboard (fallback polling documenté)
- [x] `tests/test_alerts.py` — génération sur transition d'état, acquittement, scoping

### 3.3 Synchronisation mobile (hors‑ligne → serveur)
- [x] `GET /sync/bootstrap?since=<iso>` — renvoie coopérative, producteurs, parcelles, aires protégées (GeoJSON), barème de scoring, version de schéma → permet à l'app de fonctionner hors‑ligne
- [x] `POST /sync/batch` — corps : `{device_id, client_generated_at, items: [{op, entity, client_id, data, updated_at}]}` :
  - `entity ∈ {producer, parcel}` ; `op ∈ {create, update}`
  - résolution d'ID : `client_id` (UUID généré offline) → mapping serveur renvoyé
  - **idempotence** (rejeu du même batch sans doublon) via `device_id + client_id`
  - conflits : stratégie *last‑write‑wins* horodatée + rapport des rejets
  - déclenche l'analyse asynchrone des nouvelles parcelles
  - réponse : `{batch_id, accepted, rejected, id_map, server_time}`
- [x] `GET /sync/status/{batch_id}` — avancement de l'analyse des parcelles du batch
- [x] `models/sync_batch.py` persistance + `AuditLog`
- [x] `tests/test_sync.py` — bootstrap, batch création producteur+parcelle, rejeu idempotent, conflit

### 3.4 Transverse
- [x] `app/audit.py` — helper `record(action, entity_type, entity_id, **payload)` appelé sur les écritures sensibles (analyse, rapport, acquittement, sync) ; `actor_id` validé (pas de FK cassée)
- [x] `flask` CLI : `flask reanalyze [--all]`, `flask scan-alerts`, `flask make-report --coop <code>`
- [x] `app/api/__init__.py` — 34 routes enregistrées sous `/api/v1`, CORS depuis `CORS_ORIGINS`
- [x] Couverture **83 %** (76 tests) — `tests/test_report.py`, `test_alerts.py`, `test_sync.py`

**Definition of Done Lot 3 :** ✅ validé en conteneur — `POST /reports` → PDF (`%PDF-`, carte + tableau) + GeoJSON gabarit exportateurs téléchargeables, `content_hash` stable ; `flask scan-alerts` crée des alertes visibles via `/alerts` + notif MailHog ; batch mobile simulé (`/sync/batch`) crée producteur + parcelle, renvoie l'`id_map`, rejeu idempotent, analyse déclenchée ; `make test` vert (76 tests, 83 %), `ruff` propre. **→ jalon M1 : merge `develop → preprod`.**

---

## Contrat d'API (résumé)

| Méthode | Route | Rôle min. | Description |
|--------|-------|-----------|-------------|
| POST | `/api/v1/auth/login` | public | login → tokens |
| POST | `/api/v1/auth/refresh` | refresh | renouvelle l'access token |
| GET | `/api/v1/auth/me` | agent | profil courant |
| GET/POST | `/api/v1/cooperatives` | manager/regulator | liste / création |
| GET/POST | `/api/v1/producers` | agent | liste / création |
| GET/POST | `/api/v1/parcels` | agent | liste (filtres, bbox) / création GeoJSON |
| POST | `/api/v1/parcels/{id}/analyze` | agent | analyse + score |
| POST | `/api/v1/analysis/batch` | manager | analyse par lot |
| GET | `/api/v1/parcels/{id}/history` | agent | historique |
| GET | `/api/v1/dashboard/summary` | manager | KPIs coopérative |
| GET | `/api/v1/dashboard/map` | manager | parcelles GeoJSON scorées |
| GET | `/api/v1/dashboard/regions` | public | agrégats nationaux (landing) |
| POST/GET | `/api/v1/reports` | manager | génère / liste rapports |
| GET | `/api/v1/reports/{id}/download` | manager | PDF ou GeoJSON |
| GET | `/api/v1/alerts` | manager | alertes |
| POST | `/api/v1/alerts/{id}/acknowledge` | manager | acquitte |
| GET | `/api/v1/alerts/stream` | manager | SSE temps réel |
| GET | `/api/v1/sync/bootstrap` | agent | données de référence offline |
| POST | `/api/v1/sync/batch` | agent | push relevés terrain |
| GET | `/api/v1/health` `/health/ready` `/metrics` | public | ops |
| GET | `/api/v1/openapi.json` · `/api/v1/docs` | public | contrat + Swagger UI |

## Rôles & périmètres

- **agent** : sa coopérative — crée producteurs/parcelles, lance analyses, consulte.
- **manager** : sa coopérative — + rapports, alertes, tableau de bord complet.
- **exporter** : lecture multi‑coopératives sur données partagées + téléchargement d'exports.
- **regulator** : lecture nationale + agrégats.
- **admin** : tout + gestion des comptes.

## Variables d'environnement (`backend/.env.example`)

```
FLASK_ENV=development
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me
DATABASE_URL=postgresql+psycopg://cacaosat:cacaosat@localhost:5432/cacaosat
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173,http://LAN_IP:5173
MAIL_SERVER=localhost
MAIL_PORT=1025
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=cacaosat
MOCK_SEED=42
```

## Changelog du backend

| Date | Lot | Commit | Note |
|------|-----|--------|------|
| — | 0 | `chore(repo): bootstrap` | squelette `backend/` créé |
| 2026-09-10 | 1 | `feat(backend): socle Flask + PostGIS + auth JWT` | app factory, 10 modèles PostGIS, migration Alembic réversible, auth argon2/JWT, health/ready/metrics, seed + seed-demo, Dockerfile, 20 tests (cov 85 %) |
| 2026-09-10 | 2 | `feat(backend): moteur satellite mock + scoring EUDR + API métier` | mocks Sentinel-2/GFW-Hansen/DEA/aires protégées déterministes, moteur d'analyse (rupture NDVI, perte couvert, recouvrement), scoring EUDR pondéré/explicable (5 facteurs), CRUD cooperatives/producers/parcels, `/parcels/{id}/analyze`, `/analysis/batch`, `/dashboard/{summary,map,regions}`, OpenAPI 3.0.3 + `/docs`. 62 tests (cov 86 %) |
| 2026-09-10 | 3 | `feat(backend): rapports PDF/GeoJSON + alertes précoces + sync mobile` | `app/services/report.py` (PDF ReportLab + carte + GeoJSON exportateurs + hash SHA-256), `app/storage.py` (MinIO/S3 + repli local), `app/services/alerts.py` + `/alerts` + SSE + notifs MailHog/SMS, `app/services/sync.py` + `/sync/{bootstrap,batch,status}` (idempotent, LWW, id_map), `app/tasks/scheduler.py` (job quotidien), `app/audit.py`, CLI `reanalyze`/`scan-alerts`/`make-report`. 76 tests (cov 83 %) |
