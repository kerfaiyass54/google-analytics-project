import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  signal,
} from '@angular/core';
import { ChartOptions } from 'chart.js';
import { forkJoin } from 'rxjs';

import { EdaService } from '../../core/services/eda.service';

import {
  SidebarItem,
  SidebarPage,
} from '../../shared/components/sidebar-page/sidebar-page';

import { BarChart } from '../../shared/components/charts/bar-chart/bar-chart';
import { LineChart } from '../../shared/components/charts/line-chart/line-chart';
import { PieChart } from '../../shared/components/charts/pie-chart/pie-chart';
import { ChartDataset } from '../../shared/models/chart.model';



/*
 * ============================================================
 * EDA 01
 * ============================================================
 */

interface RatingCategory {
  category: string;
  app_count: number;
  rated_app_count: number;
  average_rating: number | null;
  minimum_rating: number | null;
  maximum_rating: number | null;
  median_rating: number | null;
  rating_stddev: number | null;
}

interface RatingsByCategoryResponse {
  analyzed_at: string;
  total_categories: number;
  total_rated_applications: number;
  overall_average_rating: number | null;
  categories: RatingCategory[];
}


/*
 * ============================================================
 * EDA 02
 * ============================================================
 */

interface FreePaidApplication {
  type: string;
  app_count: number;
  rated_app_count: number;
  average_rating: number | null;
  median_rating: number | null;
  average_reviews: number | null;
  median_reviews: number | null;
  total_reviews: number;
  average_price: number | null;
  minimum_price: number | null;
  maximum_price: number | null;
}

interface FreeVsPaidResponse {
  analyzed_at: string;
  free_applications: number;
  paid_applications: number;
  free_percentage: number;
  paid_percentage: number;
  average_rating_difference: number | null;
  average_reviews_difference: number | null;
  applications: FreePaidApplication[];
}


/*
 * ============================================================
 * EDA 03
 * ============================================================
 */

interface InstallDistributionItem {
  installs: string;
  installs_numeric: number;
  app_count: number;
  percentage: number;
}

interface InstallCategory {
  category: string;
  app_count: number;
  average_installs: number | null;
  median_installs: number | null;
  minimum_installs: number;
  maximum_installs: number;
  total_installs: number;
}

interface TopInstalledApplication {
  app: string;
  category: string;
  rating: number | null;
  reviews: number;
  installs: string;
  installs_numeric: number;
  type: string;
}

interface InstallDistributionResponse {
  analyzed_at: string;
  total_applications: number;
  total_installs: number;
  average_installs: number | null;
  median_installs: number | null;
  distribution: InstallDistributionItem[];
  categories: InstallCategory[];
  top_applications: TopInstalledApplication[];
}


/*
 * ============================================================
 * EDA 04
 * ============================================================
 */

interface ReviewStatistics {
  app_count: number;
  average_reviews: number | null;
  median_reviews: number | null;
  minimum_reviews: number | null;
  maximum_reviews: number | null;
  review_stddev: number | null;
  total_reviews: number;
}

interface ReviewCategory {
  category: string;
  app_count: number;
  average_reviews: number | null;
  median_reviews: number | null;
  total_reviews: number;
  maximum_reviews: number | null;
}

interface TopReviewedApplication {
  app: string;
  category: string;
  rating: number | null;
  reviews: number;
  installs: string;
  type: string;
}

interface ReviewsVsInstalls {
  app: string;
  category: string;
  rating: number | null;
  reviews: number;
  installs: string;
  installs_numeric: number;
  type: string;
}

interface ReviewCountsResponse {
  analyzed_at: string;
  statistics: ReviewStatistics;
  categories: ReviewCategory[];
  top_applications: TopReviewedApplication[];
  reviews_vs_installs: ReviewsVsInstalls[];
}


