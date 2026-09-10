import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { GooglePlayAppStatisticsResponse } from '../../shared/models/google-play-app-statistics';

@Injectable({
  providedIn: 'root',
})
export class StatisticsService {
  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8880/api/google-play-apps/statistics';

  // =========================================================
  // GET STATISTICS
  // =========================================================

  getStatistics(): Observable<GooglePlayAppStatisticsResponse> {
    return this.http.get<GooglePlayAppStatisticsResponse>(this.apiUrl);
  }
}
