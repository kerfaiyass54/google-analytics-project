import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Observable, Subscription, interval } from 'rxjs';
import { EdaExportService } from '../../../../core/services/eda-export.service';

type ExportType = 'xlsx' | 'zip';

@Component({
  selector: 'app-export-eda',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './export-eda.html',
  styleUrl: './export-eda.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExportEda {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly edaExportService = inject(EdaExportService);

  readonly edaId = this.route.snapshot.paramMap.get('id') ?? '';

  readonly currentStep = signal(1);
  readonly fileName = signal('');
  readonly selectedType = signal<ExportType | null>(null);
  readonly isExporting = signal(false);
  readonly exportError = signal('');
  readonly exportProgressStage = signal(0);
  private progressSubscription?: Subscription;
  readonly exportStages = [
    { title: 'Preparing report', message: 'Collecting the EDA sections and metadata...' },
    { title: 'Building report', message: 'Organizing tables or rendering charts...' },
    { title: 'Formatting', message: 'Applying layout, labels, and report styling...' },
    { title: 'Finalizing', message: 'Saving the export record and preparing your download...' },
  ];

  readonly fileTypes: {
    value: ExportType;
    label: string;
    icon: string;
    description: string;
  }[] = [
    {
      value: 'xlsx',
      label: 'Excel Workbook',
      icon: 'bi-file-earmark-excel',
      description: 'Multiple sheets with organized tables',
    },
    {
      value: 'zip',
      label: 'Charts ZIP Archive',
      icon: 'bi-file-earmark-zip',
      description: 'PNG charts generated with Matplotlib',
    },
  ];

  setFileName(value: string): void {
    this.fileName.set(value);
  }

  selectType(type: ExportType): void {
    this.selectedType.set(type);
  }

  nextStep(): void {
    const step = this.currentStep();

    if (step === 1 && !this.fileName().trim()) {
      return;
    }

    if (step === 2 && !this.selectedType()) {
      return;
    }

    if (step < 3) {
      this.currentStep.update((value) => value + 1);
    }
  }

  previousStep(): void {
    if (this.currentStep() > 1) {
      this.currentStep.update((value) => value - 1);
    }
  }

  goBack(): void {
    this.router.navigate(['/operations']);
  }

  export(): void {
    const edaId = this.edaId;
    const fileName = this.fileName().trim();
    const type = this.selectedType();

    if (!edaId || !fileName || !type || this.isExporting()) {
      return;
    }

    this.isExporting.set(true);
    this.exportProgressStage.set(0);
    this.exportError.set('');
    this.progressSubscription?.unsubscribe();
    this.progressSubscription = interval(2200).subscribe(() => {
      this.exportProgressStage.update((stage) => Math.min(stage + 1, this.exportStages.length - 1));
    });

    let request$: Observable<Blob>;

    switch (type) {
      case 'xlsx':
        request$ = this.edaExportService.exportExcel(edaId);
        break;
      case 'zip':
        request$ = this.edaExportService.exportChartsZip(edaId);
        break;
      default:
        this.isExporting.set(false);
        this.progressSubscription?.unsubscribe();
        return;
    }

    request$.subscribe({
      next: (response) => {
        this.downloadFile(response, this.finalFileName);
        this.progressSubscription?.unsubscribe();
        this.isExporting.set(false);
      },
      error: (error) => {
        console.error('EDA export failed:', error);
        this.exportError.set('The export could not be generated. Please try again.');
        this.progressSubscription?.unsubscribe();
        this.isExporting.set(false);
      },
    });
  }

  private downloadFile(blob: Blob, fileName: string): void {
    const url = URL.createObjectURL(blob);

    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = fileName;
    anchor.click();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  get selectedTypeLabel(): string {
    return this.fileTypes.find((type) => type.value === this.selectedType())?.label ?? '';
  }

  get finalFileName(): string {
    const name = this.fileName().trim();

    if (!name) {
      return '';
    }

    const extension = this.selectedType();

    if (!extension) {
      return name;
    }

    return name.toLowerCase().endsWith(`.${extension}`) ? name : `${name}.${extension}`;
  }
}
