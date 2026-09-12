import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EdaFileType } from './eda-file-type';

describe('EdaFileType', () => {
  let component: EdaFileType;
  let fixture: ComponentFixture<EdaFileType>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EdaFileType],
    }).compileComponents();

    fixture = TestBed.createComponent(EdaFileType);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
