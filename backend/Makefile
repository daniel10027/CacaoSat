VENV ?= .venv
PY ?= $(shell command -v python3.12 || command -v python3)
BIN := $(VENV)/bin

.PHONY: venv install run test lint fmt migrate revision seed seed-demo shell clean

venv: ## Crée le virtualenv
	$(PY) -m venv $(VENV)

install: venv ## Installe les dépendances de dev
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements-dev.txt

run: ## Lance l'API en dev (0.0.0.0:8000)
	FLASK_APP=wsgi.py FLASK_CONFIG=development $(BIN)/flask run --host 0.0.0.0 --port 8000

test: ## Lance la suite pytest avec couverture
	$(BIN)/pytest --cov=app --cov-report=term-missing --cov-fail-under=80

lint: ## Vérifie le style (ruff)
	$(BIN)/ruff check .

fmt: ## Formate le code (ruff)
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .

migrate: ## Applique les migrations
	FLASK_APP=wsgi.py $(BIN)/flask db upgrade

revision: ## Génère une migration depuis les modèles (m="msg")
	FLASK_APP=wsgi.py $(BIN)/flask db migrate -m "$(m)"

seed: ## Peuple la base (comptes + données de base)
	FLASK_APP=wsgi.py $(BIN)/flask seed

seed-demo: ## Peuple la base avec la zone pilote
	FLASK_APP=wsgi.py $(BIN)/flask seed-demo

shell: ## Shell Flask
	FLASK_APP=wsgi.py $(BIN)/flask shell

clean:
	rm -rf $(VENV) .pytest_cache .coverage .ruff_cache
