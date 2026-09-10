import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableRequest,
  PaginatedTableResponse,
} from '../paginated-table/paginated-table';
import { CardSimple } from '../card-simple/card-simple';
import { CardDetails } from '../card-details/card-details';

interface GooglePlayApp {
  id: number;
  app: string;
  category: string;
  rating: number | null;
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
  imports: [PaginatedTable, CardSimple, CardDetails],
  templateUrl: './developer-tools.html',
  styleUrl: './developer-tools.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeveloperTools {
  // ==========================================================
  // TABLE COLUMNS
  // ==========================================================

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
  ];

  // ==========================================================
  // MOCK DATA
  // ==========================================================

  private readonly applications: GooglePlayApp[] = [
    {
      id: 1,
      app: 'Google Maps',
      category: 'TRAVEL_AND_LOCAL',
      rating: 4.5,
      reviews: 1815203,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Travel & Local',
      lastUpdated: '2026-08-20',
      currentVersion: '12.45.1',
      androidVersion: '5.0 and up',
    },
    {
      id: 2,
      app: 'Facebook',
      category: 'SOCIAL',
      rating: 4.1,
      reviews: 78158306,
      installs: '5,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Social',
      lastUpdated: '2026-08-18',
      currentVersion: '520.0.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 3,
      app: 'Instagram',
      category: 'SOCIAL',
      rating: 4.5,
      reviews: 66577313,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Social',
      lastUpdated: '2026-08-21',
      currentVersion: '395.0.0',
      androidVersion: '9.0 and up',
    },
    {
      id: 4,
      app: 'Spotify Music',
      category: 'MUSIC_AND_AUDIO',
      rating: 4.6,
      reviews: 22148593,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Music & Audio',
      lastUpdated: '2026-08-19',
      currentVersion: '9.2.10',
      androidVersion: '6.0 and up',
    },
    {
      id: 5,
      app: 'Netflix',
      category: 'VIDEO_PLAYERS',
      rating: 4.4,
      reviews: 12345678,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Video Players & Editors',
      lastUpdated: '2026-08-15',
      currentVersion: '8.145.0',
      androidVersion: '7.0 and up',
    },
    {
      id: 6,
      app: 'Duolingo',
      category: 'EDUCATION',
      rating: 4.7,
      reviews: 2567890,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Education',
      lastUpdated: '2026-08-17',
      currentVersion: '6.42.2',
      androidVersion: '6.0 and up',
    },
    {
      id: 7,
      app: 'Adobe Lightroom',
      category: 'PHOTOGRAPHY',
      rating: 4.3,
      reviews: 2456789,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Photography',
      lastUpdated: '2026-08-12',
      currentVersion: '10.5.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 8,
      app: 'Minecraft',
      category: 'GAME',
      rating: 4.6,
      reviews: 5123456,
      installs: '50,000,000+',
      type: 'Paid',
      price: 7.49,
      contentRating: 'Everyone 10+',
      genres: 'Adventure',
      lastUpdated: '2026-08-10',
      currentVersion: '1.21.50',
      androidVersion: '8.0 and up',
    },
    {
      id: 9,
      app: 'Microsoft Word',
      category: 'PRODUCTIVITY',
      rating: 4.4,
      reviews: 4856789,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2026-08-14',
      currentVersion: '16.0.19000',
      androidVersion: '10 and up',
    },
    {
      id: 10,
      app: 'Canva',
      category: 'ART_AND_DESIGN',
      rating: 4.8,
      reviews: 1234567,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Art & Design',
      lastUpdated: '2026-08-16',
      currentVersion: '4.2.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 11,
      app: 'Notion',
      category: 'PRODUCTIVITY',
      rating: 4.5,
      reviews: 987654,
      installs: '50,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2026-08-13',
      currentVersion: '2.48.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 12,
      app: 'Telegram',
      category: 'COMMUNICATION',
      rating: 4.3,
      reviews: 14567890,
      installs: '1,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Communication',
      lastUpdated: '2026-08-11',
      currentVersion: '11.14.2',
      androidVersion: '6.0 and up',
    },
    {
      id: 13,
      app: 'Amazon Shopping',
      category: 'SHOPPING',
      rating: 4.4,
      reviews: 29876543,
      installs: '500,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Teen',
      genres: 'Shopping',
      lastUpdated: '2026-08-09',
      currentVersion: '30.12.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 14,
      app: 'Coursera',
      category: 'EDUCATION',
      rating: 4.6,
      reviews: 876543,
      installs: '10,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Education',
      lastUpdated: '2026-08-07',
      currentVersion: '6.1.2',
      androidVersion: '7.0 and up',
    },
    {
      id: 15,
      app: 'Todoist',
      category: 'PRODUCTIVITY',
      rating: 4.5,
      reviews: 345678,
      installs: '10,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2026-08-06',
      currentVersion: '9.12.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 16,
      app: '1Password',
      category: 'TOOLS',
      rating: 4.6,
      reviews: 234567,
      installs: '5,000,000+',
      type: 'Paid',
      price: 2.99,
      contentRating: 'Everyone',
      genres: 'Tools',
      lastUpdated: '2026-08-05',
      currentVersion: '8.10.50',
      androidVersion: '9.0 and up',
    },
    {
      id: 17,
      app: 'Khan Academy',
      category: 'EDUCATION',
      rating: 4.6,
      reviews: 567890,
      installs: '10,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Education',
      lastUpdated: '2026-08-04',
      currentVersion: '8.2.1',
      androidVersion: '6.0 and up',
    },
    {
      id: 18,
      app: 'Shazam',
      category: 'MUSIC_AND_AUDIO',
      rating: 4.8,
      reviews: 8123456,
      installs: '500,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Music & Audio',
      lastUpdated: '2026-08-03',
      currentVersion: '15.20.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 19,
      app: 'Evernote',
      category: 'PRODUCTIVITY',
      rating: 4.2,
      reviews: 1789456,
      installs: '100,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2026-08-02',
      currentVersion: '10.100.0',
      androidVersion: '8.0 and up',
    },
    {
      id: 20,
      app: 'Google Drive',
      category: 'PRODUCTIVITY',
      rating: 4.4,
      reviews: 6543210,
      installs: '5,000,000,000+',
      type: 'Free',
      price: 0,
      contentRating: 'Everyone',
      genres: 'Productivity',
      lastUpdated: '2026-08-01',
      currentVersion: '2.26.0',
      androidVersion: '8.0 and up',
    },
  ];

  // ==========================================================
  // TABLE RESPONSE
  // ==========================================================

  readonly tableResponse = signal<PaginatedTableResponse<GooglePlayApp>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  // ==========================================================
  // LOADING
  // ==========================================================

  readonly loading = signal<boolean>(false);

  // ==========================================================
  // INITIALIZATION
  // ==========================================================

  constructor() {
    this.loadApplications(0, 10, '');
  }

  // ==========================================================
  // LOCAL PAGINATION + SEARCH
  // ==========================================================

  loadApplications(page: number, size: number, search: string): void {
    this.loading.set(true);

    setTimeout(() => {
      const normalizedSearch = search.trim().toLowerCase();

      const filteredApplications =
        normalizedSearch.length === 0
          ? this.applications
          : this.applications.filter(
              (application) =>
                application.app.toLowerCase().includes(normalizedSearch) ||
                application.category.toLowerCase().includes(normalizedSearch) ||
                application.genres.toLowerCase().includes(normalizedSearch) ||
                application.type.toLowerCase().includes(normalizedSearch),
            );

      const totalElements = filteredApplications.length;

      const totalPages = Math.ceil(totalElements / size);

      const startIndex = page * size;

      const endIndex = startIndex + size;

      const content = filteredApplications.slice(startIndex, endIndex);

      this.tableResponse.set({
        content,
        page,
        size,
        totalElements,
        totalPages,
      });

      this.loading.set(false);
    }, 300);
  }

  // ==========================================================
  // TABLE PAGINATION / SEARCH
  // ==========================================================

  onPageChange(request: PaginatedTableRequest): void {
    this.loadApplications(request.page, request.size, request.search);
  }
}
