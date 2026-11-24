import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { timer, switchMap, catchError, of } from 'rxjs';

export interface AppNotification {
  id: string;
  event_id: string;
  event_type: string;
  title: string;
  message: string;
  entity_type?: string | null;
  entity_id?: string | null;
  payload: Record<string, unknown>;
  created_at: string;
  read_at: string | null;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private readonly http = inject(HttpClient);
  private readonly api = 'http://localhost:8030/api/notifications';

  readonly notifications = signal<AppNotification[]>([]);
  readonly history = signal<AppNotification[]>([]);
  readonly unreadCount = signal(0);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  constructor() {
    timer(0, 15000).pipe(
      switchMap(() => this.http.get<AppNotification[]>(this.api, { params: { limit: '8' } }).pipe(
        catchError(() => of(null))
      ))
    ).subscribe(items => {
      if (items === null) return;
      this.notifications.set(items);
      this.refreshUnreadCount();
    });
  }

  refresh(limit = 8): void {
    this.loading.set(true);
    this.http.get<AppNotification[]>(this.api, { params: { limit: String(limit) } }).pipe(
      catchError(() => { this.error.set('Could not load notifications.'); return of([]); })
    ).subscribe(items => {
      this.notifications.set(items);
      this.loading.set(false);
      this.refreshUnreadCount();
    });
  }

  refreshHistory(): void {
    this.loading.set(true);
    this.http.get<AppNotification[]>(this.api, { params: { limit: '100' } }).pipe(
      catchError(() => { this.error.set('Could not load notification history.'); return of([]); })
    ).subscribe(items => {
      this.history.set(items);
      this.loading.set(false);
      this.refreshUnreadCount();
    });
  }

  refreshUnreadCount(): void {
    this.http.get<{ count: number }>(`${this.api}/unread-count`).pipe(
      catchError(() => of({ count: 0 }))
    ).subscribe(result => this.unreadCount.set(result.count));
  }

  markAsRead(id: string): void {
    const wasUnread = [...this.notifications(), ...this.history()].some(item => item.id === id && !item.read_at);
    this.http.patch(`${this.api}/${id}/read`, {}).subscribe(() => {
      const readAt = new Date().toISOString();
      this.notifications.update(items => items.map(item =>
        item.id === id ? { ...item, read_at: item.read_at ?? readAt } : item
      ));
      this.history.update(items => items.map(item =>
        item.id === id ? { ...item, read_at: item.read_at ?? readAt } : item
      ));
      if (wasUnread) this.unreadCount.update(count => Math.max(0, count - 1));
    });
  }

  markAllAsRead(): void {
    this.http.patch<{ updated: number }>(`${this.api}/read-all`, {}).subscribe(result => {
      const now = new Date().toISOString();
      this.notifications.update(items => items.map(item => ({ ...item, read_at: item.read_at ?? now })));
      this.history.update(items => items.map(item => ({ ...item, read_at: item.read_at ?? now })));
      this.unreadCount.update(count => Math.max(0, count - result.updated));
    });
  }
}
