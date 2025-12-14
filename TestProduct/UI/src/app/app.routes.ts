import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { ClientListComponent } from './components/client-list/client-list.component';
import { ClientUpdateComponent } from './components/client-update/client-update.component';
import { ClientActionsComponent } from './components/client-actions/client-actions.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'dashboard', component: ClientListComponent },
  { path: 'client-update/:id', component: ClientUpdateComponent },
  { path: 'client-actions/:id', component: ClientActionsComponent },
  { path: '', pathMatch: 'full', redirectTo: 'login' },
  { path: '**', redirectTo: 'login' }
];
