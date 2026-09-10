import { Page, PageHeader } from '@/components/ui/Page';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';

const FACTORS = [
  ['Déforestation post-2020', 45, 'Perte de couvert forestier sur la parcelle depuis le 31/12/2020, rapportée à sa surface. 0 perte → 45 pts ; dégressif ; > 5 % de la surface → 0.'],
  ['Recouvrement d’aire protégée', 20, 'Surface de la parcelle intersectant une forêt classée ou une aire protégée. Hors zone → 20 pts ; proportionnel au % recouvert.'],
  ['Tendance NDVI / dégradation', 15, 'Indice de dégradation des terres (Digital Earth Africa) et pente de la série NDVI. Stable → 15 pts ; déclin marqué → 0.'],
  ['Complétude de la donnée', 10, 'Producteur rattaché, pièce d’identité renseignée, géométrie valide.'],
  ['Qualité du relevé GPS + fraîcheur', 10, 'Précision GPS ≤ 5 m et relevé de moins de 12 mois → 10 pts ; dégressif.'],
];

const SOURCES = [
  ['Sentinel-2 (Copernicus)', 'Imagerie optique 10 m — séries temporelles NDVI'],
  ['Hansen / Global Forest Watch', 'Couvert arboré 2000 et perte annuelle, référence fin 2020'],
  ['Digital Earth Africa', 'Suivi de la dégradation des terres'],
  ['Relevés terrain', 'Polygones GPS des parcelles, identité des producteurs'],
];

export default function Methodology() {
  return (
    <Page>
      <PageHeader
        title="Méthodologie"
        subtitle="Comment le score de conformité EUDR est calculé"
      />

      <Card className="mb-4">
        <CardHeader
          title="Barème de scoring (100 points)"
          subtitle="score ≥ 80 → risque faible · 50–79 → moyen · < 50 → élevé"
        />
        <CardBody className="space-y-4">
          {FACTORS.map(([label, weight, desc]) => (
            <div key={label as string}>
              <div className="flex items-center justify-between">
                <span className="font-medium text-white">{label}</span>
                <span className="font-display font-bold text-ci-green">{weight} pts</span>
              </div>
              <p className="mt-1 text-sm text-sand/55">{desc}</p>
            </div>
          ))}
        </CardBody>
      </Card>

      <Card className="mb-4">
        <CardHeader title="Statut EUDR" />
        <CardBody className="grid gap-3 text-sm text-sand/65 sm:grid-cols-3">
          <div>
            <span className="font-semibold text-risk-low">Conforme</span> — risque faible, aucune
            déforestation post-2020, hors aire protégée.
          </div>
          <div>
            <span className="font-semibold text-risk-medium">À vérifier</span> — signaux
            intermédiaires nécessitant un contrôle terrain avant export.
          </div>
          <div>
            <span className="font-semibold text-risk-high">Non conforme</span> — risque élevé,
            déforestation avérée ou recouvrement significatif d'aire protégée.
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Sources de données (100 % open data)" />
        <CardBody>
          <table className="w-full text-sm">
            <tbody>
              {SOURCES.map(([name, use]) => (
                <tr key={name} className="border-b border-white/5">
                  <td className="py-2.5 pr-4 font-medium text-white">{name}</td>
                  <td className="py-2.5 text-sand/60">{use}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-4 text-xs text-sand/40">
            Prototype Ivoire Spacehack 2026 — les fournisseurs satellite sont simulés de façon
            déterministe pour la démonstration.
          </p>
        </CardBody>
      </Card>
    </Page>
  );
}
