#!/usr/bin/env python3
"""Garde-fou des docs de suivi : un lot marqué [x] ne doit pas contenir de
case enfant [ ] non justifiée (mot 'reporté' / 'Lot 11' toléré), et tous les
liens Markdown internes doivent pointer vers un fichier existant."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ["ROADMAP.md", "docs/BACKEND.md", "docs/FRONTEND.md", "docs/MOBILE.md", "docs/INFRA.md", "README.md"]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

errors: list[str] = []

for rel in DOCS:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"{rel}: fichier manquant")
        continue
    text = path.read_text(encoding="utf-8")

    # liens internes
    for m in LINK_RE.finditer(text):
        target = m.group(1).split("#")[0]
        if target.startswith(("http://", "https://", "mailto:")) or not target:
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"{rel}: lien cassé → {target}")

    # cases orphelines : un titre de lot '## Lot N — ... `[x]`' suivi de '- [ ]'
    lines = text.splitlines()
    lot_done = False
    for i, line in enumerate(lines):
        h = re.match(r"^##+ .*Lot \d+.*", line)
        if h:
            lot_done = "`[x]`" in line
        if lot_done and re.match(r"^\s*- \[ \] ", line):
            tolerated = any(w in line.lower() for w in ("reporté", "lot 11", "🔒", "nécessite"))
            if not tolerated:
                errors.append(f"{rel}:{i + 1}: case [ ] dans un lot marqué [x] → {line.strip()[:70]}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"docs OK ({len(DOCS)} fichiers, liens et cases cohérents)")
