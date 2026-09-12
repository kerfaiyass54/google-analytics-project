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

  getRatingsByCategory(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/ratings-by-category`);
  }

  // ============================================================
  // FREE VS PAID
  // ============================================================

  getFreeVsPaid(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/free-vs-paid`);
  }

  // ============================================================
  // INSTALL DISTRIBUTION
  // ============================================================

  getInstallDistribution(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/install-distribution`);
  }

  // ============================================================
  // REVIEW COUNTS
  // ============================================================

  getReviewCounts(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/review-counts`);
  }
}
