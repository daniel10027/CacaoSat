import { expect, test } from '@playwright/test';
import { mockApi } from './fixtures';

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test('login → dashboard → parcelle → analyse → rapport', async ({ page }) => {
  // --- Connexion ---
  await page.goto('/login');
  await page.getByLabel(/adresse e-mail|email address/i).fill('manager1@cacaosat.ci');
  await page.getByLabel(/mot de passe|password/i).fill('cacaosat');
  await page.getByRole('button', { name: /se connecter|sign in/i }).click();

  // --- Dashboard : KPIs présents ---
  await expect(page).toHaveURL(/\/app\/dashboard$/);
  await expect(page.getByText('Tableau de bord')).toBeVisible();
  await expect(page.getByText('Parcelles', { exact: true })).toBeVisible();
  await expect(page.getByText('Carte des parcelles')).toBeVisible();
  await expect(page.getByText('Distribution des scores')).toBeVisible();

  // --- Parcelles : table + filtres ---
  await page.getByRole('link', { name: /parcelles|plots/i }).first().click();
  await expect(page).toHaveURL(/\/app\/parcelles$/);
  const table = page.getByRole('table');
  await expect(table.getByText('COOPCA-GUIGLO-0001')).toBeVisible();
  await expect(table.getByText('Conforme', { exact: true }).first()).toBeVisible();

  // --- Détail parcelle : jauge + facteurs + NDVI ---
  await page.getByRole('link', { name: 'COOPCA-GUIGLO-0001' }).click();
  await expect(page).toHaveURL(/\/app\/parcelles\/p-1$/);
  await expect(page.getByText('Score de conformité EUDR')).toBeVisible();
  await expect(page.getByText('Déforestation post-2020')).toBeVisible();
  await expect(page.getByText(/Série NDVI/i)).toBeVisible();

  // --- Analyse (mutation) ---
  await page.getByRole('button', { name: /relancer l'analyse/i }).click();
  await expect(page.getByText(/Analyse :/i)).toBeVisible();

  // --- Rapports : génération ---
  await page.getByRole('link', { name: /rapports|reports/i }).first().click();
  await expect(page).toHaveURL(/\/app\/rapports$/);
  await page.getByRole('button', { name: /générer un rapport/i }).click();
  await page.getByRole('button', { name: 'Générer', exact: true }).click();
  await expect(page.getByText(/Rapport généré/i)).toBeVisible();
  await expect(page.getByText('Conformité EUDR')).toBeVisible();
});

test('un agent n\'accède pas à l\'écran Rapports (garde de rôle)', async ({ page }) => {
  await page.route('**/api/v1/auth/me', (r) =>
    r.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'u2',
        email: 'agent1a@cacaosat.ci',
        full_name: 'Agent',
        role: 'agent',
        is_active: true,
        cooperative_id: 'coop-1',
        created_at: '2026-01-01T00:00:00Z',
      }),
    }),
  );
  await page.goto('/login');
  await page.getByLabel(/adresse e-mail|email address/i).fill('agent1a@cacaosat.ci');
  await page.getByLabel(/mot de passe|password/i).fill('cacaosat');
  await page.getByRole('button', { name: /se connecter|sign in/i }).click();
  await expect(page).toHaveURL(/\/app\/dashboard$/);
  // l'entrée "Rapports" est masquée pour un agent
  await expect(page.getByRole('link', { name: /rapports|reports/i })).toHaveCount(0);
  // accès direct → redirigé vers le dashboard
  await page.goto('/app/rapports');
  await expect(page).toHaveURL(/\/app\/dashboard$/);
});
