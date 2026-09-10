#!/usr/bin/env bash
#
# Smoke test e2e contre une API CacaoSat.
#   ./scripts/smoke.sh [BASE_URL]     (défaut : http://localhost:8000)
#
set -uo pipefail
BASE="${1:-http://localhost:8000}/api/v1"
pass=0; fail=0
ok()  { echo "  ✓ $1"; pass=$((pass+1)); }
ko()  { echo "  ✗ $1"; fail=$((fail+1)); }

echo "Smoke test → $BASE"

curl -fsS "$BASE/health" >/dev/null && ok "health" || ko "health"
curl -fsS "$BASE/openapi.json" | grep -q CacaoSat && ok "openapi.json" || ko "openapi.json"
curl -fsS "$BASE/dashboard/regions" | grep -q regions && ok "regions (public)" || ko "regions"

TOKEN="$(curl -fsS "$BASE/auth/login" -H 'Content-Type: application/json' \
  -d '{"email":"manager1@cacaosat.ci","password":"cacaosat"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin).get("access_token",""))' 2>/dev/null)"
H=(-H "Authorization: Bearer $TOKEN")
[ -n "$TOKEN" ] && ok "login → JWT" || { ko "login → JWT"; echo "  $pass réussis · $fail échoués"; exit 1; }

PID="$(curl -fsS "$BASE/parcels?per_page=1" "${H[@]}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["items"][0]["id"])' 2>/dev/null)"
[ -n "$PID" ] && ok "liste parcelles" || ko "liste parcelles"

curl -fsS -X POST "$BASE/parcels/$PID/analyze" "${H[@]}" | grep -q compliance_score \
  && ok "analyse parcelle" || ko "analyse parcelle"
curl -fsS "$BASE/dashboard/summary" "${H[@]}" | grep -q parcels_total \
  && ok "dashboard/summary" || ko "dashboard/summary"
curl -fsS "$BASE/dashboard/map" "${H[@]}" | grep -q FeatureCollection \
  && ok "dashboard/map" || ko "dashboard/map"

RID="$(curl -fsS -X POST "$BASE/reports" "${H[@]}" -H 'Content-Type: application/json' \
  -d '{"period_start":"2026-01-01","period_end":"2026-12-31"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin).get("id",""))' 2>/dev/null)"
[ -n "$RID" ] && ok "génération rapport" || ko "génération rapport"
curl -fsS "$BASE/reports/$RID/download?format=pdf" "${H[@]}" | head -c4 | grep -q PDF \
  && ok "téléchargement PDF" || ko "téléchargement PDF"

echo
echo "  $pass réussis · $fail échoués"
exit $(( fail > 0 ? 1 : 0 ))
