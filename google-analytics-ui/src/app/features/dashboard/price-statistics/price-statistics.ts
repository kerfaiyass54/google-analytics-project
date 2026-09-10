import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-price-statistics',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './price-statistics.html',
  styleUrl: './price-statistics.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PriceStatistics {
  readonly minimum = input<number>(0);
  readonly average = input<number>(0);
  readonly maximum = input<number>(0);
}
