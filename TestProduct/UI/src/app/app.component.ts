import { Component } from '@angular/core';
import { Router, RouterOutlet, RouterLink } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { NgIf } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatToolbarModule, MatButtonModule, RouterLink, NgIf],
  template: `
    <mat-toolbar color="primary" *ngIf="!isIframeRoute">
      <span>Client Management System</span>
      <span class="spacer"></span>
      <ng-container *ngIf="isLoggedIn; else loggedOutActions">
        <span class="username">Hi {{ username }}</span>
        <button mat-button (click)="logout()">Logout</button>
      </ng-container>
      <ng-template #loggedOutActions>
        <ng-container *ngIf="!isLoginRoute">
          <a mat-button routerLink="/dashboard">Dashboard</a>
          <a mat-button routerLink="/login">Login</a>
        </ng-container>
      </ng-template>
    </mat-toolbar>
    <router-outlet></router-outlet>
  `,
  styles: [`
    .spacer{flex:1 1 auto}
    .username { margin-right: 16px; font-weight: 500; }
  `]
})
export class AppComponent {
  constructor(private router: Router) {}

  get isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  get username(): string {
    const token = localStorage.getItem('token');
    if (!token) return '';
    try {
      const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));
      return payload.username || '';
    } catch {
      return '';
    }
  }

  get isLoginRoute(): boolean {
    const url = this.router.url || '';
    return url === '/login' || url === '/' || url.startsWith('/login?');
  }

  get isIframeRoute(): boolean {
    const url = this.router.url || '';
    return url.includes('/client-actions/');
  }

  logout(): void {
    localStorage.removeItem('token');
    this.router.navigateByUrl('/login');
  }
}
