import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeveloperTools } from './developer-tools';

describe('DeveloperTools', () => {
  let component: DeveloperTools;
  let fixture: ComponentFixture<DeveloperTools>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeveloperTools],
    }).compileComponents();

    fixture = TestBed.createComponent(DeveloperTools);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
