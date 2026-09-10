# Backend — API Flask, base géospatiale, moteur satellite & scoring EUDR

**Rôle :** exposer l'API REST qui reçoit les relevés terrain, les structure dans PostGIS, les croise avec les données satellites (mockées), calcule le score de conformité EUDR, génère les rapports/certificats et les alertes.

**Stack (100 % libre) :** Flask 3 · Flask‑SQLAlchemy 3 · GeoAlchemy2 · PostgreSQL 16 + PostGIS 3 · Flask‑Migrate (Alembic) · Flask‑JWT‑Extended · Marshmallow · Shapely / pyproj · NumPy · ReportLab (PDF) · APScheduler (jobs) · Redis (file d'attente légère) · Gunicorn (prod) · pytest + coverage · Ruff (lint) · MailHog (mock e‑mail) · MinIO (mock stockage objet S3).

**Base URL :** `/api/v1` · **Auth :** Bearer JWT · **Format géo :** GeoJSON (EPSG:4326).

---

## Statut du lot : `[ ]` Lot 1 · `[ ]` Lot 2 · `[ ]` Lot 3

---

## Lot 1 — Socle backend

### 1.1 Projet & configuration
- [ ] `backend/pyproject.toml` — métadonnées, dépendances, config Ruff + pytest
- [ ] `backend/requirements.txt` + `requirements-dev.txt` (versions épinglées)
- [ ] `backend/app/__init__.py` — **application factory** `create_app(config_name)`
- [ ] `backend/app/config.py` — classes `BaseConfig / DevConfig / TestConfig / ProdConfig`, lecture `.env` via `python-dotenv`
- [ ] `backend/.env.example` — `FLASK_ENV`, `DATABASE_URL`, `JWT_SECRET_KEY`, `REDIS_URL`, `CORS_ORIGINS`, `MAIL_*`, `S3_*`, `MOCK_SEED`
- [ ] `backend/app/extensions.py` — instances `db`, `migrate`, `jwt`, `ma`, `cors`, `scheduler`
- [ ] `backend/wsgi.py` — point d'entrée Gunicorn
- [ ] `backend/app/errors.py` — handlers JSON uniformes (`400/401/403/404/409/422/500`), enveloppe `{error: {code, message, details}}`
- [ ] `backend/app/logging.py` — logs structurés JSON (stdout), niveau par env

### 1.2 Base de données géospatiale
- [ ] Connexion PostGIS + activation extension `postgis` via migration Alembic
- [ ] `backend/app/models/base.py` — `TimestampMixin`, `UUIDMixin`, `SoftDeleteMixin`
- [ ] `models/cooperative.py` — `Cooperative(id, name, code, region, department, contact_name, contact_phone, contact_email, created_at)`
- [ ] `models/user.py` — `User(id, email, password_hash, full_name, role, cooperative_id, is_active)` ; rôles : `agent | manager | exporter | regulator | admin`
- [ ] `models/producer.py` — `Producer(id, cooperative_id, external_ref, full_name, national_id, gender, village, phone, registered_at)`
- [ ] `models/parcel.py` — `Parcel(id, code, producer_id, cooperative_id, geometry: Geometry(POLYGON,4326), area_ha, centroid, planting_year, crop, gps_accuracy_m, collection_method, collected_by, collected_at, source, status)` ; index GIST sur `geometry`
- [ ] `models/analysis_run.py` — `AnalysisRun(id, parcel_id, provider_versions: JSONB, forest_cover_2020_pct, forest_cover_current_pct, forest_loss_ha, loss_events: JSONB, ndvi_series: JSONB, protected_area_overlap_ha, deforestation_detected: bool, confidence, created_at)`
- [ ] `models/compliance_score.py` — `ComplianceScore(id, parcel_id, analysis_run_id, score, risk_level, eudr_status, factors: JSONB, computed_at)` ; `risk_level: low|medium|high` ; `eudr_status: compliant|at_risk|non_compliant`
- [ ] `models/compliance_report.py` — `ComplianceReport(id, cooperative_id, title, period_start, period_end, parcel_ids: JSONB, summary: JSONB, pdf_key, geojson_key, content_hash, generated_by, generated_at)`
- [ ] `models/alert.py` — `Alert(id, parcel_id, type, severity, detected_at, area_ha, geometry, message, acknowledged, acknowledged_by, acknowledged_at)` ; `type: new_deforestation|protected_encroachment|data_gap`
- [ ] `models/sync_batch.py` — `SyncBatch(id, device_id, user_id, received_at, item_count, accepted, rejected, errors: JSONB, status)`
- [ ] `models/audit_log.py` — `AuditLog(id, actor_id, action, entity_type, entity_id, payload: JSONB, created_at, ip)`
- [ ] `backend/migrations/` — migration initiale générée + relue (types géo, index, FK, enums)

### 1.3 Authentification & autorisation
- [ ] `app/api/auth.py` — `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`
- [ ] Hash mots de passe `argon2` (via `argon2-cffi`)
- [ ] JWT access (15 min) + refresh (7 j), claims `role`, `cooperative_id`
- [ ] `app/security.py` — décorateurs `@roles_required(...)`, `@same_cooperative_or_regulator`
- [ ] Rate‑limit `POST /auth/login` (Flask‑Limiter, backend mémoire en dev / Redis en prod)

### 1.4 Schémas & validation
- [ ] `app/schemas/` — Marshmallow pour chaque ressource (dump + load), validation GeoJSON polygone (anneau fermé, ≥ 4 points, surface > 0, dans l'emprise Côte d'Ivoire)
- [ ] Helper `app/geo.py` — parse/valide GeoJSON, calcul `area_ha` (repro EPSG:32630), `centroid`, simplification tolérante

### 1.5 Santé, seed, outillage
- [ ] `GET /health` (liveness) + `GET /health/ready` (DB + Redis) + `GET /metrics` (compteurs Prometheus texte)
- [ ] `backend/seeds/seed.py` + `flask seed` (CLI) — 1 admin, 1 régulateur, 2 coopératives, 1 manager + 2 agents chacune, données mock chargées
- [ ] `backend/seeds/demo_zone.geojson` — parcelles de la zone pilote
- [ ] `flask routes` documenté ; `backend/README.md` (run local, migrations, seed, tests)

### 1.6 Conteneurisation
- [ ] `backend/Dockerfile` — multi‑stage (builder deps → runtime slim), user non‑root, `HEALTHCHECK`, `CMD gunicorn -c gunicorn.conf.py wsgi:app`
- [ ] `backend/gunicorn.conf.py` — workers = `2*cpu+1`, timeout, access log JSON
- [ ] `backend/.dockerignore`
- [ ] `backend/entrypoint.sh` — attend la DB, applique `flask db upgrade`, (option) `flask seed`, puis exec CMD

### 1.7 Tests (Lot 1)
- [ ] `backend/tests/conftest.py` — app de test, DB éphémère (PostGIS via testcontainers **ou** base `_test` dédiée), client, factories (`factory_boy`)
- [ ] `tests/test_auth.py`, `tests/test_health.py`, `tests/test_models_geo.py` (round‑trip polygone, area_ha, index GIST)
- [ ] `make test` → `pytest -q --cov=app --cov-fail-under=80`

**Definition of Done Lot 1 :** `docker compose up backend db` démarre, migrations appliquées, `flask seed` peuple la base, `GET /health/ready` = 200, `POST /auth/login` renvoie un JWT, `make test` vert.

---

## Lot 2 — Moteur satellite (mock) + scoring EUDR + API métier

### 2.1 Mocks des services externes (déterministes)
- [ ] `app/mocks/__init__.py` — registre, seed global `MOCK_SEED`
- [ ] `app/mocks/sentinel2.py` — pour une géométrie + intervalle de dates, renvoie une **série temporelle NDVI** (12–36 points) générée de façon déterministe (hash(parcel_id) → RNG NumPy) : saisonnalité + tendance + bruit ; capable de simuler une **chute nette de NDVI** (coupe forestière) à une date donnée
- [ ] `app/mocks/gfw_hansen.py` — renvoie `tree_cover_2000_pct`, `lossyear` (0 = pas de perte, sinon année 2001‑2025) échantillonné sur une grille dans le polygone → `forest_cover_2020_pct`, `forest_loss_ha` post‑2020
- [ ] `app/mocks/digital_earth_africa.py` — indice de dégradation des terres 0‑1 + tendance (utile zones frontalières)
- [ ] `app/mocks/protected_areas.py` — jeu de polygones d'aires protégées / forêts classées de la zone pilote (GeoJSON embarqué) + fonction `overlap_ha(geom)`
- [ ] `app/mocks/fixtures/` — GeoJSON aires protégées, paramètres de scénarios (`compliant`, `at_risk`, `deforested`) mappés par `parcel.code` pour une démo scénarisée
- [ ] Chaque mock expose `provider_version` (pour `AnalysisRun.provider_versions`) et est **remplaçable** par une vraie implémentation (interface `SatelliteProvider`)

### 2.2 Moteur d'analyse
- [ ] `app/services/analysis.py` — `run_analysis(parcel) -> AnalysisRun` :
  - récupère NDVI (Sentinel‑2 mock), couvert forestier (GFW mock), dégradation (DEA mock), recouvrement aire protégée
  - détecte une rupture dans la série NDVI (méthode : moyenne glissante + seuil d'écart + `lossyear > 2020`)
  - calcule `forest_loss_ha`, `loss_events` (liste `{date, area_ha, ndvi_drop}`), `confidence`
  - persiste `AnalysisRun`
- [ ] `app/services/analysis.py::analyze_many(parcel_ids)` — traitement par lot, idempotent
- [ ] Job planifié APScheduler : ré‑analyse quotidienne des parcelles `at_risk` (génère des alertes — voir Lot 3)

### 2.3 Moteur de scoring EUDR
- [ ] `app/services/scoring.py` — `compute_score(analysis_run) -> ComplianceScore`, **logique réelle, pondérée, explicable** :

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
- [ ] `tests/test_scoring.py` — cas limites : parcelle propre → `compliant` ~95 ; perte 3 % surface → `at_risk` ; coupe nette + aire protégée → `non_compliant` ; barème documenté figé par snapshot

### 2.4 Endpoints CRUD & métier
- [ ] `app/api/cooperatives.py` — `GET/POST /cooperatives`, `GET/PATCH /cooperatives/{id}` (admin/régulateur ; manager lecture de la sienne)
- [ ] `app/api/producers.py` — `GET/POST /producers`, `GET/PATCH/DELETE /producers/{id}` (scopé coopérative), recherche `?q=`
- [ ] `app/api/parcels.py` — `GET /parcels` (filtres : `cooperative_id, producer_id, risk_level, eudr_status, bbox`, pagination, tri), `POST /parcels` (GeoJSON), `GET/PATCH/DELETE /parcels/{id}`, `GET /parcels/{id}.geojson`
- [ ] `POST /parcels/{id}/analyze` — lance analyse + scoring, renvoie `{analysis_run, compliance_score}`
- [ ] `POST /analysis/batch` — `{parcel_ids | cooperative_id}` → lot, renvoie résumé
- [ ] `GET /parcels/{id}/history` — analyses + scores triés
- [ ] `app/api/dashboard.py` :
  - `GET /dashboard/summary?cooperative_id=` → `{parcels_total, area_ha_total, compliant, at_risk, non_compliant, deforestation_events, high_risk_area_ha, coverage_pct, score_distribution, trend: [{month, compliant_pct}]}`
  - `GET /dashboard/map?cooperative_id=&bbox=` → `FeatureCollection` parcelles + `properties {code, producer, score, risk_level, eudr_status, area_ha}`
  - `GET /dashboard/regions` → agrégats par région (pour la carte nationale de la landing)
- [ ] Pagination/tri/filtre factorisés (`app/api/_pagination.py`)
- [ ] OpenAPI : `app/openapi.py` sert `/api/v1/openapi.json` (généré depuis les schémas Marshmallow via `apispec`) + Swagger UI statique sur `/api/v1/docs`

### 2.5 Tests (Lot 2)
- [ ] `tests/test_mocks.py` — déterminisme (même seed → même sortie), scénarios `compliant/at_risk/deforested`
- [ ] `tests/test_analysis.py` — détection de rupture NDVI, `forest_loss_ha`, recouvrement aire protégée
- [ ] `tests/test_parcels_api.py`, `tests/test_dashboard_api.py` — auth, scoping coopérative, formes de réponse
- [ ] Couverture ≥ 82 %

**Definition of Done Lot 2 :** créer une parcelle → `POST /analyze` → score cohérent avec le scénario ; `GET /dashboard/summary` et `/dashboard/map` renvoient des données exploitables par le web ; Swagger UI accessible ; tests verts.

---

## Lot 3 — Rapports, alertes, synchronisation mobile

### 3.1 Génération de rapport / certificat de conformité
- [ ] `app/services/report.py` — `generate_report(cooperative_id, period, parcel_ids=None) -> ComplianceReport` :
  - agrège scores + analyses des parcelles retenues
  - **PDF** (ReportLab) : page de garde (logo cacao en orbite, coopérative, période, hash), tableau par producteur/parcelle (code, surface, score, statut EUDR, motifs), carte statique des parcelles (rendu Matplotlib/Shapely en PNG, couleur = statut), annexe méthodologie & sources (Sentinel‑2 / Hansen‑GFW / DEA + versions), mentions EUDR (art. coordonnées + absence de déforestation depuis 31/12/2020)
  - **GeoJSON** export : `FeatureCollection` conforme au gabarit attendu exportateurs (propriétés : `ProducerName`, `ProducerId`, `PlotId`, `Area`, `ProductionDate`, `GeoID` optionnel, `eudr_status`)
  - `content_hash` = SHA‑256 du contenu normalisé (anti‑falsification)
  - stockage : MinIO (clé `reports/{id}/rapport.pdf`, `.../parcelles.geojson`) ; fallback disque local en dev
- [ ] `app/api/reports.py` — `POST /reports`, `GET /reports` (scopé), `GET /reports/{id}`, `GET /reports/{id}/download?format=pdf|geojson` (URL signée MinIO ou stream)
- [ ] `tests/test_report.py` — le PDF se génère (> 0 octet, en‑tête `%PDF`), le GeoJSON valide le schéma, `content_hash` stable

### 3.2 Alertes précoces
- [ ] `app/services/alerts.py` — `scan_for_alerts()` : compare la dernière analyse à la précédente ; crée `Alert` si nouvelle perte de couvert, nouveau recouvrement d'aire protégée, ou `data_gap` (parcelle sans producteur/national_id)
- [ ] Job APScheduler quotidien → `scan_for_alerts()` ; notification e‑mail via MailHog (mock) au manager de la coopérative + log SMS mock (`app/mocks/sms.py`)
- [ ] `app/api/alerts.py` — `GET /alerts` (filtres `cooperative_id, severity, acknowledged, type`), `GET /alerts/{id}`, `POST /alerts/{id}/acknowledge`
- [ ] `GET /alerts/stream` — SSE (Server‑Sent Events) pour le temps réel dans le dashboard (fallback polling documenté)
- [ ] `tests/test_alerts.py` — génération sur transition d'état, acquittement, scoping

### 3.3 Synchronisation mobile (hors‑ligne → serveur)
- [ ] `GET /sync/bootstrap?since=<iso>` — renvoie coopérative, producteurs, parcelles, aires protégées (GeoJSON), barème de scoring, version de schéma → permet à l'app de fonctionner hors‑ligne
- [ ] `POST /sync/batch` — corps : `{device_id, client_generated_at, items: [{op, entity, client_id, data, updated_at}]}` :
  - `entity ∈ {producer, parcel}` ; `op ∈ {create, update}`
  - résolution d'ID : `client_id` (UUID généré offline) → mapping serveur renvoyé
  - **idempotence** (rejeu du même batch sans doublon) via `device_id + client_id`
  - conflits : stratégie *last‑write‑wins* horodatée + rapport des rejets
  - déclenche l'analyse asynchrone des nouvelles parcelles
  - réponse : `{batch_id, accepted, rejected, id_map, server_time}`
- [ ] `GET /sync/status/{batch_id}` — avancement de l'analyse des parcelles du batch
- [ ] `models/sync_batch.py` persistance + `AuditLog`
- [ ] `tests/test_sync.py` — bootstrap, batch création producteur+parcelle, rejeu idempotent, conflit

### 3.4 Transverse
- [ ] `AuditLog` branché sur toutes les écritures (middleware / signal SQLAlchemy)
- [ ] `flask` CLI : `flask analyze-all`, `flask scan-alerts`, `flask make-report --coop <code>`
- [ ] `app/api/__init__.py` — enregistrement de tous les blueprints, préfixe `/api/v1`, CORS configuré depuis `CORS_ORIGINS`
- [ ] `backend/tests/test_smoke_e2e.py` — parcours complet login→parcelle→analyse→rapport→download

**Definition of Done Lot 3 :** `POST /reports` produit un PDF + GeoJSON téléchargeables ; `flask scan-alerts` crée des alertes visibles via l'API ; un batch mobile simulé crée producteurs + parcelles et renvoie l'`id_map` ; e2e vert ; **push `develop` + merge `preprod` (jalon M1)**.

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
