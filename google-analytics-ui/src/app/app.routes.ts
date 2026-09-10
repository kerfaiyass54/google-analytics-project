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
        loadComponent: () => import('./features/list-applications/list-applications').then((m) => m.ListApplications),
      },
      {
        path: 'user-details',
        loadComponent: () =>
          import('./shared/components/user-details/user-details').then((m) => m.UserDetails),
      },
    ],
  },
  {
    path: 'developer-tools',
    component: DeveloperTools,
    children: [],
  },
];
