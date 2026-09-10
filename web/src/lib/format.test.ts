import { describe, expect, it } from 'vitest';
import { fmtHa, fmtPct, EUDR_LABEL, relativeTime } from './format';

describe('format', () => {
  it('formats hectares and percentages in fr-FR', () => {
    expect(fmtHa(1234.5)).toContain('ha');
    expect(fmtPct(82)).toContain('%');
    expect(fmtHa(null)).toBe('—');
  });

  it('maps EUDR labels', () => {
    expect(EUDR_LABEL.compliant).toBe('Conforme');
    expect(EUDR_LABEL.non_compliant).toBe('Non conforme');
  });

  it('produces a relative time string', () => {
    const now = new Date().toISOString();
    expect(relativeTime(now)).toMatch(/instant|min/);
  });
});
