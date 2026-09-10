import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SizeStatistics } from './size-statistics';

describe('SizeStatistics', () => {
  let component: SizeStatistics;
  let fixture: ComponentFixture<SizeStatistics>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SizeStatistics],
    }).compileComponents();

    fixture = TestBed.createComponent(SizeStatistics);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
