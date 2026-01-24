import client from '../api/client';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export function login(email: string, password: string): Promise<LoginResponse> {
  return client.post<LoginResponse>('/auth/login', { email, password }).then((r) => r.data);
}

export function refresh(refreshToken: string): Promise<LoginResponse> {
  return client.post<LoginResponse>('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data);
}
