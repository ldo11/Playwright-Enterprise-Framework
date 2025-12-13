import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export type Sex = 'Male' | 'Female' | 'N/A';
export interface Client {
  id: number;
  firstName: string;
  lastName: string;
  dob: string; // ISO date string (yyyy-MM-dd)
  sex: Sex;
  createdByUserId?: number;
}

@Injectable({ providedIn: 'root' })
export class ClientService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<{ token?: string; access_token?: string; [k: string]: any }> {
    return this.http.post<{ token?: string; access_token?: string }>(`${this.baseUrl}/login`, { username, password });
  }

  getClients(options?: { mine?: boolean }): Observable<Client[]> {
    let params = new HttpParams();
    if (options?.mine) params = params.set('mine', 'true');
    return this.http.get<Client[]>(`${this.baseUrl}/clients`, { params });
  }

  createClient(client: { firstName: string; lastName: string; dob: Date | string; sex: Sex }): Observable<Client> {
    const payload = {
      ...client,
      dob: typeof client.dob === 'string' ? client.dob : client.dob.toISOString().substring(0, 10),
    };
    return this.http.post<Client>(`${this.baseUrl}/clients`, payload);
  }

  updateClient(id: number, client: { firstName: string; lastName: string; dob: Date | string; sex: Sex }): Observable<Client> {
    const payload = {
      ...client,
      dob: typeof client.dob === 'string' ? client.dob : client.dob.toISOString().substring(0, 10),
    };
    return this.http.put<Client>(`${this.baseUrl}/clients/${id}`, payload);
  }

  getClient(id: number): Observable<Client> {
    return this.http.get<Client>(`${this.baseUrl}/clients/${id}`);
  }
}
