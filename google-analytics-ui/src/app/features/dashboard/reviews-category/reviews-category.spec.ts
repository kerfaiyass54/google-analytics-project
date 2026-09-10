import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReviewsCategory } from './reviews-category';

describe('ReviewsCategory', () => {
  let component: ReviewsCategory;
  let fixture: ComponentFixture<ReviewsCategory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReviewsCategory],
    }).compileComponents();

    fixture = TestBed.createComponent(ReviewsCategory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
