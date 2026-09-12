import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteApplications } from './delete-applications';

describe('DeleteApplications', () => {
  let component: DeleteApplications;
  let fixture: ComponentFixture<DeleteApplications>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeleteApplications],
    }).compileComponents();

    fixture = TestBed.createComponent(DeleteApplications);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
