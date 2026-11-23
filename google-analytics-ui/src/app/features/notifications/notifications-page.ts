import { Component, inject, OnInit } from '@angular/core';
import { DatePipe } from '@angular/common';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-notifications-page',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './notifications-page.html',
  styleUrl: './notifications-page.css'
})
export class NotificationsPage implements OnInit {
  readonly service = inject(NotificationService);
  readonly filters = ['ALL', 'UNREAD'] as const;
  filter: 'ALL' | 'UNREAD' = 'ALL';

  ngOnInit(): void { this.service.refresh(); }

  get visibleNotifications() {
    const items = this.service.notifications();
    return this.filter === 'UNREAD' ? items.filter(item => !item.read_at) : items;
  }

  markRead(id: string): void { this.service.markAsRead(id); }
  markAll(): void { this.service.markAllAsRead(); }

  icon(type: string): string {
    if (type.includes('APP')) return 'bi-phone';
    if (type.includes('EDA')) return 'bi-bar-chart';
    return 'bi-cpu';
  }
}
