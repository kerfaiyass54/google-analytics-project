import { ChartData, ChartOptions, ChartType } from 'chart.js';

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  borderRadius?: number;
  tension?: number;
  fill?: boolean;
  pointRadius?: number;
  pointHoverRadius?: number;
}

export interface BaseChartConfig {
  type: ChartType;

  title?: string;

  labels?: string[];

  datasets: ChartDataset[];

  options?: ChartOptions;

  height?: number;

  width?: number;
}

export interface BarChartConfig {
  title?: string;

  labels: string[];

  datasets: ChartDataset[];

  options?: ChartOptions;

  height?: number;

  width?: number;
}

export interface LineChartConfig {
  title?: string;

  labels: string[];

  datasets: ChartDataset[];

  options?: ChartOptions;

  height?: number;

  width?: number;
}

export interface PieChartConfig {
  title?: string;

  labels: string[];

  datasets: ChartDataset[];

  options?: ChartOptions;

  height?: number;

  width?: number;
}

export interface DoughnutChartConfig {
  title?: string;

  labels: string[];

  datasets: ChartDataset[];

  options?: ChartOptions;

  height?: number;

  width?: number;
}

export interface ScatterChartConfig {
  title?: string;

  datasets: ChartDataset[];

  options?: ChartOptions;

  height?: number;

  width?: number;
}
