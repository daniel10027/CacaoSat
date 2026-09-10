"""Génère pitch/CacaoSat-Pitch.pptx (python-pptx, aucun outil payant)."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

from deck import DECK, GREEN, NIGHT, NIGHT2, ORANGE, SAND, Slide

OUT = Path(__file__).parent / "CacaoSat-Pitch.pptx"


def _rgb(hex_str: str) -> RGBColor:
    return RGBColor.from_string(hex_str)


def _bg(slide, hex_str: str) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(hex_str)


def _ribbon(slide, prs) -> None:
    from pptx.enum.shapes import MSO_SHAPE

    w = prs.slide_width
    h = Inches(0.14)
    y = prs.slide_height - h
    thirds = [ORANGE, "FFFFFF", GREEN]
    for i, col in enumerate(thirds):
        shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, w * i // 3, y, w // 3, h)
        shp.fill.solid()
        shp.fill.fore_color.rgb = _rgb(col)
        shp.line.fill.background()


def _text(slide, left, top, width, height, runs, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, (txt, size, color, bold) in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = txt
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = _rgb(color)
        r.font.name = "Arial"
    return box


def render(slide_data: Slide, prs: Presentation) -> None:
    layout = prs.slide_layouts[6]  # vide
    s = prs.slides.add_slide(layout)
    _bg(s, NIGHT if slide_data.kind in {"cover", "closing"} else NIGHT2)
    _ribbon(s, prs)

    margin = Inches(0.7)
    width = prs.slide_width - 2 * margin

    if slide_data.kind == "cover":
        _text(s, margin, Inches(1.7), width,
              Inches(1.6), [("CACAO", 66, ORANGE, True)], PP_ALIGN.CENTER)
        _text(s, margin, Inches(2.9), width, Inches(1.4),
              [(slide_data.subtitle, 22, SAND, False)], PP_ALIGN.CENTER)
        _text(s, margin, prs.slide_height - Inches(1.1), width, Inches(0.7),
              [(slide_data.footer, 12, "9AA0A6", False)], PP_ALIGN.CENTER)
        # "SAT" en vert par-dessus (approché : deuxième ligne)
        _text(s, margin, Inches(1.7), width, Inches(1.6),
              [("        SAT", 66, GREEN, True)], PP_ALIGN.CENTER)
        return

    if slide_data.kind == "closing":
        _text(s, margin, Inches(2.2), width, Inches(2.0),
              [(slide_data.title, 34, "FFFFFF", True)], PP_ALIGN.CENTER)
        _text(s, margin, Inches(4.0), width, Inches(1.2),
              [(slide_data.subtitle, 18, SAND, False)], PP_ALIGN.CENTER)
        _text(s, margin, prs.slide_height - Inches(1.1), width, Inches(0.7),
              [(slide_data.footer, 12, "9AA0A6", False)], PP_ALIGN.CENTER)
        return

    _text(s, margin, Inches(0.55), width, Inches(1.0),
          [(slide_data.title, 30, "FFFFFF", True)])
    top = Inches(1.6)
    if slide_data.subtitle:
        _text(s, margin, top, width, Inches(1.1),
              [(slide_data.subtitle, 16, SAND, False)])
        top = Emu(int(top) + Inches(1.15))

    if slide_data.stats:
        runs = [(f"{k}   —   {v}", 18, GREEN if len(k) <= 6 else "FFFFFF", True)
                for k, v in slide_data.stats]
        _text(s, margin, top, width, Inches(3.6), runs)
    if slide_data.bullets:
        runs = [(f"•  {b}", 15, SAND, False) for b in slide_data.bullets]
        _text(s, margin, top, width, Inches(4.2), runs)


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    for slide in DECK:
        render(slide, prs)
    for i, s in enumerate(prs.slides):
        s.notes_slide.notes_text_frame.text = DECK[i].notes
    prs.save(OUT)
    print(f"→ {OUT}  ({len(DECK)} slides)")


if __name__ == "__main__":
    main()
