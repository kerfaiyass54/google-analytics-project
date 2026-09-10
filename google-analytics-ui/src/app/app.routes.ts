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
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard').then((m) => m.Dashboard),
      },
      {
        path: 'list',
        loadComponent: () =>
          import('./features/list-applications/list-applications').then((m) => m.ListApplications),
      },
      {
        path: 'operations',
        loadComponent: () =>
          import('./features/operations-page/operations-page').then((m) => m.OperationsPage),
      },
      {
        path: 'eda',
        loadComponent: () =>
          import('./features/eda-page/eda-page').then((m) => m.EdaPage),
      },
    ],
  },
  {
    path: 'developer-tools',
    component: DeveloperTools,
    children: [],
  },
];
