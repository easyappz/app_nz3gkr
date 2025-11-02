import instance from './axios';

export async function register({ username, password, email }) {
  const payload = { username, password };
  if (email) {
    payload.email = email;
  }
  const res = await instance.post('/api/auth/register', payload);
  return res.data; // {id, username, token}
}

export async function login({ username, password }) {
  const res = await instance.post('/api/auth/login', { username, password });
  return res.data; // {id, username, token}
}

export async function me() {
  const res = await instance.get('/api/auth/me');
  return res.data; // Me schema
}

export const AuthKeys = {
  me: ['me'],
};
