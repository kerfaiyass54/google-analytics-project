import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  effect,
  inject,
  input,
  output,
  signal,
} from '@angular/core';

export interface PaginatedTableColumn {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'badge';
}

export interface PaginatedTableRequest {
  page: number;
  size: number;
  search: string;
}

export interface PaginatedTableResponse<T> {
  content: T[];
  page: number;
  size: number;
  totalElements: number;
  totalPages: number;
}

@Component({
  selector: 'app-paginated-table',
  standalone: true,
  imports: [],
  templateUrl: './paginated-table.html',
  styleUrl: './paginated-table.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PaginatedTable<T> {
  private readonly destroyRef = inject(DestroyRef);

  // ==========================================================
  // INPUTS
  // ==========================================================

  readonly title = input<string>('Data');

  readonly columns = input<PaginatedTableColumn[]>([]);

  readonly response = input<PaginatedTableResponse<T>>({
    content: [],
    page: 0,
    size: 10,
    totalElements: 0,
    totalPages: 0,
  });

  readonly loading = input<boolean>(false);

  readonly searchPlaceholder = input<string>('Search applications...');

  readonly pageSizeOptions = input<number[]>([5, 10, 20, 50, 100]);

  /**
   * Controls whether row-selection checkboxes are displayed.
   *
   * Default: false
   */
  readonly showCheckbox = input<boolean>(false);

  /**
   * Arbitrary action button title.
   *
   * If empty, the action button is not displayed.
   */
  readonly actionLabel = input<string>('');

  /**
   * Optional Bootstrap icon for the action button.
   *
   * Example:
   * "bi-trash3"
   */
  readonly actionIcon = input<string>('bi-lightning-charge');

  // ==========================================================
  // OUTPUTS
  // ==========================================================

  readonly pageChange = output<PaginatedTableRequest>();

  /**
   * Emits whenever the selected rows change.
   */
  readonly selectionChange = output<T[]>();

  /**
   * Emits the currently selected rows when the action button
   * is clicked.
   */
  readonly actionClick = output<T[]>();

  // ==========================================================
  // STATE
  // ==========================================================

  readonly search = signal<string>('');

  readonly currentPage = signal<number>(0);

  readonly selectedPageSize = signal<number>(10);

  /**
   * Stores selected row identifiers.
   */
  readonly selectedIds = signal<Set<unknown>>(new Set());

  private searchTimeout: ReturnType<typeof setTimeout> | null = null;

  // ==========================================================
  // GETTERS
  // ==========================================================

  get rows(): T[] {
    return this.response().content;
  }

  get totalElements(): number {
    return this.response().totalElements;
  }

  get totalPages(): number {
    return this.response().totalPages;
  }

  get currentPageNumber(): number {
    return this.currentPage() + 1;
  }

  get firstElement(): number {
    if (this.totalElements === 0) {
      return 0;
    }

    return this.currentPage() * this.selectedPageSize() + 1;
  }

  get lastElement(): number {
    if (this.totalElements === 0) {
      return 0;
    }

    return Math.min((this.currentPage() + 1) * this.selectedPageSize(), this.totalElements);
  }

  get visiblePageNumbers(): number[] {
    const total = this.totalPages;
    const current = this.currentPage();

    if (total <= 7) {
      return Array.from({ length: total }, (_, index) => index);
    }

    if (current <= 3) {
      return [0, 1, 2, 3, 4, -1, total - 1];
    }

    if (current >= total - 4) {
      return [0, -1, total - 5, total - 4, total - 3, total - 2, total - 1];
    }

    return [0, -1, current - 1, current, current + 1, -1, total - 1];
  }

  get selectedRows(): T[] {
    const ids = this.selectedIds();

    return this.rows.filter((row) => ids.has(this.getRowId(row)));
  }

  get selectedCount(): number {
    return this.selectedIds().size;
  }

  get allVisibleSelected(): boolean {
    if (this.rows.length === 0) {
      return false;
    }

    return this.rows.every((row) => this.selectedIds().has(this.getRowId(row)));
  }

  get someVisibleSelected(): boolean {
    if (this.rows.length === 0) {
      return false;
    }

    const selectedVisibleCount = this.rows.filter((row) =>
      this.selectedIds().has(this.getRowId(row)),
    ).length;

    return selectedVisibleCount > 0 && selectedVisibleCount < this.rows.length;
  }

  get hasAction(): boolean {
    return this.showCheckbox() && this.actionLabel().trim().length > 0;
  }

  // ==========================================================
  // CONSTRUCTOR
  // ==========================================================

  constructor() {
    effect(() => {
      const response = this.response();

      if (response.page !== this.currentPage()) {
        this.currentPage.set(response.page);
      }

      if (response.size !== this.selectedPageSize()) {
        this.selectedPageSize.set(response.size);
      }

      /*
       * Remove selected IDs that no longer exist
       * in the current response.
       */
      const currentIds = new Set(response.content.map((row) => this.getRowId(row)));

      const currentSelection = this.selectedIds();

      const cleanedSelection = new Set([...currentSelection].filter((id) => currentIds.has(id)));

      if (cleanedSelection.size !== currentSelection.size) {
        this.selectedIds.set(cleanedSelection);

        this.emitSelection();
      }
    });

    this.destroyRef.onDestroy(() => {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
    });
  }

  // ==========================================================
  // SEARCH
  // ==========================================================

  onSearch(value: string): void {
    this.search.set(value);

    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }

    this.searchTimeout = setTimeout(() => {
      this.currentPage.set(0);

      this.requestPage(0, this.selectedPageSize(), this.search());
    }, 350);
  }

  clearSearch(): void {
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }

    this.search.set('');
    this.currentPage.set(0);

    this.requestPage(0, this.selectedPageSize(), '');
  }

  onSearchKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      this.clearSearch();
    }
  }

  // ==========================================================
  // PAGINATION
  // ==========================================================

  onPageSizeChange(value: string): void {
    const size = Number(value);

    if (!size || size <= 0) {
      return;
    }

    this.selectedPageSize.set(size);
    this.currentPage.set(0);

    this.clearSelection();

    this.requestPage(0, size, this.search());
  }

  goToPage(page: number): void {
    if (page < 0 || page >= this.totalPages || page === this.currentPage()) {
      return;
    }

    this.currentPage.set(page);

    this.clearSelection();

    this.requestPage(page, this.selectedPageSize(), this.search());
  }

  previousPage(): void {
    this.goToPage(this.currentPage() - 1);
  }

  nextPage(): void {
    this.goToPage(this.currentPage() + 1);
  }

  firstPage(): void {
    this.goToPage(0);
  }

  lastPage(): void {
    this.goToPage(this.totalPages - 1);
  }

  private requestPage(page: number, size: number, search: string): void {
    this.pageChange.emit({
      page,
      size,
      search: search.trim(),
    });
  }

  // ==========================================================
  // TABLE
  // ==========================================================

  getCellValue(row: T, column: PaginatedTableColumn): unknown {
    return (row as Record<string, unknown>)[column.key];
  }

  trackRow(index: number, row: T): unknown {
    return this.getRowId(row) ?? index;
  }

  private getRowId(row: T): unknown {
    const record = row as Record<string, unknown>;

    return record['id'];
  }

  // ==========================================================
  // SELECTION
  // ==========================================================

  isSelected(row: T): boolean {
    return this.selectedIds().has(this.getRowId(row));
  }

  toggleRowSelection(row: T): void {
    const id = this.getRowId(row);

    const selection = new Set(this.selectedIds());

    if (selection.has(id)) {
      selection.delete(id);
    } else {
      selection.add(id);
    }

    this.selectedIds.set(selection);

    this.emitSelection();
  }

  toggleAllVisible(): void {
    const selection = new Set(this.selectedIds());

    if (this.allVisibleSelected) {
      for (const row of this.rows) {
        selection.delete(this.getRowId(row));
      }
    } else {
      for (const row of this.rows) {
        selection.add(this.getRowId(row));
      }
    }

    this.selectedIds.set(selection);

    this.emitSelection();
  }

  clearSelection(): void {
    if (this.selectedIds().size === 0) {
      return;
    }

    this.selectedIds.set(new Set());

    this.emitSelection();
  }

  private emitSelection(): void {
    this.selectionChange.emit(this.selectedRows);
  }

  // ==========================================================
  // ACTION
  // ==========================================================

  onAction(): void {
    if (!this.hasAction) {
      return;
    }

    if (this.selectedRows.length === 0) {
      return;
    }

    this.actionClick.emit(this.selectedRows);
  }
}
