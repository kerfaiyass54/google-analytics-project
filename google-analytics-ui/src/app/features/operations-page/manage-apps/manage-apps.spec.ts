import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageApps } from './manage-apps';

describe('ManageApps', () => {
  let component: ManageApps;
  let fixture: ComponentFixture<ManageApps>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageApps],
    }).compileComponents();

    fixture = TestBed.createComponent(ManageApps);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
