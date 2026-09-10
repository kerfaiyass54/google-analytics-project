import { Routes } from '@angular/router';
import { HomePage } from './shared/components/home-page/home-page';
import { DeveloperTools } from './shared/components/developer-tools/developer-tools';

export const routes: Routes = [
  {
    path: '',
    component: HomePage,
    children: [],
  },
  {
    path: 'developer-tools',
    component: DeveloperTools,
    children: [],
  },
];
