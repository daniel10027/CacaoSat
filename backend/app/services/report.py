"""Génération du rapport / certificat de conformité EUDR (PDF + export GeoJSON)."""

from __future__ import annotations

import hashlib
import io
import json
import logging
import math
from datetime import UTC, date, datetime

from geoalchemy2.shape import to_shape
from PIL import Image as PILImage
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.graphics.shapes import Image as RLImage
from reportlab.graphics.shapes import Polygon as RLPolygon
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import joinedload, selectinload

from app.extensions import db
from app.models.compliance_report import ComplianceReport
from app.models.cooperative import Cooperative
from app.models.parcel import Parcel
from app.services import basemap as basemap_service
from app.storage import put_object

log = logging.getLogger(__name__)

CI_ORANGE = colors.HexColor("#FF7A00")
CI_GREEN = colors.HexColor("#00A651")
STATUS_COLORS = {
    "compliant": colors.HexColor("#00A651"),
    "at_risk": colors.HexColor("#E8A33D"),
    "non_compliant": colors.HexColor("#C0392B"),
    "unassessed": colors.HexColor("#9AA0A6"),
}
EUDR_CUTOFF = "31 décembre 2020"

DATA_SOURCES = [
    ("Sentinel-2 (Copernicus)", "Imagerie optique 10 m — séries temporelles NDVI"),
    ("Hansen / Global Forest Watch", "Couvert arboré 2000 et perte annuelle (référence fin 2020)"),
    ("Digital Earth Africa", "Suivi de la dégradation des terres"),
    ("Relevés terrain (coopérative)", "Polygones GPS des parcelles, identité des producteurs"),
]


def _now() -> datetime:
    return datetime.now(UTC)


def _collect_rows(parcels: list[Parcel]) -> list[dict]:
    rows = []
    for p in parcels:
        score = p.latest_score
        analysis = p.latest_analysis
        top_reason = ""
        if score:
            worst = min(score.factors, key=lambda f: f["points"] / max(f["weight"], 1))
            top_reason = worst["explanation"]
        rows.append(
            {
                "code": p.code,
                "producer_name": p.producer.full_name if p.producer else "—",
                "producer_id": str(p.producer_id) if p.producer_id else "",
                "national_id": p.producer.national_id if p.producer and p.producer.national_id else "",
                "area_ha": round(float(p.area_ha or 0), 3),
                "planting_year": p.planting_year,
                "collected_at": p.collected_at.date().isoformat() if p.collected_at else "",
                "score": round(score.score, 1) if score else None,
                "risk_level": score.risk_level.value if score else None,
                "eudr_status": score.eudr_status.value if score else "unassessed",
                "deforestation_detected": bool(analysis and analysis.deforestation_detected),
                "forest_loss_ha": round(analysis.forest_loss_ha, 3) if analysis else 0.0,
                "protected_overlap_ha": round(analysis.protected_area_overlap_ha, 3) if analysis else 0.0,
                "top_reason": top_reason,
                "geometry": to_shape(p.geometry),
            }
        )
    rows.sort(key=lambda r: r["code"])
    return rows


def _summary(rows: list[dict]) -> dict:
    def n(status: str) -> int:
        return sum(1 for r in rows if r["eudr_status"] == status)

    return {
        "parcels_total": len(rows),
        "area_ha_total": round(sum(r["area_ha"] for r in rows), 2),
        "compliant": n("compliant"),
        "at_risk": n("at_risk"),
        "non_compliant": n("non_compliant"),
        "unassessed": n("unassessed"),
        "deforestation_events": sum(1 for r in rows if r["deforestation_detected"]),
        "high_risk_area_ha": round(
            sum(r["area_ha"] for r in rows if r["risk_level"] == "high"), 2
        ),
    }


def _content_hash(coop_code: str, period: tuple, rows: list[dict], summary: dict) -> str:
    payload = {
        "cooperative": coop_code,
        "period": [str(period[0]), str(period[1])],
        "summary": summary,
        "rows": [
            {k: r[k] for k in ("code", "producer_id", "area_ha", "score", "eudr_status")}
            for r in rows
        ],
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _geojson(rows: list[dict], coop: Cooperative) -> bytes:
    features = []
    for r in rows:
        features.append(
            {
                "type": "Feature",
                "geometry": r["geometry"].__geo_interface__,
                "properties": {
                    "PlotId": r["code"],
                    "ProducerName": r["producer_name"],
                    "ProducerId": r["producer_id"],
                    "NationalId": r["national_id"],
                    "Area": r["area_ha"],
                    "AreaUnit": "ha",
                    "ProductionPlace": coop.name,
                    "ProductionDate": r["collected_at"],
                    "Commodity": "cocoa",
                    "eudr_status": r["eudr_status"],
                    "risk_level": r["risk_level"],
                    "score": r["score"],
                    "deforestation_after_2020": r["deforestation_detected"],
                    "protected_area_overlap_ha": r["protected_overlap_ha"],
                },
            }
        )
    fc = {
        "type": "FeatureCollection",
        "name": f"cacaosat_eudr_{coop.code}",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }
    return json.dumps(fc, ensure_ascii=False, indent=2).encode("utf-8")


def _merc_y(lat: float) -> float:
    """Ordonnée Web Mercator normalisée (0 au pôle nord, 1 au pôle sud)."""
    lat = max(min(lat, basemap_service.MAX_LAT), -basemap_service.MAX_LAT)
    s = math.sin(math.radians(lat))
    return 0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)


