# Mobile — Application Flutter de collecte terrain (hors‑ligne)

**Rôle :** permettre à un **agent de coopérative**, sur le terrain et **sans réseau**, de recenser un producteur, de **relever le contour GPS d'une parcelle** (marche autour ou saisie de sommets), de consulter un mini‑tableau de bord, puis de **synchroniser en différé** dès qu'une connexion est disponible.

**Stack (100 % libre) :** Flutter 3 (stable) · Dart 3 · **Riverpod** (état) · **Drift** (SQLite typé, hors‑ligne) · **flutter_map** + tuiles OSM (sans clé) · **geolocator** (GPS) + `latlong2` · **dio** (HTTP) · `connectivity_plus` · `workmanager` (sync en arrière‑plan) · `flutter_secure_storage` (token) · `path_provider` · `intl` (FR) · `mocktail` + `drift/native` (tests).

**Cible :** Android (APK/AAB) prioritaire, iOS compatible. `minSdk` 23. Thème Côte d'Ivoire cohérent avec le web.

---

## Statut du lot : `[x]` Lot 7 (terminé) · `[x]` Lot 8 (terminé) · `[x]` Lot 11 (finitions terminées)

---

## Lot 7 — Socle Flutter

### 7.1 Bootstrap
- [x] `flutter create` (org `ci.cacaosat`), nettoyage du compteur par défaut, `pubspec.yaml` avec dépendances ci‑dessus (versions épinglées)
- [x] `mobile/lib/main.dart` — `ProviderScope`, `MaterialApp.router`, init DB + secure storage
- [x] `lib/core/env.dart` — lecture `String.fromEnvironment('API_BASE_URL')` (injecté par `--dart-define`), défaut `http://10.0.2.2:8000` (émulateur Android)
- [x] `lib/core/theme.dart` — `ColorScheme` drapeau CI (orange `#FF7A00`, vert `#00A651`, nuit `#0B1F17`, sable `#F4EAD5`), typo Poppins/Inter (google_fonts), composants (boutons, cartes, champs) ; mode clair/sombre
- [x] `lib/core/router.dart` — `go_router` : `/login`, `/home`, `/producers`, `/producers/new`, `/parcels`, `/parcels/capture`, `/parcels/:id`, `/sync`, `/settings`
- [x] `assets/` — icône d'app (`flutter_launcher_icons`) + splash (`flutter_native_splash`) — **fait au Lot 11** (`assets/icon.png` = pod cacao en orbite, fond adaptatif `#08130E` ; `android/` + `ios/` régénérés)
- [x] `lib/core/result.dart` — `Result<T>` (`Ok`/`Err`) + `Failure`

### 7.2 Base locale (Drift)
- [x] `lib/data/local/database.dart` — tables :
  - `Producers(id, serverId?, coopId, fullName, nationalId, gender, village, phone, registeredAt, dirty, deleted, updatedAt)`
  - `Parcels(id, serverId?, producerLocalId, coopId, code, geojson, areaHa, plantingYear, crop, gpsAccuracyM, collectionMethod, collectedAt, dirty, syncState, updatedAt)`
  - `ReferenceData(key, json, fetchedAt)` — bootstrap (coopérative, aires protégées, barème)
  - `SyncQueue(id, entity, op, localId, payload, createdAt, attempts, lastError)`
  - `OutboxLog(id, batchId, sentAt, accepted, rejected, response)`
- [x] Migrations Drift + `daos/` (ProducerDao, ParcelDao, SyncDao)
- [x] `lib/data/repositories/` — `ProducerRepository`, `ParcelRepository`, `ReferenceRepository` (source de vérité = SQLite ; réseau optionnel)

### 7.3 Réseau & auth
- [x] `lib/data/remote/api_client.dart` — `dio` : baseUrl env, interceptor Bearer, refresh sur 401, timeouts courts, retry réseau
- [x] `lib/data/repositories/auth_repository.dart` (login/me) + `SessionController` (Riverpod, `providers.dart`) ; tokens en `flutter_secure_storage`
- [x] `lib/features/auth/login_screen.dart` — formulaire, gestion hors‑ligne (si déjà loggé + token valide → home)
- [x] `connectivityProvider` (`providers.dart`) + `OfflineBanner` global (`widgets/common.dart`)

