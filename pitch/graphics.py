"""Génère les images du deck (pitch/assets/gen/) — matplotlib + PIL.

- map_satellite.png : vue satellite stylisée avec parcelles colorées par statut
  (utilisée dans le mockup téléphone)
- ndvi.png : série NDVI Sentinel-2 avec coupe détectée annotée
- delai.png : comparatif « à la main » vs « avec CacaoSat »

Fond blanc, charte Côte d'Ivoire. Régénéré par build_pptx.py au besoin.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

GEN = Path(__file__).parent / "assets" / "gen"

INK = "#13251C"
MUTED = "#6B7A70"
GRID = "#E3E8E4"
ORANGE = "#FF7A00"
GREEN = "#00A651"
GREEN_DARK = "#007A3D"
RED = "#D9482B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK,
    "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.titlecolor": INK,
})


# ---------------------------------------------------------------- carte satellite
def _terrain(w: int = 1600, h: int = 900) -> Image.Image:
    """Fond « vue satellite » : patchs de végétation, chemins, texture."""
    rng = np.random.default_rng(42)
    small = rng.random((14, 9))
    img = Image.fromarray((small * 255).astype("uint8")).resize((w, h), Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(6))
    arr = np.asarray(img).astype(float) / 255.0

    # dégradé de teintes vegetation / sol nu
    forest = np.array([26, 62, 38]) / 255.0      # forêt dense
    grove = np.array([64, 104, 52]) / 255.0      # bosquets/cacaoyères
    field = np.array([118, 138, 70]) / 255.0     # cultures claires
    bare = np.array([148, 124, 84]) / 255.0      # sols nus / pistes

    t = arr
    t3 = t[..., None]
    rgb = np.where(t3 < 0.35, forest, grove)
    rgb = np.where(((t >= 0.35) & (t < 0.6))[..., None], field, rgb)
    rgb = np.where((t >= 0.6)[..., None], bare, rgb)
    rgb = np.clip(rgb + (rng.random((h, w, 1)) - 0.5) * 0.05, 0, 1)
    return Image.fromarray((rgb * 255).astype("uint8"))


def map_satellite() -> Image.Image:
    w, h = 1600, 900
    img = _terrain(w, h).convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # parcelles : (polygone, couleur, alpha)
    parcels = [
        ([(190, 640), (330, 590), (420, 680), (360, 800), (200, 780)], (0, 166, 81), 190),
        ([(470, 300), (640, 260), (700, 400), (560, 470), (460, 420)], (0, 166, 81), 190),
        ([(760, 560), (950, 520), (1010, 660), (860, 730), (740, 690)], (255, 122, 0), 200),
        ([(1050, 250), (1230, 220), (1290, 360), (1140, 430), (1030, 380)], (0, 166, 81), 190),
        ([(1290, 560), (1460, 540), (1500, 680), (1360, 750), (1260, 680)], (217, 72, 43), 200),
        ([(620, 90), (790, 70), (830, 190), (680, 240), (590, 180)], (255, 122, 0), 200),
    ]
    for pts, color, alpha in parcels:
        d.polygon(pts, fill=color + (alpha,), outline=(255, 255, 255, 255), width=5)
    # rivière + piste
    d.line([(60, 120), (300, 260), (520, 330), (760, 470), (980, 520), (1240, 620),
            (1520, 700)], fill=(72, 110, 130, 235), width=14, joint="curve")
    d.line([(820, 880), (900, 700), (980, 560), (1120, 470), (1300, 420)],
           fill=(196, 168, 120, 210), width=9, joint="curve")

    img = Image.alpha_composite(img, overlay)
    # léger voile + vignette pour lisibilité des overlays blancs
    veil = Image.new("RGBA", (w, h), (10, 30, 20, 36))
    img = Image.alpha_composite(img, veil)
    out = GEN / "map_satellite.png"
    img.convert("RGB").save(out, quality=92)
    return img


# ---------------------------------------------------------------- NDVI
def ndvi() -> None:
    rng = np.random.default_rng(7)
    n = 80
    t = np.arange(n)
    base = 0.68 + 0.05 * np.sin(t / 6.3) + rng.normal(0, 0.018, n)
    # coupe détectée ~ t=38 (août 2023) puis repousse partielle
    dip = np.where((t >= 38) & (t < 44), 0.30 - (t - 38) * 0.055, 0.0)
    y = np.clip(base - dip, 0.30, 0.95)
    y[t >= 44] = np.clip(y[t >= 44] + 0.06, 0, 1)

    years = 2020 + t / 12.0
    xticks = np.arange(2020, 2027)
    xlabels = [f"{y}" for y in xticks]

    fig, ax = plt.subplots(figsize=(6.9, 3.05), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.axvspan(years[37], years[44], color=RED, alpha=0.07)
    ax.plot(years, y, color=GREEN_DARK, lw=2.4, solid_capstyle="round", zorder=3)
    ax.scatter([years[38]], [y[38]], s=42, color=RED, zorder=4,
               edgecolor="white", linewidth=1.2)

    ax.annotate("Coupe détectée — chute NDVI",
                xy=(years[38], y[38]), xytext=(years[42], 0.94),
                fontsize=10.5, color=RED, fontweight="bold",
                arrowprops={"arrowstyle": "->", "color": RED, "lw": 1.4})

    ax.set_ylim(0.25, 1.0)
    ax.set_xlim(2020 - 0.1, 2026 + 0.45)
    ax.set_xticks(xticks + 0.4)
    ax.set_xticklabels([f"{y}" for y in range(2020, 2027)], fontsize=10)
    ax.set_ylabel("NDVI (Sentinel-2)", fontsize=10, color=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)
    fig.tight_layout(pad=0.4)
    fig.savefig(GEN / "ndvi.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- délai
def delai() -> None:
    fig, ax = plt.subplots(figsize=(6.1, 2.6), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    rows = [
        ("À la main aujourd'hui", 1.00, "#AEB8B1", "4–8 semaines"),
        ("Avec CacaoSat", 0.045, GREEN, "≈ 10 minutes"),
    ]
    for i, (label, width, color, value) in enumerate(rows):
        y = 1 - i
        ax.barh(y, width, height=0.42, color=color, edgecolor="none", zorder=3)
        ax.text(-0.015, y + 0.55, label, fontsize=13, color=INK,
                fontweight="bold", ha="left", va="center")
        ax.text(width + 0.02, y, value, fontsize=13,
                color=(GREEN_DARK if i == 1 else MUTED), fontweight="bold",
                ha="left", va="center")

    ax.set_xlim(-0.01, 1.24)
    ax.set_ylim(-0.45, 1.85)
    ax.axis("off")
    fig.tight_layout(pad=0.2)
    fig.savefig(GEN / "delai.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- picto score donut
def score_donut() -> None:
    """Donut 30 % zone protégée (pour la carte stat EUDR)."""
    fig, ax = plt.subplots(figsize=(2.1, 2.1), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    vals = [30, 70]
    ax.pie(vals, startangle=90, counterclock=False,
           colors=[ORANGE, "#EDEFEA"],
           wedgeprops={"width": 0.32, "edgecolor": "white", "linewidth": 2})
    ax.text(0, 0.08, "30 %", ha="center", va="center", fontsize=17,
            fontweight="bold", color=INK)
    ax.set(aspect="equal")
    fig.tight_layout(pad=0.05)
    fig.savefig(GEN / "donut_zone.png", facecolor="white", transparent=True)
    plt.close(fig)


def main() -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    map_satellite()
    ndvi()
    delai()
    score_donut()
    print(f"→ images générées dans {GEN}")


if __name__ == "__main__":
    main()