def _merc_y_inv(y: float) -> float:
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))


def _framed_bbox(geoms: list, aspect: float) -> tuple[float, float, float, float]:
    """Emprise (west, south, east, north) marginée et mise au ratio du cadre.

    L'ajustement se fait en espace Mercator, celui des tuiles : l'image remplit
    donc le cadre sans déformation, et les parcelles restent centrées.
    """
    minx = min(g.bounds[0] for g in geoms)
    miny = min(g.bounds[1] for g in geoms)
    maxx = max(g.bounds[2] for g in geoms)
    maxy = max(g.bounds[3] for g in geoms)
    # Marge relative, avec un plancher absolu : une coopérative réduite à une
    # seule parcelle aurait sinon une emprise quasi nulle et un zoom absurde.
    dx = max((maxx - minx) * 0.15, 0.0012)
    dy = max((maxy - miny) * 0.15, 0.0012)

    x0, x1 = (minx - dx + 180) / 360, (maxx + dx + 180) / 360
    y0, y1 = _merc_y(maxy + dy), _merc_y(miny - dy)  # y0 (nord) < y1 (sud)
    w, h = x1 - x0, y1 - y0
    if w / h < aspect:
        target = h * aspect
        cx = (x0 + x1) / 2
        x0, x1 = cx - target / 2, cx + target / 2
    else:
        target = w / aspect
        cy = (y0 + y1) / 2
        y0, y1 = cy - target / 2, cy + target / 2
    return (x0 * 360 - 180, _merc_y_inv(y1), x1 * 360 - 180, _merc_y_inv(y0))


def _scale_bar(d: Drawing, metres_per_point: float, width: float, on_imagery: bool) -> None:
    """Échelle graphique : sans elle, une carte sans repère n'est pas lisible."""
    if metres_per_point <= 0:
        return
    ink = colors.white if on_imagery else colors.HexColor("#333333")
    for metres in (5000, 2000, 1000, 500, 200, 100):
        length = metres / metres_per_point
        if length <= width * 0.3:
            break
    else:  # pragma: no cover — emprise extrêmement réduite
        return
    x, y = 8, 8
    d.add(Line(x, y, x + length, y, strokeColor=ink, strokeWidth=1.2))
    for end in (x, x + length):
        d.add(Line(end, y - 2.5, end, y + 2.5, strokeColor=ink, strokeWidth=1.2))
    label = f"{metres / 1000:g} km" if metres >= 1000 else f"{metres:g} m"
    d.add(String(x, y + 4.5, label, fontSize=7, fillColor=ink))


