#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
warn "Réinitialisation de la base de développement (données perdues)."
docker compose -f "$ROOT_DIR/infra/docker-compose.dev.yml" down -v
docker compose -f "$ROOT_DIR/infra/docker-compose.dev.yml" up -d db redis
for _ in $(seq 1 40); do
  docker inspect -f '{{.State.Health.Status}}' cacaosat-dev-db-1 2>/dev/null | grep -q healthy && break
  sleep 1
done
cd "$ROOT_DIR/backend"
export FLASK_APP=wsgi.py FLASK_CONFIG=development
export DATABASE_URL="postgresql+psycopg://cacaosat:cacaosat@localhost:5432/cacaosat"
.venv/bin/flask db upgrade
.venv/bin/flask seed
.venv/bin/flask seed-demo
log "Base réinitialisée + seed démo."
