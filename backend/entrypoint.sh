#!/usr/bin/env sh
set -e

: "${DATABASE_URL:?DATABASE_URL manquant}"

echo "[entrypoint] Attente de la base de données..."
python - <<'PY'
import os, sys, time
import psycopg

url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
for attempt in range(60):
    try:
        with psycopg.connect(url, connect_timeout=2):
            print(f"[entrypoint] Base joignable (tentative {attempt + 1}).")
            sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"[entrypoint] ... {exc.__class__.__name__}")
        time.sleep(2)
print("[entrypoint] Base injoignable après 120s.", file=sys.stderr)
sys.exit(1)
PY

echo "[entrypoint] Application des migrations..."
flask db upgrade

if [ "${SEED_ON_START:-0}" = "1" ]; then
  echo "[entrypoint] Seed initial..."
  flask seed || echo "[entrypoint] seed ignoré (déjà présent ?)"
fi

if [ "${SEED_DEMO_ON_START:-0}" = "1" ]; then
  echo "[entrypoint] Seed démo..."
  flask seed-demo || echo "[entrypoint] seed-demo ignoré"
fi

echo "[entrypoint] Démarrage: $*"
exec "$@"
