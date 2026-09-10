#!/usr/bin/env bash
#
# CacaoSat — lance backend + web + mobile sur le réseau local.
# Un téléphone du même Wi-Fi accède directement à l'API, sans tunnel.
#
#   ./scripts/dev.sh [--no-mobile] [--no-web] [--keep-infra] [--seed-demo]
#
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

NO_MOBILE=0; NO_WEB=0; KEEP_INFRA=0; SEED_DEMO=0
for arg in "$@"; do case "$arg" in
  --no-mobile) NO_MOBILE=1 ;;
  --no-web) NO_WEB=1 ;;
  --keep-infra) KEEP_INFRA=1 ;;
  --seed-demo) SEED_DEMO=1 ;;
  -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
  *) warn "option inconnue : $arg" ;;
esac; done

require docker
require curl

LAN_IP="$(detect_lan_ip)"
API_URL="http://${LAN_IP}:8000"
WEB_URL="http://${LAN_IP}:5173"
export HOST_LAN_IP="$LAN_IP"

mkdir -p "$ROOT_DIR/.dev/logs"
PIDS=()

cleanup() {
  echo
  log "Arrêt…"
  for pid in "${PIDS[@]:-}"; do kill "$pid" 2>/dev/null || true; done
  if [ "$KEEP_INFRA" -eq 0 ]; then
    docker compose -f "$ROOT_DIR/infra/docker-compose.dev.yml" stop >/dev/null 2>&1 || true
  fi
}
trap cleanup INT TERM EXIT

# --- 1. Services d'appui -------------------------------------------------
log "Services d'appui (PostGIS · Redis · MailHog · MinIO)…"
docker compose -f "$ROOT_DIR/infra/docker-compose.dev.yml" up -d
for _ in $(seq 1 40); do
  if docker inspect --format '{{.State.Health.Status}}' cacaosat-dev-db-1 2>/dev/null | grep -q healthy; then break; fi
  sleep 1
done

# --- 2. Backend --------------------------------------------------------
log "API Flask sur 0.0.0.0:8000  (CORS → $WEB_URL)…"
(
  cd "$ROOT_DIR/backend"
  if [ ! -d .venv ]; then
    "$(command -v python3.12 || command -v python3)" -m venv .venv
    .venv/bin/pip -q install --upgrade pip
    .venv/bin/pip -q install -r requirements.txt
  fi
  export FLASK_APP=wsgi.py FLASK_CONFIG=development
  export DATABASE_URL="postgresql+psycopg://cacaosat:cacaosat@localhost:5432/cacaosat"
  export REDIS_URL="redis://localhost:6379/0"
  export CORS_ORIGINS="http://localhost:5173,${WEB_URL}"
  .venv/bin/flask db upgrade
  if [ "$SEED_DEMO" -eq 1 ]; then .venv/bin/flask seed && .venv/bin/flask seed-demo; else .venv/bin/flask seed || true; fi
  exec .venv/bin/flask run --host 0.0.0.0 --port 8000
) >"$ROOT_DIR/.dev/logs/backend.log" 2>&1 &
PIDS+=($!)

wait_for_http "http://localhost:8000/api/v1/health" 60 \
  && log "Backend prêt → ${API_URL}/api/v1" \
  || warn "Backend lent à démarrer — voir .dev/logs/backend.log"

# --- 3. Web ----------------------------------------------------------
if [ "$NO_WEB" -eq 0 ]; then
  log "Web Vite sur 0.0.0.0:5173  (VITE_API_URL=${API_URL}/api/v1)…"
  (
    cd "$ROOT_DIR/web"
    [ -d node_modules ] || npm ci
    exec env VITE_API_URL="${API_URL}/api/v1" npm run dev -- --host 0.0.0.0 --port 5173
  ) >"$ROOT_DIR/.dev/logs/web.log" 2>&1 &
  PIDS+=($!)
fi

# --- 4. Mobile ------------------------------------------------------
DART_DEFINE="--dart-define=API_BASE_URL=${API_URL}"
if [ "$NO_MOBILE" -eq 0 ] && command -v flutter >/dev/null 2>&1; then
  DEVICE="$(flutter devices --machine 2>/dev/null | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 || true)"
  if [ -n "$DEVICE" ]; then
    log "App Flutter sur l'appareil « $DEVICE »…"
    ( cd "$ROOT_DIR/mobile" && flutter pub get >/dev/null && exec flutter run -d "$DEVICE" $DART_DEFINE ) \
      >"$ROOT_DIR/.dev/logs/mobile.log" 2>&1 &
    PIDS+=($!)
  else
    warn "Aucun appareil/emulateur détecté."
  fi
fi

# --- Récapitulatif ------------------------------------------------
echo
printf "${c_orange}╭──────────────────────────────────────────────────────────────╮${c_reset}\n"
printf "${c_orange}│${c_reset}  CacaoSat — développement · réseau local                      ${c_orange}│${c_reset}\n"
printf "${c_orange}├──────────────────────────────────────────────────────────────┤${c_reset}\n"
printf "${c_orange}│${c_reset}  IP LAN     : %-46s ${c_orange}│${c_reset}\n" "$LAN_IP"
printf "${c_orange}│${c_reset}  API        : %-46s ${c_orange}│${c_reset}\n" "${API_URL}/api/v1"
printf "${c_orange}│${c_reset}  Web        : %-46s ${c_orange}│${c_reset}\n" "$WEB_URL"
printf "${c_orange}│${c_reset}  MailHog    : %-46s ${c_orange}│${c_reset}\n" "http://${LAN_IP}:8025"
printf "${c_orange}│${c_reset}  MinIO      : %-46s ${c_orange}│${c_reset}\n" "http://${LAN_IP}:9001"
printf "${c_orange}│${c_reset}  Mobile     : flutter run %-34s ${c_orange}│${c_reset}\n" "$DART_DEFINE"
printf "${c_orange}╰──────────────────────────────────────────────────────────────╯${c_reset}\n"
command -v qrencode >/dev/null 2>&1 && { echo; dim "Scanne pour ouvrir le web sur ton téléphone :"; qrencode -t ANSIUTF8 "$WEB_URL"; }
echo
dim "Logs : .dev/logs/{backend,web,mobile}.log   ·   Ctrl+C pour tout arrêter"
echo

wait
