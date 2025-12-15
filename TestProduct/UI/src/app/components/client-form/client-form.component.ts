import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl, ValidatorFn } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ClientService, Sex } from '../../services/client.service';

// Custom validator: minimum age
function minAgeValidator(minAge: number): ValidatorFn {
  return (control: AbstractControl) => {
    const val = control.value;
    if (!val) return null;
    const dob = val instanceof Date ? val : new Date(val);
    if (isNaN(dob.getTime())) return { minAge: true };
    const now = new Date();
    const age = now.getFullYear() - dob.getFullYear() - ((now.getMonth() < dob.getMonth() || (now.getMonth() === dob.getMonth() && now.getDate() < dob.getDate())) ? 1 : 0);
    return age >= minAge ? null : { minAge: true };
  };
}

@Component({
  selector: 'app-client-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatSelectModule, MatDatepickerModule, MatNativeDateModule, MatSnackBarModule, MatDialogModule],
  template: `
  <h2 mat-dialog-title>Add Client</h2>
  <div mat-dialog-content>
    <form [formGroup]="form">
      <mat-form-field appearance="outline" class="w-100">
        <mat-label>First Name</mat-label>
        <input matInput formControlName="firstName" required />
        <mat-error *ngIf="form.controls.firstName.hasError('required')">First name is required</mat-error>
        <mat-error *ngIf="form.controls.firstName.hasError('maxlength')">Max length is 25</mat-error>
        <mat-error *ngIf="form.controls.firstName.hasError('pattern')">Only letters are allowed</mat-error>
      </mat-form-field>

      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Last Name</mat-label>
        <input matInput formControlName="lastName" required />
        <mat-error *ngIf="form.controls.lastName.hasError('required')">Last name is required</mat-error>
        <mat-error *ngIf="form.controls.lastName.hasError('maxlength')">Max length is 20</mat-error>
        <mat-error *ngIf="form.controls.lastName.hasError('pattern')">Only letters are allowed</mat-error>
      </mat-form-field>

      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Date of Birth</mat-label>
        <input matInput [matDatepicker]="picker" formControlName="dob" required />
        <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
        <mat-datepicker #picker></mat-datepicker>
        <mat-error *ngIf="form.controls.dob.hasError('required')">Date of birth is required</mat-error>
        <mat-error *ngIf="form.controls.dob.hasError('minAge')">User must be at least 18 years old</mat-error>
      </mat-form-field>

      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Sex</mat-label>
        <mat-select formControlName="sex" required>
          <mat-option *ngFor="let s of sexes" [value]="s">{{ s }}</mat-option>
        </mat-select>
      </mat-form-field>
    </form>
  </div>
  <div mat-dialog-actions align="end">
    <button mat-button (click)="close(false)">Cancel</button>
    <button mat-raised-button color="primary" (click)="save()" [disabled]="form.invalid || loading">
      {{ loading ? 'Saving...' : 'Save' }}
    </button>
  </div>
  `,
  styles: [`.w-100{width:100%}`]
})
export class ClientFormComponent {
  private fb = inject(FormBuilder);
  private clientService = inject(ClientService);
  private dialogRef = inject(MatDialogRef<ClientFormComponent>);
  private snack = inject(MatSnackBar);
  loading = false;

  sexes: Sex[] = ['Male', 'Female'];

  form = this.fb.group({
    firstName: ['', [Validators.required, Validators.maxLength(25), Validators.pattern(/^[A-Za-z]+$/)]],
    lastName: ['', [Validators.required, Validators.maxLength(20), Validators.pattern(/^[A-Za-z]+$/)]],
    dob: [null as Date | null, [Validators.required, minAgeValidator(18)]],
    sex: ['Male' as Sex, Validators.required]
  });

  close(result: boolean) { this.dialogRef.close(result); }

  save() {
    if (this.form.invalid || this.loading) return;
    this.loading = true;
    this.clientService.createClient(this.form.value as any).subscribe({
      next: () => {
        this.snack.open('Client created', 'Dismiss', { duration: 2000 });
        this.dialogRef.close(true);
      },
      error: (err: unknown) => {
        console.error(err);
        this.snack.open('Failed to create client', 'Dismiss', { duration: 3000 });
        this.loading = false;
      }
    });
  }
}
