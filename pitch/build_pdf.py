"""Génère pitch/CacaoSat-Pitch.pdf (ReportLab) — une slide par page, paysage.

Indépendant de LibreOffice : le PDF est un livrable de première classe, pas une
conversion du PPTX. Rendu textuel fidèle au deck (fond blanc, charte CI).
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from deck import (BODY, BORDER, CARD, DECK, GREEN_DARK, GREEN_SOFT, INK, MUTED,
                  ORANGE, ORANGE_DARK, ORANGE_SOFT, TIMINGS, Slide)

OUT = Path(__file__).parent / "CacaoSat-Pitch.pdf"
PAGE = landscape((297 * mm, 167 * mm))  # 16:9
W, H = PAGE


def _ribbon_mini(c: canvas.Canvas, x: float, y: float) -> None:
    for i, col in enumerate((ORANGE, BORDER, "00A651")):
        c.setFillColor(HexColor(f"#{col}"))
        c.rect(x + i * 11 * mm, y, 8.6 * mm, 2.2 * mm, stroke=0, fill=1)


def _ribbon_full(c: canvas.Canvas) -> None:
    third = W / 3
    for i, col in enumerate((ORANGE, BORDER, "00A651")):
        c.setFillColor(HexColor(f"#{col}"))
        c.rect(i * third, 0, third, 3 * mm, stroke=0, fill=1)


def _bg(c: canvas.Canvas) -> None:
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0, 0, W, H, stroke=0, fill=1)


def _wrap(c: canvas.Canvas, text: str, x: float, y: float, size: int, color: str,
          leading: float, max_width: float, bold: bool = False) -> float:
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    c.setFillColor(HexColor(f"#{color}"))
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for wd in words:
            trial = f"{line} {wd}".strip()
            if c.stringWidth(trial, font, size) > max_width and line:
                c.drawString(x, y, line)
                y -= leading
                line = wd
            else:
                line = trial
        c.drawString(x, y, line)
        y -= leading
    return y


def _card(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(HexColor(f"#{CARD}"))
    c.setStrokeColor(HexColor(f"#{BORDER}"))
    c.roundRect(x, y, w, h, 3 * mm, stroke=1, fill=1)


def render(c: canvas.Canvas, s: Slide, idx: int) -> None:
    _bg(c)
    m = 20 * mm
    maxw = W - 2 * m

    if s.kind == "cover":
        c.setFillColor(HexColor(f"#{GREEN_SOFT}"))
        c.roundRect(m, H - 42 * mm, 118 * mm, 11 * mm, 5 * mm, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(HexColor(f"#{GREEN_DARK}"))
        c.drawCentredString(m + 59 * mm, H - 38.6 * mm, s.kicker.upper())
        c.setFont("Helvetica-Bold", 44)
        c.setFillColor(HexColor(f"#{ORANGE}"))
        w1 = c.stringWidth("Cacao", "Helvetica-Bold", 44)
        c.drawString(m, H - 62 * mm, "Cacao")
        c.setFillColor(HexColor("#00A651"))
        c.drawString(m + w1, H - 62 * mm, "Sat")
        c.setFillColor(HexColor(f"#{ORANGE}"))
        c.rect(m + 1 * mm, H - 70 * mm, 24 * mm, 1.6 * mm, stroke=0, fill=1)
        c.setFillColor(HexColor("#00A651"))
        c.rect(m + 25 * mm, H - 70 * mm, 24 * mm, 1.6 * mm, stroke=0, fill=1)
        y = H - 78 * mm
        y = _wrap(c, s.subtitle.split("\n")[0], m, y, 15, INK, 20, maxw * 0.75, bold=True)
        y = _wrap(c, s.subtitle.split("\n")[1], m, y - 2 * mm, 10.5, BODY, 15, maxw * 0.72)
        _card(c, m, 24 * mm, 118 * mm, 22 * mm)
        _wrap(c, "ÉQUIPE CACAOSAT", m + 6 * mm, 40.6 * mm, 7.5, GREEN_DARK, 9, 100 * mm)
        _wrap(c, s.footer, m + 6 * mm, 35 * mm, 11, INK, 14, 106 * mm, bold=True)
        _wrap(c, "github.com/daniel10027/CacaoSat · Abidjan — 24–26 septembre 2026",
              m, 17 * mm, 8.5, MUTED, 11, maxw)
        _ribbon_full(c)
        return

    if s.kind == "closing":
        y = H - 55 * mm
        y = _wrap(c, s.title, m, y, 24, INK, 32, maxw, bold=True)
        y = _wrap(c, s.subtitle, m, y - 4 * mm, 12, BODY, 17, maxw * 0.9)
        _ribbon_mini(c, W / 2 - 14 * mm, H - 92 * mm)
        _wrap(c, s.footer, m, 20 * mm, 9, MUTED, 12, maxw)
        return

    # entête commune
    y = H - 14 * mm
    if s.kicker:
        y = _wrap(c, s.kicker.upper(), m, y, 8.5, GREEN_DARK, 11, maxw) - 2 * mm
    y = _wrap(c, s.title, m, y, 20, INK, 25, maxw, bold=True) - 3 * mm
    if s.subtitle:
        y = _wrap(c, s.subtitle, m, y, 10.5, BODY, 15, maxw) - 3 * mm

    # cartes de contenu
    if s.bullets:
        _card(c, m, 16 * mm, 150 * mm, y - 20 * mm + 2 * mm)
        yy = y - 6 * mm
        for b in s.bullets:
            c.setFillColor(HexColor(f"#{ORANGE}"))
            c.circle(m + 7 * mm, yy + 1.2 * mm, 1.1 * mm, stroke=0, fill=1)
            yy = _wrap(c, b, m + 12 * mm, yy, 10.5, BODY, 15, 132 * mm) - 2 * mm
    if s.stats:
        n = len(s.stats)
        cols = 2 if n <= 4 else 1
        cw = (150 * mm - (cols - 1) * 5 * mm) / cols
        x0 = m + 158 * mm
        yy = y - 2 * mm
        for i, (k, v) in enumerate(s.stats):
            col = i % cols
            row = i // cols
            x = x0 + col * (cw + 5 * mm)
            ry = yy - row * 24 * mm
            _card(c, x, ry - 20 * mm, cw, 22 * mm)
            c.setFillColor(HexColor(f"#{ORANGE if i % 2 == 0 else GREEN_DARK}"))
            c.setFont("Helvetica-Bold", 15)
            c.drawString(x + 5 * mm, ry - 4.5 * mm, k)
            _wrap(c, v, x + 5 * mm, ry - 10.5 * mm, 8, BODY, 10.5, cw - 10 * mm)

    _ribbon_mini(c, m, 8 * mm)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HexColor(f"#{MUTED}"))
    c.drawString(m + 40 * mm, 7.4 * mm,
                 s.footer or "CacaoSat · Ivoire Spacehack 2026 — Abidjan")
    c.drawRightString(W - m, 7.4 * mm, f"{idx + 1:02d} / {len(DECK)}  ·  ~{TIMINGS[idx]}s")


def main() -> None:
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    c.setTitle("CacaoSat — Pitch Ivoire Spacehack 2026")
    for i, s in enumerate(DECK):
        render(c, s, idx=i)
        c.showPage()
    c.save()
    total = sum(TIMINGS)
    print(f"→ {OUT}  ({len(DECK)} pages, ~{total // 60}min{total % 60:02d})")


if __name__ == "__main__":
    main()