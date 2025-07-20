import { API_BASE_URL } from '$lib/constants.js';

export async function fetchUser(token) {
	const res = await fetch(`${API_BASE_URL}/user/`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!res.ok) throw new Error('Failed to fetch user');
	return await res.json();
}

export async function getUserById(userId) {
	const res = await fetch(`${API_BASE_URL}/users/${userId}/`);
	if (!res.ok) {
		// Fallback display if user not found or error occurs
		return { username: `User ${userId}` };
	}
	return await res.json();
}
