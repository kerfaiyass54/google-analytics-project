import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';
import { DatePipe } from '@angular/common';
import { NotificationService } from '../../../core/services/notification.service';
import { Router } from '@angular/router';

@Component({selector:'app-nav-bar',standalone:true,imports:[RouterLink,RouterLinkActive,DatePipe],templateUrl:'./nav-bar.html',styleUrl:'./nav-bar.css',changeDetection:ChangeDetectionStrategy.OnPush})
export class NavBar {
  readonly authService=inject(AuthService);
  readonly notificationService=inject(NotificationService);
  private readonly router=inject(Router);
  notificationsOpen=false;
  toggleNotifications():void { this.notificationsOpen=!this.notificationsOpen; if(this.notificationsOpen) this.notificationService.refresh(); }
  openNotification(id:string):void { this.notificationService.markAsRead(id); this.notificationsOpen=false; this.router.navigate(['/notifications']); }
  openAllNotifications():void { this.notificationsOpen=false; this.router.navigate(['/notifications']); }
  markAllNotificationsRead():void { this.notificationService.markAllAsRead(); }
  get navigationItems(){
    const items=[
      {label:'Home',icon:'bi-grid-1x2-fill',route:'/dashboard'},
      {label:'Applications',icon:'bi-phone-fill',route:'/list'},
      {label:'Operations',icon:'bi-sliders2-vertical',route:'/operations'},
      {label:'EDA',icon:'bi-bar-chart-fill',route:'/eda'},
    ];
    if(this.authService.isAdmin()){
      items.push(
        {label:'Model settings',icon:'bi-cpu-fill',route:'/admin/predictions'},
        {label:'Evaluations',icon:'bi-clipboard-data-fill',route:'/admin/evaluations'},
      );
    } else {
      items.push({label:'Predictions',icon:'bi-stars',route:'/predictions'});
    }
    return items;
  }
  async logout():Promise<void>{await this.authService.logout();}
}
