#!/usr/bin/env bash
# Fonctions partagées par les scripts CacaoSat.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

c_reset='\033[0m'; c_green='\033[0;32m'; c_orange='\033[0;33m'; c_red='\033[0;31m'; c_dim='\033[2m'
log()  { printf "${c_green}▸${c_reset} %s\n" "$*"; }
warn() { printf "${c_orange}!${c_reset} %s\n" "$*"; }
err()  { printf "${c_red}✗${c_reset} %s\n" "$*" >&2; }
dim()  { printf "${c_dim}%s${c_reset}\n" "$*"; }

# IP LAN de la machine (portable macOS / Linux).
detect_lan_ip() {
  if [ -n "${HOST_LAN_IP:-}" ]; then echo "$HOST_LAN_IP"; return; fi
  local ip=""
  if command -v ipconfig >/dev/null 2>&1 && [ "$(uname)" = "Darwin" ]; then
    ip="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
  fi
  if [ -z "$ip" ] && command -v ip >/dev/null 2>&1; then
    ip="$(ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src"){print $(i+1); exit}}')"
  fi
  if [ -z "$ip" ] && command -v hostname >/dev/null 2>&1; then
    ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
  fi
  echo "${ip:-127.0.0.1}"
}

require() { command -v "$1" >/dev/null 2>&1 || { err "Commande requise absente : $1"; exit 1; }; }

wait_for_http() {
  local url="$1" tries="${2:-60}"
  for _ in $(seq 1 "$tries"); do
    if curl -fsS -o /dev/null "$url" 2>/dev/null; then return 0; fi
    sleep 1
  done
  return 1
}
