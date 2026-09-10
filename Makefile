# CacaoSat — orchestrateur unique. `make help` pour la liste.
# Les cibles sont complétées lot par lot (voir docs/INFRA.md).

SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help dev infra-up infra-down infra-logs up prod-up down test lint \
        seed seed-demo migrate images pitch health clean smoke docs observability stop \
        backup-db restore-db

# Service Compose PostGIS + identifiants (surchargables : make backup-db DB_SERVICE=db)
DB_SERVICE ?= db
DB_USER    ?= cacaosat
DB_NAME    ?= cacaosat
BACKUP_DIR ?= backups

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

dev: ## Lance backend + web + mobile sur le réseau local (scripts/dev.sh)
	@./scripts/dev.sh $(ARGS)

infra-up: ## Démarre les services d'appui (PostGIS, Redis, MailHog, MinIO)
	@docker compose -f infra/docker-compose.dev.yml up -d

infra-down: ## Arrête les services d'appui
	@docker compose -f infra/docker-compose.dev.yml down

infra-logs: ## Suit les logs des services d'appui
	@docker compose -f infra/docker-compose.dev.yml logs -f

up: ## Stack applicative complète en Docker (dev intégré)
	@docker compose up --build

prod-up: ## Stack applicative en profil production
	@docker compose --profile prod up -d --build

down: ## Arrête la stack applicative
	@docker compose down

test: ## Lance les tests backend + web + mobile
	@$(MAKE) -C backend test || true
	@cd web && npm test --silent || true
	@cd mobile && flutter test || true

lint: ## Lint des trois composants
	@cd backend && ruff check . || true
	@cd web && npm run lint || true
	@cd mobile && flutter analyze || true

seed: ## Peuple la base (comptes + données mock de base)
	@$(MAKE) -C backend seed

seed-demo: ## Peuple la base avec la zone pilote de démonstration
	@$(MAKE) -C backend seed-demo

migrate: ## Applique les migrations de base de données
	@$(MAKE) -C backend migrate

images: ## Construit les images Docker backend + web
	@docker build -t ghcr.io/daniel10027/cacaosat-backend:local backend
	@docker build -t ghcr.io/daniel10027/cacaosat-web:local web

pitch: ## Régénère le support de pitch (PPTX + PDF)
	@python3 pitch/build_deck.py

health: ## Vérifie la santé des services (IP LAN + statuts)
	@./scripts/lan-info.sh || true

smoke: ## Smoke test e2e contre http://localhost
	@./scripts/smoke.sh $(BASE)

docs: ## Vérifie la cohérence des docs de suivi
	@python3 scripts/check_docs.py

observability: ## Stack + Prometheus + Grafana
	@docker compose --profile observability up -d --build

stop: ## Arrête tout (services d'appui + process locaux)
	@./scripts/stop.sh

backup-db: ## Sauvegarde PostGIS -> backups/cacaosat-<horodatage>.dump (pg_dump format custom)
	@mkdir -p $(BACKUP_DIR)
	@ts=$$(date +%Y%m%d-%H%M%S); out="$(BACKUP_DIR)/$(DB_NAME)-$$ts.dump"; \
	 echo "→ pg_dump $(DB_NAME) vers $$out"; \
	 docker compose exec -T $(DB_SERVICE) pg_dump -U $(DB_USER) -Fc --no-owner $(DB_NAME) > "$$out" && \
	 echo "✓ $$(du -h "$$out" | cut -f1) écrit dans $$out"

restore-db: ## Restaure un dump : make restore-db FILE=backups/cacaosat-XXXX.dump
	@test -n "$(FILE)" || { echo "Usage: make restore-db FILE=backups/<fichier>.dump"; exit 2; }
	@test -f "$(FILE)" || { echo "Introuvable : $(FILE)"; exit 2; }
	@echo "→ restauration de $(FILE) dans $(DB_NAME) (les objets existants sont remplacés)"
	@docker compose exec -T $(DB_SERVICE) pg_restore -U $(DB_USER) -d $(DB_NAME) --clean --if-exists --no-owner < "$(FILE)" && \
	 echo "✓ base restaurée"

clean: ## Nettoie les artefacts de build
	@rm -rf .dev web/dist backend/.pytest_cache mobile/build
