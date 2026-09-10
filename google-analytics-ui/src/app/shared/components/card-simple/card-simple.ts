import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-card-simple',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './card-simple.html',
  styleUrl: './card-simple.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CardSimple {
  // ==========================================================
  // INPUTS
  // ==========================================================

  readonly icon = input<string>('bi bi-grid');

  readonly title = input<string>('Card');

  readonly link = input<string>('/');

  readonly color = input<string>('#6366f1');
}
