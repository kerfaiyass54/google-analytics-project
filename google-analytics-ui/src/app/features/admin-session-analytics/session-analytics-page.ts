import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, OnDestroy, ViewChild, inject, signal } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { IdentityService, SessionSummary } from '../../core/services/identity.service';
import { ScrollRevealDirective } from '../../shared/directives/scroll-reveal.directive';

Chart.register(...registerables);

@Component({
  selector: 'app-session-analytics-page',
  standalone: true,
  imports: [ScrollRevealDirective],
  templateUrl: './session-analytics-page.html',
  styleUrl: './session-analytics-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SessionAnalyticsPage implements AfterViewInit, OnDestroy {
  @ViewChild('sessionChart') private chartCanvas?: ElementRef<HTMLCanvasElement>;
  private readonly identity = inject(IdentityService);
  private chart?: Chart;
  readonly summary = signal<SessionSummary | null>(null);
  readonly loading = signal(true);
  readonly error = signal('');

  ngAfterViewInit(): void { this.load(); }
  ngOnDestroy(): void { this.chart?.destroy(); }

  load(): void {
    this.loading.set(true); this.error.set('');
    this.identity.getSessionSummary().subscribe({
      next: data => { this.summary.set(data); this.loading.set(false); this.renderChart(data); },
      error: () => { this.loading.set(false); this.error.set('Unable to load session analytics. Confirm the identity service and ADMIN role.'); },
    });
  }

  private renderChart(data: SessionSummary): void {
    if (!this.chartCanvas) return;
    this.chart?.destroy();
    this.chart = new Chart(this.chartCanvas.nativeElement, {
      type: 'bar',
      data: {
        labels: data.daily.map(item => item.date),
        datasets: [
          { label: 'Sessions started', data: data.daily.map(item => item.started), backgroundColor: 'rgba(99,102,241,.78)', borderRadius: 7, maxBarThickness: 32 },
          { label: 'Sessions closed', data: data.daily.map(item => item.closed), backgroundColor: 'rgba(14,165,233,.68)', borderRadius: 7, maxBarThickness: 32 },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 7, padding: 20 } } },
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: 'rgba(148,163,184,.16)' } } },
      },
    });
  }
}
