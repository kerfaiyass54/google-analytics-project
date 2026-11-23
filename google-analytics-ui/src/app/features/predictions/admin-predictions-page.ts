import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PredictionService } from '../../core/services/prediction.service';

@Component({selector:'app-admin-predictions-page',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./admin-predictions-page.html',styleUrl:'./admin-predictions-page.css'})
export class AdminPredictionsPage implements OnInit {
  private readonly api=inject(PredictionService);
  readonly regression=signal<any[]>([]);
  readonly classification=signal<any[]>([]);
  readonly loading=signal(true);
  readonly busy=signal('');
  readonly message=signal('');
  readonly selected=signal<any|null>(null);
  readonly task=signal<'regression'|'classification'>('regression');
  readonly algorithm=signal('random_forest');
  readonly testSize=signal(0.2);

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

  ngOnInit(){this.refresh();}

  refresh(){
    this.loading.set(true);
    let pending = 2;
    const complete = () => {
      pending -= 1;
      if (pending === 0) this.loading.set(false);
    };
    this.api.evaluations('regression').subscribe({
      next:v=>{this.regression.set(v);complete();},
      error:()=>{this.message.set('Could not load regression evaluations.');complete();}
    });
    this.api.evaluations('classification').subscribe({
      next:v=>{this.classification.set(v);complete();},
      error:()=>{this.message.set('Could not load classification evaluations.');complete();}
    });
  }

  onTaskChange(task:'regression'|'classification'){
    this.task.set(task);
    this.algorithm.set(task === 'regression' ? this.regressionAlgorithms[0] : this.classificationAlgorithms[0]);
  }

  get currentAlgorithms(): string[] {
    return this.task() === 'regression' ? this.regressionAlgorithms : this.classificationAlgorithms;
  }

  get algorithmDescription(): string {
    const descriptions: Record<string, string> = {
      linear_regression: 'A simple, interpretable baseline for predicting numeric ratings.',
      logistic_regression: 'A linear classification baseline for predicting install ranges.',
      random_forest: 'An ensemble of decision trees that captures non-linear relationships.',
      extra_trees: 'A randomized tree ensemble for robust predictions.',
      gradient_boosting: 'A boosted tree ensemble that learns patterns iteratively.'
    };
    return descriptions[this.algorithm()] ?? 'Train and evaluate this algorithm on the Google Play dataset.';
  }

  train(){
    this.busy.set(this.task());
    this.message.set('');
    this.api.train(this.task(),this.algorithm(),this.testSize()).subscribe({
      next:r=>{
        this.message.set(`Evaluation completed: ${r.algorithm} · ${r.dataset_rows} apps · ${r.test_rows} test rows. Model remains inactive.`);
        this.busy.set('');
        this.refresh();
      },
      error:e=>{
        this.message.set(e?.error?.detail||'Training/evaluation failed.');
        this.busy.set('');
      }
    });
  }

  formatMetricKey(key: string | number | symbol): string { return String(key).replace(/_/g, ' '); }

  showDetails(item:any){this.selected.set(item);}
  closeDetails(){this.selected.set(null);}
  get evaluations(){
    return [...this.regression(),...this.classification()]
      .sort((a,b)=>new Date(b.created_at).getTime()-new Date(a.created_at).getTime());
  }
}
