import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { openEventStream } from '@/lib/sse';
import { toast } from '@/components/ui/Toast';
import type { Alert } from '@/types/api';

/**
 * S'abonne au flux SSE `/alerts/stream` : à chaque nouvelle alerte, invalide les
 * requêtes d'alertes (dashboard + cloche) et affiche un toast. Le polling reste
 * en place comme filet de sécurité.
 */
export function useAlertStream(enabled: boolean): void {
  const qc = useQueryClient();
  useEffect(() => {
    if (!enabled) return;
    const close = openEventStream('/alerts/stream', (event, data) => {
      if (event !== 'alert') return;
      const a = data as Alert;
      void qc.invalidateQueries({ queryKey: ['alerts'] });
      toast.info(`Alerte : ${a.parcel_code ?? ''} — ${a.message}`);
    });
    return close;
  }, [enabled, qc]);
}
