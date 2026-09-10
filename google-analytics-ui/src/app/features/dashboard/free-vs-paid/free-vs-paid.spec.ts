import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FreeVsPaid } from './free-vs-paid';

describe('FreeVsPaid', () => {
  let component: FreeVsPaid;
  let fixture: ComponentFixture<FreeVsPaid>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FreeVsPaid],
    }).compileComponents();

    fixture = TestBed.createComponent(FreeVsPaid);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
