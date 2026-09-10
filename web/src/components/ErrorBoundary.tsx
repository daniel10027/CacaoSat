import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button } from '@/components/ui/Button';

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('[CacaoSat] Erreur non capturée', error, info);
  }

  render(): ReactNode {
    if (this.state.error) {
      return (
        <div className="grid min-h-screen place-items-center bg-night px-4 text-center">
          <div className="max-w-md">
            <h1 className="font-display text-2xl font-bold">Une anomalie est survenue</h1>
            <p className="mt-2 text-sm text-sand/60">{this.state.error.message}</p>
            <Button className="mt-6" onClick={() => window.location.reload()}>
              Recharger
            </Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
