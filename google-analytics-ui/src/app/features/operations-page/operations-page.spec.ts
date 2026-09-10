import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OperationsPage } from './operations-page';

describe('OperationsPage', () => {
  let component: OperationsPage;
  let fixture: ComponentFixture<OperationsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OperationsPage],
    }).compileComponents();

    fixture = TestBed.createComponent(OperationsPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
