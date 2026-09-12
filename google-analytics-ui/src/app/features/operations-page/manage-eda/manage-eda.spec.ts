import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageEda } from './manage-eda';

describe('ManageEda', () => {
  let component: ManageEda;
  let fixture: ComponentFixture<ManageEda>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageEda],
    }).compileComponents();

    fixture = TestBed.createComponent(ManageEda);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
