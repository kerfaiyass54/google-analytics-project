import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReviewsStatistics } from './reviews-statistics';

describe('ReviewsStatistics', () => {
  let component: ReviewsStatistics;
  let fixture: ComponentFixture<ReviewsStatistics>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReviewsStatistics],
    }).compileComponents();

    fixture = TestBed.createComponent(ReviewsStatistics);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
