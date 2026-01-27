import axios, { AxiosError } from 'axios';

const client = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

async function tryRefresh(refreshToken: string): Promise<{ access_token: string; refresh_token: string } | null> {
  const res = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!res.ok) return null;
  return res.json();
}

client.interceptors.response.use(
  (res) => res,
  async (err: AxiosError<{ detail?: string; message?: string; error?: { message?: string } }>) => {
    const orig = err.config;
    const isAuth = orig?.url?.includes('/auth/');
    const is401 = err.response?.status === 401;

    if (is401 && !isAuth && orig) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        const data = await tryRefresh(refreshToken);
        if (data) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          if (orig.headers) orig.headers.Authorization = `Bearer ${data.access_token}`;
          return client(orig);
        }
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.dispatchEvent(new Event('auth:sessionExpired'));
    }

    const msg =
      err.response?.data?.detail ??
      err.response?.data?.message ??
      err.response?.data?.error?.message ??
      (typeof err.response?.data === 'string' ? err.response.data : null) ??
      err.message ??
      'Request failed';
    return Promise.reject(new Error(msg));
  }
);

export default client;
