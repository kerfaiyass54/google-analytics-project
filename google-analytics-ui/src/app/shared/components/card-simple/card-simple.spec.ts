import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CardSimple } from './card-simple';

describe('CardSimple', () => {
  let component: CardSimple;
  let fixture: ComponentFixture<CardSimple>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CardSimple],
    }).compileComponents();

    fixture = TestBed.createComponent(CardSimple);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
