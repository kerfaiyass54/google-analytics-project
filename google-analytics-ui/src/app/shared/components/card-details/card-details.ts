import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-card-details',
  standalone: true,
  imports: [],
  templateUrl: './card-details.html',
  styleUrl: './card-details.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CardDetails {
  // ==========================================================
  // INPUTS
  // ==========================================================

  readonly title = input<string>('Details');

  readonly icon = input<string>('bi bi-info-circle');

  readonly attributes = input<string[]>([]);

  readonly values = input<unknown[]>([]);
}
