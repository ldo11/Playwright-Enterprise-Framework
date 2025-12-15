import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export type Sex = 'Male' | 'Female';
export interface Client {
  firstName: string;
  lastName: string;
  dob: string; // ISO date string (yyyy-MM-dd)
  sex: Sex;
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

  createClient(client: Omit<Client, 'dob'> & { dob: Date | string }): Observable<Client> {
    const payload = {
      ...client,
      dob: typeof client.dob === 'string' ? client.dob : client.dob.toISOString().substring(0, 10),
    };
    return this.http.post<Client>(`${this.baseUrl}/clients`, payload);
  }
}
