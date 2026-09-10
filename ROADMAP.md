# CacaoSat — Feuille de route & suivi d'exécution

Ce document est le **pilote central** du projet. Il découpe la livraison en **lots** ordonnés.
Chaque lot se termine par un **commit + push sur `develop`**. Les jalons déclenchent un merge `develop → preprod → prod`.

## Légende de statut

| Symbole | Sens |
|---------|------|
| `[ ]` | à faire |
| `[~]` | en cours |
| `[x]` | **terminé** — code réel, testé, exécutable, committé |
| 🔒 | bloqué (dépendance / décision externe) |

**Règle d'or :** une case n'est cochée que si le livrable tourne réellement (`make test` vert, service qui démarre, écran qui s'affiche). Pas de TODO, pas de pseudo‑code.

---

## Vue d'ensemble des lots

| Lot | Titre | Doc de détail | Statut | Push |
|-----|-------|---------------|--------|------|
| 0 | Fondations du dépôt | ce fichier | `[x]` | `chore: bootstrap monorepo + tracking docs` |
| 1 | Backend — socle (app factory, DB, auth, Docker) | [BACKEND.md](docs/BACKEND.md) | `[ ]` | — |
| 2 | Backend — moteur satellite (mock) + scoring EUDR + API métier | [BACKEND.md](docs/BACKEND.md) | `[ ]` | — |
| 3 | Backend — rapports PDF/GeoJSON + alertes + sync mobile | [BACKEND.md](docs/BACKEND.md) | `[ ]` | — |
| 4 | Web — socle + design system Côte d'Ivoire + auth | [FRONTEND.md](docs/FRONTEND.md) | `[ ]` | — |
| 5 | Web — landing page immersive (cacao en orbite) | [FRONTEND.md](docs/FRONTEND.md) | `[ ]` | — |
| 6 | Web — dashboards conformité (carte, KPIs, rapports, alertes) | [FRONTEND.md](docs/FRONTEND.md) | `[ ]` | — |
| 7 | Mobile — socle Flutter (thème, DB locale, auth, nav) | [MOBILE.md](docs/MOBILE.md) | `[ ]` | — |
| 8 | Mobile — collecte terrain hors‑ligne + sync différée | [MOBILE.md](docs/MOBILE.md) | `[ ]` | — |
| 9 | Infra — Docker Compose, CI/CD, `dev.sh`, observabilité | [INFRA.md](docs/INFRA.md) | `[ ]` | — |
| 10 | Pitch — deck 5 min PPTX + PDF | ce fichier | `[ ]` | — |
| 11 | Durcissement, seed démo, release preprod/prod | ce fichier | `[ ]` | — |

---

## Lot 0 — Fondations du dépôt  `[x]`

- [x] Arborescence monorepo (`backend/ web/ mobile/ infra/ scripts/ pitch/ docs/`)
- [x] `.gitignore` (Python, Node, Flutter, Docker, IDE)
- [x] `.editorconfig`
- [x] `LICENSE` (MIT)
- [x] `README.md` — présentation, architecture, quickstart, workflow Git
- [x] `ROADMAP.md` — ce fichier
- [x] `docs/BACKEND.md`, `docs/FRONTEND.md`, `docs/MOBILE.md`, `docs/INFRA.md` — listes de tâches détaillées
- [x] `git init`, commit initial sur `main`, création des branches `develop`, `preprod`, `prod`
- [x] `git remote add origin https://github.com/daniel10027/CacaoSat.git`
- [ ] 🔒 `git push` des 4 branches — **nécessite `gh auth login` par l'utilisateur** (voir « Accès GitHub » plus bas)

**Definition of Done :** `git log` montre le commit de bootstrap, `git branch` liste `develop/preprod/prod`, les 6 docs existent.

---

## Lot 10 — Pitch (5 minutes)  `[ ]`

- [ ] `pitch/build_deck.py` — génération du `.pptx` via **python-pptx** (aucun outil payant)
- [ ] Charte : drapeau CI (orange `#FF8200`, blanc, vert `#009A44`), logo cacao en orbite, typo libre (Poppins/Inter)
- [ ] Trame 5 min / ~12 slides :
  1. Titre — *CacaoSat, le spatial pour bâtir*
  2. Le choc réglementaire EUDR (chiffres : N°1 mondial, 82 %, 30 %, 2M+ foyers)
  3. Qui porte le poids : les petites coopératives
  4. Insight — *la donnée existe déjà, gratuite ; ce qui manque, c'est le pipeline*
  5. La solution CacaoSat — le pipeline en 6 étapes
  6. Démo 1 — app mobile : relevé GPS hors‑ligne d'une parcelle
  7. Démo 2 — dashboard : carte des parcelles scorées, zone à risque
  8. Démo 3 — certificat de conformité EUDR généré en 1 clic (PDF)
  9. Sous le capot — Sentinel‑2 + Hansen/GFW + Digital Earth Africa, 100 % open data
  10. Impact — économique / social / environnemental / institutionnel
  11. Au‑delà du hackathon — pilote coopérative + Conseil du Café‑Cacao
  12. L'équipe + appel à soutien
- [ ] Export **PDF** (`libreoffice --headless --convert-to pdf`) → `pitch/CacaoSat-Pitch.pdf`
- [ ] `pitch/SCRIPT.md` — texte minuté du pitch (chrono par slide)
- [ ] `make pitch` régénère `.pptx` + `.pdf`

**Definition of Done :** `pitch/CacaoSat-Pitch.pptx` et `.pdf` présents, régénérables, cohérents avec la démo.

---

## Lot 11 — Durcissement & release  `[ ]`

- [ ] Seed de démo réaliste : 1 zone pilote (région du Cavally/Guémon), 2 coopératives, ~40 producteurs, ~60 parcelles dont plusieurs en zone à risque et 1 cas de déforestation post‑2020 net
- [ ] Smoke test e2e : `scripts/smoke.sh` (login → créer parcelle → analyser → générer rapport → télécharger PDF)
- [ ] `docker compose up` à froid : stack complète verte en < 3 min
- [ ] Revue accessibilité web (contraste AA, navigation clavier, `prefers-reduced-motion`)
- [ ] Relecture des 6 docs : toutes les cases pertinentes cochées
- [ ] Merge `develop → preprod` (CI verte) puis `preprod → prod` ; tags `v1.0.0-preprod`, `v1.0.0`
- [ ] README : badges CI, captures d'écran, lien démo

**Definition of Done :** les 3 branches à jour, tag `v1.0.0` sur `prod`, `scripts/smoke.sh` vert.

---

## Jalons Git

| Jalon | Contenu | Action |
|-------|---------|--------|
| **M1** | Lots 1–3 (backend complet) | push `develop` → merge `preprod` |
| **M2** | Lots 4–6 (web complet) | push `develop` → merge `preprod` |
| **M3** | Lots 7–8 (mobile complet) | push `develop` → merge `preprod` |
| **M4** | Lot 9 (infra/CI) | push `develop` → merge `preprod` |
| **M5** | Lots 10–11 (pitch + release) | merge `preprod` → `prod`, tag `v1.0.0` |

## Convention de commits

`type(scope): sujet` — types : `feat`, `fix`, `chore`, `docs`, `test`, `ci`, `refactor`, `perf`.
Scopes : `backend`, `web`, `mobile`, `infra`, `pitch`, `repo`.
Chaque commit de fin de lot met aussi à jour les cases `[x]` des docs concernés **dans le même commit**.

## Accès GitHub (action requise de l'utilisateur)

Le push nécessite une authentification. Dans ce terminal, lancer :

```
! gh auth login
```

(ou fournir un *Personal Access Token* avec scope `repo`). Une fois authentifié, l'agent poussera `main`, `develop`, `preprod`, `prod` sur `https://github.com/daniel10027/CacaoSat.git` et poursuivra les lots.
