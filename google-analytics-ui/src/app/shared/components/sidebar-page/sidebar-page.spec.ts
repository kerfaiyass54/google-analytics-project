import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SidebarPage } from './sidebar-page';

describe('SidebarPage', () => {
  let component: SidebarPage;
  let fixture: ComponentFixture<SidebarPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarPage],
    }).compileComponents();

    fixture = TestBed.createComponent(SidebarPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
