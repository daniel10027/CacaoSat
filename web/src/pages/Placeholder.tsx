import { Card, CardHeader, CardBody } from '@/components/ui/Card';
import { PageTransition } from '@/components/motion/PageTransition';

export function Placeholder({ title }: { title: string }) {
  return (
    <PageTransition>
      <Card className="max-w-xl">
        <CardHeader title={title} subtitle="Écran livré au Lot 6." />
        <CardBody>
          <p className="text-sm text-sand/60">
            Le socle applicatif (auth, layout, thème, client API, i18n) est en place. Cet écran est
            branché sur l'API réelle dans le lot suivant.
          </p>
        </CardBody>
      </Card>
    </PageTransition>
  );
}
