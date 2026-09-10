import { API_URL, tokenStore } from './api';

type Handler = (event: string, data: unknown) => void;

/**
 * Flux SSE authentifié : `EventSource` ne permet pas d'en-tête `Authorization`,
 * on lit donc le flux via `fetch` + `ReadableStream`, avec reconnexion.
 * Retourne une fonction d'arrêt.
 */
export function openEventStream(path: string, onEvent: Handler): () => void {
  let stopped = false;
  let controller: AbortController | null = null;

  const connect = async () => {
    if (stopped) return;
    controller = new AbortController();
    try {
      const res = await fetch(`${API_URL}${path}`, {
        headers: tokenStore.access ? { Authorization: `Bearer ${tokenStore.access}` } : {},
        signal: controller.signal,
      });
      if (!res.ok || !res.body) throw new Error(`SSE ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (!stopped) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split('\n\n');
        buffer = chunks.pop() ?? '';
        for (const chunk of chunks) {
          let event = 'message';
          let data = '';
          for (const line of chunk.split('\n')) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            else if (line.startsWith('data:')) data += line.slice(5).trim();
          }
          if (data) {
            try {
              onEvent(event, JSON.parse(data));
            } catch {
              onEvent(event, data);
            }
          }
        }
      }
    } catch {
      // erreur réseau : on retentera
    }
    if (!stopped) {
      await new Promise((r) => setTimeout(r, 5000));
      void connect();
    }
  };

  void connect();

  return () => {
    stopped = true;
    controller?.abort();
  };
}
