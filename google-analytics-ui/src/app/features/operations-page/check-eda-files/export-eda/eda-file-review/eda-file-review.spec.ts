import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EdaFileReview } from './eda-file-review';

describe('EdaFileReview', () => {
  let component: EdaFileReview;
  let fixture: ComponentFixture<EdaFileReview>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EdaFileReview],
    }).compileComponents();

    fixture = TestBed.createComponent(EdaFileReview);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
