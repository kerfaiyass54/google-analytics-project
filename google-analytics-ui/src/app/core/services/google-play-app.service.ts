import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { GooglePlayAppRequest } from '../../shared/models/google-play-app-request';
import { GooglePlayAppResponse } from '../../shared/models/google-play-app';

export interface GooglePlayAppPage {
  content: GooglePlayAppResponse[];
  pageable: {
    pageNumber: number;
    pageSize: number;
  };
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
  first: boolean;
  last: boolean;
  empty: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class GooglePlayAppService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8880/api/google-play-apps';

  // =========================================================
  // CREATE
  // =========================================================

  create(request: GooglePlayAppRequest): Observable<GooglePlayAppResponse> {
    return this.http.post<GooglePlayAppResponse>(this.apiUrl, request);
  }

  // =========================================================
  // GET DETAILS
  // =========================================================

  getDetails(id: number): Observable<GooglePlayAppResponse> {
    return this.http.get<GooglePlayAppResponse>(`${this.apiUrl}/${id}`);
  }

  // =========================================================
  // GET ALL - PAGINATED
  // =========================================================

  findAll(page: number = 0, size: number = 20): Observable<GooglePlayAppPage> {
    const params = new HttpParams().set('page', page).set('size', size).set('sort', 'app,asc');

    return this.http.get<GooglePlayAppPage>(this.apiUrl, { params });
  }

  // =========================================================
  // UPDATE
  // =========================================================

  update(id: number, request: GooglePlayAppRequest): Observable<GooglePlayAppResponse> {
    return this.http.put<GooglePlayAppResponse>(`${this.apiUrl}/${id}`, request);
  }

  // =========================================================
  // DELETE
  // =========================================================

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
