import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-size-statistics',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './size-statistics.html',
  styleUrl: './size-statistics.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SizeStatistics {
  readonly minimum = input<number>(0);
  readonly average = input<number>(0);
  readonly maximum = input<number>(0);
}
