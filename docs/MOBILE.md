# Mobile — Application Flutter de collecte terrain (hors‑ligne)

**Rôle :** permettre à un **agent de coopérative**, sur le terrain et **sans réseau**, de recenser un producteur, de **relever le contour GPS d'une parcelle** (marche autour ou saisie de sommets), de consulter un mini‑tableau de bord, puis de **synchroniser en différé** dès qu'une connexion est disponible.

**Stack (100 % libre) :** Flutter 3 (stable) · Dart 3 · **Riverpod** (état) · **Drift** (SQLite typé, hors‑ligne) · **flutter_map** + tuiles OSM (sans clé) · **geolocator** (GPS) + `latlong2` · **dio** (HTTP) · `connectivity_plus` · `workmanager` (sync en arrière‑plan) · `flutter_secure_storage` (token) · `path_provider` · `intl` (FR) · `mocktail` + `drift/native` (tests).

**Cible :** Android (APK/AAB) prioritaire, iOS compatible. `minSdk` 23. Thème Côte d'Ivoire cohérent avec le web.

---

## Statut du lot : `[ ]` Lot 7 · `[ ]` Lot 8

---

## Lot 7 — Socle Flutter

### 7.1 Bootstrap
- [ ] `flutter create` (org `ci.cacaosat`), nettoyage du compteur par défaut, `pubspec.yaml` avec dépendances ci‑dessus (versions épinglées)
- [ ] `mobile/lib/main.dart` — `ProviderScope`, `MaterialApp.router`, init DB + secure storage
- [ ] `lib/core/env.dart` — lecture `String.fromEnvironment('API_BASE_URL')` (injecté par `--dart-define`), défaut `http://10.0.2.2:8000` (émulateur Android)
- [ ] `lib/core/theme.dart` — `ColorScheme` drapeau CI (orange `#FF7A00`, vert `#00A651`, nuit `#0B1F17`, sable `#F4EAD5`), typo Poppins/Inter (google_fonts), composants (boutons, cartes, champs) ; mode clair/sombre
- [ ] `lib/core/router.dart` — `go_router` : `/login`, `/home`, `/producers`, `/producers/new`, `/parcels`, `/parcels/capture`, `/parcels/:id`, `/sync`, `/settings`
- [ ] `assets/` — logo cacao en orbite (SVG via `flutter_svg`), icône d'app (`flutter_launcher_icons`), splash (`flutter_native_splash`)
- [ ] `lib/core/result.dart` — type `Result<T>` (ok/err) ; `lib/core/failure.dart`

### 7.2 Base locale (Drift)
- [ ] `lib/data/local/database.dart` — tables :
  - `Producers(id, serverId?, coopId, fullName, nationalId, gender, village, phone, registeredAt, dirty, deleted, updatedAt)`
  - `Parcels(id, serverId?, producerLocalId, coopId, code, geojson, areaHa, plantingYear, crop, gpsAccuracyM, collectionMethod, collectedAt, dirty, syncState, updatedAt)`
  - `ReferenceData(key, json, fetchedAt)` — bootstrap (coopérative, aires protégées, barème)
  - `SyncQueue(id, entity, op, localId, payload, createdAt, attempts, lastError)`
  - `OutboxLog(id, batchId, sentAt, accepted, rejected, response)`
- [ ] Migrations Drift + `daos/` (ProducerDao, ParcelDao, SyncDao)
- [ ] `lib/data/repositories/` — `ProducerRepository`, `ParcelRepository`, `ReferenceRepository` (source de vérité = SQLite ; réseau optionnel)

### 7.3 Réseau & auth
- [ ] `lib/data/remote/api_client.dart` — `dio` : baseUrl env, interceptor Bearer, refresh sur 401, timeouts courts, retry réseau
- [ ] `lib/data/remote/auth_api.dart` — login/refresh/me ; `lib/features/auth/auth_controller.dart` (Riverpod) ; token en `flutter_secure_storage`
- [ ] `lib/features/auth/login_screen.dart` — formulaire, gestion hors‑ligne (si déjà loggé + token valide → home)
- [ ] `lib/core/connectivity.dart` — provider d'état réseau (bannière « hors‑ligne » globale)

### 7.4 Coquille applicative
- [ ] `lib/features/home/home_screen.dart` — mini‑dashboard : nb producteurs, nb parcelles, nb en attente de sync, dernier sync ; boutons « Nouveau producteur », « Nouvelle parcelle », « Synchroniser »
- [ ] `lib/features/settings/settings_screen.dart` — URL API (affichée, modifiable en dev), langue, purge locale, déconnexion
- [ ] Splash + gestion permissions (localisation) au 1er lancement (`permission_handler`)
- [ ] Tests : DB en mémoire monte, repositories CRUD, auth controller (login mock), router redirige si non authentifié

