import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { PredictionService, PredictionRecord } from '../../core/services/prediction.service';

@Component({selector:'app-admin-predictions-page',standalone:true,imports:[CommonModule],templateUrl:'./admin-predictions-page.html',styleUrl:'./admin-predictions-page.css'})
export class AdminPredictionsPage implements OnInit {
  private readonly api=inject(PredictionService);
  readonly models=signal<any[]>([]);
  readonly regression=signal<any[]>([]);
  readonly classification=signal<any[]>([]);
  readonly summary=signal<any|null>(null);
  readonly recent=signal<any[]>([]);
  readonly predictions=signal<PredictionRecord[]>([]);
  readonly selectedModel=signal('all');
  readonly loading=signal(true);
  readonly busy=signal('');
  readonly message=signal('');
  ngOnInit(){this.refresh();}
  refresh(){
    this.loading.set(true);
    this.api.models().subscribe({next:v=>{this.models.set(v);this.loadPredictions(this.selectedModel());},error:()=>this.message.set('Could not load model registry.')});
    this.api.evaluations('regression').subscribe({next:v=>this.regression.set(v),error:()=>this.message.set('Regression evaluations unavailable.')});
    this.api.evaluations('classification').subscribe({next:v=>this.classification.set(v),error:()=>this.message.set('Classification evaluations unavailable.')});
    this.api.summary().subscribe({next:v=>this.summary.set(v),error:()=>this.message.set('Kafka dashboard is offline. Start prediction-events service.')});
    this.api.recent().subscribe({next:v=>this.recent.set(v),error:()=>{}});
    this.loading.set(false);
  }
  loadPredictions(modelId:string){this.selectedModel.set(modelId);this.api.adminPredictions(modelId).subscribe({next:v=>this.predictions.set(v),error:()=>this.message.set('Unable to load prediction results for this model.')});}
  activate(id:string){this.busy.set(id);this.message.set('');this.api.activate(id).subscribe({next:()=>{this.message.set('Model activated successfully.');this.busy.set('');this.refresh();},error:e=>{this.message.set(e?.error?.detail||'Could not activate model.');this.busy.set('');}});}
  evaluationFor(modelId:string){return [...this.regression(),...this.classification()].find(e=>e.model_id===modelId);}
  metrics(modelId:string){return this.evaluationFor(modelId)?.metrics||{};}
}
