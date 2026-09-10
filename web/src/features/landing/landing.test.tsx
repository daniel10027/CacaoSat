import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { StatsBar } from './StatsBar';
import { EudrShock } from './EudrShock';
import { UnderHood } from './UnderHood';

function wrap(node: React.ReactNode) {
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{node}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe('landing sections render', () => {
  it('stats bar renders the four key figures', () => {
    render(wrap(<StatsBar />));
    expect(screen.getByText(/Rang mondial/i)).toBeInTheDocument();
    expect(screen.getByText(/foyers dépendants/i)).toBeInTheDocument();
  });

  it('EUDR section explains the 2020 cutoff and the conviction', () => {
    render(wrap(<EudrShock />));
    expect(screen.getByText(/La date de référence/i)).toBeInTheDocument();
    expect(screen.getByText(/Notre conviction/i)).toBeInTheDocument();
  });

  it('under-the-hood section lists the open-data sources', () => {
    render(wrap(<UnderHood />));
    expect(screen.getByText('Sentinel‑2')).toBeInTheDocument();
    expect(screen.getByText(/Digital Earth Africa/i)).toBeInTheDocument();
  });
});
