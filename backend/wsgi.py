"""Point d'entrée WSGI (Gunicorn en production, `flask run` en dev)."""

import os

from app import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "production"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
