"""Contenu du pitch CacaoSat — 5 minutes / 12 slides.

Partagé par build_pptx.py (PowerPoint) et build_pdf.py (PDF).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Charte drapeau de la Côte d'Ivoire.
ORANGE = "FF7A00"
GREEN = "00A651"
NIGHT = "08130E"
NIGHT2 = "0E211A"
SAND = "F4EAD5"


@dataclass
class Slide:
    kind: str  # "cover" | "content" | "stats" | "closing"
    title: str
    subtitle: str = ""
    bullets: list[str] = field(default_factory=list)
    stats: list[tuple[str, str]] = field(default_factory=list)
    footer: str = ""
    notes: str = ""


DECK: list[Slide] = [
    Slide(
        kind="cover",
        title="CACAOSAT",
        subtitle="Traçabilité géospatiale du cacao ivoirien\nLe spatial pour bâtir",
        footer="Ivoire Spacehack 2026 · Abidjan · Akandji Timothé · Elie Konan · Daniel Guedegbe",
        notes="Bonjour. Nous sommes l'équipe CacaoSat. En 5 minutes, comment le spatial "
        "peut sécuriser l'accès de milliers de coopératives ivoiriennes au marché européen.",
    ),
    Slide(
        kind="stats",
        title="Le choc réglementaire EUDR",
        subtitle="Depuis fin 2024/2025, chaque cargaison de cacao exportée vers l'UE doit fournir "
        "les coordonnées GPS de chaque parcelle et prouver l'absence de déforestation depuis "
        "le 31 décembre 2020.",
        stats=[
            ("N°1", "producteur mondial de cacao"),
            ("82 %", "traçable à la parcelle en 2023"),
            ("~30 %", "de la surface cacaoyère en zone protégée"),
            ("2M+", "foyers dépendants de la filière"),
        ],
        notes="L'Europe impose une preuve géospatiale. La Côte d'Ivoire est n°1 mondial, "
        "mais seulement 82 % du cacao était traçable à la parcelle, et près de 30 % des "
        "surfaces sont en zone protégée. L'enjeu est énorme.",
    ),
    Slide(
        kind="content",
        title="Qui porte le poids ?",
        subtitle="Les petites coopératives.",
        bullets=[
            "Elles doivent cartographier des milliers d'exploitations…",
            "…sans outils numériques ni compétences juridiques.",
            "Une charge disproportionnée qui menace l'accès de milliers de producteurs au marché européen.",
        ],
        notes="Ce sont les petites coopératives qui doivent produire cette preuve, à la main, "
        "sans moyens. Si elles échouent, leurs producteurs sont exclus du marché.",
    ),
    Slide(
        kind="content",
        title="L'insight",
        subtitle="La donnée existe déjà. Gratuitement.",
        bullets=[
            "Sentinel-2 (Copernicus) — imagerie optique 10 m",
            "Hansen / Global Forest Watch — couvert forestier et perte annuelle",
            "Digital Earth Africa — dégradation des terres",
            "Ce qui manque, ce n'est pas la donnée — c'est le PIPELINE qui la relie au terrain.",
        ],
        notes="L'imagerie satellite nécessaire est déjà publique et gratuite. Le problème "
        "n'est pas la donnée globale : c'est le pipeline qui la connecte à chaque parcelle "
        "de chaque coopérative. C'est ce pipeline que nous avons construit.",
    ),
    Slide(
        kind="content",
        title="La solution : le pipeline CacaoSat",
        bullets=[
            "1 · Cartographie participative — relevé GPS hors-ligne des parcelles (app mobile)",
            "2 · Ingestion — base géospatiale PostGIS unique et interopérable",
            "3 · Croisement satellite — Sentinel-2 + Hansen/GFW + Digital Earth Africa depuis 2020",
            "4 · Scoring EUDR — score pondéré et explicable par parcelle",
            "5 · Rapport de conformité — certificat PDF + GeoJSON en minutes",
            "6 · Alerte précoce — toute nouvelle déforestation détectée",
        ],
        notes="Six étapes : du relevé terrain hors-ligne, à l'ingestion, au croisement "
        "satellite, au scoring, au certificat exportable, jusqu'à l'alerte précoce.",
    ),
    Slide(
        kind="content",
        title="Démo 1 — Terrain, sans réseau",
        subtitle="Application mobile Flutter",
        bullets=[
            "L'agent relève le contour GPS d'une parcelle (marche, sommets ou saisie manuelle)",
            "Surface calculée en direct · alerte si recoupement d'une forêt classée",
            "Tout est enregistré localement (SQLite) et synchronisé plus tard, en un lot idempotent",
        ],
        notes="Première démo : un agent de coopérative, sur le terrain, sans réseau. "
        "Il marche autour de la parcelle, la surface s'affiche en direct, et l'app "
        "l'alerte si la parcelle touche une aire protégée.",
    ),
    Slide(
        kind="content",
        title="Démo 2 — Le tableau de bord",
        subtitle="Web React · dignes d'un outil national",
        bullets=[
            "Carte satellite des parcelles colorées par statut EUDR (conforme / à vérifier / non conforme)",
            "KPIs : % conformes, surface à haut risque, événements de déforestation",
            "Détail parcelle : jauge de score, ventilation des 5 facteurs, série NDVI",
        ],
        notes="Deuxième démo : le tableau de bord de la coopérative. Sur fond satellite, "
        "on voit chaque parcelle, son score, et pour chacune la ventilation du calcul.",
    ),
    Slide(
        kind="content",
        title="Démo 3 — Le certificat, en un clic",
        subtitle="Preuve de conformité EUDR",
        bullets=[
            "Rapport PDF : préambule légal, synthèse, carte, tableau par producteur, méthodologie",
            "Export GeoJSON au gabarit attendu par les exportateurs et le Conseil du Café-Cacao",
            "Empreinte SHA-256 du contenu — anti-falsification",
            "Minutes, au lieu de semaines.",
        ],
        notes="Troisième démo : la coopérative génère son certificat de conformité. "
        "PDF signé par une empreinte cryptographique, plus export GeoJSON pour les acheteurs. "
        "Quelques minutes au lieu de plusieurs semaines.",
    ),
    Slide(
        kind="content",
        title="Sous le capot",
        subtitle="100 % outils libres · coût d'infrastructure minimal",
        bullets=[
            "Backend Flask + PostGIS · moteur d'analyse & scoring · rapports ReportLab",
            "Web React/Vite · Mobile Flutter hors-ligne (Drift/SQLite)",
            "Tout containerisé (Docker) · CI/CD GitHub Actions · déployable en une commande",
            "Services externes mockés de façon déterministe pour une démo reproductible",
        ],
        notes="Toute la stack est open source, containerisée, testée en CI. Pour la démo, "
        "les fournisseurs satellite sont simulés de façon déterministe ; l'architecture est "
        "prête à brancher les flux réels sans changement de contrat.",
    ),
    Slide(
        kind="stats",
        title="Impact",
        stats=[
            ("Économique", "accès au marché UE sécurisé, délai et coût de conformité réduits"),
            ("Social", "un outil pour les petites coopératives, sans intermédiaire coûteux"),
            ("Environnemental", "suivi continu du couvert forestier autour des zones de production"),
            ("Institutionnel", "base nationale consolidée pour le Conseil du Café-Cacao"),
        ],
        notes="Impact sur quatre plans : économique, social, environnemental et institutionnel — "
        "jusqu'à une base nationale consolidée pour le pilotage des politiques agricoles.",
    ),
    Slide(
        kind="content",
        title="Au-delà du hackathon",
        bullets=[
            "Pilote avec une coopérative volontaire de la région du Cavally",
            "Partenariat avec le Conseil du Café-Cacao pour valider en conditions réelles",
            "Déploiement progressif à l'échelle des principales zones de production",
        ],
        notes="Après le hackathon : un pilote réel avec une coopérative volontaire et le "
        "Conseil du Café-Cacao, puis un déploiement progressif.",
    ),
    Slide(
        kind="closing",
        title="Le spatial, entre les mains de la jeunesse ivoirienne.",
        subtitle="CacaoSat répond à une exigence déjà en vigueur, qui touche des millions de foyers.",
        footer="github.com/daniel10027/CacaoSat · Équipe CacaoSat — Ivoire Spacehack 2026",
        notes="CacaoSat n'est pas un projet théorique : c'est une réponse concrète à un défi "
        "national. Merci.",
    ),
]

TIMINGS = [15, 30, 20, 25, 35, 32, 32, 32, 25, 22, 17, 15]  # secondes ≈ 4 min 50 (marge démo)
