import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

@Component({
  selector: 'app-free-vs-paid',
  standalone: true,
  imports: [],
  templateUrl: './free-vs-paid.html',
  styleUrl: './free-vs-paid.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FreeVsPaid {
  readonly freeApps = input<number>(0);

  readonly paidApps = input<number>(0);

  readonly totalApps = computed(() => this.freeApps() + this.paidApps());

  readonly freePercentage = computed(() => {
    const total = this.totalApps();

    if (total === 0) {
      return 0;
    }

    return (this.freeApps() / total) * 100;
  });

  readonly paidPercentage = computed(() => {
    const total = this.totalApps();

    if (total === 0) {
      return 0;
    }

    return (this.paidApps() / total) * 100;
  });

  readonly freeAngle = computed(() => this.freePercentage() * 3.6);

  readonly chartBackground = computed(() => {
    const freeAngle = this.freeAngle();

    return `conic-gradient(
      #6366f1 0deg ${freeAngle}deg,
      #e2e8f0 ${freeAngle}deg 360deg
    )`;
  });
}
