import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';

import { GooglePlayAppService } from '../../core/services/google-play-app.service';

import { GooglePlayAppPage } from '../../core/services/google-play-app.service';

import { GooglePlayAppResponse } from '../../shared/models/google-play-app';

import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableRequest,
  PaginatedTableResponse,
} from '../../shared/components/paginated-table/paginated-table';

import { CardDetails } from '../../shared/components/card-details/card-details';

@Component({
  selector: 'app-list-applications',
  standalone: true,
  imports: [PaginatedTable, CardDetails],
  templateUrl: './list-applications.html',
  styleUrl: './list-applications.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListApplications implements OnInit {
  private readonly googlePlayAppService = inject(GooglePlayAppService);

  // ==========================================================
  // TABLE
  // ==========================================================

  readonly tableLoading = signal(false);

  readonly tableError = signal<string | null>(null);

  readonly tableResponse = signal<PaginatedTableResponse<GooglePlayAppResponse>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  readonly tableColumns: PaginatedTableColumn[] = [
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

  // ==========================================================
  // DETAILS DIALOG
  // ==========================================================

  readonly selectedApplication = signal<GooglePlayAppResponse | null>(null);

  readonly detailsLoading = signal(false);

  readonly detailsError = signal<string | null>(null);

  readonly detailsOpen = signal(false);

  // ==========================================================
  // DETAILS ATTRIBUTES
  // ==========================================================

  readonly detailAttributes: string[] = [
    'Application',
    'Category',
    'Rating',
    'Reviews',
    'Size',
    'Installs',
    'Type',
    'Price',
    'Content Rating',
    'Genres',
    'Last Updated',
    'Current Version',
    'Android Version',
  ];

  // ==========================================================
  // INIT
  // ==========================================================

  ngOnInit(): void {
    this.loadApplications(0, 10);
  }

  // ==========================================================
  // LOAD APPLICATIONS
  // ==========================================================

  private loadApplications(page: number, size: number): void {
    this.tableLoading.set(true);
    this.tableError.set(null);

    this.googlePlayAppService.findAll(page, size).subscribe({
      next: (response: GooglePlayAppPage) => {
        this.tableResponse.set({
          content: response.content,
          page: response.number,
          size: response.size,
          totalElements: response.totalElements,
          totalPages: response.totalPages,
        });

        this.tableLoading.set(false);
      },

      error: (error: unknown) => {
        console.error('Failed to load Google Play applications:', error);

        this.tableLoading.set(false);

        this.tableError.set('Unable to load applications. Please try again.');

        this.tableResponse.set({
          content: [],
          page: 0,
          size,
          totalElements: 0,
          totalPages: 0,
        });
      },
    });
  }

  // ==========================================================
  // TABLE PAGINATION
  // ==========================================================

  onPageChange(request: PaginatedTableRequest): void {
    this.loadApplications(request.page, request.size);
  }

  // ==========================================================
  // ROW CLICK
  // ==========================================================

  onTableClick(event: MouseEvent): void {
    const target = event.target;

    if (!(target instanceof HTMLElement)) {
      return;
    }

    const row = target.closest('tr.table-row');

    if (!row) {
      return;
    }

    const tableRows = Array.from(row.parentElement?.querySelectorAll('tr.table-row') ?? []);

    const rowIndex = tableRows.indexOf(row);

    if (rowIndex < 0) {
      return;
    }

    const applications = this.tableResponse().content;

    const application = applications[rowIndex];

    if (!application) {
      return;
    }

    this.openDetails(application.id);
  }

  // ==========================================================
  // OPEN DETAILS
  // ==========================================================

  private openDetails(id: number): void {
    this.detailsLoading.set(true);
    this.detailsError.set(null);
    this.selectedApplication.set(null);
    this.detailsOpen.set(true);

    requestAnimationFrame(() => {
      const dialog = document.getElementById(
        'application-details-dialog',
      ) as HTMLDialogElement | null;

      if (dialog && !dialog.open) {
        dialog.showModal();
      }
    });

    this.googlePlayAppService.getDetails(id).subscribe({
      next: (application) => {
        this.selectedApplication.set(application);
        this.detailsLoading.set(false);
      },

      error: (error: unknown) => {
        console.error('Failed to load application details:', error);

        this.detailsLoading.set(false);

        this.detailsError.set('Unable to load application details.');
      },
    });
  }

  // ==========================================================
  // CLOSE DETAILS
  // ==========================================================

  closeDetails(): void {
    const dialog = document.getElementById(
      'application-details-dialog',
    ) as HTMLDialogElement | null;

    if (dialog?.open) {
      dialog.close();
    }

    this.detailsOpen.set(false);
    this.selectedApplication.set(null);
    this.detailsError.set(null);
  }

  // ==========================================================
  // CLOSE WHEN CLICKING BACKDROP
  // ==========================================================

  onDialogClick(event: MouseEvent): void {
    const target = event.target;

    if (target instanceof HTMLDialogElement) {
      this.closeDetails();
    }
  }

  // ==========================================================
  // DETAILS VALUES
  // ==========================================================

  get detailValues(): unknown[] {
    const application = this.selectedApplication();

    if (!application) {
      return [];
    }

    return [
      application.app,
      application.category,
      application.rating,
      application.reviews.toLocaleString(),
      `${application.sizeMb.toFixed(2)} MB`,
      application.installs,
      application.type,
      this.formatPrice(application.price),
      application.contentRating,
      application.genres,
      application.lastUpdated,
      application.currentVersion,
      application.androidVersion,
    ];
  }

  // ==========================================================
  // FORMAT PRICE
  // ==========================================================

  private formatPrice(price: number): string {
    if (price === 0) {
      return 'Free';
    }

    return `$${price.toFixed(2)}`;
  }
}
