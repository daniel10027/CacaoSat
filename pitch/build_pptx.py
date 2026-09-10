"""Génère pitch/CacaoSat-Pitch.pptx — deck professionnel, fond blanc.

- Charte drapeau ivoirien (orange / blanc / vert), typographie Arial.
- Mise en page illustrée par slide : schémas natifs (chevrons, architecture,
  mockups téléphone/certificat/navigateur), captures réelles du produit et
  graphiques matplotlib (pitch/graphics.py).
- Animations : fondu enchaîné à l'ouverture de chaque slide + apparitions
  progressives des éléments (timing XML injecté, compatible PowerPoint).
- Notes du présentateur reprises de deck.py.

Aucun outil payant requis : python-pptx + matplotlib + PIL.
"""

from __future__ import annotations

import colorsys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pptx.util import Emu, Inches, Pt

import graphics
from deck import (BODY, BORDER, CARD, DECK, GREEN, GREEN_DARK, GREEN_SOFT, INK,
                  MUTED, ORANGE, ORANGE_DARK, ORANGE_SOFT, RED, Slide)

HERE = Path(__file__).parent
REPO = HERE.parent
OUT = HERE / "CacaoSat-Pitch.pptx"

LOGO = REPO / "web/src/assets/logo-cacaosat.png"
SHOTS = REPO / "docs/screenshots"
GEN = HERE / "assets/gen"

# 16:9
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN = Inches(0.62)
CONTENT_W = SLIDE_W - 2 * MARGIN

WHITE = "FFFFFF"
GREY_BAR = "ECEFEA"      # segment « blanc » du ruban, lisible sur fond blanc
CHROME = "F1F3F1"


# ----------------------------------------------------------------- helpers bas niveau
def _rgb(h: str) -> RGBColor:
    return RGBColor.from_string(h)


