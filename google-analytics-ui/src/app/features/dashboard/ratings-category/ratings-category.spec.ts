import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RatingsCategory } from './ratings-category';

describe('RatingsCategory', () => {
  let component: RatingsCategory;
  let fixture: ComponentFixture<RatingsCategory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RatingsCategory],
    }).compileComponents();

    fixture = TestBed.createComponent(RatingsCategory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
