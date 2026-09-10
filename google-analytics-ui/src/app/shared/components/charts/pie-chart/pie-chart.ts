import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  effect,
  inject,
  input,
  viewChild,
} from '@angular/core';

import { ChartConfiguration, ChartOptions } from 'chart.js';

import { Chart } from '../../../utils/chartjs'
import { ChartDataset } from '../../../models/chart.model';

@Component({
  selector: 'app-pie-chart',
  standalone: true,
  templateUrl: './pie-chart.html',
  styleUrl: './pie-chart.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PieChart {
  private readonly destroyRef = inject(DestroyRef);

  private chart?: Chart<'pie'>;

  readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  /*
   * ============================================================
   * SIGNAL INPUTS
   * ============================================================
   */

  readonly title = input<string>('');

  readonly labels = input<string[]>([]);

  readonly datasets = input<ChartDataset[]>([]);

  readonly options = input<ChartOptions<'pie'>>({});

  readonly height = input<number>(400);

  readonly width = input<number | null>(null);

  readonly showLegend = input<boolean>(true);

  readonly showTitle = input<boolean>(true);

  /*
   * ============================================================
   * CONSTRUCTOR
   * ============================================================
   */

  constructor() {
    effect(() => {
      const labels = this.labels();
      const datasets = this.datasets();
      const title = this.title();
      const options = this.options();

      const canvas = this.canvas().nativeElement;

      this.renderChart(canvas, labels, datasets, title, options);
    });

    this.destroyRef.onDestroy(() => {
      this.chart?.destroy();
    });
  }

  /*
   * ============================================================
   * CHART CREATION
   * ============================================================
   */

  private renderChart(
    canvas: HTMLCanvasElement,
    labels: string[],
    datasets: ChartDataset[],
    title: string,
    customOptions: ChartOptions<'pie'>,
  ): void {
    this.chart?.destroy();

    const configuration: ChartConfiguration<'pie'> = {
      type: 'pie',

      data: {
        labels,

        datasets: datasets.map((dataset) => ({
          label: dataset.label,

          data: dataset.data,

          backgroundColor: dataset.backgroundColor,

          borderColor: dataset.borderColor,

          borderWidth: dataset.borderWidth ?? 1,
        })),
      },

      options: {
        responsive: true,

        maintainAspectRatio: false,

        plugins: {
          legend: {
            display: this.showLegend(),

            position: 'right',
          },

          title: {
            display: this.showTitle() && title.trim().length > 0,

            text: title,
          },
        },

        ...customOptions,
      },
    };

    this.chart = new Chart(canvas, configuration);
  }
}
