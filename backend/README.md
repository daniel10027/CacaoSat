# Backend — CacaoSat

API Flask + PostGIS + moteur satellite/scoring EUDR + rapports.
Contrat d'API complet et liste des tâches : [../docs/BACKEND.md](../docs/BACKEND.md).

## Démarrage local

```bash
# 1. Services d'appui (PostGIS, Redis, MailHog, MinIO)
docker compose -f ../infra/docker-compose.dev.yml up -d

# 2. Environnement Python
make install                 # crée .venv (python3.12) + dépendances de dev
cp .env.example .env

# 3. Base de données
make migrate                 # applique les migrations Alembic
make seed                    # comptes + coopératives  (mot de passe : cacaosat)
make seed-demo               # + zone pilote géolocalisée

# 4. Lancer l'API
make run                     # http://localhost:8000/api/v1/health
```

## Comptes de démonstration

| Email | Rôle | Mot de passe |
|-------|------|--------------|
| `admin@cacaosat.ci` | admin | `cacaosat` |
| `regulateur@conseilcafecacao.ci` | regulator | `cacaosat` |
| `manager1@cacaosat.ci` | manager | `cacaosat` |
| `agent1a@cacaosat.ci` | agent | `cacaosat` |

## Tests

```bash
make test        # pytest + couverture (seuil 80 %)
make lint        # ruff
```

Les tests créent automatiquement la base `cacaosat_test` (+ extension PostGIS)
à partir de `TEST_DATABASE_URL`. Un PostgreSQL/PostGIS doit être joignable.

## Structure

```
app/
  __init__.py       application factory
  config.py         Dev / Test / Prod
  extensions.py     db, migrate, jwt, cors, limiter
  errors.py         enveloppe JSON uniforme
  security.py       argon2 + décorateurs de rôle
  geo.py            validation GeoJSON, surface (ha), centroïde
  models/           SQLAlchemy (PostGIS)
  schemas/          Marshmallow
  api/              blueprints /api/v1
  services/         logique métier
  mocks/            services externes mockés (Lot 2-3)
migrations/          Alembic (Flask-Migrate)
seeds/              flask seed / seed-demo
tests/              pytest
```