@Component({
  selector: 'app-eda-page',
  standalone: true,
  imports: [
    SidebarPage,
    BarChart,
    LineChart,
    PieChart,
  ],
  templateUrl: './eda-page.html',
  styleUrl: './eda-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EdaPage implements OnInit {

  private readonly edaService = new EdaService();

  /*
   * ============================================================
   * STATE
   * ============================================================
   */

  readonly loading = signal(true);

  readonly error = signal<string | null>(null);

  readonly ratings = signal<RatingsByCategoryResponse | null>(null);

  readonly freeVsPaid = signal<FreeVsPaidResponse | null>(null);

  readonly installs = signal<InstallDistributionResponse | null>(null);

  readonly reviews = signal<ReviewCountsResponse | null>(null);


  /*
   * ============================================================
   * SIDEBAR
   * ============================================================
   */

  readonly sidebarItems: SidebarItem[] = [
    {
      id: 'eda-ratings',
      name: 'Ratings',
      icon: 'bi bi-star',
    },
    {
      id: 'eda-free-paid',
      name: 'Free vs Paid',
      icon: 'bi bi-pie-chart',
    },
    {
      id: 'eda-installs',
      name: 'Installations',
      icon: 'bi bi-download',
    },
    {
      id: 'eda-reviews',
      name: 'Reviews',
      icon: 'bi bi-chat-left-text',
    },
  ];


  /*
   * ============================================================
   * CHART OPTIONS
   * ============================================================
   */

  readonly categoryBarOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 5,
        title: {
          display: true,
          text: 'Average rating',
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  };


  readonly comparisonBarOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };


  readonly installDistributionOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Applications',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };


  readonly pieOptions: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
      },
    },
  };


  /*
   * ============================================================
   * CHART DATA
   * ============================================================
   */

  readonly ratingsLabels = signal<string[]>([]);

  readonly ratingsDataset = signal<ChartDataset[]>([]);


  readonly freePaidLabels = signal<string[]>([
    'Free',
    'Paid',
  ]);

  readonly freePaidDataset = signal<ChartDataset[]>([]);


  readonly freePaidRatingLabels = signal<string[]>([
    'Free',
    'Paid',
  ]);

  readonly freePaidRatingDataset = signal<ChartDataset[]>([]);


  readonly installDistributionLabels = signal<string[]>([]);

  readonly installDistributionDataset = signal<ChartDataset[]>([]);


  readonly installCategoryLabels = signal<string[]>([]);

  readonly installCategoryDataset = signal<ChartDataset[]>([]);


  readonly reviewCategoryLabels = signal<string[]>([]);

  readonly reviewCategoryDataset = signal<ChartDataset[]>([]);


  readonly topReviewedLabels = signal<string[]>([]);

  readonly topReviewedDataset = signal<ChartDataset[]>([]);


  /*
   * ============================================================
   * LIFECYCLE
   * ============================================================
   */

  ngOnInit(): void {
    this.loadAllAnalyses();
  }


  /*
   * ============================================================
   * LOAD ALL FOUR EDAS
   * ============================================================
   */

  private loadAllAnalyses(): void {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      ratings: this.edaService.getRatingsByCategory(),
      freeVsPaid: this.edaService.getFreeVsPaid(),
      installs: this.edaService.getInstallDistribution(),
      reviews: this.edaService.getReviewCounts(),
    }).subscribe({
      next: (response) => {
        this.ratings.set(
          response.ratings as RatingsByCategoryResponse
        );

        this.freeVsPaid.set(
          response.freeVsPaid as FreeVsPaidResponse
        );

        this.installs.set(
          response.installs as InstallDistributionResponse
        );

        this.reviews.set(
          response.reviews as ReviewCountsResponse
        );

        this.prepareCharts();

        this.loading.set(false);
      },

      error: () => {
        this.error.set(
          'Unable to load the EDA analyses. Please check that the FastAPI backend is running.'
        );

        this.loading.set(false);
      },
    });
  }


  /*
   * ============================================================
   * PREPARE CHARTS
   * ============================================================
   */

  private prepareCharts(): void {
    this.prepareRatingsChart();
    this.prepareFreePaidCharts();
    this.prepareInstallCharts();
    this.prepareReviewCharts();
  }


  /*
   * ============================================================
   * EDA 01 — RATINGS
   * ============================================================
   */

  private prepareRatingsChart(): void {
    const response = this.ratings();

    if (!response) {
      return;
    }

    const categories = response.categories ?? [];

    this.ratingsLabels.set(
      categories.map(
        (item) => item.category
      )
    );

    this.ratingsDataset.set([
      {
        label: 'Average rating',
        data: categories.map(
          (item) =>
            this.numberOrZero(
              item.average_rating
            )
        ),
        borderWidth: 0,
        borderRadius: 7,
        backgroundColor: 'rgba(99, 102, 241, 0.78)',
      },
    ]);
  }


  /*
   * ============================================================
   * EDA 02 — FREE VS PAID
   * ============================================================
   */

  private prepareFreePaidCharts(): void {
    const response = this.freeVsPaid();

    if (!response) {
      return;
    }

    this.freePaidDataset.set([
      {
        label: 'Applications',
        data: [
          response.free_applications,
          response.paid_applications,
        ],
        borderWidth: 1,
        backgroundColor: [
          'rgba(59, 130, 246, 0.82)',
          'rgba(168, 85, 247, 0.82)',
        ],
      },
    ]);

    const applications = response.applications ?? [];

    this.freePaidRatingDataset.set([
      {
        label: 'Average rating',
        data: [
          this.numberOrZero(
            applications.find(
              (item) => item.type === 'FREE'
            )?.average_rating
          ),
          this.numberOrZero(
            applications.find(
              (item) => item.type === 'PAID'
            )?.average_rating
          ),
        ],
        borderWidth: 0,
        borderRadius: 8,
        backgroundColor: [
          'rgba(59, 130, 246, 0.78)',
          'rgba(168, 85, 247, 0.78)',
        ],
      },
    ]);
  }


  /*
   * ============================================================
   * EDA 03 — INSTALLATIONS
   * ============================================================
   */

  private prepareInstallCharts(): void {
    const response = this.installs();

    if (!response) {
      return;
    }

    const distribution = response.distribution ?? [];

    this.installDistributionLabels.set(
      distribution.map(
        (item) => item.installs
      )
    );

    this.installDistributionDataset.set([
      {
        label: 'Applications',
        data: distribution.map(
          (item) => item.app_count
        ),
        borderWidth: 2,
        tension: 0.3,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6,
        backgroundColor: 'rgba(14, 165, 233, 0.12)',
        borderColor: 'rgba(14, 165, 233, 0.9)',
      },
    ]);

    const categories = (
      response.categories ?? []
    ).slice(0, 15);

    this.installCategoryLabels.set(
      categories.map(
        (item) => item.category
      )
    );

    this.installCategoryDataset.set([
      {
        label: 'Average installs',
        data: categories.map(
          (item) =>
            this.numberOrZero(
              item.average_installs
            )
        ),
        borderWidth: 0,
        borderRadius: 7,
        backgroundColor: 'rgba(16, 185, 129, 0.78)',
      },
    ]);
  }


  /*
   * ============================================================
   * EDA 04 — REVIEWS
   * ============================================================
   */

  private prepareReviewCharts(): void {
    const response = this.reviews();

    if (!response) {
      return;
    }

    const categories = (
      response.categories ?? []
    ).slice(0, 15);

    this.reviewCategoryLabels.set(
      categories.map(
        (item) => item.category
      )
    );

    this.reviewCategoryDataset.set([
      {
        label: 'Total reviews',
        data: categories.map(
          (item) => item.total_reviews
        ),
        borderWidth: 0,
        borderRadius: 7,
        backgroundColor: 'rgba(245, 158, 11, 0.78)',
      },
    ]);

    const topApplications = (
      response.top_applications ?? []
    ).slice(0, 10);

    this.topReviewedLabels.set(
      topApplications.map(
        (item) => this.shortLabel(item.app)
      )
    );

    this.topReviewedDataset.set([
      {
        label: 'Reviews',
        data: topApplications.map(
          (item) => item.reviews
        ),
        borderWidth: 0,
        borderRadius: 7,
        backgroundColor: 'rgba(239, 68, 68, 0.78)',
      },
    ]);
  }


  /*
   * ============================================================
   * HELPERS
   * ============================================================
   */

  numberOrZero(
    value: number | null | undefined
  ): number {
    if (
      value === null ||
      value === undefined ||
      !Number.isFinite(value)
    ) {
      return 0;
    }

    return value;
  }


  formatNumber(
    value: number | null | undefined
  ): string {
    if (
      value === null ||
      value === undefined ||
      !Number.isFinite(value)
    ) {
      return '—';
    }

    return new Intl.NumberFormat(
      'en-US',
      {
        maximumFractionDigits: 2,
      }
    ).format(value);
  }


  formatRating(
    value: number | null | undefined
  ): string {
    if (
      value === null ||
      value === undefined ||
      !Number.isFinite(value)
    ) {
      return '—';
    }

    return value.toFixed(2);
  }


  shortLabel(
    value: string
  ): string {
    if (value.length <= 24) {
      return value;
    }

    return `${value.substring(0, 21)}...`;
  }
}
