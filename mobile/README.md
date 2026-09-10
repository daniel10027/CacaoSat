# Mobile — CacaoSat

Application Flutter de collecte terrain **hors-ligne** des parcelles cacaoyères (conformité EUDR).
Toutes les tâches : [../docs/MOBILE.md](../docs/MOBILE.md).

## Stack

Flutter 3 · Riverpod · **Drift** (SQLite hors-ligne) · dio (refresh JWT auto) ·
**flutter_map** (OSM, sans clé) · geolocator · latlong2 · connectivity_plus ·
workmanager (sync périodique) · go_router · flutter_secure_storage · google_fonts.

## Démarrer

```bash
flutter pub get
dart run build_runner build          # génère database.g.dart

# Émulateur Android (API sur l'hôte) :
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000

# Appareil physique (même Wi-Fi que la machine) :
flutter run --dart-define=API_BASE_URL=http://<IP_LAN>:8000
```

`scripts/dev.sh` (racine) fournit l'IP LAN et lance la commande `--dart-define` prête à copier.

## Build

```bash
flutter analyze          # 0 issue
flutter test             # 12 tests (géométrie + repositories + validation)
flutter build apk --release --dart-define=API_BASE_URL=https://api.exemple
```

## Structure

```
lib/
  core/        env, theme (drapeau CI), router (go_router), result, background_sync
  data/
    local/     database.dart (Drift : Producers, Parcels, ReferenceData, SyncQueue, OutboxLog) + DAOs
    remote/    api_client.dart (dio + Bearer + refresh)
    repositories/  auth, reference (bootstrap), producer, parcel, sync
  domain/      geo.dart (surface géodésique, auto-intersection, point-dans-polygone, aires protégées)
  features/    auth, home, producers, parcels (dont capture_screen), sync, settings
  providers.dart   graphe Riverpod + SessionController
```

## Flux hors-ligne

1. **Login en ligne** → `GET /sync/bootstrap` hydrate la base locale (coopérative, producteurs,
   parcelles, aires protégées, barème).
2. **Terrain sans réseau** : création de producteurs et **capture GPS de parcelles**
   (marche / sommets / manuel), surface calculée en direct, alerte si recoupement d'aire protégée.
   Chaque écriture entre dans `SyncQueue`.
3. **Retour du réseau** : « Tout synchroniser » → `POST /sync/batch` idempotent
   (`client_batch_id`), `id_map` appliqué, scores EUDR récupérés via `GET /sync/status/{id}`.
   Une tâche `workmanager` tente aussi la sync toutes les 30 min (Android).
