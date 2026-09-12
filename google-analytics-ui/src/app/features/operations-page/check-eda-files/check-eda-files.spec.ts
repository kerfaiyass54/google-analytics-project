import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CheckEdaFiles } from './check-eda-files';

describe('CheckEdaFiles', () => {
  let component: CheckEdaFiles;
  let fixture: ComponentFixture<CheckEdaFiles>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CheckEdaFiles],
    }).compileComponents();

    fixture = TestBed.createComponent(CheckEdaFiles);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
