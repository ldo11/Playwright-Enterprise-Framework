import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ClientFormComponent } from '../client-form/client-form.component';
import { ClientService, Client } from '../../services/client.service';

@Component({
  selector: 'app-client-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatToolbarModule, MatButtonModule, MatIconModule, MatDialogModule, MatSnackBarModule],
  template: `
  <mat-toolbar color="primary">
    <span>Dashboard</span>
    <span class="spacer"></span>
    <button mat-raised-button color="accent" (click)="openAddDialog()"><mat-icon>add</mat-icon> Add Client</button>
  </mat-toolbar>

  <div class="table-container">
    <table mat-table [dataSource]="clients" class="mat-elevation-z2">

      <ng-container matColumnDef="firstName">
        <th mat-header-cell *matHeaderCellDef> First Name </th>
        <td mat-cell *matCellDef="let c"> {{ c.firstName }} </td>
      </ng-container>

      <ng-container matColumnDef="lastName">
        <th mat-header-cell *matHeaderCellDef> Last Name </th>
        <td mat-cell *matCellDef="let c"> {{ c.lastName }} </td>
      </ng-container>

      <ng-container matColumnDef="dob">
        <th mat-header-cell *matHeaderCellDef> DOB </th>
        <td mat-cell *matCellDef="let c"> {{ c.dob | date:'yyyy-MM-dd' }} </td>
      </ng-container>

      <ng-container matColumnDef="sex">
        <th mat-header-cell *matHeaderCellDef> Sex </th>
        <td mat-cell *matCellDef="let c"> {{ c.sex }} </td>
      </ng-container>

      <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
      <tr mat-row *matRowDef="let row; columns: displayedColumns; trackBy: trackByIndex"></tr>
    </table>
  </div>
  `,
  styles: [`
    .spacer { flex: 1 1 auto; }
    .table-container { padding: 16px; overflow: auto; }
    table { width: 100%; }
  `]
})
export class ClientListComponent implements OnInit {
  private clientService = inject(ClientService);
  private dialog = inject(MatDialog);
  private snack = inject(MatSnackBar);

  displayedColumns = ['firstName', 'lastName', 'dob', 'sex'];
  clients: Client[] = [];

  ngOnInit(): void {
    this.load();
  }

  private getRole(): 'Admin' | 'User' {
    const token = localStorage.getItem('token');
    if (!token) return 'User';
    try {
      const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));
      const role = (payload?.role || payload?.roles?.[0] || 'User') as string;
      return role.toLowerCase() === 'admin' ? 'Admin' : 'User';
    } catch {
      return 'User';
    }
  }

  load(): void {
    const isAdmin = this.getRole() === 'Admin';
    this.clientService.getClients({ mine: !isAdmin }).subscribe({
      next: (data: Client[]) => (this.clients = data ?? []),
      error: (err: unknown) => {
        console.error(err);
        this.snack.open('Failed to load clients', 'Dismiss', { duration: 3000 });
      }
    });
  }

  openAddDialog(): void {
    const ref = this.dialog.open(ClientFormComponent, { width: '480px' });
    ref.afterClosed().subscribe((saved: boolean) => { if (saved) this.load(); });
  }

  trackByIndex = (index: number) => index;
}
