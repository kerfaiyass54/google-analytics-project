import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  inject,
  signal,
} from '@angular/core';
import { Router } from '@angular/router';
import { EdaDocument, EdaService, EdaHistoryFilters } from '../../../core/services/eda.service';
import {
  PaginatedTable,
  PaginatedTableColumn,
  PaginatedTableRequest,
} from '../../../shared/components/paginated-table/paginated-table';
import { Location } from '@angular/common';

type EdaAnalysisKey =
  | 'ratings_by_category'
  | 'free_vs_paid'
  | 'install_distribution'
  | 'review_counts';

interface AnalysisButton {
  key: EdaAnalysisKey;
  label: string;
  shortLabel: string;
  icon: string;
  description: string;
}

@Component({
  selector: 'app-manage-eda',
  standalone: true,
  imports: [PaginatedTable],
  templateUrl: './manage-eda.html',
  styleUrl: './manage-eda.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ManageEda {
  private readonly edaService = inject(EdaService);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly location = inject(Location);

  readonly loading = signal(false);
  readonly filtersExpanded = signal(true);
  readonly edaIdFilter = signal('');
  readonly creatorEmailFilter = signal('');
  readonly dateFromFilter = signal('');
  readonly dateToFilter = signal('');
  readonly filterError = signal('');

  private activeFilters: EdaHistoryFilters = {};

  readonly historyResponse = signal<any>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  readonly selectedEda = signal<EdaDocument | null>(null);
  readonly selectedAnalysis = signal<EdaAnalysisKey>('ratings_by_category');
  readonly dialogVisible = signal(false);

  goBack(): void {
    this.location.back();
  }

  readonly tableColumns: PaginatedTableColumn[] = [
    { key: 'eda_id', label: 'EDA ID', type: 'text' },
    { key: 'email', label: 'Created by', type: 'text' },
    { key: 'date', label: 'Analysis date', type: 'date' },
  ];

  readonly analysisButtons: AnalysisButton[] = [
    {
      key: 'ratings_by_category',
      label: 'Ratings by Category',
      shortLabel: 'Ratings',
      icon: 'bi-bar-chart-line-fill',
      description: 'Average application rating grouped by Google Play category.',
    },
    {
      key: 'free_vs_paid',
      label: 'Free vs Paid',
      shortLabel: 'Free vs Paid',
      icon: 'bi-pie-chart-fill',
      description: 'Comparison between free and paid applications.',
    },
    {
      key: 'install_distribution',
      label: 'Install Distribution',
      shortLabel: 'Installs',
      icon: 'bi-graph-up-arrow',
      description: 'Distribution of applications across install ranges.',
    },
    {
      key: 'review_counts',
      label: 'Review Counts',
      shortLabel: 'Reviews',
      icon: 'bi-chat-square-text-fill',
      description: 'Review activity across the analyzed applications.',
    },
  ];

  constructor() {
    this.destroyRef.onDestroy(() => this.closeDialog());
    this.loadHistory(0, 10);
  }

  loadHistory(page: number, size: number, search = ''): void {
    this.loading.set(true);
    this.edaService.getHistory(page, size, { ...this.activeFilters, search }).subscribe({
      next: (response) => {
        this.historyResponse.set({
          content: response.content ?? [],
          page: response.page ?? page,
          size: response.size ?? size,
          totalElements: response.total_elements ?? 0,
          totalPages: response.total_pages ?? 0,
        });
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.historyResponse.set({
          content: [],
          page,
          size,
          totalElements: 0,
          totalPages: 0,
        });
      },
    });
  }

  applyFilters(): void {
    this.filterError.set('');

    if (this.dateFromFilter() && this.dateToFilter() &&
        this.dateFromFilter() > this.dateToFilter()) {
      this.filterError.set('The start date must be earlier than or equal to the end date.');
      return;
    }

    this.activeFilters = {
      edaId: this.edaIdFilter().trim() || undefined,
      creatorEmail: this.creatorEmailFilter().trim() || undefined,
      dateFrom: this.dateFromFilter() ? `${this.dateFromFilter()}T00:00:00` : undefined,
      dateTo: this.dateToFilter() ? `${this.dateToFilter()}T23:59:59.999` : undefined,
    };

    this.loadHistory(0, this.historyResponse().size || 10);
  }

  resetFilters(): void {
    this.edaIdFilter.set('');
    this.creatorEmailFilter.set('');
    this.dateFromFilter.set('');
    this.dateToFilter.set('');
    this.filterError.set('');
    this.activeFilters = {};
    this.loadHistory(0, this.historyResponse().size || 10);
  }

  onPageChange(request: PaginatedTableRequest): void {
    this.loadHistory(request.page, request.size, request.search);
  }

  onTableClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target) return;

    const row = target.closest('tbody tr.table-row') as HTMLTableRowElement | null;
    if (!row) return;

    const tableRows = Array.from(row.parentElement?.querySelectorAll('tr.table-row') ?? []);
    const rowIndex = tableRows.indexOf(row);
    if (rowIndex < 0) return;

    const eda = this.historyResponse().content[rowIndex];
    if (eda) this.openDialog(eda);
  }

  openDialog(eda: EdaDocument): void {
    this.selectedEda.set(eda);
    this.selectedAnalysis.set('ratings_by_category');
    this.dialogVisible.set(true);
    document.body.classList.add('eda-dialog-open');
  }

  closeDialog(): void {
    this.dialogVisible.set(false);
    document.body.classList.remove('eda-dialog-open');
    window.setTimeout(() => {
      if (!this.dialogVisible()) this.selectedEda.set(null);
    }, 250);
  }

  selectAnalysis(key: EdaAnalysisKey): void {
    if (this.selectedAnalysis() !== key) this.selectedAnalysis.set(key);
  }

  get selectedAnalysisButton(): AnalysisButton {
    return this.analysisButtons.find((button) => button.key === this.selectedAnalysis())
      ?? this.analysisButtons[0];
  }

  getSelectedAnalysisData(): unknown {
    const eda = this.selectedEda();
    return eda ? eda[this.selectedAnalysis()] : null;
  }

  getAnalysisDataEntries(): Array<{ key: string; value: string }> {
    const data = this.getSelectedAnalysisData();
    if (!data || typeof data !== 'object') return [];

    return Object.entries(data as Record<string, unknown>).map(([key, value]) => ({
      key: this.formatKey(key),
      value: this.formatValue(value),
    }));
  }

  private formatKey(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, (character) => character.toUpperCase());
  }

  private formatValue(value: unknown): string {
    if (value === null || value === undefined) return '—';
    if (Array.isArray(value)) return `${value.length} items`;
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  formatDate(date: string | Date | null | undefined): string {
    if (!date) return '—';
    const parsedDate = new Date(date);
    if (Number.isNaN(parsedDate.getTime())) return String(date);

    return new Intl.DateTimeFormat('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(parsedDate);
  }

  exportEda(): void {
    const eda = this.selectedEda();
    if (eda?.eda_id) this.router.navigate(['/operations/export-eda', eda.eda_id]);
  }

  trackAnalysis(_index: number, item: AnalysisButton): string {
    return item.key;
  }

  trackEntry(_index: number, item: { key: string; value: string }): string {
    return item.key;
  }
}
