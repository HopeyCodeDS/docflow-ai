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

export interface RegisterResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    role: string;
    created_at: string;
  };
}

export function register(email: string, password: string): Promise<RegisterResponse> {
  return client.post<RegisterResponse>('/auth/register', { email, password }).then((r) => r.data);
}
