"""Régénère le support de pitch : PPTX + PDF + SCRIPT.md.

    python3 pitch/build_deck.py

Dépendances : `pip install -r pitch/requirements.txt` (python-pptx, reportlab).
Si LibreOffice est présent, le PPTX est aussi converti en PDF (sinon le PDF
ReportLab autonome fait foi).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import build_pdf  # noqa: E402
import build_pptx  # noqa: E402
from deck import DECK, TIMINGS  # noqa: E402


def write_script() -> None:
    lines = ["# CacaoSat — script de pitch (5 minutes)\n"]
    total = 0
    for i, (s, secs) in enumerate(zip(DECK, TIMINGS, strict=False), start=1):
        total += secs
        mm, ss = total // 60, total % 60
        lines.append(f"## {i}. {s.title}  \n_{secs}s — repère {mm}:{ss:02d}_\n")
        lines.append(f"> {s.notes}\n")
    lines.append(f"\n**Durée cible : {total // 60}min{total % 60:02d}**\n")
    (HERE / "SCRIPT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"→ {HERE / 'SCRIPT.md'}")


def try_libreoffice_pdf() -> None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(HERE),
             str(HERE / "CacaoSat-Pitch.pptx")],
            check=True, capture_output=True, timeout=120,
        )
        print("→ PDF régénéré depuis le PPTX via LibreOffice")
    except Exception as exc:  # noqa: BLE001
        print(f"(LibreOffice indisponible : {exc}) — PDF ReportLab conservé")


def main() -> None:
    build_pptx.main()
    build_pdf.main()
    write_script()
    try_libreoffice_pdf()


if __name__ == "__main__":
    main()
