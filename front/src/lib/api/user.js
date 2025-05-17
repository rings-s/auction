import { API_BASE_URL } from '../constants.js';

export async function fetchUser(token) {
  const res = await fetch(`${API_BASE_URL}/user/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) throw new Error('Failed to fetch user');
  return await res.json();
}
