# Infrastructure — Docker, CI/CD, script de dev réseau, observabilité

**Rôle :** rendre le projet **100 % reproductible et déployable** : une commande pour tout lancer en dev (backend + web + mobile sur le réseau local), une stack Docker de parité prod, une CI/CD GitHub Actions par composant, et une observabilité minimale.

**Stack (100 % libre) :** Docker + Docker Compose · GitHub Actions · GitHub Container Registry (GHCR) · Nginx (reverse proxy + statique web) · PostgreSQL 16 + PostGIS · Redis · **MailHog** (mock e‑mail) · **MinIO** (mock stockage objet) · Prometheus + Grafana (option, profil `observability`) · Trivy (scan image) · `hadolint` (lint Dockerfile).

---

## Statut du lot : `[ ]` Lot 9

---

## Lot 9 — Infrastructure & CI/CD

### 9.1 Compose de développement — services d'appui
- [ ] `infra/docker-compose.dev.yml` : `db` (postgis/postgis:16-3.4, volume, healthcheck), `redis`, `mailhog` (1025/8025), `minio` (9000/9001) + `minio-setup` (crée le bucket `cacaosat`)
- [ ] `infra/.env.dev` + `infra/.env.example` (ports, identifiants mock)
- [ ] `make infra-up` / `make infra-down` / `make infra-logs`

### 9.2 `scripts/dev.sh` — lancement réseau local (exigence clé)
- [ ] Détection IP LAN portable :
  - macOS : `ipconfig getifaddr en0 || ipconfig getifaddr en1`
  - Linux : `ip route get 1.1.1.1 | awk '{print $7; exit}'` (fallback `hostname -I | awk '{print $1}'`)
  - override : `HOST_LAN_IP=... ./scripts/dev.sh`
- [ ] Étapes du script :
  1. calcule `HOST_LAN_IP`, l'affiche en clair + QR code (via `qrencode` si dispo) de l'URL web
  2. `docker compose -f infra/docker-compose.dev.yml up -d` (db, redis, mailhog, minio) + attente healthchecks
  3. **backend** : venv, `pip install -r requirements.txt`, `flask db upgrade`, `flask seed` (si base vide), `flask run --host 0.0.0.0 --port 8000` — CORS élargi à `http://$HOST_LAN_IP:5173`
  4. **web** : `npm ci` si besoin, `VITE_API_URL=http://$HOST_LAN_IP:8000/api/v1 npm run dev -- --host 0.0.0.0 --port 5173`
  5. **mobile** : si un appareil/emulateur est détecté (`flutter devices`), `flutter run --dart-define=API_BASE_URL=http://$HOST_LAN_IP:8000` ; sinon afficher la commande exacte à lancer sur un poste avec téléphone + le `--dart-define` prêt à copier
  6. logs agrégés dans `.dev/logs/{backend,web,mobile}.log`, PID suivis
  7. `trap 'cleanup' INT TERM EXIT` — arrête proprement les 3 process + (option `--keep-infra`) laisse les conteneurs
- [ ] Flags : `--no-mobile`, `--no-web`, `--keep-infra`, `--seed-demo`
- [ ] `scripts/dev.sh` testé macOS + Linux ; `scripts/stop.sh` ; `scripts/reset-db.sh`
- [ ] `scripts/lan-info.sh` — affiche IP LAN + URLs (API, web, MailHog, MinIO console) + QR code

### 9.3 Compose applicatif complet (parité prod locale)
- [ ] `docker-compose.yml` (racine) : `db`, `redis`, `mailhog`, `minio`, `minio-setup`, `backend` (build `backend/`, `entrypoint.sh` → migrate + gunicorn), `web` (build `web/` → Nginx), `proxy` (Nginx : `/` → web, `/api` → backend, `/mail` → mailhog, gzip, en‑têtes sécurité)
- [ ] Profils : `--profile prod` (gunicorn multi‑workers, web statique, pas de hot reload), `--profile observability` (prometheus + grafana + node/pg exporters), défaut = dev intégré
- [ ] `docker compose up --build` : stack verte en < 3 min à froid, `curl localhost/api/v1/health/ready` = 200, web sur `localhost`
- [ ] `infra/nginx/default.conf`, `infra/nginx/prod.conf` ; volumes nommés ; `restart: unless-stopped`
- [ ] `.dockerignore` par contexte ; images taguées `ghcr.io/daniel10027/cacaosat-{backend,web}:<sha>`