def _map_drawing(rows: list[dict], width=170 * mm, height=120 * mm) -> Drawing:
    d = Drawing(width, height)
    geoms = [r["geometry"] for r in rows if r["geometry"] and not r["geometry"].is_empty]
    if not geoms:
        d.add(String(10, height / 2, "Aucune géométrie à afficher", fontSize=9))
        return d

    west, south, east, north = _framed_bbox(geoms, width / height)
    try:
        bm = basemap_service.build((west, south, east, north))
    except Exception as exc:  # noqa: BLE001 — un fond absent ne doit jamais bloquer un rapport
        log.info("fond de carte indisponible (%s)", exc)
        bm = None

    if bm is not None:
        # renderPDF n'accepte qu'un chemin ou un objet exposant `.mode` :
        # un ImageReader y échoue, l'image PIL passe directement.
        d.add(RLImage(0, 0, width, height, PILImage.open(io.BytesIO(bm.png))))

        def project(lon: float, lat: float) -> tuple[float, float]:
            u, v = bm.project(lon, lat)
            return u * width, (1 - v) * height

        metres_per_point = bm.metres_per_pixel((south + north) / 2) * bm.width_px / width
    else:
        d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#EEF2EC"), strokeColor=None))
        mx0, mx1 = (west + 180) / 360, (east + 180) / 360
        my0, my1 = _merc_y(north), _merc_y(south)

        def project(lon: float, lat: float) -> tuple[float, float]:
            u = ((lon + 180) / 360 - mx0) / (mx1 - mx0)
            v = (_merc_y(lat) - my0) / (my1 - my0)
            return u * width, (1 - v) * height

        metres_per_point = (north - south) * 111_320 / height

    # Sur imagerie, un remplissage opaque masquerait le couvert : on laisse
    # transparaître le fond tout en gardant le statut lisible.
    alpha = 0.55 if bm is not None else 1.0
    edge = colors.white if bm is not None else colors.HexColor("#FFFFFF")
    for r in rows:
        g = r["geometry"]
        if g is None or g.is_empty:
            continue
        polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        base = STATUS_COLORS.get(r["eudr_status"], STATUS_COLORS["unassessed"])
        col = colors.Color(base.red, base.green, base.blue, alpha=alpha)
        for poly in polys:
            pts: list[float] = []
            for lon, lat in poly.exterior.coords:
                px, py = project(lon, lat)
                pts.extend([px, py])
            d.add(RLPolygon(pts, fillColor=col, strokeColor=edge, strokeWidth=0.9))

    _scale_bar(d, metres_per_point, width, on_imagery=bm is not None)
    if bm is not None and bm.attribution:
        d.add(
            String(
                width - 4, 8, bm.attribution, fontSize=6,
                fillColor=colors.white, textAnchor="end",
            )
        )
    d.add(Rect(0, 0, width, height, fillColor=None, strokeColor=colors.HexColor("#B9C2B4"), strokeWidth=0.6))
    return d


def _build_pdf(coop: Cooperative, meta: dict, rows: list[dict], summary: dict, content_hash: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=18 * mm, bottomMargin=16 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm, title=f"CacaoSat — Conformité EUDR — {coop.name}",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=CI_GREEN, fontSize=22, spaceAfter=4)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#555"))
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9, leading=13)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=7.5, textColor=colors.HexColor("#666"))
    # Les chaînes nues d'un tableau ReportLab ne se replient pas : elles
    # débordent sur la colonne voisine. Les colonnes textuelles passent donc
    # par des Paragraph, qui eux savent revenir à la ligne.
    cell = ParagraphStyle("cell", parent=styles["Normal"], fontSize=7.2, leading=8.6)
    cell_code = ParagraphStyle("cell_code", parent=cell, wordWrap="CJK")

    el: list = []
    el.append(Paragraph("CACAO<font color='#FF7A00'>SAT</font>", h1))
    el.append(Paragraph("Certificat de conformité EUDR — traçabilité géospatiale du cacao", sub))
    el.append(Spacer(1, 8 * mm))

    info = [
        ["Coopérative", f"{coop.name} ({coop.code})"],
        ["Région / département", f"{coop.region or '—'} / {coop.department or '—'}"],
        ["Période couverte", f"{meta['period_start']} → {meta['period_end']}"],
        ["Généré le", meta["generated_at"]],
        ["Empreinte du document (SHA-256)", content_hash],
    ]
    t = Table(info, colWidths=[55 * mm, 115 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#444")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4EAD5")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(t)
    el.append(Spacer(1, 6 * mm))

    el.append(Paragraph(
        f"Le présent document atteste, sur la base des relevés GPS des parcelles et de l'imagerie "
        f"satellite en libre accès, l'état de conformité au règlement européen anti-déforestation "
        f"(EUDR) des parcelles productrices listées. La référence d'absence de déforestation est "
        f"fixée au <b>{EUDR_CUTOFF}</b>. Les parcelles marquées « à vérifier » ou « non conforme » "
        f"nécessitent un contrôle terrain avant export.", body))
    el.append(Spacer(1, 4 * mm))

    sm = [
        ["Parcelles", summary["parcels_total"], "Surface totale (ha)", summary["area_ha_total"]],
        ["Conformes", summary["compliant"], "À vérifier", summary["at_risk"]],
        ["Non conformes", summary["non_compliant"], "Non évaluées", summary["unassessed"]],
        ["Événements de déforestation", summary["deforestation_events"],
         "Surface à haut risque (ha)", summary["high_risk_area_ha"]],
    ]
    ts = Table(sm, colWidths=[45 * mm, 40 * mm, 45 * mm, 40 * mm])
    ts.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDD")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF7EF")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EAF7EF")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(KeepTogether([Paragraph("<b>Synthèse</b>", body), Spacer(1, 2 * mm), ts]))
    el.append(Spacer(1, 6 * mm))

    el.append(KeepTogether([
        Paragraph("<b>Carte des parcelles</b> (vert = conforme, ambre = à vérifier, rouge = non conforme)", body),
        Spacer(1, 2 * mm),
        _map_drawing(rows),
    ]))
    el.append(Spacer(1, 6 * mm))

    head = ["Code", "Producteur", "Surface", "Score", "Statut EUDR", "Motif principal"]
    data = [head]
    for r in rows:
        data.append([
            Paragraph(r["code"], cell_code),
            Paragraph(r["producer_name"], cell),
            f"{r['area_ha']:.2f}",
            "—" if r["score"] is None else f"{r['score']:.0f}",
            # Laissé en chaîne nue : la couleur par statut est posée plus bas
            # via TableStyle, qui n'a pas prise sur un Paragraph.
            {"compliant": "Conforme", "at_risk": "À vérifier",
             "non_compliant": "Non conforme", "unassessed": "Non évaluée"}[r["eudr_status"]],
            Paragraph((r["top_reason"] or "")[:70], cell),
        ])
    # Largeurs calées sur le contenu réel, marge interne comprise : le code le
    # plus large mesure 28,2 mm et le motif peut atteindre 88,9 mm — d'où le
    # repli sur deux lignes plutôt qu'un débordement.
    pt = Table(data, colWidths=[32 * mm, 28 * mm, 14 * mm, 11 * mm, 20 * mm, 65 * mm], repeatRows=1)
    style = [
        ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("BACKGROUND", (0, 0), (-1, 0), CI_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FafafA")]),
    ]
    for i, r in enumerate(rows, start=1):
        style.append(("TEXTCOLOR", (4, i), (4, i), STATUS_COLORS.get(r["eudr_status"])))
    pt.setStyle(TableStyle(style))
    el.append(pt)
    el.append(Spacer(1, 6 * mm))

    el.append(Paragraph("<b>Méthodologie & sources de données</b>", body))
    src = [["Source", "Usage"]] + [[a, b] for a, b in DATA_SOURCES]
    st = Table(src, colWidths=[55 * mm, 115 * mm])
    st.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 7.6),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4EAD5")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDD")),
    ]))
    el.append(st)
    el.append(Spacer(1, 3 * mm))
    el.append(Paragraph(
        "Prototype Ivoire Spacehack 2026 — les fournisseurs de données satellite sont simulés de "
        "façon déterministe pour la démonstration. L'architecture est prévue pour brancher les "
        "flux Copernicus / GFW / Digital Earth Africa réels sans changement de contrat d'API.",
        small))

    doc.build(el)
    return buf.getvalue()


