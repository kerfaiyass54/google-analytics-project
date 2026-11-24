import { CommonModule } from '@angular/common';
import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PredictionService } from '../../core/services/prediction.service';

@Component({
  selector: 'app-admin-predictions-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-predictions-page.html',
  styleUrl: './admin-predictions-page.css',
})
export class AdminPredictionsPage implements OnInit, OnDestroy {
  private readonly api = inject(PredictionService);
  readonly models = signal<any[]>([]);
  readonly loading = signal(true);
  readonly busy = signal('');
  readonly message = signal('');
  readonly task = signal<'regression' | 'classification'>('regression');
  readonly algorithm = signal('random_forest');
  readonly testSize = signal(0.2);
  readonly progressPercent = signal(0);
  readonly progressStage = signal(0);
  readonly trainingResult = signal<any | null>(null);
  readonly trainingSteps = [
    'Loading and validating dataset',
    'Preparing training and test sets',
    'Training selected algorithm',
    'Testing model and calculating metrics',
    'Saving model and evaluation results',
  ];
  private progressTimer?: ReturnType<typeof setInterval>;

  readonly regressionAlgorithms = [
    'linear_regression',
    'random_forest',
    'extra_trees',
    'gradient_boosting',
  ];
  readonly classificationAlgorithms = [
    'logistic_regression',
    'random_forest',
    'extra_trees',
    'gradient_boosting',
  ];

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.api.models().subscribe({
      next: (rows) => {
        this.models.set(rows ?? []);
        this.loading.set(false);
      },
      error: () => {
        this.message.set('Could not load the model registry.');
        this.loading.set(false);
      },
    });
  }

  onTaskChange(task: 'regression' | 'classification'): void {
    this.task.set(task);
    this.algorithm.set(
      task === 'regression' ? this.regressionAlgorithms[0] : this.classificationAlgorithms[0],
    );
  }
  get currentAlgorithms(): string[] {
    return this.task() === 'regression' ? this.regressionAlgorithms : this.classificationAlgorithms;
  }
  get algorithmDescription(): string {
    const descriptions: Record<string, string> = {
      linear_regression: 'An interpretable baseline for predicting numeric app ratings.',
      logistic_regression: 'A linear classification baseline for predicting install ranges.',
      random_forest: 'An ensemble of decision trees that captures non-linear relationships.',
      extra_trees: 'A randomized tree ensemble for robust predictions.',
      gradient_boosting: 'A boosted tree ensemble that learns patterns iteratively.',
    };
    return (
      descriptions[this.algorithm()] ??
      'Train and evaluate this algorithm on the Google Play dataset.'
    );
  }

  train(): void {
    if (this.busy()) return;

    this.clearProgressTimer();
    this.trainingResult.set(null);
    this.progressPercent.set(5);
    this.progressStage.set(0);
    this.busy.set('training');
    this.message.set('');

    // The current API is synchronous, so these are estimated UI stages.
    // The request's final response remains the source of truth for completion.
    const progressTargets = [8, 22, 43, 67, 86];
    let stage = 0;
    this.progressTimer = setInterval(() => {
      if (stage < this.trainingSteps.length - 1) stage++;
      this.progressStage.set(stage);
      this.progressPercent.set(progressTargets[stage]);
    }, 1800);

    this.api.train(this.task(), this.algorithm(), this.testSize()).subscribe({
      next: (r) => {
        this.clearProgressTimer();
        this.progressStage.set(this.trainingSteps.length);
        this.progressPercent.set(100);
        this.trainingResult.set(r);
        this.message.set(
          'Training and test evaluation completed successfully. The new candidate is inactive until you activate it.',
        );
        this.busy.set('');
        this.refresh();
      },
      error: (e) => {
        this.clearProgressTimer();
        this.progressPercent.set(0);
        this.progressStage.set(0);
        this.message.set(
          e?.error?.detail || 'Training failed. Please review the dataset and try again.',
        );
        this.busy.set('');
      },
    });
  }

  private clearProgressTimer(): void {
    if (this.progressTimer) {
      clearInterval(this.progressTimer);
      this.progressTimer = undefined;
    }
  }

  resultMetricEntries(): Array<{ key: string; value: unknown }> {
    const metrics = this.trainingResult()?.metrics;
    return metrics && typeof metrics === 'object'
      ? Object.entries(metrics).map(([key, value]) => ({ key, value }))
      : [];
  }

  formatResultValue(value: unknown): string {
    if (value === null || value === undefined) return '—';
    if (Array.isArray(value)) return JSON.stringify(value);
    if (typeof value === 'number')
      return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(4);
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  ngOnDestroy(): void {
    this.clearProgressTimer();
  }

  activate(model: any): void {
    if (model.is_active) return;
    this.busy.set(model.model_id);
    this.message.set('');
    this.api.activate(model.model_id).subscribe({
      next: () => {
        this.message.set(`Model ${model.model_id} is now active for ${model.task}.`);
        this.busy.set('');
        this.refresh();
      },
      error: (e) => {
        this.message.set(e?.error?.detail || 'Could not activate this model.');
        this.busy.set('');
      },
    });
  }
}
