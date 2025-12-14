import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { ClientService } from '../../services/client.service';

@Component({
  selector: 'app-client-actions',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  template: `
    <div class="actions-container">
      <button mat-raised-button color="primary" (click)="onUpdate()">Update</button>
      <button mat-raised-button color="warn" (click)="onDelete()">Delete</button>
    </div>
  `,
  styles: [`
    .actions-container { display: flex; gap: 8px; justify-content: center; padding: 4px; }
    button { font-size: 12px; line-height: 24px; min-height: 24px; padding: 0 8px; }
  `]
})
export class ClientActionsComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private clientService = inject(ClientService);

  clientId: number | null = null;

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.clientId = Number(id);
    }
  }

  onUpdate() {
    if (!this.clientId) return;
    // Navigate parent window to update page
    window.top!.location.href = `/client-update/${this.clientId}`;
  }

  onDelete() {
    if (!this.clientId) return;
    if (confirm('Are you sure you want to delete this client?')) {
      this.clientService.deleteClient(this.clientId).subscribe({
        next: () => {
          // Reload parent window to refresh list
          window.top!.location.reload();
        },
        error: (err) => {
          console.error(err);
          alert('Failed to delete client');
        }
      });
    }
  }
}
