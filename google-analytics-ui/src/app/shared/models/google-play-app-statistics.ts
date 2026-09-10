export interface GooglePlayAppStatisticsResponse {
  totalApps: number;

  freeApps: number;

  paidApps: number;

  averageRating: number;

  minimumRating: number;

  maximumRating: number;

  averageReviews: number;

  minimumReviews: number;

  maximumReviews: number;

  averageSizeMb: number;

  minimumSizeMb: number;

  maximumSizeMb: number;

  averagePrice: number;

  minimumPrice: number;

  maximumPrice: number;

  oldestLastUpdated: string;

  newestLastUpdated: string;

  categories: CategoryStatistics[];
}

export interface CategoryStatistics {
  category: string;

  appCount: number;

  averageRating: number;

  totalReviews: number;
}
