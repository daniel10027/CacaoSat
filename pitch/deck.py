"""Contenu du pitch CacaoSat — 5 minutes / 14 slides.

Partagé par build_pptx.py (PowerPoint) et build_pdf.py (PDF).
`visual` indique à build_pptx.py quelle mise en page illustrée utiliser ;
le PDF, lui, reste textuel (contenu identique).

Charte : fond blanc, drapeau de la Côte d'Ivoire (orange / blanc / vert).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Charte drapeau de la Côte d'Ivoire.
ORANGE = "FF7A00"
GREEN = "00A651"
INK = "13251C"        # texte titre (noir-vert profond)
BODY = "3D4A43"       # texte courant
MUTED = "6B7A70"      # texte secondaire
CARD = "F7F9F7"       # fond de carte
BORDER = "E3E8E4"     # bordures
ORANGE_DARK = "D95E00"
GREEN_DARK = "007A3D"
ORANGE_SOFT = "FFF1E1"
GREEN_SOFT = "E2F4E9"
RED = "D9482B"


@dataclass
class Slide:
    kind: str  # "cover" | "content" | "stats" | "closing"
    title: str
    subtitle: str = ""
    bullets: list[str] = field(default_factory=list)
    stats: list[tuple[str, str]] = field(default_factory=list)
    footer: str = ""
    notes: str = ""
    kicker: str = ""        # petit libellé au-dessus du titre
    visual: str = ""        # clé de mise en page pour build_pptx.py


DECK: list[Slide] = [
    Slide(
        kind="cover",
        title="CacaoSat",
        subtitle="Traçabilité géospatiale du cacao ivoirien\nMettre la donnée satellite libre "
        "au service des coopératives",
        kicker="Ivoire Spacehack 2026 · Abidjan · Africa Space Expo",
        footer="Akandji Timothé · Elie Konan · Daniel Guedegbe",
        notes="Bonjour. Nous sommes l'équipe CacaoSat. En 5 minutes, comment le spatial "
        "peut sécuriser l'accès de milliers de coopératives ivoiriennes au marché européen.",
        visual="cover",
    ),
    Slide(
        kind="stats",
        title="Le choc réglementaire EUDR",
        subtitle="Chaque cargaison exportée vers l'UE doit fournir les coordonnées GPS de "
        "chaque parcelle et prouver l'absence de déforestation depuis le 31 décembre 2020.",
        kicker="Contexte",
        bullets=[
            "31 déc. 2020 — date de référence « zéro déforestation »",
            "Fin 2024 — EUDR entre en vigueur",
            "2025 — application stricte, contrôles sur le terrain",
            "Aujourd'hui — chaque export : GPS + preuve, sinon exclusion",
        ],
        stats=[
            ("N°1", "producteur mondial de cacao"),
            ("82 %", "traçable à la parcelle en 2023"),
            ("~30 %", "de la surface en zone protégée"),
            ("2 M+", "foyers dépendant de la filière"),
        ],
        notes="L'Europe impose une preuve géospatiale. La Côte d'Ivoire est n°1 mondial, "
        "mais seulement 82 % du cacao était traçable à la parcelle, et près de 30 % des "
        "surfaces sont en zone protégée. L'enjeu est énorme, et l'échéance est déjà là.",
        visual="eudr",
    ),
    Slide(
        kind="content",
        title="Qui porte le poids ? Les petites coopératives.",
        kicker="Problème",
        bullets=[
            "Elles doivent cartographier des milliers d'exploitations, à la main",
            "Sans outils numériques, sans compétences juridiques",
            "En cas d'échec : leurs producteurs sont exclus du marché européen",
        ],
        stats=[
            ("Charge", "des milliers de parcelles à relever et documenter"),
            ("Moyens", "pas d'outil, pas d'expertise, pas de budget"),
            ("Risque", "exclusion du marché UE pour des milliers de foyers"),
        ],
        notes="Ce sont les petites coopératives qui doivent produire cette preuve, à la main, "
        "sans moyens. Si elles échouent, leurs producteurs sont exclus du marché.",
        visual="problem",
    ),
    Slide(
        kind="content",
        title="La donnée existe déjà. Gratuitement.",
        kicker="Insight",
        bullets=[
            "Sentinel-2 (Copernicus) — imagerie optique 10 m, relevé tous les 5 jours",
            "Hansen / Global Forest Watch — couvert forestier et perte annuelle depuis 2000",
            "Digital Earth Africa — dégradation des terres, à l'échelle du continent",
        ],
        footer="Ce qui manque : le pipeline qui relie ces données à chaque parcelle.",
        notes="L'imagerie satellite nécessaire est déjà publique et gratuite. Le problème "
        "n'est pas la donnée globale : c'est le pipeline qui la connecte à chaque parcelle "
        "de chaque coopérative. C'est ce pipeline que nous avons construit.",
        visual="sources",
    ),
    Slide(
        kind="content",
        title="Un pipeline complet, de la parcelle au certificat",
        kicker="Notre solution",
        bullets=[
            "01 Cartographie — relevé GPS hors-ligne (app mobile)",
            "02 Ingestion — base géospatiale PostGIS unique",
            "03 Croisement — Sentinel-2 + Hansen/GFW + DEA depuis 2020",
            "04 Scoring EUDR — score pondéré et explicable par parcelle",
            "05 Certificat — rapport PDF + GeoJSON en minutes",
            "06 Alerte précoce — toute nouvelle déforestation détectée",
        ],
        notes="Six étapes : du relevé terrain hors-ligne, à l'ingestion, au croisement "
        "satellite, au scoring, au certificat exportable, jusqu'à l'alerte précoce. "
        "Tout est automatisé de bout en bout.",
        visual="pipeline",
    ),
    Slide(
        kind="content",
        title="L'app terrain — cartographier sans réseau",
        kicker="Solution 01 · App mobile",
        bullets=[
            "Contour relevé en marchant, par sommets ou saisie manuelle",
            "Surface calculée en direct, alerte si recoupement d'une forêt classée",
            "Tout est stocké en local (SQLite) — 100 % hors-ligne",
            "Synchronisation en un lot idempotent dès que le réseau revient",
        ],
        stats=[
            ("3 modes", "de relevé GPS"),
            ("0 réseau", "requis sur le terrain"),
            ("1 lot", "de sync idempotent"),
        ],
        notes="Première brique : un agent de coopérative, sur le terrain, sans réseau. "
        "Il marche autour de la parcelle, la surface s'affiche en direct, et l'app "
        "l'alerte si la parcelle touche une aire protégée. Tout part ensuite en un "
        "seul lot, sans doublon.",
        visual="mobile",
    ),
    Slide(
        kind="content",
        title="Un socle géospatial ouvert et interopérable",
        kicker="Solution 02 · Backend & données",
        bullets=[
            "Sources satellites publiques croisées automatiquement",
            "API Flask + PostGIS : une seule base géospatiale, formats ouverts",
            "34 routes REST sécurisées (JWT), audit et traçabilité intégrés",
            "Services mockés de façon déterministe pour une démo reproductible",
        ],
        stats=[
            ("34", "routes API"),
            ("PostGIS", "base géospatiale"),
            ("100 %", "outils libres"),
        ],
        notes="Deuxième brique : le socle. Les trois sources satellites arrivent dans une "
        "base PostGIS unique ; le moteur d'analyse et le scoring y tournent. Tout est "
        "open source, containerisé, et prêt à brancher les flux réels.",
        visual="arch",
    ),
    Slide(
        kind="content",
        title="Un score EUDR explicable, facteur par facteur",
        kicker="Solution 03 · Analyse & scoring",
        bullets=[
            "Déforestation post-2020 détectée par Sentinel-2 + Hansen",
            "Recouvrement d'aires protégées, tendance NDVI, complétude, qualité GPS",
            "Score /100 par parcelle, chaque point justifié — audit facile",
        ],
        stats=[
            ("45 pts", "déforestation post-2020"),
            ("20 pts", "recouvrement aire protégée"),
            ("15 pts", "tendance NDVI"),
            ("20 pts", "complétude + qualité GPS"),
        ],
        notes="Troisième brique : le croisement satellite. Chaque parcelle reçoit un score "
        "sur 100, construit sur cinq facteurs pondérés et affichés avec leur calcul. "
        "Ce n'est pas une boîte noire : un exportateur ou un régulateur peut auditer "
        "chaque point.",
        visual="scoring",
    ),
    Slide(
        kind="content",
        title="Le tableau de bord de la coopérative",
        kicker="Solution 04 · Dashboard web",
        bullets=[
            "Carte satellite : parcelles colorées par statut EUDR",
            "KPIs en direct : conformes, surface à haut risque, événements post-2020",
            "Alertes récentes acquittables en un clic",
        ],
        stats=[
            ("21", "parcelles suivies (démo)"),
            ("72 ha", "surface analysée"),
            ("100 %", "couverture d'analyse"),
        ],
        notes="Quatrième brique : le tableau de bord. Sur fond satellite, on voit chaque "
        "parcelle, son statut, les KPIs de la coopérative et les alertes. C'est un outil "
        "digne d'un niveau national, mis entre les mains d'une coopérative.",
        visual="dashboard",
    ),
    Slide(
        kind="content",
        title="Le certificat, en un clic — et l'alerte qui veille",
        kicker="Solution 05 · Preuve & vigilance",
        bullets=[
            "Rapport PDF : préambule légal, synthèse, carte, tableau par producteur",
            "Export GeoJSON au gabarit attendu par exportateurs et Conseil du Café-Cacao",
            "Empreinte SHA-256 du contenu — anti-falsification",
            "Alerte précoce : perte de couvert ou empiètement détectés en continu",
        ],
        footer="Des semaines de paperasse → quelques minutes.",
        notes="Cinquième brique : la preuve. La coopérative génère son certificat de "
        "conformité : PDF signé par une empreinte cryptographique, export GeoJSON pour "
        "les acheteurs. Et le système continue de veiller après la certification.",
        visual="certificate",
    ),
    Slide(
        kind="stats",
        title="Quatre plans d'impact, un seul outil",
        kicker="Impact",
        stats=[
            ("Économique", "accès au marché UE sécurisé, délai et coût de conformité réduits"),
            ("Social", "un outil direct pour les petites coopératives, sans intermédiaire coûteux"),
            ("Environnemental", "suivi continu du couvert forestier autour des zones de production"),
            ("Institutionnel", "base nationale consolidée pour le Conseil du Café-Cacao"),
        ],
        notes="Impact sur quatre plans : économique, social, environnemental et institutionnel — "
        "jusqu'à une base nationale consolidée pour le pilotage des politiques agricoles.",
        visual="impact",
    ),
    Slide(
        kind="content",
        title="Sous le capot : prêt pour la production",
        kicker="Crédibilité",
        bullets=[
            "Flask 3 + PostGIS · React 18 · Flutter hors-ligne · Docker Compose",
            "CI/CD GitHub Actions : backend, web, mobile, docs — tout est testé",
            "76 tests backend, 84 % de couverture · smoke e2e 10/10",
            "Déployable en une commande : docker compose up",
        ],
        footer="Des semaines de conformité à la main → quelques minutes avec CacaoSat.",
        notes="Ce n'est pas un prototype sur papier : c'est un produit testé, containerisé, "
        "déployable. Les fournisseurs satellite sont simulés de façon déterministe pour "
        "la démo ; l'architecture est prête à brancher les flux réels sans changement de "
        "contrat.",
        visual="proof",
    ),
    Slide(
        kind="content",
        title="Du pilote à l'échelle nationale",
        kicker="Au-delà du hackathon",
        bullets=[
            "Fin 2026 — Pilote terrain avec une coopérative volontaire du Cavally",
            "2027 — Partenariat avec le Conseil du Café-Cacao, validation en conditions réelles",
            "2028+ — Déploiement progressif sur les principales zones de production",
        ],
        notes="Après le hackathon : un pilote réel avec une coopérative volontaire et le "
        "Conseil du Café-Cacao, puis un déploiement progressif jusqu'à une base nationale.",
        visual="roadmap",
    ),
    Slide(
        kind="closing",
        title="Le spatial, entre les mains de la jeunesse ivoirienne.",
        subtitle="CacaoSat répond à une exigence déjà en vigueur, qui touche des millions de foyers.",
        footer="github.com/daniel10027/CacaoSat · Équipe CacaoSat — Ivoire Spacehack 2026",
        notes="CacaoSat n'est pas un projet théorique : c'est une réponse concrète à un défi "
        "national. Merci.",
        visual="closing",
    ),
]

TIMINGS = [12, 28, 20, 20, 30, 28, 22, 30, 25, 24, 18, 18, 16, 12]  # ≈ 5 min 03