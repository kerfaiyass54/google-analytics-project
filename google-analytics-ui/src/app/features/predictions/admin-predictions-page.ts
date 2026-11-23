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
  readonly algorithms=['random_forest','gradient_boosting','decision_tree','linear_regression','extra_trees','hist_gradient_boosting','logistic_regression','extra_trees_classifier','random_forest_classifier'];
  ngOnInit(){this.refresh();}
  refresh(){
    this.loading.set(true);
    this.api.evaluations('regression').subscribe({next:v=>{this.regression.set(v);this.loading.set(false);},error:()=>{this.message.set('Could not load regression evaluations.');this.loading.set(false);}});
    this.api.evaluations('classification').subscribe({next:v=>{this.classification.set(v);this.loading.set(false);},error:()=>{this.message.set('Could not load classification evaluations.');this.loading.set(false);}});
  }
  train(){
    this.busy.set(this.task());this.message.set('');
    this.api.train(this.task(),this.algorithm(),this.testSize()).subscribe({
      next:r=>{this.message.set(`Evaluation completed: ${r.algorithm} · ${r.dataset_rows} apps · ${r.test_rows} test rows. Model remains inactive.`);this.busy.set('');this.refresh();},
      error:e=>{this.message.set(e?.error?.detail||'Training/evaluation failed.');this.busy.set('');}
    });
  }
  showDetails(item:any){this.selected.set(item);}
  closeDetails(){this.selected.set(null);}
  get evaluations(){return [...this.regression(),...this.classification()].sort((a,b)=>new Date(b.created_at).getTime()-new Date(a.created_at).getTime());}
}
