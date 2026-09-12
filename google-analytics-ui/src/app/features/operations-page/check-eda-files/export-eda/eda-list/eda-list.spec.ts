import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EdaList } from './eda-list';

describe('EdaList', () => {
  let component: EdaList;
  let fixture: ComponentFixture<EdaList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EdaList],
    }).compileComponents();

    fixture = TestBed.createComponent(EdaList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
