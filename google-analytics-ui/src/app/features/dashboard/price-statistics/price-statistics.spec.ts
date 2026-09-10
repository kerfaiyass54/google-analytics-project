import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PriceStatistics } from './price-statistics';

describe('PriceStatistics', () => {
  let component: PriceStatistics;
  let fixture: ComponentFixture<PriceStatistics>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PriceStatistics],
    }).compileComponents();

    fixture = TestBed.createComponent(PriceStatistics);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
