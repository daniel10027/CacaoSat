"""Génération du rapport / certificat de conformité EUDR (PDF + export GeoJSON)."""

from __future__ import annotations

import hashlib
import io
import json
from datetime import UTC, date, datetime

from geoalchemy2.shape import to_shape
from reportlab.graphics.shapes import Drawing, String
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
from app.storage import put_object

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


def _map_drawing(rows: list[dict], width=170 * mm, height=95 * mm) -> Drawing:
    d = Drawing(width, height)
    geoms = [r["geometry"] for r in rows if r["geometry"] and not r["geometry"].is_empty]
    if not geoms:
        d.add(String(10, height / 2, "Aucune géométrie à afficher", fontSize=9))
        return d
    minx = min(g.bounds[0] for g in geoms)
    miny = min(g.bounds[1] for g in geoms)
    maxx = max(g.bounds[2] for g in geoms)
    maxy = max(g.bounds[3] for g in geoms)
    pad = 6
    sx = (width - 2 * pad) / (maxx - minx or 1e-6)
    sy = (height - 2 * pad) / (maxy - miny or 1e-6)
    s = min(sx, sy)

    def project(x, y):
        return (pad + (x - minx) * s, pad + (y - miny) * s)

    for r in rows:
        g = r["geometry"]
        if g is None or g.is_empty:
            continue
        polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        col = STATUS_COLORS.get(r["eudr_status"], STATUS_COLORS["unassessed"])
        for poly in polys:
            pts: list[float] = []
            for x, y in poly.exterior.coords:
                px, py = project(x, y)
                pts.extend([px, py])
            d.add(RLPolygon(pts, fillColor=col, strokeColor=colors.white, strokeWidth=0.4))
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
            r["code"],
            r["producer_name"],
            f"{r['area_ha']:.2f}",
            "—" if r["score"] is None else f"{r['score']:.0f}",
            {"compliant": "Conforme", "at_risk": "À vérifier",
             "non_compliant": "Non conforme", "unassessed": "Non évaluée"}[r["eudr_status"]],
            (r["top_reason"] or "")[:70],
        ])
    pt = Table(data, colWidths=[26 * mm, 34 * mm, 16 * mm, 14 * mm, 24 * mm, 56 * mm], repeatRows=1)
    style = [
        ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("BACKGROUND", (0, 0), (-1, 0), CI_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDD")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
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
