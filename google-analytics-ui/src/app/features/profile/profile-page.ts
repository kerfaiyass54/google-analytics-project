import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { IdentityService, UserProfile, UserSession } from '../../core/services/identity.service';
import { ScrollRevealDirective } from '../../shared/directives/scroll-reveal.directive';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [DatePipe, FormsModule, ScrollRevealDirective],
  templateUrl: './profile-page.html',
  styleUrl: './profile-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfilePage implements OnInit {
  private readonly identity = inject(IdentityService);
  readonly profile = signal<UserProfile | null>(null);
  readonly sessions = signal<UserSession[]>([]);
  readonly loading = signal(true);
  readonly saving = signal(false);
  readonly error = signal('');
  readonly success = signal('');
  readonly profileDialogOpen = signal(false);
  readonly passwordDialogOpen = signal(false);
  readonly details = { firstName: '', lastName: '', email: '' };
  readonly passwords = { currentPassword: '', newPassword: '', confirmPassword: '' };

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.error.set('');
    this.identity.getProfile().subscribe({
      next: profile => {
        this.profile.set(profile);
        this.details.firstName = profile.firstName ?? '';
        this.details.lastName = profile.lastName ?? '';
        this.details.email = profile.email ?? '';
        this.loading.set(false);
      },
      error: () => { this.error.set('Could not load your profile. Check that the identity service is running.'); this.loading.set(false); },
    });
    this.identity.getMySessions().subscribe({
      next: sessions => this.sessions.set(sessions),
      error: () => this.sessions.set([]),
    });
  }

  openProfileDialog(): void {
    const profile = this.profile();
    if (!profile) return;
    this.details.firstName = profile.firstName ?? '';
    this.details.lastName = profile.lastName ?? '';
    this.details.email = profile.email ?? '';
    this.profileDialogOpen.set(true);
  }

  saveProfile(): void {
    this.saving.set(true); this.error.set(''); this.success.set('');
    this.identity.updateProfile(this.details).subscribe({
      next: profile => {
        this.profile.set(profile); this.profileDialogOpen.set(false); this.saving.set(false);
        this.success.set('Your profile details were updated in Keycloak.');
      },
      error: err => { this.saving.set(false); this.error.set(err?.error?.detail ?? 'Profile update failed. Please verify your details and try again.'); },
    });
  }

  changePassword(): void {
    if (this.passwords.newPassword !== this.passwords.confirmPassword) {
      this.error.set('The new password and confirmation do not match.'); return;
    }
    this.saving.set(true); this.error.set(''); this.success.set('');
    this.identity.changePassword(this.passwords.currentPassword, this.passwords.newPassword).subscribe({
      next: () => {
        this.passwordDialogOpen.set(false); this.saving.set(false);
        this.passwords.currentPassword = ''; this.passwords.newPassword = ''; this.passwords.confirmPassword = '';
        this.success.set('Your password was changed successfully.');
      },
      error: err => { this.saving.set(false); this.error.set(err?.error?.detail ?? 'Password update failed. Check your current password and Keycloak account settings.'); },
    });
  }

  activeSessions(): number { return this.sessions().filter(session => session.status === 'ACTIVE').length; }
  sessionLabel(session: UserSession): string { return session.status === 'ACTIVE' ? 'Active now' : 'Closed'; }
}
