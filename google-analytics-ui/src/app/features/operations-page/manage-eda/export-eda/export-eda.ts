import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { EdaExportService } from '../../../../core/services/eda-export.service';

type ExportType = 'json' | 'csv' | 'pdf';

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

  readonly fileTypes: {
    value: ExportType;
    label: string;
    icon: string;
    description: string;
  }[] = [
    {
      value: 'json',
      label: 'JSON',
      icon: 'bi-braces',
      description: 'Machine-readable structured data',
    },
    {
      value: 'csv',
      label: 'CSV',
      icon: 'bi-filetype-csv',
      description: 'Tabular data for spreadsheets',
    },
    {
      value: 'pdf',
      label: 'PDF',
      icon: 'bi-filetype-pdf',
      description: 'Formatted document for sharing',
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

    if (!edaId || !fileName || !type) {
      return;
    }

    let request$;

    switch (type) {
      case 'json':
        request$ = this.edaExportService.exportJson(edaId);
        break;

      case 'csv':
        request$ = this.edaExportService.exportCsv(edaId);
        break;

      case 'pdf':
        request$ = this.edaExportService.exportPdf(edaId);
        break;

      default:
        return;
    }

    request$.subscribe({
      next: (response) => {
        this.downloadFile(response, this.finalFileName);
      },
      error: (error) => {
        console.error('EDA export failed:', error);
      },
    });
  }

  private downloadFile(response: unknown, fileName: string): void {
    let blob: Blob;

    if (response instanceof Blob) {
      blob = response;
    } else {
      blob = new Blob([response as BlobPart], {
        type: this.getMimeType(),
      });
    }

    const url = URL.createObjectURL(blob);

    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = fileName;
    anchor.click();

    URL.revokeObjectURL(url);
  }

  private getMimeType(): string {
    switch (this.selectedType()) {
      case 'json':
        return 'application/json';

      case 'csv':
        return 'text/csv';

      case 'pdf':
        return 'application/pdf';

      default:
        return 'application/octet-stream';
    }
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
