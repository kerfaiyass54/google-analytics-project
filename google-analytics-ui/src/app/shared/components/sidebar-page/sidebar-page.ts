import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  input,
  signal,
} from '@angular/core';

export interface SidebarItem {
  id: string;
  name: string;
  icon: string;
}

@Component({
  selector: 'app-sidebar-page',
  standalone: true,
  imports: [],
  templateUrl: './sidebar-page.html',
  styleUrl: './sidebar-page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SidebarPage implements AfterViewInit {
  /**
   * Sections that exist on the current page.
   *
   * Example:
   * [
   *   { id: 'overview', name: 'Overview', icon: 'bi bi-house' },
   *   { id: 'statistics', name: 'Statistics', icon: 'bi bi-bar-chart' }
   * ]
   */
  readonly items = input<SidebarItem[]>([]);

  /**
   * Currently visible section.
   */
  readonly activeId = signal<string>('');

  private observer?: IntersectionObserver;

  constructor(private readonly destroyRef: DestroyRef) {
    this.destroyRef.onDestroy(() => {
      this.observer?.disconnect();
    });
  }

  ngAfterViewInit(): void {
    this.observeSections();
  }

  /**
   * Scroll to a page section.
   */
  scrollToSection(id: string): void {
    const element = document.getElementById(id);

    if (!element) {
      return;
    }

    this.activeId.set(id);

    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }

  /**
   * Observe sections to automatically update
   * the active sidebar item while scrolling.
   */
  private observeSections(): void {
    const elements = this.items()
      .map((item) => document.getElementById(item.id))
      .filter((element): element is HTMLElement => element !== null);

    if (!elements.length) {
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        const visibleEntries = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

        if (visibleEntries.length > 0) {
          this.activeId.set(visibleEntries[0].target.id);
        }
      },
      {
        root: null,
        rootMargin: '-20% 0px -60% 0px',
        threshold: [0, 0.25, 0.5, 0.75, 1],
      },
    );

    elements.forEach((element) => {
      this.observer?.observe(element);
    });
  }
}
