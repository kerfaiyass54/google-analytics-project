import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PredictionService, AppFeatures, PredictionRecord } from '../../core/services/prediction.service';

@Component({selector:'app-prediction-page',standalone:true,imports:[CommonModule,FormsModule],templateUrl:'./prediction-page.html',styleUrl:'./prediction-page.css'})
export class PredictionPage {
  private readonly api=inject(PredictionService);
  readonly tab=signal<'create'|'history'>('create');
  readonly step=signal(0);
  readonly task=signal<'rating'|'installs'>('rating');
  readonly loading=signal(false);
  readonly error=signal('');
  readonly result=signal<PredictionRecord|null>(null);
  readonly records=signal<PredictionRecord[]>([]);
  readonly selected=signal<PredictionRecord|null>(null);
  readonly form:AppFeatures={app:'',category:'GAME',reviews:0,size_mb:25,type:'FREE',price:0,content_rating:'Everyone',genres:'Game',last_updated:new Date().toISOString().slice(0,10),current_version:'1.0',android_version:'5.0 and up'};
  readonly categories=['ART_AND_DESIGN','AUTO_AND_VEHICLES','BEAUTY','BOOKS_AND_REFERENCE','BUSINESS','COMICS','COMMUNICATION','EDUCATION','ENTERTAINMENT','FINANCE','FOOD_AND_DRINK','GAME','HEALTH_AND_FITNESS','LIBRARIES_AND_DEMO','LIFESTYLE','MAPS_AND_NAVIGATION','MEDICAL','MUSIC_AND_AUDIO','NEWS_AND_MAGAZINES','PARENTING','PERSONALIZATION','PHOTOGRAPHY','PRODUCTIVITY','SHOPPING','SOCIAL','SPORTS','TOOLS','TRAVEL_AND_LOCAL','VIDEO_PLAYERS','WEATHER'];
  next(){if(this.step()<2)this.step.update(v=>v+1);}
  back(){if(this.step()>0)this.step.update(v=>v-1);}
  setType(value:'FREE'|'PAID'){this.form.type=value;if(value==='FREE')this.form.price=0;}
  submit(){
    this.error.set('');this.loading.set(true);
    this.api.predict(this.task(),{...this.form}).subscribe({next:r=>{this.result.set(r);this.loading.set(false);this.loadHistory();},error:e=>{this.error.set(e?.error?.detail||'Prediction failed. Check that a model is trained and activated.');this.loading.set(false);}});
  }
  loadHistory(){this.api.mine().subscribe({next:r=>this.records.set(r),error:()=>this.error.set('Unable to load your prediction history.')});}
  openDetails(item:PredictionRecord){this.api.detail(item.id ?? item.prediction_id ?? '').subscribe({next:r=>this.selected.set(r),error:()=>this.selected.set(item)});}
  closeDetails(){this.selected.set(null);}
  showHistory(){this.tab.set('history');this.loadHistory();}
  newPrediction(){this.result.set(null);this.step.set(0);this.tab.set('create');}
  get canContinue(){if(this.step()===0)return !!this.form.app.trim()&&!!this.form.category;if(this.step()===1)return this.form.reviews>=0&&this.form.size_mb>0&&this.form.price>=0;return !!this.form.content_rating&&!!this.form.genres&&!!this.form.last_updated&&!!this.form.current_version&&!!this.form.android_version;}
}
