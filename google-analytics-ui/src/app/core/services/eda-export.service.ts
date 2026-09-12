import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ExportResponse {
  export_id: string;
  eda_id: string;
  email: string;
  date: string;
  file_type: string;
  filename: string;
}

export interface ExportPage {
  content: ExportResponse[];
  page: number;
  size: number;
  total_elements: number;
  total_pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class EdaExportService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/api/eda';

  // ============================================================
  // CREATE JSON EXPORT
  // ============================================================

  exportJson(edaId: string): Observable<ExportResponse> {
    return this.http.post<ExportResponse>(`${this.apiUrl}/${edaId}/exports/json`, {});
  }

  // ============================================================
  // CREATE CSV EXPORT
  // ============================================================

  exportCsv(edaId: string): Observable<ExportResponse> {
    return this.http.post<ExportResponse>(`${this.apiUrl}/${edaId}/exports/csv`, {});
  }

  // ============================================================
  // CREATE PDF EXPORT
  // ============================================================

  exportPdf(edaId: string): Observable<ExportResponse> {
    return this.http.post<ExportResponse>(`${this.apiUrl}/${edaId}/exports/pdf`, {});
  }

  // ============================================================
  // GET EXPORT HISTORY
  // ============================================================

  getExports(edaId: string, page = 0, size = 20): Observable<ExportPage> {
    const params = new HttpParams().set('page', page).set('size', size);

    return this.http.get<ExportPage>(`${this.apiUrl}/${edaId}/exports`, { params });
  }

  // ============================================================
  // DOWNLOAD EXPORT
  // ============================================================

  downloadExport(exportId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/exports/${exportId}`, {
      responseType: 'blob',
    });
  }
}
