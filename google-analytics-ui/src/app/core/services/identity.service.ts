import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface UserProfile {
  id: string;
  username: string;
  email: string | null;
  firstName: string | null;
  lastName: string | null;
  enabled: boolean;
  emailVerified: boolean;
  createdAt: string | null;
}

export interface UserSession {
  id: string;
  ipAddress: string | null;
  startedAt: string | null;
  lastAccessAt: string | null;
  closedAt: string | null;
  status: 'ACTIVE' | 'CLOSED';
  clients: string | null;
}

export interface SessionSummary {
  active: number;
  closed: number;
  daily: Array<{ date: string; started: number; closed: number }>;
}

@Injectable({ providedIn: 'root' })
export class IdentityService {
  private readonly http = inject(HttpClient);
  private readonly api = 'http://localhost:8040/api';

  getProfile(): Observable<UserProfile> { return this.http.get<UserProfile>(`${this.api}/profile`); }
  updateProfile(data: Pick<UserProfile, 'firstName' | 'lastName' | 'email'>): Observable<UserProfile> {
    return this.http.put<UserProfile>(`${this.api}/profile`, data);
  }
  requestPasswordReset(): Observable<void> {
    return this.http.put<void>(`${this.api}/profile/password-reset`, {});
  }
  getMySessions(): Observable<UserSession[]> { return this.http.get<UserSession[]>(`${this.api}/profile/sessions`); }
  getSessionSummary(): Observable<SessionSummary> { return this.http.get<SessionSummary>(`${this.api}/admin/sessions/summary`); }
}
