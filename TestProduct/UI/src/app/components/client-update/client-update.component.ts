import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ClientService, Sex } from '../../services/client.service';

@Component({
  selector: 'app-client-update',
  standalone: true,
  imports: [
    CommonModule, 
    ReactiveFormsModule, 
    MatFormFieldModule, 
    MatInputModule, 
    MatButtonModule, 
    MatSelectModule, 
    MatDatepickerModule, 
    MatNativeDateModule, 
    MatSnackBarModule
  ],
  template: `
    <div class="container">
      <h2>Update Client</h2>
      <div *ngIf="loading" class="loading">Loading...</div>
      <form [formGroup]="form" *ngIf="!loading">
        <mat-form-field appearance="outline" class="w-100">
          <mat-label>First Name</mat-label>
          <input matInput formControlName="firstName" required />
        </mat-form-field>

        <mat-form-field appearance="outline" class="w-100">
          <mat-label>Last Name</mat-label>
          <input matInput formControlName="lastName" required />
        </mat-form-field>

        <mat-form-field appearance="outline" class="w-100">
          <mat-label>Date of Birth</mat-label>
          <input matInput [matDatepicker]="picker" formControlName="dob" required />
          <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
          <mat-datepicker #picker></mat-datepicker>
        </mat-form-field>

        <mat-form-field appearance="outline" class="w-100">
          <mat-label>Sex</mat-label>
          <mat-select formControlName="sex" required>
            <mat-option *ngFor="let s of sexes" [value]="s">{{ s }}</mat-option>
          </mat-select>
        </mat-form-field>

        <div class="actions">
          <button mat-button (click)="cancel()">Cancel</button>
          <button mat-raised-button color="primary" (click)="save()" [disabled]="form.invalid || saving">
            {{ saving ? 'Saving...' : 'Update' }}
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .container { max-width: 600px; margin: 2rem auto; padding: 1rem; border: 1px solid #ccc; border-radius: 8px; }
    .w-100 { width: 100%; }
    .actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem; }
    .loading { text-align: center; margin: 2rem; }
  `]
})
export class ClientUpdateComponent implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private clientService = inject(ClientService);
  private snack = inject(MatSnackBar);

  clientId: number | null = null;
  loading = true;
  saving = false;
  sexes: Sex[] = ['Male', 'Female', 'N/A'];

  form = this.fb.group({
    firstName: ['', Validators.required],
    lastName: ['', Validators.required],
    dob: [null as Date | null, Validators.required],
    sex: ['Male' as Sex, Validators.required]
  });

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.clientId = Number(id);
      this.loadClient(this.clientId);
    } else {
      this.error('Invalid Client ID');
      this.router.navigate(['/dashboard']);
    }
  }

  loadClient(id: number) {
    this.clientService.getClient(id).subscribe({
      next: (client) => {
        this.form.patchValue({
          firstName: client.firstName,
          lastName: client.lastName,
          dob: client.dob ? new Date(client.dob) : null,
          sex: client.sex
        });
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.error('Failed to load client');
        this.router.navigate(['/dashboard']);
      }
    });
  }

  save() {
    if (this.form.invalid || this.saving || !this.clientId) return;
    this.saving = true;
    const value = this.form.value as { firstName: string; lastName: string; dob: Date; sex: Sex };

    this.clientService.updateClient(this.clientId, value).subscribe({
      next: () => {
        this.snack.open('Client updated', 'Dismiss', { duration: 2000 });
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        console.error(err);
        this.error('Failed to update client');
        this.saving = false;
      }
    });
  }

  cancel() {
    this.router.navigate(['/dashboard']);
  }

  private error(msg: string) {
    this.snack.open(msg, 'Dismiss', { duration: 3000 });
  }
}
