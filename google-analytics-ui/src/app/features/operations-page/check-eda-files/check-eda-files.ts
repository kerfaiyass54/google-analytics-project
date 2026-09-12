import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableResponse,
} from '../../../shared/components/paginated-table/paginated-table';

import { EdaExportService, ExportResponse } from '../../../core/services/eda-export.service';

interface ExportTableRow {
  export_id: string;
  eda_id: string;
  email: string;
  date: string;
  file_type: string;
  filename: string;
}

@Component({
  selector: 'app-check-eda-files',
  standalone: true,
  imports: [PaginatedTable],
  templateUrl: './check-eda-files.html',
  styleUrl: './check-eda-files.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CheckEdaFiles implements OnInit {
  private readonly router = inject(Router);
  private readonly edaExportService = inject(EdaExportService);

  readonly loading = signal(false);

  readonly columns: PaginatedTableColumn[] = [
    {
      key: 'filename',
      label: 'File name',
    },
    {
      key: 'file_type',
      label: 'Type',
    },
    {
      key: 'date',
      label: 'Exported',
    },
    {
      key: 'export_id',
      label: 'Export ID',
    },
  ];

  readonly response = signal<PaginatedTableResponse<ExportTableRow>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  ngOnInit(): void {
    this.loadExports(0, 10);
  }

  // ============================================================
  // LOAD CURRENT USER EXPORTS
  // ============================================================

  loadExports(page = 0, size = 10): void {
    this.loading.set(true);

    this.edaExportService.getMyExports(page, size).subscribe({
      next: (exportPage) => {
        this.response.set({
          content: exportPage.content.map((item: ExportResponse): ExportTableRow => ({
            export_id: item.export_id,
            eda_id: item.eda_id,
            email: item.email,
            date: item.date,
            file_type: item.file_type,
            filename: item.filename,
          })),
          page: exportPage.page,
          size: exportPage.size,
          totalElements: exportPage.total_elements,
          totalPages: exportPage.total_pages,
        });

        this.loading.set(false);
      },

      error: (error) => {
        console.error('Failed to load user exports:', error);

        this.response.set({
          content: [],
          page: 0,
          size,
          totalElements: 0,
          totalPages: 0,
        });

        this.loading.set(false);
      },
    });
  }

  // ============================================================
  // PAGINATION
  // ============================================================

  onPageChange(request: { page: number; size: number; search: string }): void {
    this.loadExports(request.page, request.size);
  }

  // ============================================================
  // FORMAT TYPE
  // ============================================================

  formatType(type: string): string {
    return type.toUpperCase();
  }

  // ============================================================
  // FORMAT DATE
  // ============================================================

  formatDate(date: string): string {
    if (!date) {
      return '—';
    }

    return new Intl.DateTimeFormat('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(date));
  }

  // ============================================================
  // DOWNLOAD EXPORT
  // ============================================================

  download(exportItem: ExportTableRow): void {
    this.edaExportService.downloadExport(exportItem.export_id).subscribe({
      next: (response) => {
        this.downloadFile(response, exportItem.filename, exportItem.file_type);
      },

      error: (error) => {
        console.error('Failed to download export:', error);
      },
    });
  }

  // ============================================================
  // CREATE DOWNLOAD
  // ============================================================

  private downloadFile(response: Blob, fallbackFileName: string, fileType: string): void {
    const blob = new Blob([response], {
      type: this.getMimeType(fileType),
    });

    const url = URL.createObjectURL(blob);

    const anchor = document.createElement('a');

    anchor.href = url;
    anchor.download = fallbackFileName;

    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    URL.revokeObjectURL(url);
  }

  // ============================================================
  // MIME TYPE
  // ============================================================

  private getMimeType(type: string): string {
    switch (type.toLowerCase()) {
      case 'json':
        return 'application/json';

      case 'csv':
        return 'text/csv';

      case 'pdf':
        return 'application/pdf';

      case 'xlsx':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

      default:
        return 'application/octet-stream';
    }
  }

  // ============================================================
  // GO BACK
  // ============================================================

  goBack(): void {
    this.router.navigate(['/operations']);
  }
}
