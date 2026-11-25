import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { AppNotification, NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-nav-bar',
  standalone: true,
  imports: [DatePipe, RouterLink, RouterLinkActive],
  templateUrl: './nav-bar.html',
  styleUrl: './nav-bar.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NavBar {
  readonly authService = inject(AuthService);
  readonly notificationService = inject(NotificationService);
  private readonly router = inject(Router);
  readonly notificationsOpen = signal(false);

  get navigationItems() {
    const items = [
      { label: 'Home', icon: 'bi-grid-1x2-fill', route: '/dashboard' },
      { label: 'Applications', icon: 'bi-phone-fill', route: '/list' },
      { label: 'Operations', icon: 'bi-sliders2-vertical', route: '/operations' },
      { label: 'EDA', icon: 'bi-bar-chart-fill', route: '/eda' },
    ];
    if (this.authService.isAdmin()) {
      items.push(
        { label: 'Model settings', icon: 'bi-cpu-fill', route: '/admin/predictions' },
        { label: 'Evaluations', icon: 'bi-clipboard-data-fill', route: '/admin/evaluations' },
      );
    } else {
      items.push({ label: 'Predictions', icon: 'bi-stars', route: '/predictions' });
    }
    return items;
  }

  toggleNotifications(): void {
    const opening = !this.notificationsOpen();
    this.notificationsOpen.set(opening);
    if (opening) this.notificationService.refresh(8);
  }

  markAllNotificationsRead(): void {
    this.notificationService.markAllAsRead();
  }

  openNotification(id: string): void {
    this.notificationService.markAsRead(id);
    this.notificationsOpen.set(false);
    void this.router.navigate(['/notifications']);
  }

  openAllNotifications(): void {
    this.notificationsOpen.set(false);
    void this.router.navigate(['/notifications']);
  }

  notificationIcon(item: AppNotification): string {
    if (item.event_type.startsWith('APP_')) return 'bi-phone';
    if (item.event_type.startsWith('EDA_')) return 'bi-bar-chart';
    if (item.event_type.startsWith('MODEL_')) return 'bi-cpu';
    return 'bi-bell';
  }

  async logout(): Promise<void> {
    await this.authService.logout();
  }
}
