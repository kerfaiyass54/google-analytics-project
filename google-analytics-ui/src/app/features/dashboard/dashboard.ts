import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';

import { FreeVsPaid } from './free-vs-paid/free-vs-paid';
import { ApplicationCategory } from './application-category/application-category';
import { RatingsCategory } from './ratings-category/ratings-category';
import { ReviewsCategory } from './reviews-category/reviews-category';
import { RatingsStatistics } from './ratings-statistics/ratings-statistics';
import { ReviewsStatistics } from './reviews-statistics/reviews-statistics';
import { SizeStatistics } from './size-statistics/size-statistics';
import { PriceStatistics } from './price-statistics/price-statistics';
import { StatisticsService } from '../../core/services/statistics.service';
import { GooglePlayAppStatisticsResponse } from '../../shared/models/google-play-app-statistics';



@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
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