def generate_report(
    *, cooperative_id, period_start: date, period_end: date, parcel_ids: list | None = None,
    generated_by=None, title: str | None = None,
) -> ComplianceReport:
    coop = db.session.get(Cooperative, cooperative_id)
    if coop is None:
        raise ValueError("Coopérative introuvable")

    q = (
        db.select(Parcel)
        .filter(Parcel.cooperative_id == cooperative_id, Parcel.deleted_at.is_(None))
        .options(selectinload(Parcel.scores), selectinload(Parcel.analyses), joinedload(Parcel.producer))
    )
    if parcel_ids:
        q = q.filter(Parcel.id.in_(parcel_ids))
    parcels = db.session.scalars(q).unique().all()
    if not parcels:
        raise ValueError("Aucune parcelle pour ce périmètre")

    rows = _collect_rows(parcels)
    summary = _summary(rows)
    content_hash = _content_hash(coop.code, (period_start, period_end), rows, summary)
    generated_at = _now()

    report = ComplianceReport(
        cooperative_id=cooperative_id,
        title=title or f"Conformité EUDR — {coop.name} — {period_start:%Y-%m} à {period_end:%Y-%m}",
        period_start=period_start,
        period_end=period_end,
        parcel_ids=[str(p.id) for p in parcels],
        summary={**summary, "generated_at": generated_at.isoformat(), "content_hash": content_hash},
        content_hash=content_hash,
        generated_by=generated_by,
        generated_at=generated_at,
    )
    db.session.add(report)
    db.session.flush()

    meta = {
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "generated_at": generated_at.strftime("%Y-%m-%d %H:%M UTC"),
    }
    pdf_bytes = _build_pdf(coop, meta, rows, summary, content_hash)
    geojson_bytes = _geojson(rows, coop)

    report.pdf_key = f"reports/{report.id}/rapport-conformite-eudr.pdf"
    report.geojson_key = f"reports/{report.id}/parcelles.geojson"
    put_object(report.pdf_key, pdf_bytes, "application/pdf")
    put_object(report.geojson_key, geojson_bytes, "application/geo+json")

    db.session.commit()
    return report
