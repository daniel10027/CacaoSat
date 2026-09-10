import type { ReactNode } from 'react';

/**
 * Passe-plat : le contenu des pages ne doit jamais dépendre d'une animation pour
 * être visible. Le mouvement d'entrée vit dans les composants `Reveal` internes.
 */
export function PageTransition({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
