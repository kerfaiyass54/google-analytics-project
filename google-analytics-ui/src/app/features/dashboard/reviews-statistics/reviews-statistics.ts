import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-reviews-statistics',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './reviews-statistics.html',
  styleUrl: './reviews-statistics.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReviewsStatistics {
  readonly minimum = input<number>(0);
  readonly average = input<number>(0);
  readonly maximum = input<number>(0);
}
