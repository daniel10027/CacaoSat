#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
IP="$(detect_lan_ip)"
echo "IP LAN     : $IP"
echo "API        : http://$IP:8000/api/v1"
echo "Web        : http://$IP:5173"
echo "MailHog    : http://$IP:8025"
echo "MinIO      : http://$IP:9001"
echo "Mobile     : flutter run --dart-define=API_BASE_URL=http://$IP:8000"
for name in db redis mailhog minio; do
  s="$(docker inspect -f '{{.State.Status}}' "cacaosat-dev-${name}-1" 2>/dev/null || echo 'absent')"
  printf "  %-8s %s\n" "$name" "$s"
done
command -v curl >/dev/null && curl -fsS "http://localhost:8000/api/v1/health/ready" 2>/dev/null \
  | sed 's/^/  backend  /' || echo "  backend  injoignable"
command -v qrencode >/dev/null 2>&1 && qrencode -t ANSIUTF8 "http://$IP:5173"
