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
  selector: 'app-bar-chart',
  standalone: true,
  templateUrl: './bar-chart.html',
  styleUrl: './bar-chart.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BarChart {
  private readonly destroyRef = inject(DestroyRef);

  private chart?: Chart<'bar'>;

  readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  /*
   * ============================================================
   * SIGNAL INPUTS
   * ============================================================
   */

  readonly title = input<string>('');

  readonly labels = input<string[]>([]);

  readonly datasets = input<ChartDataset[]>([]);

  readonly options = input<ChartOptions<'bar'>>({});

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
      /*
       * Reading the signal inputs here makes the effect
       * automatically react whenever one of them changes.
       */

      const labels = this.labels();
      const datasets = this.datasets();
      const title = this.title();
      const options = this.options();

      /*
       * Access the canvas through the signal query.
       */

      const canvas = this.canvas().nativeElement;

      this.renderChart(canvas, labels, datasets, title, options);
    });

    /*
     * Destroy the Chart.js instance when Angular
     * destroys the component.
     */

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
    customOptions: ChartOptions<'bar'>,
  ): void {
    /*
     * Destroy the previous Chart.js instance before
     * creating a new one.
     */

    this.chart?.destroy();

    const configuration: ChartConfiguration<'bar'> = {
      type: 'bar',

      data: {
        labels,

        datasets: datasets.map((dataset) => ({
          label: dataset.label,

          data: dataset.data,

          backgroundColor: dataset.backgroundColor,

          borderColor: dataset.borderColor,

          borderWidth: dataset.borderWidth ?? 1,

          borderRadius: dataset.borderRadius ?? 6,

          tension: dataset.tension,

          fill: dataset.fill,

          pointRadius: dataset.pointRadius,

          pointHoverRadius: dataset.pointHoverRadius,
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
