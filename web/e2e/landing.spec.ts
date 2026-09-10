import { expect, test } from '@playwright/test';
import { mockApi } from './fixtures';

test('la landing se charge, scrolle et n\'émet aucune erreur console', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text());
  });

  await mockApi(page);
  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1, name: 'CACAOSAT' })).toBeVisible();
  await expect(page.getByRole('link', { name: /voir le tableau de bord/i })).toBeVisible();

  // parcourt toute la page (déclenche les sections lazy + reveals)
  await page.evaluate(async () => {
    for (let y = 0; y <= document.body.scrollHeight; y += 600) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 60));
    }
  });

  await expect(page.getByText(/Le pipeline CacaoSat/i)).toBeVisible();
  await expect(page.getByText(/Notre équipe/i)).toBeVisible();
  expect(errors, errors.join('\n')).toEqual([]);
});

test('CTA « Espace coopérative » mène à la connexion', async ({ page }) => {
  await mockApi(page);
  await page.goto('/');
  await page.getByRole('link', { name: /espace coopérative/i }).click();
  await expect(page).toHaveURL(/\/login$/);
});