**Definition of Done Lot 7 :** l'app se lance sur émulateur + appareil physique, login réel contre l'API du réseau local, home affiche des compteurs (0), navigation complète, `flutter test` vert, `flutter analyze` sans warning.

---

## Lot 8 — Collecte terrain hors‑ligne + synchronisation

### 8.1 Bootstrap des données de référence
- [ ] Au login (si en ligne) : `GET /sync/bootstrap` → stocke coopérative, producteurs existants, aires protégées (GeoJSON), barème de scoring dans `ReferenceData` + tables locales
- [ ] Écran « Données de référence » : date du dernier bootstrap, bouton « Rafraîchir », taille locale
- [ ] Pré‑téléchargement des **tuiles carte** de la zone de la coopérative (cache `flutter_map` sur disque) pour usage hors‑ligne

### 8.2 Fiche producteur
- [ ] `lib/features/producers/producer_form.dart` — nom, `national_id`, genre, village (autocomplete depuis référentiel), téléphone ; validation ; enregistrement **local** (`dirty=true`)
- [ ] `producers_list.dart` — recherche, filtre (synchronisé / en attente), pull‑to‑refresh
- [ ] Lien producteur ↔ parcelles

### 8.3 Capture de parcelle (cœur métier)
- [ ] `lib/features/parcels/capture_screen.dart` — carte `flutter_map` centrée sur position GPS :
  - **Mode « marche »** : enregistre un point toutes les N secondes / M mètres pendant que l'agent contourne la parcelle ; tracé en direct ; bouton pause/reprise/terminer
  - **Mode « sommets »** : l'agent se place à chaque coin et appuie « Ajouter un sommet »
  - **Mode « manuel »** : tap sur la carte pour poser/déplacer des sommets
  - affichage précision GPS (cercle), altitude, nb de points, **surface calculée en direct** (Shapely‑like via `latlong2` + formule de l'aire géodésique)
  - fermeture automatique du polygone, validation (≥ 3 sommets, non auto‑intersectant, surface plausible 0,1–50 ha, dans l'emprise CI)
  - alerte visuelle si le polygone **recoupe une aire protégée** du référentiel local
- [ ] `lib/domain/geo.dart` — aire géodésique (ha), test d'auto‑intersection, point‑dans‑polygone, intersection polygone/polygone (référentiel aires protégées)
- [ ] Formulaire post‑capture : producteur (sélection/creation rapide), année de plantation, culture, méthode, note ; `code` parcelle généré `<COOP>-<seq>` ; enregistrement local `syncState=pending`
- [ ] `parcels_list.dart` — liste avec badge état (local / envoyé / analysé), surface, producteur ; `parcel_detail.dart` — carte + infos + (si analysé après sync) score & statut EUDR récupérés
- [ ] Reprise d'une capture interrompue (brouillon persistant)

### 8.4 Synchronisation différée
- [ ] `lib/features/sync/sync_service.dart` :
  - construit un batch depuis `SyncQueue` (producteurs puis parcelles, ordre des dépendances)
  - `POST /sync/batch` avec `device_id` (persistant), `client_id` = UUID local ; applique l'`id_map` renvoyé (met à jour `serverId`, `syncState=synced`)
  - **idempotent** : un batch renvoyé en échec réseau peut être rejoué sans doublon
  - gère les rejets (affiche la raison par item, garde en file avec `lastError`)
  - `GET /sync/status/{batch_id}` → met à jour l'état d'analyse des parcelles
- [ ] `sync_screen.dart` — liste des éléments en attente, bouton « Tout synchroniser », journal des batchs (Outbox), résolution manuelle des rejets
- [ ] `workmanager` — tâche périodique : si réseau + éléments en attente → sync auto ; notification locale de résultat
- [ ] Bannière globale « X éléments à synchroniser » + action rapide

### 8.5 Qualité & packaging
- [ ] Tests unitaires : `geo.dart` (aire, auto‑intersection, intersection aire protégée), `sync_service` (batch, id_map, rejeu idempotent — API mockée), DAOs
- [ ] Test widget : `capture_screen` (mode sommets), `producer_form` (validation)
- [ ] Test d'intégration (`integration_test/`) : login → créer producteur → capturer parcelle → synchroniser (contre backend local ou mock dio)
- [ ] `flutter_launcher_icons` + `flutter_native_splash` appliqués (logo cacao en orbite)
- [ ] Build : `flutter build apk --release --dart-define=API_BASE_URL=...` documenté ; artefact APK produit en CI (voir INFRA.md)
- [ ] `mobile/README.md` — run, dart‑define, build, tests

**Definition of Done Lot 8 :** en mode avion, un agent crée un producteur + une parcelle (polygone GPS, surface calculée, alerte aire protégée) ; au retour du réseau, « Tout synchroniser » pousse le batch, les `serverId` sont renseignés, et après analyse le score EUDR remonte dans le détail ; tests + `integration_test` verts ; **push `develop` + merge `preprod` (jalon M3)**.

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
