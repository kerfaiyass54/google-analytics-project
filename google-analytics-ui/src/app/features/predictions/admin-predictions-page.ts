import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PredictionService } from '../../core/services/prediction.service';

@Component({selector:'app-admin-predictions-page',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./admin-predictions-page.html',styleUrl:'./admin-predictions-page.css'})
export class AdminPredictionsPage implements OnInit {
  private readonly api=inject(PredictionService);
  readonly models=signal<any[]>([]);
  readonly loading=signal(true);
  readonly busy=signal('');
  readonly message=signal('');
  readonly task=signal<'regression'|'classification'>('regression');
  readonly algorithm=signal('random_forest');
  readonly testSize=signal(0.2);

  readonly regressionAlgorithms=['linear_regression','random_forest','extra_trees','gradient_boosting'];
  readonly classificationAlgorithms=['logistic_regression','random_forest','extra_trees','gradient_boosting'];

  ngOnInit():void { this.refresh(); }

  refresh():void {
    this.loading.set(true);
    this.api.models().subscribe({
      next:rows=>{this.models.set(rows ?? []);this.loading.set(false);},
      error:()=>{this.message.set('Could not load the model registry.');this.loading.set(false);}
    });
  }

  onTaskChange(task:'regression'|'classification'):void {
    this.task.set(task);
    this.algorithm.set(task==='regression'?this.regressionAlgorithms[0]:this.classificationAlgorithms[0]);
  }
  get currentAlgorithms():string[]{return this.task()==='regression'?this.regressionAlgorithms:this.classificationAlgorithms;}
  get algorithmDescription():string {
    const descriptions:Record<string,string>={
      linear_regression:'An interpretable baseline for predicting numeric app ratings.',
      logistic_regression:'A linear classification baseline for predicting install ranges.',
      random_forest:'An ensemble of decision trees that captures non-linear relationships.',
      extra_trees:'A randomized tree ensemble for robust predictions.',
      gradient_boosting:'A boosted tree ensemble that learns patterns iteratively.'
    };
    return descriptions[this.algorithm()]??'Train and evaluate this algorithm on the Google Play dataset.';
  }

  train():void {
    this.busy.set('training');this.message.set('');
    this.api.train(this.task(),this.algorithm(),this.testSize()).subscribe({
      next:r=>{
        this.message.set(`Training completed: ${r.algorithm} · ${r.dataset_rows} apps · ${r.test_rows} test rows. The candidate is inactive until you activate it.`);
        this.busy.set('');this.refresh();
      },
      error:e=>{this.message.set(e?.error?.detail||'Training failed.');this.busy.set('');}
    });
  }

  activate(model:any):void {
    if(model.is_active)return;
    this.busy.set(model.model_id);this.message.set('');
    this.api.activate(model.model_id).subscribe({
      next:()=>{
        this.message.set(`Model ${model.model_id} is now active for ${model.task}.`);
        this.busy.set('');this.refresh();
      },
      error:e=>{this.message.set(e?.error?.detail||'Could not activate this model.');this.busy.set('');}
    });
  }
}
