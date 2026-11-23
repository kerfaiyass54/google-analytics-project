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
  // CREATE EXCEL EXPORT
  // ============================================================

  exportExcel(edaId: string): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/${edaId}/exports/xlsx`,
      {},
      { responseType: 'blob' },
    );
  }

  // ============================================================
  // CREATE CHART ZIP EXPORT
  // ============================================================

  exportChartsZip(edaId: string): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/${edaId}/exports/zip`,
      {},
      { responseType: 'blob' },
    );
  }

  // ============================================================
  // GET EXPORT HISTORY FOR ONE EDA
  // ============================================================

  getExports(edaId: string, page = 0, size = 20): Observable<ExportPage> {
    const params = new HttpParams().set('page', page).set('size', size);

    return this.http.get<ExportPage>(`${this.apiUrl}/${edaId}/exports`, { params });
  }

  // ============================================================
  // GET CURRENT USER EXPORTS
  // ============================================================

  getMyExports(page = 0, size = 20): Observable<ExportPage> {
    const params = new HttpParams().set('page', page).set('size', size);

    return this.http.get<ExportPage>(`${this.apiUrl}/exports/my`, { params });
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
