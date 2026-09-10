import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RatingsStatistics } from './ratings-statistics';

describe('RatingsStatistics', () => {
  let component: RatingsStatistics;
  let fixture: ComponentFixture<RatingsStatistics>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RatingsStatistics],
    }).compileComponents();

    fixture = TestBed.createComponent(RatingsStatistics);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