### 7.4 Coquille applicative
- [x] `lib/features/home/home_screen.dart` — mini‑dashboard : nb producteurs, nb parcelles, nb en attente de sync, dernier sync ; boutons « Nouveau producteur », « Nouvelle parcelle », « Synchroniser »
- [x] `lib/features/settings/settings_screen.dart` — URL API (affichée, modifiable en dev), langue, purge locale, déconnexion
- [x] Permission de localisation demandée à l'ouverture de la capture (`geolocator.requestPermission`) ; splash au Lot 11
- [x] Tests : DB en mémoire (Drift `NativeDatabase.memory`), `ProducerRepository`/`ParcelRepository` CRUD + file de sync, `markSynced`, `Geo` (surface, auto‑intersection, point‑dans‑polygone, GeoJSON round‑trip) — **12 tests verts**

**Definition of Done Lot 7 :** ✅ `flutter analyze` **0 issue**, `flutter test` **12 verts** (géométrie + repositories Drift). App structurée : `ProviderScope` + `MaterialApp.router`, thème drapeau CI, Drift + DAOs générés (`dart run build_runner build`), `api_client` (Bearer + refresh JWT), `SessionController`, login, accueil (compteurs live), réglages, `OfflineBanner`. Build APK : via CI (Lot 9 — `cmdline-tools` Android absents localement).

---

## Lot 8 — Collecte terrain hors‑ligne + synchronisation

### 8.1 Bootstrap des données de référence
- [x] Au login (si en ligne) : `GET /sync/bootstrap` → stocke coopérative, producteurs existants, aires protégées (GeoJSON), barème de scoring dans `ReferenceData` + tables locales
- [x] Rafraîchissement du bootstrap : pull‑to‑refresh sur l'accueil + bouton dans Réglages ; date du dernier bootstrap affichée sur l'accueil
- [x] Cache disque des tuiles carte (`lib/core/tile_cache.dart`) — **fait au Lot 11** : `CachedTileProvider` (cache borné ~40 Mo, éviction LRU) ; toute zone déjà consultée reste affichable hors‑ligne sur la capture et le détail parcelle

### 8.2 Fiche producteur
- [x] `lib/features/producers/producer_form.dart` — nom, `national_id`, genre, village (autocomplete depuis référentiel), téléphone ; validation ; enregistrement **local** (`dirty=true`)
- [x] `producers_list.dart` — recherche, filtre (synchronisé / en attente), pull‑to‑refresh
- [x] Lien producteur ↔ parcelles

