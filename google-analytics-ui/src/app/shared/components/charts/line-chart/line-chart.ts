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
import { Chart } from '../../../utils/chartjs';
import { ChartDataset } from '../../../models/chart.model';

@Component({
  selector: 'app-line-chart',
  standalone: true,
  templateUrl: './line-chart.html',
  styleUrl: './line-chart.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LineChart {
  private readonly destroyRef = inject(DestroyRef);

  private chart?: Chart<'line'>;

  readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  /*
   * ============================================================
   * SIGNAL INPUTS
   * ============================================================
   */

  readonly title = input<string>('');

  readonly labels = input<string[]>([]);

  readonly datasets = input<ChartDataset[]>([]);

  readonly options = input<ChartOptions<'line'>>({});

  readonly height = input<number>(400);

  readonly width = input<number | null>(null);

  readonly showLegend = input<boolean>(true);

  readonly showTitle = input<boolean>(true);

  readonly showGrid = input<boolean>(true);

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
    customOptions: ChartOptions<'line'>,
  ): void {
    this.chart?.destroy();

    const configuration: ChartConfiguration<'line'> = {
      type: 'line',

      data: {
        labels,

        datasets: datasets.map((dataset) => ({
          label: dataset.label,

          data: dataset.data,

          backgroundColor: dataset.backgroundColor,

          borderColor: dataset.borderColor,

          borderWidth: dataset.borderWidth ?? 2,

          borderRadius: dataset.borderRadius,

          tension: dataset.tension ?? 0.3,

          fill: dataset.fill ?? false,

          pointRadius: dataset.pointRadius ?? 4,

          pointHoverRadius: dataset.pointHoverRadius ?? 6,
        })),
      },

      options: {
        responsive: true,

        maintainAspectRatio: false,

        plugins: {
          legend: {
            display: this.showLegend(),
          },

          title: {
            display: this.showTitle() && title.trim().length > 0,

            text: title,
          },
        },

        scales: {
          x: {
            grid: {
              display: this.showGrid(),
            },
          },

          y: {
            beginAtZero: true,

            grid: {
              display: this.showGrid(),
            },
          },
        },

        ...customOptions,
      },
    };

    this.chart = new Chart(canvas, configuration);
  }
}
