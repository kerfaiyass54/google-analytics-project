import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { GooglePlayAppService } from '../../../core/services/google-play-app.service';
import { AppType } from '../../../shared/models/app-type';
import { GooglePlayAppRequest } from '../../../shared/models/google-play-app-request';

@Component({
  selector: 'app-add-application',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './add-application.html',
  styleUrl: './add-application.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddApplication {
  private readonly fb = inject(FormBuilder);
  private readonly appService = inject(GooglePlayAppService);

  readonly submitting = signal(false);
  readonly errorMessage = signal('');
  readonly successMessage = signal('');

  readonly currentStep = signal(1);

  readonly appTypes = Object.values(AppType);

  readonly applicationForm = this.fb.nonNullable.group({
    app: ['', [Validators.required, Validators.maxLength(255)]],

    category: ['', [Validators.required, Validators.maxLength(100)]],

    rating: [0, [Validators.required, Validators.min(0), Validators.max(5)]],

    reviews: [0, [Validators.required, Validators.min(0)]],

    sizeMb: [0, [Validators.required, Validators.min(0)]],

    installs: ['', [Validators.required, Validators.maxLength(50)]],

    type: [AppType.FREE, Validators.required],

    price: [0, [Validators.required, Validators.min(0)]],

    contentRating: ['', [Validators.required, Validators.maxLength(50)]],

    genres: ['', [Validators.required, Validators.maxLength(255)]],

    lastUpdated: ['', Validators.required],

    currentVersion: ['', [Validators.required, Validators.maxLength(100)]],

    androidVersion: ['', [Validators.required, Validators.maxLength(100)]],
  });

  get app() {
    return this.applicationForm.controls.app;
  }

  get category() {
    return this.applicationForm.controls.category;
  }

  get rating() {
    return this.applicationForm.controls.rating;
  }

  get reviews() {
    return this.applicationForm.controls.reviews;
  }

  get sizeMb() {
    return this.applicationForm.controls.sizeMb;
  }

  get installs() {
    return this.applicationForm.controls.installs;
  }

  get type() {
    return this.applicationForm.controls.type;
  }

  get price() {
    return this.applicationForm.controls.price;
  }

  get contentRating() {
    return this.applicationForm.controls.contentRating;
  }

  get genres() {
    return this.applicationForm.controls.genres;
  }

  get lastUpdated() {
    return this.applicationForm.controls.lastUpdated;
  }

  get currentVersion() {
    return this.applicationForm.controls.currentVersion;
  }

  get androidVersion() {
    return this.applicationForm.controls.androidVersion;
  }

  isStep(step: number): boolean {
    return this.currentStep() === step;
  }

  isCompleted(step: number): boolean {
    return this.currentStep() > step;
  }

  goToStep(step: number): void {
    if (step < 1 || step > 3) {
      return;
    }

    if (step > this.currentStep()) {
      return;
    }

    this.currentStep.set(step);
    this.clearMessages();
  }

  nextStep(): void {
    const step = this.currentStep();

    if (!this.validateStep(step)) {
      return;
    }

    if (step < 3) {
      this.clearMessages();
      this.currentStep.set(step + 1);
      return;
    }

    this.submit();
  }

  previousStep(): void {
    if (this.currentStep() <= 1) {
      return;
    }

    this.clearMessages();
    this.currentStep.update((step) => step - 1);
  }

  private validateStep(step: number): boolean {
    const controlsByStep: Record<number, string[]> = {
      1: ['app', 'category', 'type', 'genres'],

      2: ['rating', 'reviews', 'sizeMb', 'installs', 'price', 'contentRating'],

      3: ['lastUpdated', 'currentVersion', 'androidVersion'],
    };

    const controlNames = controlsByStep[step] ?? [];

    let valid = true;

    for (const controlName of controlNames) {
      const control = this.applicationForm.get(controlName);

      if (!control) {
        continue;
      }

      if (control.invalid) {
        control.markAsTouched();
        valid = false;
      }
    }

    if (!valid) {
      this.errorMessage.set('Please complete all required fields before continuing.');
    }

    return valid;
  }

  submit(): void {
    this.errorMessage.set('');
    this.successMessage.set('');

    if (this.applicationForm.invalid) {
      this.applicationForm.markAllAsTouched();

      return;
    }

    this.submitting.set(true);

    const request: GooglePlayAppRequest = {
      app: this.app.value.trim(),
      category: this.category.value.trim(),
      rating: this.rating.value,
      reviews: this.reviews.value,
      sizeMb: this.sizeMb.value,
      installs: this.installs.value.trim(),
      type: this.type.value,
      price: this.price.value,
      contentRating: this.contentRating.value.trim(),
      genres: this.genres.value.trim(),
      lastUpdated: this.lastUpdated.value,
      currentVersion: this.currentVersion.value.trim(),
      androidVersion: this.androidVersion.value.trim(),
    };

    this.appService.create(request).subscribe({
      next: () => {
        this.submitting.set(false);

        this.successMessage.set('Application added successfully.');

        this.currentStep.set(4);
      },

      error: (error) => {
        console.error('Failed to add application:', error);

        this.errorMessage.set(error?.error?.message ?? 'Failed to add application.');

        this.submitting.set(false);
      },
    });
  }

  resetForm(): void {
    this.applicationForm.reset({
      app: '',
      category: '',
      rating: 0,
      reviews: 0,
      sizeMb: 0,
      installs: '',
      type: AppType.FREE,
      price: 0,
      contentRating: '',
      genres: '',
      lastUpdated: '',
      currentVersion: '',
      androidVersion: '',
    });

    this.currentStep.set(1);

    this.errorMessage.set('');
    this.successMessage.set('');

    this.applicationForm.markAsPristine();
    this.applicationForm.markAsUntouched();
  }

  clearMessages(): void {
    this.errorMessage.set('');
    this.successMessage.set('');
  }

  showError(control: { invalid: boolean; touched: boolean; dirty: boolean }): boolean {
    return control.invalid && (control.touched || control.dirty);
  }
}
