import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  OnChanges,
  SimpleChanges,
  ViewChild,
  inject,
  input,
} from '@angular/core';

import {
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';



Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

@Component({
  selector: 'app-application-category',
  standalone: true,
  imports: [],
  templateUrl: './application-category.html',
  styleUrl: './application-category.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ApplicationCategory implements AfterViewInit, OnChanges {
  private readonly destroyRef = inject(DestroyRef);

  @ViewChild('chartCanvas')
  private readonly chartCanvas?: ElementRef<HTMLCanvasElement>;

  readonly categories = input<any[]>([]);

  private chart: Chart<'bar'> | null = null;
  private viewInitialized = false;

  ngAfterViewInit(): void {
    this.viewInitialized = true;
    this.createChart();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!changes['categories'] || !this.viewInitialized) {
      return;
    }

    this.createChart();
  }

  private createChart(): void {
    const canvas = this.chartCanvas?.nativeElement;
    const categories = this.categories();

    if (!canvas || categories.length === 0) {
      this.destroyChart();
      return;
    }

    this.destroyChart();

    this.chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: categories.map((category) => category.category),
        datasets: [
          {
            label: 'Application',
            data: categories.map((category) => category.appCount),
            borderRadius: 8,
            borderSkipped: false,
            maxBarThickness: 42,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,

        animation: {
          duration: 900,
          easing: 'easeOutQuart',
        },

        interaction: {
          intersect: false,
          mode: 'index',
        },

        plugins: {
          legend: {
            display: false,
          },

          tooltip: {
            enabled: true,
            displayColors: false,
            padding: 12,

            callbacks: {
              label: (context) => {
                const value = context.parsed.y ?? 0;
                return ` Application: ${value.toLocaleString()}`;
              },
            },
          },
        },

        scales: {
          x: {
            grid: {
              display: false,
            },

            ticks: {
              color: '#64748b',
              font: {
                size: 11,
              },
              maxRotation: 45,
              minRotation: 0,
            },
          },

          y: {
            beginAtZero: true,

            grid: {
              color: 'rgba(148, 163, 184, 0.15)',
            },

            border: {
              display: false,
            },

            ticks: {
              color: '#64748b',
              precision: 0,

              callback: (value) => {
                return Number(value).toLocaleString();
              },
            },
          },
        },
      },
    });
  }

  private destroyChart(): void {
    if (!this.chart) {
      return;
    }

    this.chart.destroy();
    this.chart = null;
  }

  constructor() {
    this.destroyRef.onDestroy(() => {
      this.destroyChart();
    });
  }
}
