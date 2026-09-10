import { ChangeDetectionStrategy, Component } from '@angular/core';
import { Location } from '@angular/common';

@Component({
  selector: 'app-cancel-button',
  standalone: true,
  imports: [],
  templateUrl: './cancel-button.html',
  styleUrl: './cancel-button.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CancelButton {
  constructor(private readonly location: Location) {}

  // ==========================================================
  // RETURN TO PREVIOUS PAGE
  // ==========================================================

  goBack(): void {
    this.location.back();
  }
}
