import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'app-ratings-statistics',
  standalone: true,
  imports: [],
  templateUrl: './ratings-statistics.html',
  styleUrl: './ratings-statistics.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RatingsStatistics {
  readonly minimum = input<number>(0);
  readonly average = input<number>(0);
  readonly maximum = input<number>(0);
}
