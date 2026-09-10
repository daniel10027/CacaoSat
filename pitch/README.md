# Pitch — CacaoSat

Support de pitch 5 minutes pour Ivoire Spacehack 2026.

## Régénérer

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build_deck.py        # ou : make pitch (racine)
```

Produit :
- `CacaoSat-Pitch.pptx` — 12 slides + notes du présentateur (python-pptx)
- `CacaoSat-Pitch.pdf` — 12 pages paysage 16:9, autonome (ReportLab)
- `SCRIPT.md` — texte minuté, repères chrono par slide (~5 min)

`deck.py` contient tout le contenu (une seule source de vérité).
Charte : orange FF7A00 / vert 00A651 / nuit, ruban tricolore.
