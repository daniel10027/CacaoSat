import '@testing-library/jest-dom/vitest';

// jsdom : stubs pour les API non implémentées utilisées par framer-motion / maplibre
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList;
}

if (!window.ResizeObserver) {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

if (!window.IntersectionObserver) {
  window.IntersectionObserver = class {
    readonly root = null;
    readonly rootMargin = '';
    readonly thresholds = [];
    constructor(cb: IntersectionObserverCallback) {
      // Simule une entrée immédiate dans le viewport.
      queueMicrotask(() =>
        cb(
          [
            {
              isIntersecting: true,
              intersectionRatio: 1,
              target: document.body,
            } as unknown as IntersectionObserverEntry,
          ],
          this as unknown as IntersectionObserver,
        ),
      );
    }
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  } as unknown as typeof IntersectionObserver;
}
