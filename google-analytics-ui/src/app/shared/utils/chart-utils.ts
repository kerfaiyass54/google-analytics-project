import { Chart, ChartConfiguration, ChartType } from 'chart.js';

export function createChart<TType extends ChartType>(
  canvas: HTMLCanvasElement,
  configuration: ChartConfiguration<TType>,
): Chart<TType> {
  return new Chart(canvas, configuration);
}
