import { Routes } from '@angular/router';
import { HomePage } from './shared/components/home-page/home-page';
import { DeveloperTools } from './shared/components/developer-tools/developer-tools';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';
import { userGuard } from './core/guards/user.guard';

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
        path: 'predictions',
        canActivate: [userGuard],
        loadComponent: () =>
          import('./features/predictions/prediction-page').then((m) => m.PredictionPage),
      },
      {
        path: 'admin/predictions',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./features/predictions/admin-predictions-page').then(
            (m) => m.AdminPredictionsPage,
          ),
      },
      {
        path: 'admin/evaluations',
        canActivate: [adminGuard],
        loadComponent: () =>
          import('./features/predictions/admin-evaluations-page').then(
            (m) => m.AdminEvaluationsPage,
          ),
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
        path: 'operations/export-eda/:id',
        loadComponent: () =>
          import('./features/operations-page/manage-eda/export-eda/export-eda').then(
            (m) => m.ExportEda,
          ),
      },
      {
        path: 'operations/delete-applications',
        canActivate: [adminGuard],
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
        path: 'notifications',
        loadComponent: () => import('./features/notifications/notifications-page').then((m) => m.NotificationsPage),
      },
      {
        path: 'eda',
        loadComponent: () => import('./features/eda-page/eda-page').then((m) => m.EdaPage),
      },
    ],
  },
  { path: 'developer-tools', component: DeveloperTools, children: [] },
];
