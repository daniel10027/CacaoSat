"""Génère pitch/CacaoSat-Pitch.pdf (ReportLab) — une slide par page, paysage.

Indépendant de LibreOffice : le PDF est un livrable de première classe, pas une
conversion du PPTX.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from deck import DECK, GREEN, NIGHT, NIGHT2, ORANGE, SAND, TIMINGS, Slide

OUT = Path(__file__).parent / "CacaoSat-Pitch.pdf"
PAGE = landscape((297 * mm, 167 * mm))  # 16:9
W, H = PAGE


def _ribbon(c: canvas.Canvas) -> None:
    third = W / 3
    for i, col in enumerate((ORANGE, "FFFFFF", GREEN)):
        c.setFillColor(HexColor(f"#{col}"))
        c.rect(i * third, 0, third, 5 * mm, stroke=0, fill=1)


def _wrap(c: canvas.Canvas, text: str, x: float, y: float, size: int, color: str,
          leading: float, max_width: float, bold: bool = False) -> float:
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    c.setFillColor(HexColor(f"#{color}"))
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            trial = f"{line} {w}".strip()
            if c.stringWidth(trial, font, size) > max_width and line:
                c.drawString(x, y, line)
                y -= leading
                line = w
            else:
                line = trial
        c.drawString(x, y, line)
        y -= leading
    return y


def render(c: canvas.Canvas, s: Slide, idx: int) -> None:
    c.setFillColor(HexColor(f"#{NIGHT if s.kind in {'cover', 'closing'} else NIGHT2}"))
    c.rect(0, 0, W, H, stroke=0, fill=1)
    _ribbon(c)
    m = 22 * mm
    maxw = W - 2 * m

    if s.kind == "cover":
        c.setFont("Helvetica-Bold", 52)
        c.setFillColor(HexColor(f"#{ORANGE}"))
        c.drawCentredString(W / 2 - 55, H / 2 + 20, "CACAO")
        c.setFillColor(HexColor(f"#{GREEN}"))
        c.drawString(W / 2 - 55 + c.stringWidth("CACAO", "Helvetica-Bold", 52), H / 2 + 20, "SAT")
        _wrap(c, s.subtitle, m, H / 2 - 8, 16, SAND, 22, maxw)
        _wrap(c, s.footer, m, 18 * mm, 9, "9AA0A6", 12, maxw)
        return

    if s.kind == "closing":
        _wrap(c, s.title, m, H - 60 * mm, 26, "FFFFFF", 34, maxw, bold=True)
        _wrap(c, s.subtitle, m, H - 110 * mm, 13, SAND, 18, maxw)
        _wrap(c, s.footer, m, 18 * mm, 9, "9AA0A6", 12, maxw)
        return

    y = H - 26 * mm
    y = _wrap(c, s.title, m, y, 24, "FFFFFF", 30, maxw, bold=True) - 4 * mm
    if s.subtitle:
        y = _wrap(c, s.subtitle, m, y, 12.5, SAND, 17, maxw) - 4 * mm
    for k, v in s.stats:
        y = _wrap(c, f"{k}   —   {v}", m, y, 13, GREEN if len(k) <= 6 else "FFFFFF", 22,
                  maxw, bold=True)
    for b in s.bullets:
        y = _wrap(c, f"•  {b}", m + 3 * mm, y, 11.5, SAND, 17, maxw - 3 * mm)

    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#9AA0A6"))
    c.drawRightString(W - m, 9 * mm, f"{idx + 1}/{len(DECK)}  ·  ~{TIMINGS[idx]}s")


def main() -> None:
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    c.setTitle("CacaoSat — Pitch Ivoire Spacehack 2026")
    for i, s in enumerate(DECK):
        render(c, s, i)
        c.showPage()
    c.save()
    total = sum(TIMINGS)
    print(f"→ {OUT}  ({len(DECK)} pages, ~{total // 60}min{total % 60:02d})")


if __name__ == "__main__":
    main()
