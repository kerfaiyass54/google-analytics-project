import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApplicationCategory } from './application-category';

describe('ApplicationCategory', () => {
  let component: ApplicationCategory;
  let fixture: ComponentFixture<ApplicationCategory>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApplicationCategory],
    }).compileComponents();

    fixture = TestBed.createComponent(ApplicationCategory);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
