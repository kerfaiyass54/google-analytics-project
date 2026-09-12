import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  GooglePlayAppService,
  GooglePlayAppPage,
} from '../../../core/services/google-play-app.service';

import { GooglePlayAppResponse } from '../../../shared/models/google-play-app';

import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableResponse,

} from '../../../shared/components/paginated-table/paginated-table';

import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';

@Component({
  selector: 'app-delete-applications',
  standalone: true,
  imports: [CommonModule, PaginatedTable, ConfirmDialog],
  templateUrl: './delete-applications.html',
  styleUrl: './delete-applications.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeleteApplications implements OnInit {
  private readonly appService = inject(GooglePlayAppService);

  readonly loading = signal(false);
  readonly deleting = signal(false);

  readonly confirmVisible = signal(false);

  readonly errorMessage = signal('');
  readonly successMessage = signal('');

  readonly selectedIds = signal<Set<number>>(new Set());

  readonly columns: PaginatedTableColumn[] = [
    {
      key: 'app',
      label: 'Application',
    },
    {
      key: 'category',
      label: 'Category',
    },
    {
      key: 'rating',
      label: 'Rating',
    },
    {
      key: 'reviews',
      label: 'Reviews',
    },
    {
      key: 'type',
      label: 'Type',
    },
    {
      key: 'lastUpdated',
      label: 'Last Updated',
    },
  ];

  /**
   * Row action shown by PaginatedTable.
   *
   * The label can be changed to anything:
   * "Delete", "View", "Edit", "Details", etc.
   */
  readonly rowAction: any = {
    label: 'Delete',
    icon: 'bi bi-trash3',
    condition: (app:any) => app.id > 0,
  };

  readonly tableResponse = signal<PaginatedTableResponse<GooglePlayAppResponse>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  onTableAction(apps: GooglePlayAppResponse[]): void {
    this.selectedIds.set(new Set(apps.map((app) => app.id)));

    this.errorMessage.set('');
    this.successMessage.set('');

    this.openDeleteConfirmation();
  }

  ngOnInit(): void {
    this.loadApps(0, 10);
  }

  loadApps(page: number, size: number): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.appService.findAll(page, size).subscribe({
      next: (response: GooglePlayAppPage) => {
        this.tableResponse.set({
          content: response.content,
          page: response.number,
          size: response.size,
          totalElements: response.totalElements,
          totalPages: response.totalPages,
        });

        this.loading.set(false);
      },

      error: (error) => {
        console.error('Failed to load applications:', error);

        this.errorMessage.set(error?.error?.message ?? 'Failed to load applications.');

        this.loading.set(false);
      },
    });
  }

  onPageChange(event: { page: number; size: number; search?: string }): void {
    this.loadApps(event.page, event.size);
  }

  /**
   * Called by PaginatedTable whenever the selection changes.
   */
  onSelectionChange(apps: GooglePlayAppResponse[]): void {
    this.selectedIds.set(new Set(apps.map((app) => app.id)));
  }

  /**
   * Only applications satisfying this condition
   * can be selected.
   *
   * This is where the business rule belongs.
   */
  canSelectApplication(app: GooglePlayAppResponse): boolean {
    return app.id > 0;
  }

  /**
   * Called when the row action button is clicked.
   */
  onRowAction(app: GooglePlayAppResponse): void {
    this.errorMessage.set('');
    this.successMessage.set('');

    this.selectedIds.set(new Set([app.id]));
    this.confirmVisible.set(true);
  }

  clearSelection(): void {
    this.selectedIds.set(new Set());
  }

  get selectedCount(): number {
    return this.selectedIds().size;
  }

  openDeleteConfirmation(): void {
    if (this.selectedIds().size === 0) {
      this.errorMessage.set('Please select at least one application.');
      return;
    }

    this.errorMessage.set('');
    this.successMessage.set('');
    this.confirmVisible.set(true);
  }

  cancelDelete(): void {
    this.confirmVisible.set(false);
  }

  confirmDelete(): void {
    const ids = Array.from(this.selectedIds());

    if (ids.length === 0) {
      this.confirmVisible.set(false);
      return;
    }

    this.deleting.set(true);
    this.confirmVisible.set(false);
    this.errorMessage.set('');
    this.successMessage.set('');

    const deleteRequests = ids.map((id) => this.appService.delete(id));

    let completed = 0;
    let failed = false;

    deleteRequests.forEach((request) => {
      request.subscribe({
        next: () => {
          completed++;

          if (completed === deleteRequests.length && !failed) {
            this.onDeleteSuccess();
          }
        },

        error: (error) => {
          if (failed) {
            return;
          }

          failed = true;

          console.error('Failed to delete application:', error);

          this.deleting.set(false);

          this.errorMessage.set(
            error?.error?.message ?? 'One or more applications could not be deleted.',
          );
        },
      });
    });
  }

  private onDeleteSuccess(): void {
    const deletedCount = this.selectedIds().size;

    this.selectedIds.set(new Set());

    this.successMessage.set(
      `${deletedCount} application${deletedCount === 1 ? '' : 's'} deleted successfully.`,
    );

    this.deleting.set(false);

    const currentPage = this.tableResponse().page;
    const pageSize = this.tableResponse().size;

    this.loadApps(currentPage, pageSize);
  }
}
