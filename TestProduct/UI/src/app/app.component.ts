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
    <mat-toolbar color="primary">
      <span>Client Management System</span>
      <span class="spacer"></span>
      <ng-container *ngIf="isLoggedIn; else loggedOutActions">
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
  styles: [`.spacer{flex:1 1 auto}`]
})
export class AppComponent {
  constructor(private router: Router) {}

  get isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  get isLoginRoute(): boolean {
    const url = this.router.url || '';
    return url === '/login' || url === '/' || url.startsWith('/login?');
  }

  logout(): void {
    localStorage.removeItem('token');
    this.router.navigateByUrl('/login');
  }
}
