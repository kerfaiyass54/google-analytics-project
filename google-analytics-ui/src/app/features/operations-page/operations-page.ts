import { ChangeDetectionStrategy, Component } from '@angular/core';

import { CardSimple } from '../../shared/components/card-simple/card-simple';

interface OperationCard {
  icon: string;
  title: string;
  link: string;
  color: string;
}

@Component({
  selector: 'app-operations-page',
  standalone: true,
  imports: [CardSimple],
  templateUrl: './operations-page.html',
  styleUrl: './operations-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OperationsPage {
  readonly operations: OperationCard[] = [
    {
      icon: 'bi bi-plus-circle-fill',
      title: 'Add Application',
      link: '/operations/add-application',
      color: '#6366f1',
    },
    {
      icon: 'bi bi-file-earmark-bar-graph-fill',
      title: 'Check EDA Files',
      link: '/operations/check-eda-files',
      color: '#06b6d4',
    },
    {
      icon: 'bi bi-trash3-fill',
      title: 'Delete Applications',
      link: '/operations/delete-applications',
      color: '#ef4444',
    },
    {
      icon: 'bi bi-grid-1x2-fill',
      title: 'Manage Apps',
      link: '/operations/manage-apps',
      color: '#8b5cf6',
    },
    {
      icon: 'bi bi-bar-chart-line-fill',
      title: 'Manage EDA',
      link: '/operations/manage-eda',
      color: '#10b981',
    },
  ];
}