### 8.3 Capture de parcelle (cœur métier)
- [x] `lib/features/parcels/capture_screen.dart` — carte `flutter_map` centrée sur position GPS :
  - **Mode « marche »** : enregistre un point toutes les N secondes / M mètres pendant que l'agent contourne la parcelle ; tracé en direct ; bouton pause/reprise/terminer
  - **Mode « sommets »** : l'agent se place à chaque coin et appuie « Ajouter un sommet »
  - **Mode « manuel »** : tap sur la carte pour poser/déplacer des sommets
  - affichage précision GPS (cercle), altitude, nb de points, **surface calculée en direct** (Shapely‑like via `latlong2` + formule de l'aire géodésique)
  - fermeture automatique du polygone, validation (≥ 3 sommets, non auto‑intersectant, surface plausible 0,1–50 ha, dans l'emprise CI)
  - alerte visuelle si le polygone **recoupe une aire protégée** du référentiel local
- [x] `lib/domain/geo.dart` — aire géodésique (ha), test d'auto‑intersection, point‑dans‑polygone, intersection polygone/polygone (référentiel aires protégées)
- [x] Formulaire post‑capture : producteur (sélection/creation rapide), année de plantation, culture, méthode, note ; `code` parcelle généré `<COOP>-<seq>` ; enregistrement local `syncState=pending`
- [x] `parcels_list.dart` — liste avec badge état (local / envoyé / analysé), surface, producteur ; `parcel_detail.dart` — carte + infos + (si analysé après sync) score & statut EUDR récupérés
- [x] Reprise d'une capture interrompue (brouillon persistant) — **fait au Lot 11** : `ReferenceRepository.saveDraft/loadDraft/clearDraft` (débounce 600 ms), dialogue « Reprendre la capture ? » à l'ouverture ; brouillon purgé à l'enregistrement

### 8.4 Synchronisation différée
- [x] `lib/features/sync/sync_service.dart` :
  - construit un batch depuis `SyncQueue` (producteurs puis parcelles, ordre des dépendances)
  - `POST /sync/batch` avec `device_id` (persistant), `client_id` = UUID local ; applique l'`id_map` renvoyé (met à jour `serverId`, `syncState=synced`)
  - **idempotent** : un batch renvoyé en échec réseau peut être rejoué sans doublon
  - gère les rejets (affiche la raison par item, garde en file avec `lastError`)
  - `GET /sync/status/{batch_id}` → met à jour l'état d'analyse des parcelles
- [x] `sync_screen.dart` — nb d'éléments en attente, « Tout synchroniser » (désactivé hors‑ligne), journal des envois (Outbox : accepté/rejeté + horodatage)
- [x] `core/background_sync.dart` — `workmanager` : tâche périodique 30 min (Android), contrainte réseau, `pushAll` si file non vide, backoff sur échec
- [x] Bannière globale « X éléments à synchroniser » + action rapide

### 8.5 Qualité & packaging
- [x] Tests unitaires : `geo.dart` (aire, auto‑intersection, intersection aire protégée), `sync_service` (batch, id_map, rejeu idempotent — API mockée), DAOs
- [x] Tests widget `test/widget/capture_screen_test.dart` (rendu sans GPS, « Terminer » désactivé < 3 sommets, bascule mode « Manuel ») + `test/widget/producer_form_test.dart` (refus nom vide, persistance locale `dirty=true` + entrée `SyncQueue`) — **fait au Lot 11**
- [x] `integration_test/offline_flow_test.dart` — accueil → fiche producteur → file de sync (« 1 élément(s) en attente ») — **fait au Lot 11** (exécution `flutter test integration_test/` sur appareil/émulateur)
- [x] `flutter_launcher_icons` + `flutter_native_splash` — **fait au Lot 11**
- [x] Build : `flutter build apk --release --dart-define=API_BASE_URL=...` documenté ; artefact APK produit en CI (voir INFRA.md)
- [x] `mobile/README.md` — run, dart‑define, build, tests

**Definition of Done Lot 8 :** ✅ hors‑ligne, création de producteurs + **capture GPS de parcelles** (3 modes marche/sommets/manuel, surface géodésique en direct, validation ≥3 sommets / non auto‑intersectant / emprise CI / 0,05–50 ha, **alerte recoupement d'aire protégée** depuis le référentiel local) ; chaque écriture entre en `SyncQueue`. `SyncRepository.pushAll` → `POST /sync/batch` idempotent (`client_batch_id`), `id_map` appliqué (`serverId`, `syncState`), scores EUDR récupérés via `/sync/status/{id}` ; `OutboxLog` ; `workmanager` (Android). `flutter analyze` 0 issue, `flutter test` 12 verts. Finitions (icônes/splash, tuiles offline, brouillon de capture, tests widget/integration) → **Lot 11**. **→ jalon M3 : merge `develop → preprod`.**

---

## Lot 11 — Finitions mobile

- [x] **Icône d'app + splash natif** — `assets/icon.png` (pod cacao en orbite, 1254×1254), `flutter_launcher_icons` (fond adaptatif `#08130E`) + `flutter_native_splash` (fond `#08130E`) ; `android/` (`mipmap-*`, `colors.xml`, `styles.xml`) et `ios/` (`Runner` assets) régénérés.
- [x] **Cache disque des tuiles** — `lib/core/tile_cache.dart` : `CachedTileProvider extends TileProvider` + `_CachedNetworkImage extends ImageProvider` (lecture disque prioritaire, écriture après téléchargement, `pruneIfNeeded()` LRU ~40 Mo). Branché sur `capture_screen` (instance propre, `dispose()` + prune à l'enregistrement) et `parcel_detail_screen` (`sharedTileProvider`).
- [x] **Reprise de capture (brouillon persistant)** — `ReferenceRepository.saveDraft(points, mode)` / `loadDraft()` / `clearDraft()` ; `capture_screen` : `_persistDraft()` débouncé 600 ms sur chaque mutation via `_editPoints()`, `_offerDraftResume()` en `initState` (dialogue « Reprendre la capture ? »), purge du brouillon à l'enregistrement.
- [x] **Robustesse hors‑GPS** — `_initLocation()` encadré de `try/catch` autour de `Geolocator.checkPermission/requestPermission` : sur une plateforme sans GPS (test / émulateur nu) la capture manuelle reste utilisable, aucune exception.
- [x] **Navigation testable** — `lib/core/nav.dart` `safePop()` : `GoRouter.maybeOf` sinon `Navigator.maybeOf`, pour que les écrans montés isolément en test ne lèvent pas « No GoRouter found in context ».
- [x] **Tests** — `test/widget/capture_screen_test.dart`, `test/widget/producer_form_test.dart`, `integration_test/offline_flow_test.dart`. `flutter analyze` 0 issue, `flutter test` **14 verts** (12 socle + 2 widget).
- [x] **CI** — `.github/workflows/mobile.yml` : `build_runner build --delete-conflicting-outputs`, `flutter test --coverage`.

**Definition of Done Lot 11 :** ✅ icône + splash aux couleurs du drapeau, tuiles carte consultables hors‑ligne, capture reprenable après interruption, `flutter analyze` 0 issue, `flutter test` 14 verts, `integration_test/` prêt pour appareil. **→ inclus au jalon M5 (retag `v1.0.0`).**

---

## Écrans (récap)

| Écran | Route | Hors‑ligne | Contenu |
|-------|-------|:----------:|---------|
| Login | `/login` | partiel | auth, reprise session |
| Accueil | `/home` | ✅ | compteurs, actions rapides, état sync |
| Producteurs | `/producers` | ✅ | liste, recherche, état |
| Nouveau producteur | `/producers/new` | ✅ | formulaire validé |
| Parcelles | `/parcels` | ✅ | liste, badges d'état |
| Capture parcelle | `/parcels/capture` | ✅ | carte GPS, 3 modes, surface live, alerte aire protégée |
| Détail parcelle | `/parcels/:id` | ✅ | polygone, infos, score après sync |
| Synchronisation | `/sync` | ✅ | file d'attente, journal, rejets |
| Réglages | `/settings` | ✅ | API, langue, purge, logout |

## Injection de configuration

```
flutter run --dart-define=API_BASE_URL=http://<IP_LAN>:8000
# émulateur Android sans dart-define : http://10.0.2.2:8000
# appareil physique : IP LAN de la machine (fournie par scripts/dev.sh)
```

## Changelog du mobile

| Date | Lot | Commit | Note |
|------|-----|--------|------|
| — | 0 | `chore(repo): bootstrap` | dossier `mobile/` réservé |
| 2026-09-10 | 7-8 | `feat(mobile): app Flutter de collecte terrain hors-ligne` | Drift (5 tables + DAOs), api_client (refresh JWT), SessionController, go_router, thème CI, écrans login/accueil/producteurs/parcelles/capture/sync/réglages, `domain/geo.dart` (surface géodésique, auto-intersection, aires protégées), repositories (bootstrap, producer, parcel, sync idempotent), `background_sync` (workmanager). `flutter analyze` 0 issue, 12 tests verts |
| 2026-09-10 | 11 | `feat(mobile): finitions — icône/splash, cache tuiles, reprise capture, tests` | `flutter_launcher_icons` + `flutter_native_splash` (drapeau CI), `core/tile_cache.dart` (cache disque LRU ~40 Mo), reprise de capture (brouillon persistant débouncé), `core/nav.dart` `safePop`, robustesse hors-GPS, 2 tests widget + `integration_test/offline_flow_test.dart`. `flutter analyze` 0 issue, **14 tests verts** |
