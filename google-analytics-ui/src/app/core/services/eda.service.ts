import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EdaDocument {
  eda_id: string | null;
  email: string;
  date: string;
  ratings_by_category: any;
  free_vs_paid: any;
  install_distribution: any;
  review_counts: any;
}

export interface EdaPage {
  content: EdaDocument[];
  page: number;
  size: number;
  total_elements: number;
  total_pages: number;
}

export interface EdaHistoryFilters {
  edaId?: string;
  creatorEmail?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  metricFilters?: Record<string, { min?: number; max?: number }>;
}

@Injectable({
  providedIn: 'root',
})
export class EdaService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/eda';

  runAndSave(): Observable<EdaDocument> {
    return this.http.post<EdaDocument>(this.apiUrl, {});
  }

  getHistory(page = 0, size = 20, filters: EdaHistoryFilters = {}): Observable<EdaPage> {
    let params = new HttpParams().set('page', page).set('size', size);

    if (filters.edaId?.trim()) params = params.set('eda_id', filters.edaId.trim());
    if (filters.creatorEmail?.trim()) {
      params = params.set('creator_email', filters.creatorEmail.trim());
    }
    if (filters.dateFrom) params = params.set('date_from', filters.dateFrom);
    if (filters.dateTo) params = params.set('date_to', filters.dateTo);
    if (filters.search?.trim()) params = params.set('search', filters.search.trim());
    if (filters.metricFilters && Object.keys(filters.metricFilters).length) {
      params = params.set('metric_filters', JSON.stringify(filters.metricFilters));
    }

    return this.http.get<EdaPage>(this.apiUrl, { params });
  }

  getById(edaId: string): Observable<EdaDocument> {
    return this.http.get<EdaDocument>(`${this.apiUrl}/${edaId}`);
  }

  delete(edaId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${edaId}`);
  }

  getRatingsByCategory(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/ratings-by-category`);
  }

  getFreeVsPaid(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/free-vs-paid`);
  }

  getInstallDistribution(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/install-distribution`);
  }

  getReviewCounts(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/review-counts`);
  }
}
