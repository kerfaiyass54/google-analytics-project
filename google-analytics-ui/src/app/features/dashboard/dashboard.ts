import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';

import { StatisticsService } from '../../core/services/statistics.service';

import { GooglePlayAppStatisticsResponse } from '../../shared/models/google-play-app-statistics';

import { SidebarItem, SidebarPage } from '../../shared/components/sidebar-page/sidebar-page';

import { ScrollRevealDirective } from '../../shared/directives/scroll-reveal.directive';

import { FreeVsPaid } from './free-vs-paid/free-vs-paid';
import { ApplicationCategory } from './application-category/application-category';
import { RatingsCategory } from './ratings-category/ratings-category';
import { ReviewsCategory } from './reviews-category/reviews-category';
import { RatingsStatistics } from './ratings-statistics/ratings-statistics';
import { ReviewsStatistics } from './reviews-statistics/reviews-statistics';
import { SizeStatistics } from './size-statistics/size-statistics';
import { PriceStatistics } from './price-statistics/price-statistics';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    SidebarPage,
    ScrollRevealDirective,

    FreeVsPaid,
    ApplicationCategory,
    RatingsCategory,
    ReviewsCategory,
    RatingsStatistics,
    ReviewsStatistics,
    SizeStatistics,
    PriceStatistics,
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Dashboard implements OnInit {
  private readonly statisticsService = inject(StatisticsService);

  readonly stats = signal<GooglePlayAppStatisticsResponse | null>(null);

  readonly loading = signal(true);

  readonly error = signal<string | null>(null);

  /**
   * Sidebar navigation for the dashboard sections.
   *
   * The IDs here must match the IDs used by the
   * dashboard sections in dashboard.html.
   */
  readonly sidebarItems: SidebarItem[] = [
    {
      id: 'free-paid',
      name: 'Free vs Paid',
      icon: 'bi bi-pie-chart-fill',
    },
    {
      id: 'applications-category',
      name: 'Applications',
      icon: 'bi bi-grid-fill',
    },
    {
      id: 'ratings-category',
      name: 'Ratings',
      icon: 'bi bi-star-fill',
    },
    {
      id: 'reviews-category',
      name: 'Reviews',
      icon: 'bi bi-chat-square-text-fill',
    },
    {
      id: 'rating-statistics',
      name: 'Rating Statistics',
      icon: 'bi bi-bar-chart-fill',
    },
    {
      id: 'review-statistics',
      name: 'Review Statistics',
      icon: 'bi bi-graph-up',
    },
    {
      id: 'size-statistics',
      name: 'Size Statistics',
      icon: 'bi bi-phone-fill',
    },
    {
      id: 'price-statistics',
      name: 'Price Statistics',
      icon: 'bi bi-currency-dollar',
    },
  ];

  ngOnInit(): void {
    this.loadStatistics();
  }

  // =========================================================
  // LOAD STATISTICS
  // =========================================================

  private loadStatistics(): void {
    this.loading.set(true);
    this.error.set(null);

    this.statisticsService.getStatistics().subscribe({
      next: (response) => {
        this.stats.set(response);
        this.loading.set(false);
      },

      error: (error: unknown) => {
        console.error('Failed to load dashboard statistics:', error);

        this.stats.set(null);

        this.error.set('Unable to load dashboard statistics. Please try again.');

        this.loading.set(false);
      },
    });
  }

  // =========================================================
  // RETRY
  // =========================================================

  retry(): void {
    this.loadStatistics();
  }
}
