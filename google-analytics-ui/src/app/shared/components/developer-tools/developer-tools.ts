import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableRequest,
  PaginatedTableResponse,
} from '../paginated-table/paginated-table';
import { SidebarItem, SidebarPage } from '../sidebar-page/sidebar-page';



export interface GooglePlayApp {
  id: number;
  app: string;
  category: string;
  rating: number;
  reviews: number;
  installs: string;
  type: string;
  price: number;
  contentRating: string;
  genres: string;
  lastUpdated: string;
  currentVersion: string;
  androidVersion: string;
}

@Component({
  selector: 'app-developer-tools',
  standalone: true,
  imports: [PaginatedTable, SidebarPage],
  templateUrl: './developer-tools.html',
  styleUrl: './developer-tools.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeveloperTools {
  // ============================================================
  // SIDEBAR
  // ============================================================

  readonly sidebarItems: SidebarItem[] = [
    {
      id: 'developer-overview',
      name: 'Overview',
      icon: 'bi bi-speedometer2',
    },
    {
      id: 'developer-applications',
      name: 'Applications',
      icon: 'bi bi-grid-3x3-gap-fill',
    },
    {
      id: 'developer-statistics',
      name: 'Statistics',
      icon: 'bi bi-bar-chart-fill',
    },
    {
      id: 'developer-analytics',
      name: 'Analytics',
      icon: 'bi bi-graph-up-arrow',
    },
  ];

  // ============================================================
  // TABLE COLUMNS
  // ============================================================

  readonly columns: PaginatedTableColumn[] = [
    {
      key: 'app',
      label: 'Application',
      type: 'text',
    },
    {
      key: 'category',
      label: 'Category',
      type: 'text',
    },
    {
      key: 'rating',
      label: 'Rating',
      type: 'number',
    },
    {
      key: 'reviews',
      label: 'Reviews',
      type: 'number',
    },
    {
      key: 'installs',
      label: 'Installs',
      type: 'text',
    },
    {
      key: 'type',
      label: 'Type',
      type: 'badge',
    },
    {
      key: 'price',
      label: 'Price',
      type: 'number',
    },
  ];

  // ============================================================
  // MOCK DATA
  // ============================================================

  private readonly applications: GooglePlayApp[] = [
    {
      id: 1,
      app: 'Photo Editor Pro',
      category: 'PHOTOGRAPHY',
      rating: 4.5,
      reviews: 125430,
      installs: '10,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Photography',
      lastUpdated: '2025-08-12',
      currentVersion: '4.2.1',
      androidVersion: '5.0 and up',
    },
    {
      id: 2,
      app: 'Google Maps',
      category: 'TRAVEL_AND_LOCAL',
      rating: 4.3,
      reviews: 4523100,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Travel & Local',
      lastUpdated: '2025-08-20',
      currentVersion: '11.45',
      androidVersion: '6.0 and up',
    },
    {
      id: 3,
      app: 'Spotify Music',
      category: 'MUSIC_AND_AUDIO',
      rating: 4.4,
      reviews: 1892300,
      installs: '500,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Music & Audio',
      lastUpdated: '2025-08-18',
      currentVersion: '9.1.0',
      androidVersion: '6.0 and up',
    },
    {
      id: 4,
      app: 'Netflix',
      category: 'VIDEO_PLAYERS',
      rating: 4.2,
      reviews: 1625400,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Video Players & Editors',
      lastUpdated: '2025-08-21',
      currentVersion: '8.120',
      androidVersion: '7.0 and up',
    },
    {
      id: 5,
      app: 'Minecraft',
      category: 'GAME',
      rating: 4.6,
      reviews: 4832100,
      installs: '50,000,000+',
      type: 'Paid',
      price: 7.49,
      contentRating: 'Everyone 10+',
      genres: 'Arcade',
      lastUpdated: '2025-08-10',
      currentVersion: '1.21.20',
      androidVersion: '8.0 and up',
    },
    {
      id: 6,
      app: 'WhatsApp Messenger',
      category: 'COMMUNICATION',
      rating: 4.4,
      reviews: 13245000,
      installs: '5,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Communication',
      lastUpdated: '2025-08-22',
      currentVersion: '2.25.18',
      androidVersion: '5.0 and up',
    },
    {
      id: 7,
      app: 'Duolingo',
      category: 'EDUCATION',
      rating: 4.7,
      reviews: 2154300,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Education',
      lastUpdated: '2025-08-19',
      currentVersion: '6.48',
      androidVersion: '7.0 and up',
    },
    {
      id: 8,
      app: 'Adobe Lightroom',
      category: 'PHOTOGRAPHY',
      rating: 4.5,
      reviews: 985400,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Photography',
      lastUpdated: '2025-08-17',
      currentVersion: '10.4',
      androidVersion: '8.0 and up',
    },
    {
      id: 9,
      app: 'Google Drive',
      category: 'PRODUCTIVITY',
      rating: 4.3,
      reviews: 4215600,
      installs: '5,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2025-08-21',
      currentVersion: '2.25',
      androidVersion: '6.0 and up',
    },
    {
      id: 10,
      app: 'Canva',
      category: 'PRODUCTIVITY',
      rating: 4.7,
      reviews: 1265400,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2025-08-20',
      currentVersion: '4.85',
      androidVersion: '8.0 and up',
    },
    {
      id: 11,
      app: 'Microsoft Word',
      category: 'PRODUCTIVITY',
      rating: 4.5,
      reviews: 4521000,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2025-08-18',
      currentVersion: '16.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 12,
      app: 'Telegram',
      category: 'COMMUNICATION',
      rating: 4.5,
      reviews: 8542100,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Communication',
      lastUpdated: '2025-08-22',
      currentVersion: '11.5',
      androidVersion: '6.0 and up',
    },
    {
      id: 13,
      app: 'Amazon Shopping',
      category: 'SHOPPING',
      rating: 4.3,
      reviews: 3421500,
      installs: '500,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Shopping',
      lastUpdated: '2025-08-16',
      currentVersion: '28.12',
      androidVersion: '8.0 and up',
    },
    {
      id: 14,
      app: 'Coursera',
      category: 'EDUCATION',
      rating: 4.6,
      reviews: 185400,
      installs: '10,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Education',
      lastUpdated: '2025-08-14',
      currentVersion: '6.9',
      androidVersion: '7.0 and up',
    },
    {
      id: 15,
      app: 'Calm',
      category: 'HEALTH_AND_FITNESS',
      rating: 4.4,
      reviews: 492300,
      installs: '50,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Health & Fitness',
      lastUpdated: '2025-08-13',
      currentVersion: '6.42',
      androidVersion: '7.0 and up',
    },
    {
      id: 16,
      app: 'Todoist',
      category: 'PRODUCTIVITY',
      rating: 4.6,
      reviews: 325600,
      installs: '10,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2025-08-15',
      currentVersion: '9.12',
      androidVersion: '8.0 and up',
    },
    {
      id: 17,
      app: 'PUBG Mobile',
      category: 'GAME',
      rating: 4.3,
      reviews: 18745000,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Action',
      lastUpdated: '2025-08-21',
      currentVersion: '3.9.0',
      androidVersion: '5.1 and up',
    },
    {
      id: 18,
      app: 'Shazam',
      category: 'MUSIC_AND_AUDIO',
      rating: 4.8,
      reviews: 872300,
      installs: '500,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Music & Audio',
      lastUpdated: '2025-08-19',
      currentVersion: '14.32',
      androidVersion: '8.0 and up',
    },
    {
      id: 19,
      app: 'Forest',
      category: 'PRODUCTIVITY',
      rating: 4.5,
      reviews: 62500,
      installs: '10,000,000+',
      type: 'Paid',
      price: 1.99,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2025-08-11',
      currentVersion: '4.75',
      androidVersion: '6.0 and up',
    },
    {
      id: 20,
      app: 'Notion',
      category: 'PRODUCTIVITY',
      rating: 4.4,
      reviews: 185600,
      installs: '50,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2025-08-20',
      currentVersion: '0.6.5',
      androidVersion: '8.0 and up',
    },
  ];

  // ============================================================
  // TABLE STATE
  // ============================================================

  readonly tableResponse = signal<PaginatedTableResponse<GooglePlayApp>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  readonly loading = signal<boolean>(false);

  // ============================================================
  // CONSTRUCTOR
  // ============================================================

  constructor() {
    this.loadApplications(0, 10, '');
  }

  // ============================================================
  // PAGINATION / SEARCH
  // ============================================================

  onPageChange(request: PaginatedTableRequest): void {
    this.loadApplications(request.page, request.size, request.search);
  }

  private loadApplications(page: number, size: number, search: string): void {
    this.loading.set(true);

    setTimeout(() => {
      const normalizedSearch = search.trim().toLowerCase();

      const filteredApplications =
        normalizedSearch.length === 0
          ? this.applications
          : this.applications.filter((application) =>
              [
                application.app,
                application.category,
                application.genres,
                application.type,
                application.contentRating,
              ].some((value) => value.toLowerCase().includes(normalizedSearch)),
            );

      const totalElements = filteredApplications.length;

      const totalPages = totalElements === 0 ? 0 : Math.ceil(totalElements / size);

      const safePage = totalPages === 0 ? 0 : Math.min(page, totalPages - 1);

      const startIndex = safePage * size;
      const endIndex = startIndex + size;

      const content = filteredApplications.slice(startIndex, endIndex);

      this.tableResponse.set({
        content,
        page: safePage,
        size,
        totalElements,
        totalPages,
      });

      this.loading.set(false);
    }, 300);
  }
}
