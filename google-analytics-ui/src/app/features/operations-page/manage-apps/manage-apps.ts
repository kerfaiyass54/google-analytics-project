import { Component, HostListener, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import {
  GooglePlayAppService,
  GooglePlayAppPage,
} from '../../../core/services/google-play-app.service';

import { GooglePlayAppRequest } from '../../../shared/models/google-play-app-request';

import { GooglePlayAppResponse } from '../../../shared/models/google-play-app';

import { AppType } from '../../../shared/models/app-type';


import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableResponse,
} from '../../../shared/components/paginated-table/paginated-table';

@Component({
  selector: 'app-manage-apps',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, PaginatedTable],
  templateUrl: './manage-apps.html',
  styleUrl: './manage-apps.css',
})
export class ManageApps implements OnInit {
  private readonly appService = inject(GooglePlayAppService);
  private readonly fb = inject(FormBuilder);

  readonly AppType = AppType;

  readonly loading = signal(false);
  readonly saving = signal(false);

  readonly dialogVisible = signal(false);

  readonly selectedApp = signal<GooglePlayAppResponse | null>(null);

  readonly errorMessage = signal('');
  readonly successMessage = signal('');

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

  readonly tableResponse = signal<PaginatedTableResponse<GooglePlayAppResponse>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  readonly form = this.fb.nonNullable.group({
    app: ['', [Validators.required, Validators.maxLength(255)]],

    category: ['', [Validators.required, Validators.maxLength(100)]],

    rating: [0, [Validators.required, Validators.min(0), Validators.max(5)]],

    reviews: [0, [Validators.required, Validators.min(0)]],

    sizeMb: [0, [Validators.required, Validators.min(0)]],

    installs: ['', [Validators.required, Validators.maxLength(50)]],

    type: [AppType.FREE, [Validators.required]],

    price: [0, [Validators.required, Validators.min(0)]],

    contentRating: ['', [Validators.required, Validators.maxLength(50)]],

    genres: ['', [Validators.required, Validators.maxLength(255)]],

    lastUpdated: ['', [Validators.required]],

    currentVersion: ['', [Validators.required, Validators.maxLength(100)]],

    androidVersion: ['', [Validators.required, Validators.maxLength(100)]],
  });

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
   * PaginatedTable does not expose a row-click output.
   * We therefore listen to clicks bubbling from the table
   * and identify the clicked tbody row.
   */
  @HostListener('click', ['$event'])
  onTableClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;

    const row = target.closest('tbody tr.table-row');

    if (!row) {
      return;
    }

    const tbody = row.parentElement;

    if (!tbody) {
      return;
    }

    const rowIndex = Array.from(tbody.children).indexOf(row);

    const apps = this.tableResponse().content;

    const app = apps[rowIndex];

    if (app) {
      this.openUpdateDialog(app);
    }
  }

  openUpdateDialog(app: GooglePlayAppResponse): void {
    this.selectedApp.set(app);

    this.form.patchValue({
      app: app.app,
      category: app.category,
      rating: app.rating,
      reviews: app.reviews,
      sizeMb: app.sizeMb,
      installs: app.installs,
      type: app.type,
      price: app.price,
      contentRating: app.contentRating,
      genres: app.genres,
      lastUpdated: app.lastUpdated,
      currentVersion: app.currentVersion,
      androidVersion: app.androidVersion,
    });

    this.errorMessage.set('');
    this.successMessage.set('');

    this.dialogVisible.set(true);

    document.body.classList.add('modal-open');
  }

  closeDialog(): void {
    this.dialogVisible.set(false);
    this.selectedApp.set(null);

    this.form.reset({
      app: '',
      category: '',
      rating: 0,
      reviews: 0,
      sizeMb: 0,
      installs: '',
      type: AppType.FREE,
      price: 0,
      contentRating: '',
      genres: '',
      lastUpdated: '',
      currentVersion: '',
      androidVersion: '',
    });

    document.body.classList.remove('modal-open');
  }

  updateApp(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const app = this.selectedApp();

    if (!app) {
      return;
    }

    this.saving.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    const request: GooglePlayAppRequest = {
      app: this.form.controls.app.value.trim(),
      category: this.form.controls.category.value.trim(),
      rating: this.form.controls.rating.value,
      reviews: this.form.controls.reviews.value,
      sizeMb: this.form.controls.sizeMb.value,
      installs: this.form.controls.installs.value.trim(),
      type: this.form.controls.type.value,
      price: this.form.controls.price.value,
      contentRating: this.form.controls.contentRating.value.trim(),
      genres: this.form.controls.genres.value.trim(),
      lastUpdated: this.form.controls.lastUpdated.value,
      currentVersion: this.form.controls.currentVersion.value.trim(),
      androidVersion: this.form.controls.androidVersion.value.trim(),
    };

    this.appService.update(app.id, request).subscribe({
      next: (updatedApp) => {
        const currentResponse = this.tableResponse();

        const updatedContent = currentResponse.content.map((item) =>
          item.id === updatedApp.id ? updatedApp : item,
        );

        this.tableResponse.set({
          ...currentResponse,
          content: updatedContent,
        });

        this.saving.set(false);

        this.successMessage.set('Application updated successfully.');

        setTimeout(() => {
          this.closeDialog();
        }, 700);
      },

      error: (error) => {
        console.error('Failed to update application:', error);

        this.errorMessage.set(error?.error?.message ?? 'Failed to update application.');

        this.saving.set(false);
      },
    });
  }

  hasError(controlName: keyof typeof this.form.controls, errorType: string): boolean {
    const control = this.form.controls[controlName];

    return control.touched && control.hasError(errorType);
  }
}
