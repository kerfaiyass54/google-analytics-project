import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { PredictionService } from '../../core/services/prediction.service';

@Component({
  selector: 'app-admin-evaluations-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin-evaluations-page.html',
  styleUrl: './admin-evaluations-page.css',
})
export class AdminEvaluationsPage implements OnInit {
  private readonly api = inject(PredictionService);
  readonly regression = signal<any[]>([]);
  readonly classification = signal<any[]>([]);
  readonly loading = signal(true);
  readonly error = signal('');
  readonly selected = signal<any | null>(null);
  readonly filter = signal<'all' | 'regression' | 'classification'>('all');

  ngOnInit(): void { this.refresh(); }

  refresh(): void {
    this.loading.set(true);
    this.error.set('');
    let remaining = 2;
    const done = () => { remaining -= 1; if (!remaining) this.loading.set(false); };
    this.api.evaluations('regression').subscribe({
      next: rows => { this.regression.set(rows ?? []); done(); },
      error: () => { this.error.set('Unable to load regression evaluations.'); done(); },
    });
    this.api.evaluations('classification').subscribe({
      next: rows => { this.classification.set(rows ?? []); done(); },
      error: () => { this.error.set('Unable to load classification evaluations.'); done(); },
    });
  }

  get allEvaluations(): any[] {
    return [...this.regression(), ...this.classification()]
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }
  get visibleEvaluations(): any[] {
    return this.filter() === 'all' ? this.allEvaluations :
      this.allEvaluations.filter(item => item.task === this.filter());
  }
  get total(): number { return this.allEvaluations.length; }
  get regressionCount(): number { return this.regression().length; }
  get classificationCount(): number { return this.classification().length; }
  get averageAccuracy(): number | null {
    const values = this.classification().map(item => Number(item.metrics?.accuracy)).filter(Number.isFinite);
    return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
  }
  get averageR2(): number | null {
    const values = this.regression().map(item => Number(item.metrics?.r2)).filter(Number.isFinite);
    return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
  }
  formatMetricKey(key: string): string { return key.replace(/_/g, ' '); }
  showDetails(item: any): void { this.selected.set(item); }
  closeDetails(): void { this.selected.set(null); }
}
