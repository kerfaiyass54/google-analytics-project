import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NavBar {
  readonly authService = inject(AuthService);

  readonly navigationItems = [
    {
      label: 'Home',
      icon: 'bi-grid-1x2-fill',
      route: '/dashboard',
    },
    {
      label: 'Applications',
      icon: 'bi-phone-fill',
      route: '/list',
    },
    {
      label: 'Operations',
      icon: 'bi-sliders2-vertical',
      route: '/operations',
    },
    {
      label: 'EDA',
      icon: 'bi-bar-chart-fill',
      route: '/eda',
    },
  ];

  async logout(): Promise<void> {
    await this.authService.logout();
  }
}
