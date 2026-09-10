import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EdaPage } from './eda-page';

describe('EdaPage', () => {
  let component: EdaPage;
  let fixture: ComponentFixture<EdaPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EdaPage],
    }).compileComponents();

    fixture = TestBed.createComponent(EdaPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
