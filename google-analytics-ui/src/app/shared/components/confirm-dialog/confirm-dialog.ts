import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [],
  templateUrl: './confirm-dialog.html',
  styleUrl: './confirm-dialog.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfirmDialog {
  // ==========================================================
  // INPUTS
  // ==========================================================

  readonly title = input<string>('Confirm Action');

  readonly text = input<string>('Are you sure you want to continue?');

  readonly yesLabel = input<string>('Yes');

  readonly noLabel = input<string>('No');

  // ==========================================================
  // OUTPUTS
  // ==========================================================

  readonly confirmed = output<void>();

  readonly cancelled = output<void>();

  // ==========================================================
  // ACTIONS
  // ==========================================================

  onConfirm(): void {
    this.confirmed.emit();
  }

  onCancel(): void {
    this.cancelled.emit();
  }
}
