import { Routes } from '@angular/router';

import { HomePage } from './shared/components/home-page/home-page';
import { DeveloperTools } from './shared/components/developer-tools/developer-tools';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: HomePage,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        loadComponent: () => import('./features/dashboard/dashboard').then((m) => m.Dashboard),
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard').then((m) => m.Dashboard),
      },
      {
        path: 'list',
        loadComponent: () =>
          import('./features/list-applications/list-applications').then((m) => m.ListApplications),
      },

      // Operations
      {
        path: 'operations/add-application',
        loadComponent: () =>
          import('./features/operations-page/add-application/add-application').then(
            (m) => m.AddApplication,
          ),
      },
      {
        path: 'operations/check-eda-files',
        loadComponent: () =>
          import('./features/operations-page/check-eda-files/check-eda-files').then(
            (m) => m.CheckEdaFiles,
          ),
      },
      {
        path: 'operations/delete-applications',
        loadComponent: () =>
          import('./features/operations-page/delete-applications/delete-applications').then(
            (m) => m.DeleteApplications,
          ),
      },
      {
        path: 'operations/manage-apps',
        loadComponent: () =>
          import('./features/operations-page/manage-apps/manage-apps').then((m) => m.ManageApps),
      },
      {
        path: 'operations/manage-eda',
        loadComponent: () =>
          import('./features/operations-page/manage-eda/manage-eda').then((m) => m.ManageEda),
      },

      {
        path: 'eda',
        loadComponent: () => import('./features/eda-page/eda-page').then((m) => m.EdaPage),
      },
    ],
  },

  {
    path: 'developer-tools',
    component: DeveloperTools,
    children: [],
  },
];
