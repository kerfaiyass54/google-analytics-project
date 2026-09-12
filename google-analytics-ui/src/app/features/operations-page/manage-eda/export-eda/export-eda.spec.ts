import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExportEda } from './export-eda';

describe('ExportEda', () => {
  let component: ExportEda;
  let fixture: ComponentFixture<ExportEda>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ExportEda],
    }).compileComponents();

    fixture = TestBed.createComponent(ExportEda);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
