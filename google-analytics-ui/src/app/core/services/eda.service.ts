import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EdaDocument {
  eda_id: string | null;
  email: string;
  date: string;
  ratings_by_category: Record<string, unknown>;
  free_vs_paid: Record<string, unknown>;
  install_distribution: Record<string, unknown>;
  review_counts: Record<string, unknown>;
}

export interface EdaPage {
  content: EdaDocument[];
  page: number;
  size: number;
  total_elements: number;
  total_pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class EdaService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/api/eda';

  // ============================================================
  // RUN + SAVE COMPLETE EDA
  // ============================================================

  runAndSave(): Observable<EdaDocument> {
    return this.http.post<EdaDocument>(this.apiUrl, {});
  }

  // ============================================================
  // GET EDA HISTORY
  // ============================================================

  getHistory(page = 0, size = 20): Observable<EdaPage> {
    const params = new HttpParams().set('page', page).set('size', size);

    return this.http.get<EdaPage>(this.apiUrl, { params });
  }

  // ============================================================
  // GET EDA BY ID
  // ============================================================

  getById(edaId: string): Observable<EdaDocument> {
    return this.http.get<EdaDocument>(`${this.apiUrl}/${edaId}`);
  }

  // ============================================================
  // DELETE EDA
  // ============================================================

  delete(edaId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${edaId}`);
  }

  // ============================================================
  // RATINGS BY CATEGORY
  // ============================================================

  getRatingsByCategory(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.apiUrl}/ratings-by-category`);
  }

  // ============================================================
  // FREE VS PAID
  // ============================================================

  getFreeVsPaid(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.apiUrl}/free-vs-paid`);
  }

  // ============================================================
  // INSTALL DISTRIBUTION
  // ============================================================

  getInstallDistribution(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.apiUrl}/install-distribution`);
  }

  // ============================================================
  // REVIEW COUNTS
  // ============================================================

  getReviewCounts(): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.apiUrl}/review-counts`);
  }
}
