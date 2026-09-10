import { ChangeDetectionStrategy, Component, input } from '@angular/core';

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
}
