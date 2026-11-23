import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AppFeatures {
  app: string; category: string; reviews: number; size_mb: number; type: 'FREE'|'PAID'; price: number;
  content_rating: string; genres: string; last_updated: string; current_version: string; android_version: string;
}
export interface PredictionRecord {
  id: string; prediction_id?: string; task: 'regression'|'classification'; app_name: string;
  input_data?: AppFeatures; prediction: number|string; model_id: string; created_at: string;
}
@Injectable({providedIn:'root'})
export class PredictionService {
  private readonly http = inject(HttpClient);
  private readonly api = 'http://localhost:8010/api/v1';
  private readonly events = 'http://localhost:8020/api/dashboard';
  predict(task:'rating'|'installs', payload:AppFeatures) {
    return this.http.post<PredictionRecord>(`${this.api}/predictions/${task}`, payload);
  }
  mine(task='all') { return this.http.get<PredictionRecord[]>(`${this.api}/predictions/mine`, {params:new HttpParams().set('task',task)}); }
  detail(id:string) { return this.http.get<PredictionRecord>(`${this.api}/predictions/${id}`); }
  models() { return this.http.get<any[]>(`${this.api}/models`); }
  evaluations(task:'regression'|'classification') { return this.http.get<any[]>(`${this.api}/evaluations/${task}`); }
  activate(modelId:string) { return this.http.post<any>(`${this.api}/models/${modelId}/activate`, {}); }
  summary() { return this.http.get<any>(`${this.events}/summary`); }
  recent() { return this.http.get<any[]>(`${this.events}/recent`); }
}
