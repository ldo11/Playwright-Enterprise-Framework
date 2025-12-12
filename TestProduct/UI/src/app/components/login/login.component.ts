import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatCardModule, MatSnackBarModule],
  template: `
  <mat-card class="login-card">
    <h2>Login</h2>
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Username</mat-label>
        <input matInput formControlName="username" required />
      </mat-form-field>

      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Password</mat-label>
        <input matInput type="password" formControlName="password" required />
      </mat-form-field>

      <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || loading">
        {{ loading ? 'Signing in...' : 'Login' }}
      </button>
    </form>
  </mat-card>
  `,
  styles: [`.login-card{max-width:400px;margin:48px auto;padding:16px}.w-100{width:100%}`]
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private clientService = inject(ClientService);
  private router = inject(Router);
  private snack = inject(MatSnackBar);
  loading = false;

  form = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  onSubmit() {
    if (this.form.invalid || this.loading) return;
    this.loading = true;
    const { username, password } = this.form.value;
    this.clientService.login(username!, password!).subscribe({
      next: (res: { token?: string; access_token?: string }) => {
        const token = (res as any)?.token || (res as any)?.access_token;
        if (token) {
          localStorage.setItem('token', token);
          this.router.navigateByUrl('/dashboard');
        } else {
          this.snack.open('Login succeeded but no token returned', 'Dismiss', { duration: 3000 });
        }
      },
      error: (err: unknown) => {
        console.error(err);
        this.snack.open('Invalid credentials', 'Dismiss', { duration: 3000 });
      },
      complete: () => (this.loading = false),
    });
  }
}
