#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
log "Arrêt des services d'appui…"
docker compose -f "$ROOT_DIR/infra/docker-compose.dev.yml" down "$@"
pkill -f "flask run --host 0.0.0.0 --port 8000" 2>/dev/null || true
pkill -f "vite.*--port 5173" 2>/dev/null || true
log "Terminé."
