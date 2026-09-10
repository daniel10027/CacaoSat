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
| API Flask | Render / Railway | `render.yaml` |
| API Flask | Fly.io | `fly.toml` |
| Web | Netlify / Vercel / GitHub Pages | `netlify.toml` |
| PostGIS | Neon / Supabase (extension `postgis`) | — |

Ces fichiers sont fournis pour référence ; la démo du hackathon tourne entièrement via
`docker compose --profile prod`.

### Fly.io (`fly.toml`)

```bash
fly launch --no-deploy --copy-config --dockerfile backend/Dockerfile
fly postgres create --name cacaosat-db --region cdg
fly postgres attach cacaosat-db            # injecte DATABASE_URL
fly secrets set SECRET_KEY=... JWT_SECRET_KEY=...
fly deploy                                  # release_command = flask db upgrade
```

## Sauvegarde / restauration de la base

```bash
make backup-db                              # -> backups/cacaosat-<horodatage>.dump
make restore-db FILE=backups/cacaosat-20260910-120000.dump
```

`backup-db` lance `pg_dump -Fc` dans le conteneur `db` ; `restore-db` rejoue le dump
avec `pg_restore --clean --if-exists`. Surcharges : `DB_SERVICE`, `DB_USER`, `DB_NAME`,
`BACKUP_DIR`.
