import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddApplication } from './add-application';

describe('AddApplication', () => {
  let component: AddApplication;
  let fixture: ComponentFixture<AddApplication>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddApplication],
    }).compileComponents();

    fixture = TestBed.createComponent(AddApplication);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
