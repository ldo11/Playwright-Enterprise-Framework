import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, MatToolbarModule, MatButtonModule, RouterLink],
  template: `
    <mat-toolbar color="primary">
      <span>Client Management System</span>
      <span class="spacer"></span>
      <a mat-button routerLink="/dashboard">Dashboard</a>
      <a mat-button routerLink="/login">Login</a>
    </mat-toolbar>
    <router-outlet></router-outlet>
  `,
  styles: [`.spacer{flex:1 1 auto}`]
})
export class AppComponent {}
