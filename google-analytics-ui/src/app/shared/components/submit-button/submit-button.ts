import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

@Component({
  selector: 'app-submit-button',
  standalone: true,
  imports: [],
  templateUrl: './submit-button.html',
  styleUrl: './submit-button.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SubmitButton {
  // ==========================================================
  // INPUTS
  // ==========================================================

  readonly label = input<string>('Submit');

  readonly icon = input<string>('bi bi-check-lg');

  readonly type = input<'button' | 'submit' | 'reset'>('submit');

  readonly variant = input<'primary' | 'success' | 'danger' | 'warning' | 'secondary'>('primary');

  readonly loading = input<boolean>(false);

  readonly disabled = input<boolean>(false);

  readonly fullWidth = input<boolean>(false);

  // ==========================================================
  // OUTPUTS
  // ==========================================================

  readonly clicked = output<void>();

  // ==========================================================
  // CLICK
  // ==========================================================

  onClick(): void {
    if (this.loading() || this.disabled()) {
      return;
    }

    this.clicked.emit();
  }
}
