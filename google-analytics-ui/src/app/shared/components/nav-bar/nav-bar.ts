import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
})
export class NavBar {
  readonly navigationItems = [
    {
      label: 'Home',
      icon: 'bi-grid-1x2-fill',
      route: '/dashboard',
    },
    {
      label: 'Apps',
      icon: 'bi-phone-fill',
      route: '/applications',
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
}
