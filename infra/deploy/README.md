# Déploiement CacaoSat

## Cible par défaut : un hôte unique (coût nul si auto-hébergé)

Sur le serveur :

```bash
git clone https://github.com/daniel10027/CacaoSat.git /opt/cacaosat
cd /opt/cacaosat
cp infra/deploy/.env.prod.example .env          # remplir les secrets
docker compose --profile prod up -d
docker compose exec backend flask db upgrade
```

Le workflow `.github/workflows/deploy.yml` automatise ce flux en SSH sur `push` vers `prod`
(ou via *Run workflow*), à condition de définir les **secrets GitHub** :

| Secret | Rôle |
|--------|------|
| `SSH_HOST`, `SSH_USER`, `SSH_KEY` | accès au serveur |
| `DEPLOY_PATH` | chemin du dépôt sur le serveur (défaut `/opt/cacaosat`) |
| `REGISTRY_TOKEN` | PAT `read:packages` pour tirer les images GHCR |
| `SECRET_KEY`, `JWT_SECRET_KEY` | secrets applicatifs (dans `.env`) |

TLS : placer un `caddy` ou un `nginx` + certbot devant le service `proxy` (port 80).

## Alternatives free-tier (services externes toujours mockés)

| Composant | Option gratuite | Fichier fourni |
|-----------|-----------------|----------------|
| API Flask | Render / Railway / Fly.io | `render.yaml` |
| Web | Netlify / Vercel / GitHub Pages | `netlify.toml` |
| PostGIS | Neon / Supabase (extension `postgis`) | — |

Ces fichiers sont fournis pour référence ; la démo du hackathon tourne entièrement via
`docker compose --profile prod`.