### 9.4 CI — GitHub Actions
- [ ] `.github/workflows/backend.yml` : sur `push`/`PR` touchant `backend/**` → matrice Python 3.12, services `postgis` + `redis`, `ruff check`, `pytest --cov` (seuil 80 %), upload coverage (artefact), `hadolint backend/Dockerfile`
- [ ] `.github/workflows/web.yml` : sur `web/**` → Node 20, `npm ci`, `npm run lint`, `npm run typecheck`, `npm run build`, `npm run test`, Playwright (navigateur headless, backend mocké via MSW ou service compose), upload `dist/` + rapport Playwright
- [ ] `.github/workflows/mobile.yml` : sur `mobile/**` → `subosito/flutter-action`, `flutter pub get`, `flutter analyze`, `flutter test`, `flutter build apk --release --dart-define=API_BASE_URL=https://api.example` → artefact APK
- [ ] `.github/workflows/images.yml` : sur `push` `develop`/`preprod`/`prod` → build + push images GHCR (`backend`, `web`), scan **Trivy** (échec si CVE `HIGH/CRITICAL` corrigeable), cache layers
- [ ] `.github/workflows/deploy.yml` : `workflow_dispatch` + push `prod` → déploiement (voir 9.5), `environment:` `preprod` / `prod` avec approbation requise pour `prod`
- [ ] `.github/workflows/docs-check.yml` : vérifie qu'aucun lot marqué `[x]` dans les docs n'a de case enfant `[ ]` non justifiée (script `scripts/check_docs.py`) + liens Markdown valides
- [ ] Badges CI ajoutés au `README.md`
- [ ] Branch protection documentée : `develop` (CI verte requise), `preprod` (CI + 1 review), `prod` (CI + review + approbation environnement)

### 9.5 Déploiement (options gratuites, mock‑friendly)
- [ ] Cible par défaut : **un hôte unique** (VPS/poste) via `docker compose --profile prod up -d` piloté par `deploy.yml` en SSH (clé en secret GitHub) — coût nul si auto‑hébergé
- [ ] Alternative documentée (free tier) : backend sur **Render**/**Railway**/**Fly.io**, web sur **Netlify**/**Vercel**/**GitHub Pages**, DB PostGIS sur **Neon**/**Supabase** (extension postgis) — fichiers `render.yaml` / `fly.toml` / `netlify.toml` fournis mais non requis pour la démo
- [ ] `infra/deploy/` : `deploy.sh` (pull images, `compose up -d`, `flask db upgrade`, health check, rollback si échec), `caddy`/`nginx` TLS via Let's Encrypt (doc)
- [ ] Variables/secrets : `infra/deploy/README.md` liste les secrets GitHub (`SSH_HOST`, `SSH_KEY`, `REGISTRY_TOKEN`, `JWT_SECRET_KEY`, …)
- [ ] `preprod` et `prod` = mêmes images, `.env` distinct ; données de démo seedées en `preprod` uniquement

### 9.6 Observabilité & ops
- [ ] Backend expose `/api/v1/metrics` (Prometheus text) ; `infra/prometheus/prometheus.yml` scrape backend + exporters
- [ ] `infra/grafana/` : provisioning datasource + dashboard « CacaoSat » (req/s, latence p95, erreurs 5xx, analyses/j, alertes/j, taille DB)
- [ ] Logs JSON stdout collectés par `docker compose logs` ; doc rotation
- [ ] `make health` — vérifie tous les endpoints ; `make backup-db` / `make restore-db` (pg_dump vers `infra/backups/`)

### 9.7 Makefile racine (orchestrateur unique)
- [ ] Cibles : `dev` (→ `scripts/dev.sh`), `infra-up|down`, `up` (compose complet), `prod-up`, `down`, `test` (backend+web+mobile), `lint`, `seed`, `seed-demo`, `migrate`, `images`, `deploy-preprod`, `deploy-prod`, `pitch`, `health`, `clean`
- [ ] `make help` auto‑documenté (parse des commentaires `## `)

**Definition of Done Lot 9 :** `./scripts/dev.sh` lance backend+web+mobile sur l'IP LAN, un téléphone du même Wi‑Fi ouvre le web et l'app tape l'API sans tunnel ; `docker compose up --build` monte toute la stack ; les 4 workflows CI passent au vert sur `develop` ; images publiées sur GHCR ; **push `develop` + merge `preprod` (jalon M4)**.

---

## Schéma des environnements

| Env | Branche | Compose / Cible | Données | Accès |
|-----|---------|-----------------|---------|-------|
| **dev** | feature/`develop` | `scripts/dev.sh` + `docker-compose.dev.yml` | seed + `--seed-demo` | LAN (IP machine) |
| **integration** | `develop` | `docker-compose.yml` (défaut) en CI | seed | éphémère CI |
| **preprod** | `preprod` | `docker-compose.yml --profile prod` | seed démo réaliste | hôte preprod |
| **prod** | `prod` | `docker-compose.yml --profile prod` | vierge | hôte prod |

## Ports (dev)

| Service | Port | Note |
|---------|-----:|------|
| Backend Flask | 8000 | `0.0.0.0` |
| Web Vite | 5173 | `0.0.0.0` |
| PostGIS | 5432 | |
| Redis | 6379 | |
| MailHog SMTP / UI | 1025 / 8025 | mock e‑mail |
| MinIO API / console | 9000 / 9001 | mock S3 |
| Proxy Nginx (compose complet) | 80 | `/` web, `/api` backend |
| Grafana (profil observability) | 3000 | |

## Changelog infra

| Date | Lot | Commit | Note |
|------|-----|--------|------|
| — | 0 | `chore(repo): bootstrap` | dossiers `infra/`, `scripts/`, `.github/` réservés |
