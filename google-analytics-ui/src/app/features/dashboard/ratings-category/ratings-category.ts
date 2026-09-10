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
  selector: 'app-ratings-category',
  standalone: true,
  imports: [],
  templateUrl: './ratings-category.html',
  styleUrl: './ratings-category.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RatingsCategory implements AfterViewInit, OnChanges {
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
            label: 'Average Rating',
            data: categories.map((category) => category.averageRating),
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
                return ` Average rating: ${value.toFixed(2)} / 5`;
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
            min: 0,
            max: 5,

            grid: {
              color: 'rgba(148, 163, 184, 0.15)',
            },

            border: {
              display: false,
            },

            ticks: {
              color: '#64748b',
              stepSize: 0.5,

              callback: (value) => {
                return `${value}`;
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
