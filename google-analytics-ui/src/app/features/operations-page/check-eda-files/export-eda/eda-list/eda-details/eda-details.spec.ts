import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EdaDetails } from './eda-details';

describe('EdaDetails', () => {
  let component: EdaDetails;
  let fixture: ComponentFixture<EdaDetails>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EdaDetails],
    }).compileComponents();

    fixture = TestBed.createComponent(EdaDetails);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