def _mix(c1: str, c2: str, t: float) -> str:
    a = [int(c1[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(c2[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def _shadow(shape, blur: float = 0.10, dist: float = 0.045, alpha: int = 17) -> None:
    """Ombre portée douce (injectée en XML, python-pptx n'a pas d'API)."""
    spPr = shape._element.spPr
    xml = (
        f'<a:effectLst {nsdecls("a")}>'
        f'<a:outerShdw blurRad="{Inches(blur)}" dist="{Inches(dist)}" dir="5400000" '
        f'rotWithShape="0"><a:srgbClr val="13251C"><a:alpha val="{alpha * 1000}"/>'
        f"</a:srgbClr></a:outerShdw></a:effectLst>"
    )
    spPr.append(parse_xml(xml))


def _bg(slide) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = _rgb(WHITE)


def _ribbon(slide, y: float, h: float = 0.075, full: bool = False) -> None:
    """Bandes tricolores. full : pleine largeur (couverture/clôture)."""
    h_emu = Inches(h)
    y = Inches(y)
    cols = [(ORANGE, None), (GREY_BAR, BORDER), (GREEN, None)]
    for i, (col, line) in enumerate(cols):
        if full:
            x, seg = i * (SLIDE_W / 3), SLIDE_W / 3
        else:
            x, seg = MARGIN + i * Inches(0.35), Inches(0.30)
        shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, seg, h_emu)
        shp.fill.solid()
        shp.fill.fore_color.rgb = _rgb(col)
        if line:
            shp.line.color.rgb = _rgb(line)
            shp.line.width = Pt(0.5)
        else:
            shp.line.fill.background()
        shp.shadow.inherit = False


def _txt(slide, x, y, w, h, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         line_spacing=1.0, wrap=True, spc=None):
    """paras : liste de paragraphes ; chaque paragraphe = liste de runs
    (texte, taille, couleur, gras[, italique])."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    _reg(box)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        if len(paras) > 1:
            p.space_after = Pt(4)
        for run in para:
            text, size, color, bold = run[:4]
            italic = run[4] if len(run) > 4 else False
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = _rgb(color)
            r.font.name = "Arial"
            if spc:
                r._r.get_or_add_rPr().set("spc", str(spc))
    return box


def _shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=0.75,
           adj=None, rot=None, shadow=False):
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    _reg(shp)
    shp.shadow.inherit = False
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = _rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = _rgb(line)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    if adj is not None:
        try:
            shp.adjustments[0] = adj
        except Exception:  # noqa: BLE001
            pass
    if rot:
        shp.rotation = rot
    if shadow:
        _shadow(shp)
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    tf.margin_top = tf.margin_bottom = Inches(0.04)
    return shp


def _set_text(shp, paras, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE,
              line_spacing=1.0):
    """Écrit du texte dans une autoshape (même format que _txt)."""
    tf = shp.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        if len(paras) > 1:
            p.space_after = Pt(3)
        for run in para:
            text, size, color, bold = run[:4]
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.color.rgb = _rgb(color)
            r.font.name = "Arial"
    return shp


def _card(slide, x, y, w, h, fill=WHITE, line=BORDER, adj=0.085, shadow=True,
          line_w=0.75):
    return _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h,
                  fill=fill, line=line, adj=adj, shadow=shadow, line_w=line_w)


def _chip(slide, x, y, w, h, text, fill=GREEN_SOFT, color=GREEN_DARK, size=10,
          bold=True, line=None):
    shp = _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill,
                 line=line, adj=0.5)
    _set_text(shp, [[(text, size, color, bold)]], align=PP_ALIGN.CENTER)
    return shp


# ----------------------------------------------------------------- icônes dessinées
def _icon_satellite(slide, cx, cy, s=0.62, color=ORANGE):
    """Petit satellite : corps + panneaux."""
    _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, cx - s * 0.16, cy - s * 0.16,
           s * 0.32, s * 0.32, fill=color, adj=0.25)
    _shape(slide, MSO_SHAPE.RECTANGLE, cx - s * 0.52, cy - s * 0.11,
           s * 0.30, s * 0.22, fill=_mix(color, INK, 0.25))
    _shape(slide, MSO_SHAPE.RECTANGLE, cx + s * 0.22, cy - s * 0.11,
           s * 0.30, s * 0.22, fill=_mix(color, INK, 0.25))
    _shape(slide, MSO_SHAPE.OVAL, cx - s * 0.06, cy + s * 0.20, s * 0.12, s * 0.12,
           fill=color)


def _icon_tree(slide, cx, cy, s=0.62, color=GREEN):
    _shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, cx - s * 0.30, cy - s * 0.42,
           s * 0.60, s * 0.62, fill=color)
    _shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, cx - s * 0.055, cy + s * 0.14,
           s * 0.11, s * 0.30, fill=_mix(color, INK, 0.3), adj=0.3)


def _icon_globe(slide, cx, cy, s=0.62, color=ORANGE):
    _shape(slide, MSO_SHAPE.OVAL, cx - s * 0.32, cy - s * 0.32, s * 0.64, s * 0.64,
           fill=None, line=color, line_w=2.2)
    _shape(slide, MSO_SHAPE.OVAL, cx - s * 0.32, cy - s * 0.10, s * 0.64, s * 0.20,
           fill=None, line=color, line_w=1.4)
    _shape(slide, MSO_SHAPE.RECTANGLE, cx - s * 0.012, cy - s * 0.32,
           s * 0.024, s * 0.64, fill=color)


def _icon_people(slide, cx, cy, s=0.62, color=GREEN):
    for dx in (-s * 0.26, 0.0, s * 0.26):
        _shape(slide, MSO_SHAPE.OVAL, cx + dx - s * 0.09, cy - s * 0.30,
               s * 0.18, s * 0.18, fill=color)
        _shape(slide, MSO_SHAPE.OVAL, cx + dx - s * 0.13, cy - s * 0.06,
               s * 0.26, s * 0.36, fill=color)


def _icon_coin(slide, cx, cy, s=0.62, color=ORANGE):
    _shape(slide, MSO_SHAPE.DONUT, cx - s * 0.32, cy - s * 0.32, s * 0.64, s * 0.64,
           fill=color, adj=0.22)
    _txt(slide, cx - s * 0.32, cy - s * 0.19, s * 0.64, s * 0.4,
         [[("€", s * 22, INK, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def _icon_building(slide, cx, cy, s=0.62, color=GREEN_DARK):
    _shape(slide, MSO_SHAPE.RECTANGLE, cx - s * 0.28, cy - s * 0.36, s * 0.56, s * 0.72,
           fill=color)
    for i in range(3):
        for j in range(2):
            _shape(slide, MSO_SHAPE.RECTANGLE, cx - s * 0.19 + i * s * 0.15,
                   cy - s * 0.26 + j * s * 0.2, s * 0.08, s * 0.1, fill=WHITE)


def _icon_warn(slide, cx, cy, s=0.62, color=ORANGE):
    _shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, cx - s * 0.34, cy - s * 0.34,
           s * 0.68, s * 0.62, fill=color)
    _txt(slide, cx - s * 0.2, cy - s * 0.12, s * 0.4, s * 0.3,
         [[("!", s * 16, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def _icon_check(slide, cx, cy, s=0.62, color=GREEN):
    _shape(slide, MSO_SHAPE.OVAL, cx - s * 0.30, cy - s * 0.30, s * 0.60, s * 0.60,
           fill=color)
    _txt(slide, cx - s * 0.3, cy - s * 0.24, s * 0.6, s * 0.5,
         [[("✓", s * 18, WHITE, True)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def _icon_doc(slide, cx, cy, s=0.62, color=GREEN_DARK):
    _shape(slide, MSO_SHAPE.RECTANGLE, cx - s * 0.22, cy - s * 0.30, s * 0.44, s * 0.60,
           fill=WHITE, line=color, line_w=1.6)
    for i in range(3):
        _shape(slide, MSO_SHAPE.RECTANGLE, cx - s * 0.13, cy - s * 0.16 + i * s * 0.14,
               s * 0.26 - (s * 0.08 if i == 2 else 0), s * 0.035, fill=color)


# ----------------------------------------------------------------- structure de slide
class Ctx:
    """Contexte d'une slide : slide, numéro, formes à animer."""

    def __init__(self, slide, idx: int):
        self.slide = slide
        self.idx = idx
        self.anim: list = []

    def add(self, *shapes):
        return shapes  # l'enregistrement est automatique via _CTX


_CTX: Ctx | None = None


def _reg(shape) -> None:
    """Enregistre une forme pour l'apparition progressive (ordre de création)."""
    if _CTX is not None and shape is not None:
        _CTX.anim.append(shape)


def _pic(slide, path, x, y, w=None, h=None):
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                   width=Inches(w) if w else None,
                                   height=Inches(h) if h else None)
    _reg(pic)
    return pic


def _header(ctx: Ctx, kicker: str, title: str, subtitle: str = "") -> None:
    s = ctx.slide
    if kicker:
        _txt(s, 0.64, 0.34, 11.5, 0.3,
             [[(kicker.upper(), 10, GREEN_DARK, True)]], spc=160)
    _txt(s, 0.62, 0.62, 12.1, 0.75, [[(title, 26, INK, True)]])
    if subtitle:
        _txt(s, 0.62, 1.22, 12.0, 0.55, [[(subtitle, 12, BODY, False)]],
             line_spacing=1.08)


def _footer(ctx: Ctx, footer_text: str = "") -> None:
    s = ctx.slide
    _ribbon(s, 7.20, h=0.065)
    _txt(s, 1.78, 7.10, 9.0, 0.28,
         [[(footer_text or "CacaoSat · Ivoire Spacehack 2026 — Abidjan",
            8.5, MUTED, False)]])
    _txt(s, 11.9, 7.10, 0.85, 0.28,
         [[(f"{ctx.idx + 1:02d} / {len(DECK)}", 8.5, MUTED, True)]], align=PP_ALIGN.RIGHT)


def _browser_frame(ctx: Ctx, x, y, w, img: Path, url: str) -> None:
    """Capture dans une fenêtre de navigateur (barre d'adresse + ombre)."""
    s = ctx.slide
    ratio = None
    from PIL import Image
    with Image.open(img) as im:
        ratio = im.height / im.width
    img_w = w - 0.04
    img_h = img_w * ratio
    bar_h = 0.36
    frame_h = bar_h + img_h + 0.02
    frame = _card(s, x, y, w, frame_h, fill=WHITE, line=BORDER, adj=0.045)
    ctx.add(frame)
    _shape(s, MSO_SHAPE.RECTANGLE, x + 0.015, y + 0.015, w - 0.03, bar_h, fill=CHROME)
    for i in range(3):
        _shape(s, MSO_SHAPE.OVAL, x + 0.14 + i * 0.17, y + bar_h / 2 - 0.045,
               0.09, 0.09, fill="C9CEC9")
    pill = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.62, y + bar_h / 2 - 0.11,
                  w - 0.78, 0.22, fill=WHITE, line=BORDER, adj=0.5)
    _set_text(pill, [[(url, 8, MUTED, False)]], align=PP_ALIGN.LEFT)
    pic = _pic(s, img, x + 0.02, y + bar_h + 0.02, w=img_w)
    _shadow(pic, blur=0.06, dist=0.02, alpha=10)
    return y + frame_h


# ================================================================= SLIDES
def s_cover(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    # décor
    _shape(s, MSO_SHAPE.OVAL, 7.45, 0.55, 5.35, 5.35, fill=ORANGE_SOFT)
    _shape(s, MSO_SHAPE.OVAL, 11.75, 4.95, 1.7, 1.7, fill=GREEN_SOFT)
    _shape(s, MSO_SHAPE.OVAL, 6.9, 5.6, 0.55, 0.55, fill=None, line=ORANGE, line_w=2)
    _shape(s, MSO_SHAPE.OVAL, 7.45, 0.55, 5.35, 5.35, fill=ORANGE_SOFT)
    _shape(s, MSO_SHAPE.OVAL, 11.75, 4.95, 1.7, 1.7, fill=GREEN_SOFT)
    _shape(s, MSO_SHAPE.OVAL, 6.62, 4.02, 0.5, 0.5, fill=None, line=ORANGE, line_w=2)
    _pic(s, LOGO, 8.25, 0.95, w=3.75)
    # kicker
    chip = _chip(s, 0.62, 1.55, 4.62, 0.44, sl.kicker.upper(), fill=GREEN_SOFT,
                 color=GREEN_DARK, size=10)
    ctx.add(chip)
    # titre bicolore
    title = _txt(s, 0.58, 2.02, 7.2, 1.15,
                 [[("Cacao", 58, ORANGE, True), ("Sat", 58, GREEN, True)]])
    ctx.add(title)
    # séparateur tricolore
    seg1 = _shape(s, MSO_SHAPE.RECTANGLE, 0.64, 3.28, 1.15, 0.07, fill=ORANGE)
    seg2 = _shape(s, MSO_SHAPE.RECTANGLE, 1.79, 3.28, 1.15, 0.07, fill=GREEN)
    ctx.add(seg1, seg2)
    tagline = _txt(s, 0.62, 3.52, 6.9, 0.95,
                   [[(sl.subtitle.split("\n")[0], 18, INK, True)],
                    [(sl.subtitle.split("\n")[1], 12.5, BODY, False)]],
                   line_spacing=1.12)
    ctx.add(tagline)
    # carte équipe
    team = _card(s, 0.62, 4.95, 6.55, 1.25, fill=CARD, line=BORDER)
    _txt(s, 0.88, 5.14, 6.0, 0.28, [[("ÉQUIPE CACAOSAT", 9, GREEN_DARK, True)]], spc=140)
    _txt(s, 0.88, 5.44, 6.0, 0.35,
         [[("Akandji Timothé · Elie Konan · Daniel Guedegbe", 13, INK, True)]])
    _txt(s, 0.88, 5.80, 6.0, 0.3,
         [[("Data engineering · Traitement géospatial · Mobile & terrain", 9.5, MUTED, False)]])
    ctx.add(team)
    # bas de page
    _txt(s, 0.62, 6.55, 8.0, 0.3,
         [[("github.com/daniel10027/CacaoSat   ·   Abidjan — 24–26 septembre 2026",
            10, MUTED, False)]])
    _ribbon(s, 7.41, h=0.09, full=True)


def s_eudr(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title, sl.subtitle)
    # timeline (gauche)
    card = _card(s, 0.62, 1.78, 6.05, 4.95, fill=WHITE, line=BORDER)
    ctx.add(card)
    _txt(s, 0.92, 1.98, 5.4, 0.3, [[("L'EXIGENCE, ÉTAPE PAR ÉTAPE", 9.5, GREEN_DARK, True)]],
         spc=120)
    _shape(s, MSO_SHAPE.RECTANGLE, 1.05, 2.52, 0.028, 3.65, fill=BORDER)
    rows = [
        ("31 déc. 2020", "Date de référence : aucune déforestation après cette date", ORANGE),
        ("Fin 2024", "EUDR entre en vigueur — preuve géospatiale obligatoire", ORANGE),
        ("2025", "Application stricte : contrôles, sanctions, exclusion possible", GREEN),
        ("Aujourd'hui", "Chaque export : coordonnées GPS + preuve, parcelle par parcelle", GREEN_DARK),
    ]
    y = 2.42
    for date, desc, col in rows:
        dot = _shape(s, MSO_SHAPE.OVAL, 0.965, y + 0.10, 0.19, 0.19, fill=col)
        box = _txt(s, 1.38, y, 5.1, 0.85,
                   [[(date, 12, INK, True)], [(desc, 10, BODY, False)]],
                   line_spacing=1.05)
        y += 0.94
        ctx.add(dot, box)
    # stats (droite) 2×2
    stats = [
        ("N°1", "producteur mondial de cacao", ORANGE),
        ("82 %", "traçable à la parcelle en 2023", GREEN),
        ("~30 %", "de la surface en zone protégée", ORANGE),
        ("2 M+", "foyers dépendant de la filière", GREEN_DARK),
    ]
    xs, ys, w, h, gap = 7.0, 1.78, 2.82, 2.28, 0.28
    for i, (num, label, col) in enumerate(stats):
        x = xs + (i % 2) * (w + gap)
        yy = ys + (i // 2) * (h + gap)
        c = _card(s, x, yy, w, h, fill=WHITE, line=BORDER)
        bar = _shape(s, MSO_SHAPE.RECTANGLE, x + 0.28, yy + 0.30, 0.42, 0.07, fill=col)
        num_box = _txt(s, x + 0.28, yy + 0.52, w - 0.5, 0.75, [[(num, 30, col, True)]])
        lbl = _txt(s, x + 0.28, yy + 1.5, w - 0.52, 0.65, [[(label, 11, BODY, False)]],
                   line_spacing=1.1)
        ctx.add(c, bar, num_box, lbl)
    _footer(ctx)


def s_problem(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    cards = [
        ("L'UE EXIGE", "Une preuve géospatiale par parcelle",
         "Coordonnées GPS + absence de déforestation post-2020, pour chaque cargaison.",
         WHITE, BORDER, GREEN_DARK),
        ("LA RÉALITÉ TERRAIN", "Des milliers de parcelles à cartographier… à la main",
         "Sans outil numérique, sans expertise juridique, avec un papier et un crayon.",
         ORANGE_SOFT, ORANGE, ORANGE_DARK),
        ("LA CONSÉQUENCE", "Exclusion du marché européen",
         "Des milliers de foyers perdent leur débouché principal faute de dossier.",
         WHITE, BORDER, RED),
    ]
    w, h, y = 3.75, 2.05, 1.80
    xs = [0.62, 4.79, 8.96]
    for (kick, title, desc, fill, line, kcol), x in zip(cards, xs):
        c = _card(s, x, y, w, h, fill=fill, line=line)
        _txt(s, x + 0.26, y + 0.2, w - 0.5, 0.28, [[(kick, 9, kcol, True)]], spc=120)
        _txt(s, x + 0.26, y + 0.5, w - 0.5, 0.62, [[(title, 13.5, INK, True)]],
             line_spacing=1.05)
        _txt(s, x + 0.26, y + 1.22, w - 0.5, 0.7, [[(desc, 10, BODY, False)]],
             line_spacing=1.15)
        ctx.add(c)
    for ax in (4.42, 8.59):
        arr = _shape(s, MSO_SHAPE.RIGHT_ARROW, ax, y + 0.82, 0.32, 0.4,
                     fill="C9CEC9")
        ctx.add(arr)
    # bandeau clé
    band = _card(s, 0.62, 4.28, 12.1, 1.1, fill=GREEN_SOFT, line=None)
    _txt(s, 1.0, 4.47, 11.4, 0.45,
         [[("Une charge disproportionnée pour ceux qui font tourner la filière.",
            15, INK, True)]])
    _txt(s, 1.0, 4.92, 11.4, 0.35,
         [[("Le coût de mise en conformité menace directement les petites coopératives.",
            10.5, GREEN_DARK, False)]])
    ctx.add(band)
    # 3 constats
    facts = [("Charge", "des milliers de relevés à produire et documenter"),
             ("Moyens", "ni outil numérique, ni budget, ni expertise"),
             ("Risque", "perte d'accès au marché UE dès 2025")]
    for i, (k, v) in enumerate(facts):
        x = 0.62 + i * 4.17
        c = _card(s, x, 5.72, 3.86, 1.0, fill=WHITE, line=BORDER)
        _txt(s, x + 0.24, 5.9, 3.4, 0.3, [[(k.upper(), 10, ORANGE_DARK, True)]], spc=100)
        _txt(s, x + 0.24, 6.04, 3.4, 0.55, [[(v, 9.5, BODY, False)]], line_spacing=1.1)
        ctx.add(c)
    _footer(ctx)


def s_sources(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    src = [
        ("Sentinel-2", "Copernicus — Union européenne",
         "Imagerie optique 10 m, revisitée tous les 5 jours : état du couvert végétal.",
         "satellite", ORANGE, ORANGE_SOFT),
        ("Hansen / Global Forest Watch", "Université du Maryland + WRI",
         "Couvert forestier et perte annuelle, depuis 2000, à 30 m.", "tree", GREEN, GREEN_SOFT),
        ("Digital Earth Africa", "Programme continental ouvert",
         "Dégradation des terres et services d'analyse prêts à l'emploi.", "globe", ORANGE_DARK, ORANGE_SOFT),
    ]
    w, y0 = 3.9, 1.85
    xs = [0.62, 4.72, 8.82]
    icons = {"satellite": _icon_satellite, "tree": _icon_tree, "globe": _icon_globe}
    for (name, org, desc, icon, col, soft), x in zip(src, xs):
        c = _card(s, x, y0, w, 3.05, fill=WHITE, line=BORDER)
        ctx.add(c)
        circ = _shape(s, MSO_SHAPE.OVAL, x + 0.3, y0 + 0.28, 0.95, 0.95, fill=soft)
        icons[icon](s, x + 0.3 + 0.475, y0 + 0.28 + 0.475, s=0.72, color=col)
        ctx.add(circ)
        _txt(s, x + 0.3, y0 + 1.42, w - 0.6, 0.35, [[(name, 14, INK, True)]])
        _txt(s, x + 0.3, y0 + 1.78, w - 0.6, 0.3, [[(org, 9.5, MUTED, False)]])
        _txt(s, x + 0.3, y0 + 2.1, w - 0.6, 0.75, [[(desc, 10, BODY, False)]],
             line_spacing=1.15)
        chip = _chip(s, x + 0.3, y0 + 2.62, 2.5, 0.32, "Gratuit · données ouvertes",
                     fill=GREEN_SOFT, color=GREEN_DARK, size=8.5)
        ctx.add(chip)
    # flèche + bandeau insight
    arr = _shape(s, MSO_SHAPE.DOWN_ARROW, 6.55, 5.08, 0.24, 0.3, fill="C9CEC9")
    ctx.add(arr)
    band = _card(s, 0.62, 5.5, 12.1, 1.2, fill=INK, line=None)
    _txt(s, 1.05, 5.72, 11.3, 0.4,
         [[("Ce qui manque n'est pas la donnée — c'est le ", 14.5, WHITE, True),
           ("pipeline", 14.5, "7BD9A2", True),
           (" qui la relie au terrain.", 14.5, WHITE, True)]])
    _txt(s, 1.05, 6.18, 11.3, 0.35,
         [[("C'est exactement ce que CacaoSat construit.", 10.5, "9DB5A8", False)]])
    ctx.add(band)
    _footer(ctx)


def s_pipeline(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    steps = [
        ("01", "Cartographie", "Relevé GPS hors-ligne des parcelles — app mobile"),
        ("02", "Ingestion", "Base géospatiale PostGIS unique et interopérable"),
        ("03", "Croisement satellite", "Sentinel-2 + Hansen/GFW + DEA, depuis 2020"),
        ("04", "Scoring EUDR", "Score /100 pondéré et explicable, par parcelle"),
        ("05", "Certificat", "Rapport PDF + GeoJSON, empreinte SHA-256"),
        ("06", "Alerte précoce", "Détection continue, notification coopérative"),
    ]
    n = len(steps)
    w, h, y = 2.24, 0.98, 1.92
    step = (12.1 - w) / (n - 1) if n > 1 else 0
    for i, (num, label, desc) in enumerate(steps):
        col = _mix(ORANGE, GREEN, i / (n - 1))
        x = 0.62 + i * step
        chev = _shape(s, MSO_SHAPE.CHEVRON, x, y, w, h, fill=col, adj=0.42)
        _set_text(chev, [[(num, 9, "FFFFFF", True)], [(label, 10.5, "FFFFFF", True)]],
                  align=PP_ALIGN.CENTER)
        ctx.add(chev)
        dc = _card(s, x + 0.06, y + 1.22, w - 0.12, 1.45, fill=CARD, line=None,
                   shadow=False)
        _set_text(dc, [[(desc, 9.5, BODY, False)]], align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.TOP, line_spacing=1.12)
        ctx.add(dc)
    band = _card(s, 0.62, 5.05, 12.1, 1.5, fill=WHITE, line=GREEN, line_w=1.2)
    _txt(s, 1.0, 5.28, 11.3, 0.45,
         [[("Automatisé de bout en bout : ", 15, INK, True),
           ("quelques minutes au lieu de plusieurs semaines", 15, GREEN_DARK, True),
           (".", 15, INK, True)]])
    _txt(s, 1.0, 5.82, 11.3, 0.4,
         [[("Du relevé terrain au document exportable — sans étape manuelle, "
            "sans intermédiaire coûteux.", 11, MUTED, False)]])
    ctx.add(band)
    _footer(ctx)


def s_mobile(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    # --- téléphone (gauche)
    px, py, pw, ph = 0.85, 1.68, 2.8, 5.3
    body = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pw, ph, fill=INK, adj=0.14,
                  shadow=True)
    ctx.add(body)
    scr_x, scr_y, scr_w = px + 0.11, py + 0.30, pw - 0.22
    # carte satellite
    map_h = 1.75
    pic = _pic(s, GEN / "map_satellite.png", scr_x, scr_y, w=scr_w)
    _shadow(pic, blur=0.03, dist=0.01, alpha=8)
    # position agent + halo
    halo = _shape(s, MSO_SHAPE.OVAL, scr_x + 0.78, scr_y + 0.72, 0.5, 0.5,
                  fill=None, line=ORANGE, line_w=1.6)
    pos = _shape(s, MSO_SHAPE.OVAL, scr_x + 0.96, scr_y + 0.90, 0.15, 0.15,
                 fill=ORANGE, line="FFFFFF", line_w=1.2)
    # parcelle surlignée sur la carte (rectangle vert)
    sel = _shape(s, MSO_SHAPE.RECTANGLE, scr_x + 1.42, scr_y + 0.28, 0.72, 0.5,
                 fill=None, line="FFFFFF", line_w=2.2)
    ctx.add(halo, pos, sel)
    # panneau bas du téléphone
    panel_y = scr_y + map_h + 0.06
    _txt(s, scr_x + 0.12, panel_y, scr_w - 0.2, 0.3,
         [[("Parcelle #0042", 11, "FFFFFF", True)]])
    _txt(s, scr_x + 0.12, panel_y + 0.3, scr_w - 0.2, 0.26,
         [[("4,2 ha · relevé GPS terminé", 8.5, "AEBBB2", False)]])
    score = _chip(s, scr_x + 0.12, panel_y + 0.62, 1.7, 0.4,
                  "Score 87 · Conforme", fill=GREEN_SOFT, color=GREEN_DARK, size=9)
    btn = _chip(s, scr_x + 0.12, panel_y + 1.14, scr_w - 0.24, 0.42,
                "Synchroniser le lot", fill=ORANGE, color="FFFFFF", size=10)
    ctx.add(score, btn)
    home = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, px + pw / 2 - 0.25, py + ph - 0.14,
                  0.5, 0.05, fill="3A4A41", adj=0.5)
    # --- features (droite)
    feats = [
        ("Contour relevé en marchant, par sommets ou saisie manuelle", "path", GREEN),
        ("Surface calculée en direct — alerte si aire protégée touchée", "warn", ORANGE),
        ("100 % hors-ligne : tout est stocké en local (SQLite)", "offline", GREEN_DARK),
        ("Sync en un lot idempotent dès que le réseau revient — zéro doublon", "sync", ORANGE_DARK),
    ]
    x0, y0, wrow = 4.15, 1.78, 8.55
    for i, (text, icon, col) in enumerate(feats):
        yy = y0 + i * 0.78
        sq = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, yy, 0.5, 0.5, fill=WHITE,
                    line=col, line_w=1.4, adj=0.3)
        cx, cy = x0 + 0.25, yy + 0.25
        if icon == "path":
            _shape(s, MSO_SHAPE.OVAL, cx - 0.14, cy - 0.14, 0.28, 0.28, fill=None,
                   line=col, line_w=1.6)
            _shape(s, MSO_SHAPE.OVAL, cx - 0.045, cy - 0.045, 0.09, 0.09, fill=col)
        elif icon == "warn":
            _icon_warn(s, cx, cy, s=0.36, color=col)
        elif icon == "offline":
            _shape(s, MSO_SHAPE.RECTANGLE, cx - 0.14, cy - 0.05, 0.28, 0.1, fill=col)
            _shape(s, MSO_SHAPE.RECTANGLE, cx - 0.012, cy + 0.05, 0.024, 0.06, fill=col)
            _shape(s, MSO_SHAPE.RECTANGLE, cx - 0.16, cy - 0.16, 0.03, 0.34,
                   fill=col, rot=45)
        else:
            _shape(s, MSO_SHAPE.UP_ARROW, cx - 0.08, cy - 0.14, 0.16, 0.28, fill=col)
        t = _txt(s, x0 + 0.72, yy + 0.02, wrow - 0.7, 0.55, [[(text, 12, INK, False)]],
                 line_spacing=1.08, anchor=MSO_ANCHOR.MIDDLE)
        ctx.add(sq, t)
    # flux de sync
    _txt(s, x0, 5.05, 8.5, 0.3, [[("LE PARCOURS D'UNE DONNÉE TERRAIN", 9.5, GREEN_DARK, True)]],
         spc=120)
    flow = ["Terrain sans réseau", "SQLite locale", "Lot idempotent", "API + PostGIS"]
    cw, ch, gap = 1.92, 0.5, 0.24
    for i, label in enumerate(flow):
        x = x0 + i * (cw + gap + 0.12)
        c = _chip(s, x, 5.42, cw, ch, label, fill=(GREEN_SOFT if i == 3 else CARD),
                  color=(GREEN_DARK if i == 3 else BODY), size=9.5,
                  line=(None if i == 3 else BORDER))
        ctx.add(c)
        if i < 3:
            a = _shape(s, MSO_SHAPE.RIGHT_ARROW, x + cw + 0.015, 5.42 + ch / 2 - 0.09,
                       0.21, 0.18, fill="C9CEC9")
            ctx.add(a)
    # chips stats
    stats = ["3 modes de relevé", "0 réseau requis", "1 lot de sync"]
    for i, st in enumerate(stats):
        c = _chip(s, x0 + i * 2.95, 6.18, 2.75, 0.44, st, fill=ORANGE_SOFT,
                  color=ORANGE_DARK, size=10)
        ctx.add(c)
    _footer(ctx)


def s_arch(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    # sources satellites (haut, centrées sur le socle)
    _txt(s, 3.52, 1.62, 6.0, 0.28, [[("SOURCES SATELLITE PUBLIQUES", 9.5, GREEN_DARK, True)]],
         spc=120, align=PP_ALIGN.CENTER)
    src = ["Sentinel-2 (Copernicus)", "Hansen / Global Forest Watch", "Digital Earth Africa"]
    sw, sh_, sy = 2.42, 0.46, 1.95
    x_start = 3.52 + (6.0 - (sw * 3 + 0.24)) / 2
    for i, name in enumerate(src):
        x = x_start + i * (sw + 0.12)
        c = _chip(s, x, sy, sw, sh_, name, fill=ORANGE_SOFT, color=ORANGE_DARK, size=9)
        arr = _shape(s, MSO_SHAPE.DOWN_ARROW, x + sw / 2 - 0.08, sy + sh_ + 0.05,
                     0.16, 0.28, fill="C9CEC9")
        ctx.add(c, arr)
    # entrées (gauche)
    inputs = [("App mobile", "relevés GPS hors-ligne, sync par lot"),
              ("Dashboard web", "consultation, KPIs, rapports")]
    for i, (t, d) in enumerate(inputs):
        y = 3.05 + i * 1.62
        c = _card(s, 0.62, y, 2.5, 1.4, fill=WHITE, line=BORDER)
        _txt(s, 0.82, y + 0.18, 2.1, 0.32, [[(t, 11.5, INK, True)]])
        _txt(s, 0.82, y + 0.52, 2.1, 0.75, [[(d, 9, BODY, False)]], line_spacing=1.1)
        arr = _shape(s, MSO_SHAPE.RIGHT_ARROW, 3.2, y + 0.5, 0.26, 0.36, fill="C9CEC9")
        ctx.add(c, arr)
    # socle (centre)
    box = _card(s, 3.52, 2.98, 6.0, 3.3, fill=WHITE, line=GREEN, line_w=1.5, adj=0.05)
    hdr = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 3.66, 3.10, 5.72, 0.44,
                 fill=GREEN_SOFT, adj=0.16)
    _set_text(hdr, [[("API Flask + PostGIS — le socle CacaoSat", 11.5, GREEN_DARK, True)]],
              align=PP_ALIGN.CENTER)
    ctx.add(box, hdr)
    mods = [
        ("Moteur satellite", "analyse Sentinel-2 / Hansen / DEA"),
        ("Scoring EUDR", "5 facteurs pondérés, score /100"),
        ("Rapports", "PDF + GeoJSON + empreinte SHA-256"),
        ("Alertes", "détection continue, notifications"),
    ]
    for i, (t, d) in enumerate(mods):
        x = 3.66 + (i % 2) * 2.92
        y = 3.66 + (i // 2) * 1.24
        c = _card(s, x, y, 2.8, 1.12, fill=CARD, line=None, shadow=False)
        _txt(s, x + 0.16, y + 0.12, 2.5, 0.3, [[(t, 11, INK, True)]])
        _txt(s, x + 0.16, y + 0.44, 2.5, 0.6, [[(d, 8.5, BODY, False)]], line_spacing=1.08)
        ctx.add(c)
    # sorties (droite)
    outs = [("Certificat", "PDF + GeoJSON exportables"),
            ("Tableaux de bord", "KPIs conformité en direct"),
            ("Alertes précoces", "SMS / e-mail, acquittement")]
    for i, (t, d) in enumerate(outs):
        y = 3.05 + i * 1.12
        arr = _shape(s, MSO_SHAPE.RIGHT_ARROW, 9.6, y + 0.28, 0.26, 0.36, fill="C9CEC9")
        c = _card(s, 9.94, y, 2.78, 0.96, fill=WHITE, line=BORDER)
        _txt(s, 10.14, y + 0.1, 2.4, 0.3, [[(t, 11, INK, True)]])
        _txt(s, 10.14, y + 0.4, 2.4, 0.5, [[(d, 8.5, BODY, False)]], line_spacing=1.05)
        ctx.add(arr, c)
    # bandeau bas
    chips = ["34 routes API", "JWT + audit", "PostGIS", "100 % open source", "Mock déterministe"]
    cw, gap = 2.28, 0.14
    x0 = 0.62 + (12.1 - (cw * 5 + gap * 4)) / 2
    for i, label in enumerate(chips):
        c = _chip(s, x0 + i * (cw + gap), 6.5, cw, 0.42, label, fill=CARD,
                  color=BODY, size=9.5, line=BORDER, bold=False)
        ctx.add(c)
    _footer(ctx)


def s_scoring(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    bottom = _browser_frame(ctx, 0.62, 1.62, 7.35, SHOTS / "parcel-detail.jpg",
                            "cacaosat.ci/parcelles/COOPCA-GUIGLO-0004")
    cap = _txt(s, 0.62, bottom + 0.12, 7.35, 0.3,
               [[("Détail parcelle : carte satellite, jauge de score, facteurs, série NDVI",
                  9.5, MUTED, False)]])
    ctx.add(cap)
    # droite : les 5 facteurs
    x0, w = 8.35, 4.35
    ttl = _txt(s, x0, 1.72, w, 0.35, [[("Les 5 facteurs du score EUDR", 14, INK, True)]])
    ctx.add(ttl)
    factors = [
        ("Déforestation post-2020", 45, ORANGE),
        ("Recouvrement aire protégée", 20, GREEN),
        ("Tendance NDVI / dégradation", 15, GREEN),
        ("Complétude des données", 10, GREEN_DARK),
        ("Qualité du relevé GPS", 10, GREEN_DARK),
    ]
    y = 2.22
    for label, val, col in factors:
        t = _txt(s, x0, y, w - 0.9, 0.26, [[(label, 10.5, INK, False)]])
        v = _txt(s, x0 + w - 0.95, y - 0.02, 0.95, 0.28,
                 [[(f"{val} pts", 10.5, col, True)]], align=PP_ALIGN.RIGHT)
        track = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, y + 0.3, w, 0.14,
                       fill="EDEFEA", adj=0.5)
        fill_w = max(0.18, w * val / 45)
        bar = _shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x0, y + 0.3, fill_w, 0.14,
                     fill=col, adj=0.5)
        ctx.add(t, v, track, bar)
        y += 0.63
    total = _chip(s, x0, 5.5, 2.3, 0.5, "Score total / 100", fill=ORANGE,
                  color="FFFFFF", size=11)
    ctx.add(total)
    note = _card(s, x0, 6.14, w, 0.78, fill=GREEN_SOFT, line=None)
    _set_text(note, [[("Chaque point est justifié : le score n'est pas une boîte noire.",
                       10.5, GREEN_DARK, True)]], align=PP_ALIGN.LEFT, line_spacing=1.1)
    note.text_frame.margin_left = Inches(0.16)
    ctx.add(note)
    _footer(ctx)


def s_dashboard(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    bottom = _browser_frame(ctx, 0.62, 1.58, 7.55, SHOTS / "dashboard.jpg",
                            "cacaosat.ci — tableau de bord coopérative")
    cap = _txt(s, 0.62, bottom + 0.1, 7.55, 0.3,
               [[("Carte satellite Esri, statuts par couleur, alertes acquittables en un clic",
                  9.5, MUTED, False)]])
    ctx.add(cap)
    # KPIs droite
    x0, w = 8.6, 4.1
    kpis = [
        ("21", "parcelles suivies dans la démo", GREEN),
        ("72 ha", "de surface analysée en continu", ORANGE),
        ("100 %", "de couverture d'analyse satellite", GREEN_DARK),
    ]
    for i, (num, label, col) in enumerate(kpis):
        y = 1.72 + i * 1.35
        c = _card(s, x0, y, w, 1.18, fill=WHITE, line=BORDER)
        _shape(s, MSO_SHAPE.RECTANGLE, x0 + 0.24, y + 0.24, 0.36, 0.06, fill=col)
        _txt(s, x0 + 0.24, y + 0.34, w - 0.45, 0.5, [[(num, 22, col, True)]])
        _txt(s, x0 + 0.24, y + 0.82, w - 0.45, 0.3, [[(label, 9.5, BODY, False)]])
        ctx.add(c)
    band = _card(s, x0, 5.85, w, 0.85, fill=GREEN_SOFT, line=None)
    _set_text(band, [[("Un outil de niveau national,", 10.5, INK, True)],
                     [("entre les mains d'une coopérative.", 10.5, INK, True)]],
              align=PP_ALIGN.LEFT, line_spacing=1.15)
    band.text_frame.margin_left = Inches(0.16)
    ctx.add(band)
    _footer(ctx)


def s_certificate(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    # --- certificat (gauche)
    cx, cy, cw, chh = 0.62, 1.62, 5.15, 5.15
    card = _card(s, cx, cy, cw, chh, fill=WHITE, line=BORDER, adj=0.045)
    ctx.add(card)
    _shape(s, MSO_SHAPE.RECTANGLE, cx + 0.02, cy + 0.02, cw - 0.04, 0.1, fill=ORANGE)
    _shape(s, MSO_SHAPE.RECTANGLE, cx + cw / 3 + 0.02, cy + 0.02, cw / 3 - 0.04, 0.1,
           fill=GREY_BAR)
    _shape(s, MSO_SHAPE.RECTANGLE, cx + 2 * cw / 3 + 0.02, cy + 0.02, cw / 3 - 0.04, 0.1,
           fill=GREEN)
    _txt(s, cx + 0.35, cy + 0.34, cw - 0.7, 0.26,
         [[("RAPPORT OFFICIEL DE CONFORMITÉ", 8.5, GREEN_DARK, True)]], spc=120)
    _txt(s, cx + 0.35, cy + 0.62, cw - 1.3, 0.62,
         [[("Certificat de conformité EUDR", 16, INK, True)]])
    _txt(s, cx + 0.35, cy + 1.18, cw - 0.7, 0.28,
         [[("Coopérative COOPCA-GUIGLO · 21 parcelles · 72 ha", 9.5, MUTED, False)]])
    _shape(s, MSO_SHAPE.RECTANGLE, cx + 0.35, cy + 1.55, cw - 0.7, 0.016, fill=BORDER)
    rows = [
        "Synthèse : 12 conformes · 4 à vérifier · 5 non conformes",
        "Carte des parcelles avec périmètres GPS",
        "Méthodologie satellite et sources citées",
    ]
    for i, row in enumerate(rows):
        y = cy + 1.75 + i * 0.5
        _shape(s, MSO_SHAPE.OVAL, cx + 0.38, y + 0.05, 0.12, 0.12, fill=GREEN)
        _txt(s, cx + 0.62, y - 0.02, cw - 1.1, 0.4, [[(row, 9.5, BODY, False)]])
    seal = _shape(s, MSO_SHAPE.DONUT, cx + cw - 1.28, cy + 0.52, 0.92, 0.92,
                  fill=GREEN, adj=0.18)
    inner = _shape(s, MSO_SHAPE.OVAL, cx + cw - 1.13, cy + 0.67, 0.62, 0.62, fill=WHITE)
    _txt(s, cx + cw - 1.13, cy + 0.76, 0.62, 0.45, [[("✓", 20, GREEN_DARK, True)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    ctx.add(seal, inner)
    sha = _chip(s, cx + 0.35, cy + 3.45, 2.6, 0.36, "SHA-256 · anti-falsification",
                fill=INK, color="FFFFFF", size=8.5)
    ctx.add(sha)
    _txt(s, cx + 0.35, cy + 4.05, cw - 0.7, 0.55,
         [[("Généré en quelques minutes — export PDF + GeoJSON au gabarit des "
            "exportateurs.", 9.5, MUTED, False)]], line_spacing=1.15)
    _txt(s, cx + 0.35, cy + 4.62, cw - 0.7, 0.3,
         [[("Préambule légal · tableau par producteur · audit trail", 8.5, MUTED, False)]])
    # --- alertes (droite)
    x0, w = 6.25, 6.45
    ttl = _txt(s, x0, 1.72, w, 0.35, [[("Le système continue de veiller", 14, INK, True)]])
    ctx.add(ttl)
    flow = [
        ("Passage satellite", "chaque nouvelle image Sentinel-2 est analysée", ORANGE, "satellite"),
        ("Détection", "perte de couvert ou empiètement d'aire protégée", RED, "warn"),
        ("Alerte coopérative", "notification + acquittement tracé dans l'audit", GREEN, "check"),
    ]
    icons = {"satellite": _icon_satellite, "warn": _icon_warn, "check": _icon_check}
    for i, (t, d, col, icon) in enumerate(flow):
        y = 2.22 + i * 1.12
        c = _card(s, x0, y, w, 0.96, fill=WHITE, line=BORDER)
        circ = _shape(s, MSO_SHAPE.OVAL, x0 + 0.2, y + 0.17, 0.62, 0.62,
                      fill=(_mix(col, "FFFFFF", 0.82)))
        icons[icon](s, x0 + 0.51, y + 0.48, s=0.42, color=col)
        _txt(s, x0 + 1.05, y + 0.14, w - 1.3, 0.3, [[(t, 11.5, INK, True)]])
        _txt(s, x0 + 1.05, y + 0.45, w - 1.3, 0.4, [[(d, 10, BODY, False)]])
        ctx.add(c, circ)
        if i < 2:
            arr = _shape(s, MSO_SHAPE.DOWN_ARROW, x0 + 0.38, y + 0.97, 0.18, 0.14,
                         fill="C9CEC9")
            ctx.add(arr)
    band = _card(s, x0, 5.72, w, 1.05, fill=ORANGE_SOFT, line=None)
    _txt(s, x0 + 0.35, 5.92, w - 0.6, 0.4,
         [[("Des semaines de paperasse → ", 14, INK, True),
           ("quelques minutes.", 14, ORANGE_DARK, True)]])
    _txt(s, x0 + 0.35, 6.34, w - 0.6, 0.3,
         [[("Délai de production du dossier de conformité complet.", 9.5, BODY, False)]])
    ctx.add(band)
    _footer(ctx)


def s_impact(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    cards = [
        ("Économique", "Accès au marché UE sécurisé — délai et coût de conformité réduits.",
         "coin", ORANGE, ORANGE_SOFT),
        ("Social", "Un outil direct pour les petites coopératives, sans intermédiaire coûteux.",
         "people", GREEN, GREEN_SOFT),
        ("Environnemental", "Suivi continu du couvert forestier autour des zones de production.",
         "tree", GREEN_DARK, GREEN_SOFT),
        ("Institutionnel", "Une base nationale consolidée pour le Conseil du Café-Cacao.",
         "building", ORANGE_DARK, ORANGE_SOFT),
    ]
    icons = {"coin": _icon_coin, "people": _icon_people, "tree": _icon_tree,
             "building": _icon_building}
    w, h = 5.9, 2.42
    for i, (title, desc, icon, col, soft) in enumerate(cards):
        x = 0.62 + (i % 2) * (w + 0.3)
        y = 1.78 + (i // 2) * (h + 0.32)
        c = _card(s, x, y, w, h, fill=WHITE, line=BORDER)
        ctx.add(c)
        circ = _shape(s, MSO_SHAPE.OVAL, x + 0.32, y + 0.36, 1.05, 1.05, fill=soft)
        icons[icon](s, x + 0.32 + 0.525, y + 0.36 + 0.525, s=0.78, color=col)
        ctx.add(circ)
        _txt(s, x + 1.66, y + 0.42, w - 2.0, 0.4, [[(title, 15.5, INK, True)]])
        _txt(s, x + 1.66, y + 0.88, w - 2.0, 1.3, [[(desc, 11, BODY, False)]],
             line_spacing=1.25)
    _footer(ctx)


def s_proof(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    # gauche : graphique délai
    c = _card(s, 0.62, 1.72, 6.4, 3.35, fill=WHITE, line=BORDER)
    ctx.add(c)
    _txt(s, 0.92, 1.92, 5.8, 0.3,
         [[("Temps de production du dossier de conformité", 12.5, INK, True)]])
    _pic(s, GEN / "delai.png", 0.85, 2.35, w=5.95)
    band = _card(s, 0.62, 5.35, 6.4, 1.4, fill=GREEN_SOFT, line=None)
    _txt(s, 0.95, 5.56, 5.9, 0.4,
         [[("Mock déterministe des services satellite", 12, GREEN_DARK, True)]])
    _txt(s, 0.95, 5.95, 5.9, 0.65,
         [[("Démo reproductible ; l'architecture est prête à brancher les flux "
            "réels sans changement de contrat.", 10, BODY, False)]], line_spacing=1.15)
    ctx.add(band)
    # droite : stack + preuves
    x0, w = 7.4, 5.3
    _txt(s, x0, 1.78, w, 0.32, [[("UNE STACK LIBRE, TESTÉE, DÉPLOYABLE", 10, GREEN_DARK, True)]],
         spc=110)
    stack = ["Flask 3 + PostGIS", "React 18 + Vite", "Flutter hors-ligne",
             "Docker Compose", "GitHub Actions CI", "ReportLab (PDF)"]
    cw, chh = 2.62, 0.5
    for i, name in enumerate(stack):
        x = x0 + (i % 2) * (cw + 0.18)
        y = 2.2 + (i // 2) * (chh + 0.16)
        chip = _chip(s, x, y, cw, chh, name, fill=CARD, color=INK, size=10.5,
                     line=BORDER, bold=False)
        ctx.add(chip)
    tests = [("76 tests backend · 84 % de couverture", GREEN_SOFT, GREEN_DARK),
             ("Smoke e2e 10/10 · CI verte sur 3 composants", GREEN_SOFT, GREEN_DARK),
             ("34 routes API · JWT + journal d'audit", ORANGE_SOFT, ORANGE_DARK)]
    for i, (t, fill, col) in enumerate(tests):
        y = 4.35 + i * 0.62
        c = _chip(s, x0, y, w, 0.5, t, fill=fill, color=col, size=10)
        ctx.add(c)
    deploy = _card(s, x0, 6.35, w, 0.72, fill=INK, line=None, adj=0.16)
    _set_text(deploy, [[("Déployable en une commande :  ", 11.5, "FFFFFF", True),
                        ("docker compose up", 11.5, "7BD9A2", True)]],
              align=PP_ALIGN.CENTER)
    ctx.add(deploy)
    _footer(ctx)


def s_roadmap(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _header(ctx, sl.kicker, sl.title)
    # ligne de temps
    line_y = 2.55
    _shape(s, MSO_SHAPE.RECTANGLE, 0.95, line_y, 11.45, 0.035, fill=BORDER)
    start = _chip(s, 0.62, 1.78, 2.6, 0.44, "Sept. 2026 · Ivoire Spacehack",
                  fill=GREEN_SOFT, color=GREEN_DARK, size=9)
    ctx.add(start)
    phases = [
        ("FIN 2026", "Pilote terrain",
         "Une coopérative volontaire de la région du Cavally : relevés réels, "
         "feedback des agents, premières analyses satellite en production.", ORANGE),
        ("2027", "Partenariat institutionnel",
         "Validation avec le Conseil du Café-Cacao en conditions réelles ; "
         "interconnexion avec les exportateurs.", GREEN),
        ("2028+", "Échelle nationale",
         "Déploiement progressif sur les principales zones de production ; "
         "base nationale de conformité.", GREEN_DARK),
    ]
    w = 3.75
    xs = [0.62, 4.79, 8.96]
    for (date, title, desc, col), x in zip(phases, xs):
        dot = _shape(s, MSO_SHAPE.OVAL, x + w / 2 - 0.11, line_y - 0.095, 0.22, 0.22,
                     fill=col, line="FFFFFF", line_w=1.5)
        c = _card(s, x, 3.0, w, 2.6, fill=WHITE, line=BORDER)
        bar = _shape(s, MSO_SHAPE.RECTANGLE, x + 0.26, 3.24, 0.4, 0.06, fill=col)
        _txt(s, x + 0.26, 3.4, w - 0.5, 0.3, [[(date, 10.5, col, True)]], spc=110)
        _txt(s, x + 0.26, 3.72, w - 0.5, 0.4, [[(title, 14.5, INK, True)]])
        _txt(s, x + 0.26, 4.2, w - 0.5, 1.25, [[(desc, 10, BODY, False)]],
             line_spacing=1.2)
        ctx.add(dot, c, bar)
    band = _card(s, 0.62, 6.0, 12.1, 0.78, fill=CARD, line=None, shadow=False)
    _set_text(band, [[("Objectif : faire de la conformité EUDR un avantage pour la "
                       "filière ivoirienne, pas une barrière.", 12, INK, True)]],
              align=PP_ALIGN.CENTER)
    ctx.add(band)
    _footer(ctx)


def s_closing(ctx: Ctx, sl: Slide) -> None:
    s = ctx.slide
    _shape(s, MSO_SHAPE.OVAL, -1.3, -1.5, 3.6, 3.6, fill=ORANGE_SOFT)
    _shape(s, MSO_SHAPE.OVAL, 11.3, 5.6, 2.6, 2.6, fill=GREEN_SOFT)
    _pic(s, LOGO, 5.87, 0.75, w=1.6)
    stmt = _txt(s, 1.2, 2.85, 10.93, 1.15, [[(sl.title, 30, INK, True)]],
                align=PP_ALIGN.CENTER, line_spacing=1.05)
    ctx.add(stmt)
    sub = _txt(s, 2.2, 4.1, 8.93, 0.65, [[(sl.subtitle, 13.5, BODY, False)]],
               align=PP_ALIGN.CENTER, line_spacing=1.15)
    ctx.add(sub)
    seg1 = _shape(s, MSO_SHAPE.RECTANGLE, 5.87, 4.98, 0.78, 0.06, fill=ORANGE)
    seg2 = _shape(s, MSO_SHAPE.RECTANGLE, 6.65, 4.98, 0.78, 0.06, fill=GREY_BAR)
    seg3 = _shape(s, MSO_SHAPE.RECTANGLE, 7.43, 4.98, 0.78, 0.06, fill=GREEN)
    ctx.add(seg1, seg2, seg3)
    repo = _txt(s, 1.2, 5.35, 10.93, 0.35,
                [[("github.com/daniel10027/CacaoSat", 13, GREEN_DARK, True)]],
                align=PP_ALIGN.CENTER)
    ctx.add(repo)
    team = _txt(s, 1.2, 5.78, 10.93, 0.3,
                [[("Akandji Timothé · Elie Konan · Daniel Guedegbe — Ivoire Spacehack 2026",
                   10.5, MUTED, False)]], align=PP_ALIGN.CENTER)
    ctx.add(team)
    _ribbon(s, 7.41, h=0.09, full=True)


# ================================================================= animations
def _set_transition(slide) -> None:
    xml = f'<p:transition {nsdecls("p")} spd="med"><p:fade/></p:transition>'
    slide.element.append(parse_xml(xml))


def _apply_anim(ctx: Ctx, stagger: int = 130) -> None:
    """Fondu + apparition progressive : 1er clic déclenche toute la cascade."""
    shapes = [sh for sh in ctx.anim if sh is not None]
    if not shapes:
        return
    # IDs croissants dans l'ordre du document : groupe de clic d'abord (3, 4),
    # puis chaque effet (3 ids chacun).
    click_id, group_id = 3, 4
    uid = 5
    effects = []
    for i, sh in enumerate(shapes):
        spid = sh.shape_id
        nid = uid
        n_set, n_anim = uid + 1, uid + 2
        uid += 3
        node_type = "clickEffect" if i == 0 else "afterEffect"
        delay = 0 if i == 0 else stagger
        effects.append(
            f'<p:par><p:cTn id="{nid}" presetID="10" presetClass="entr" '
            f'presetSubtype="0" fill="hold" grpId="0" nodeType="{node_type}">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
            f'<p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{n_set}" dur="1" fill="hold">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr>'
            f'<p:cTn id="{n_anim}" dur="380"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'</p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>'
        )
    xml = (
        f'<p:timing {nsdecls("p", "a")}><p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
        f'<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        f'<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        f'<p:par><p:cTn id="{click_id}" fill="hold">'
        f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
        f'<p:par><p:cTn id="{group_id}" fill="hold">'
        f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        f'{"".join(effects)}'
        f'</p:childTnLst></p:cTn></p:par>'
        f'</p:childTnLst></p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl>'
        f'</p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl>'
        f'</p:cond></p:nextCondLst>'
        f'</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
    )
    ctx.slide.element.append(parse_xml(xml))


# ================================================================= assemblage
BUILDERS = {
    "cover": s_cover,
    "eudr": s_eudr,
    "problem": s_problem,
    "sources": s_sources,
    "pipeline": s_pipeline,
    "mobile": s_mobile,
    "arch": s_arch,
    "scoring": s_scoring,
    "dashboard": s_dashboard,
    "certificate": s_certificate,
    "impact": s_impact,
    "proof": s_proof,
    "roadmap": s_roadmap,
    "closing": s_closing,
}


def main() -> None:
    global _CTX
    graphics.main()
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    for i, sl in enumerate(DECK):
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # vierge
        _bg(slide)
        ctx = Ctx(slide, i)
        _CTX = ctx
        BUILDERS[sl.visual](ctx, sl)
        _CTX = None
        _set_transition(slide)
        _apply_anim(ctx)
        slide.notes_slide.notes_text_frame.text = sl.notes
    cp = prs.core_properties
    cp.title = "CacaoSat — Pitch Ivoire Spacehack 2026"
    cp.author = "Équipe CacaoSat"
    cp.subject = "Traçabilité géospatiale du cacao ivoirien (EUDR)"
    prs.save(OUT)
    print(f"→ {OUT}  ({len(DECK)} slides, animées)")


if __name__ == "__main__":
    main()