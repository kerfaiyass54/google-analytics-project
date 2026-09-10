import { Component, signal } from '@angular/core';
import { BarChart } from '../charts/bar-chart/bar-chart';
import { ChartDataset } from '../../models/chart.model';
import { LineChart } from '../../../shared/components/charts/line-chart/line-chart';


@Component({
  selector: 'app-developer-tools',
  imports: [BarChart, LineChart],
  templateUrl: './developer-tools.html',
  styleUrl: './developer-tools.css',
})
export class DeveloperTools {
  readonly lineChartDatasets = signal<ChartDataset[]>([
    {
      label: 'Average Rating',
      data: [3.8, 4.1, 4.3, 4.0, 4.5],
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99, 102, 241, 0.15)',
      borderWidth: 3,
      tension: 0.4,
      fill: true,
      pointRadius: 5,
      pointHoverRadius: 8,
    },
  ]);

  readonly chartTitle = signal('Applications by Category');

  readonly chartLabels = signal(['Games', 'Education', 'Business', 'Medical', 'Sports']);

  readonly chartDatasets = signal<ChartDataset[]>([
    {
      label: 'Applications',
      data: [120, 85, 65, 45, 30],
      backgroundColor: ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'],
      borderWidth: 0,
      borderRadius: 8,
    },
  ]);
}
