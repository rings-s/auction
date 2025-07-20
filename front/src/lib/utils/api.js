// src/lib/utils/api.js

import { refreshToken } from '$lib/api/auth';
import { goto } from '$app/navigation';

/**
 * Performs an authenticated fetch request.
 * @param {string} url The URL to fetch.
 * @param {RequestInit} [options={}] Fetch options.
 * @returns {Promise<{data: any|null, error: {status?: number, message: string}|null}>} The response data or an error object.
 */
async function authenticatedFetch(url, options = {}) {
	const token = localStorage.getItem('accessToken');
	if (!token) {
		goto('/login'); // Consider if this should also return an error object
		return { data: null, error: { message: 'No access token found.' } };
	}

	/** @type {Record<string, string>} */
	const finalHeaders = {
		Authorization: `Bearer ${token}`
	};

	if (options.headers) {
		// Normalize options.headers to a Headers object and iterate
		new Headers(options.headers).forEach((value, key) => {
			finalHeaders[key] = value;
		});
	}

	// Default Content-Type to application/json if not FormData and not already set by user
	if (
		!(options.body instanceof FormData) &&
		!finalHeaders['Content-Type'] &&
		!finalHeaders['content-type']
	) {
		finalHeaders['Content-Type'] = 'application/json';
	}

	try {
		let response = await fetch(url, { ...options, headers: finalHeaders });

		if (response.status === 401) {
			// Try token refresh
			try {
				const newToken = await refreshToken();
				finalHeaders.Authorization = `Bearer ${newToken}`;
				response = await fetch(url, { ...options, headers: finalHeaders });

				if (!response.ok) {
					// Token refresh succeeded but subsequent request failed
					// goto('/login'); // Decide if redirect is appropriate here or let caller handle
					return {
						data: null,
						error: {
							status: response.status,
							message: `API request failed after token refresh: ${response.statusText}`
						}
					};
				}
			} catch (refreshError) {
				goto('/login'); // Token refresh itself failed, likely need to re-authenticate
				return { data: null, error: { message: 'Token refresh failed. Please log in again.' } };
			}
		}

		if (!response.ok) {
			// throw new Error(`HTTP error! status: ${response.status}`); // Replaced
			return {
				data: null,
				error: { status: response.status, message: `HTTP error: ${response.statusText}` }
			};
		}

		// Handle cases where response might be empty but OK (e.g., 204 No Content)
		if (response.status === 204) {
			return { data: null, error: null }; // Or { data: {}, error: null } if preferred for empty success
		}

		const data = await response.json();
		return { data, error: null };
	} catch (error) {
		// This catches network errors or issues with response.json() if response is not valid JSON
		const errorMessage =
			error instanceof Error ? error.message : 'An unknown network error occurred.';
		return { data: null, error: { message: `API call failed: ${errorMessage}` } };
	}
}

/** @type {Record<string, (url: string, ...args: any[]) => Promise<{data: any|null, error: any|null}>>} */
export const api = {
	/**
	 * @param {string} url
	 * @param {RequestInit} [options={}]
	 * @returns {Promise<{data: any|null, error: any|null}>}
	 */
	get: (url, options = {}) => authenticatedFetch(url, { ...options, method: 'GET' }),

	/**
	 * @param {string} url
	 * @param {any} body
	 * @param {RequestInit} [options={}]
	 * @returns {Promise<{data: any|null, error: any|null}>}
	 */
	post: (url, body, options = {}) => {
		const isFormData = body instanceof FormData;
		// Let authenticatedFetch handle Content-Type based on isFormData or user-provided headers
		return authenticatedFetch(url, {
			...options,
			method: 'POST',
			// headers will be merged in authenticatedFetch
			body: isFormData ? body : JSON.stringify(body)
		});
	},

	/**
	 * @param {string} url
	 * @param {any} body
	 * @param {RequestInit} [options={}]
	 * @returns {Promise<{data: any|null, error: any|null}>}
	 */
	put: (url, body, options = {}) => {
		const isFormData = body instanceof FormData;
		return authenticatedFetch(url, {
			...options,
			method: 'PUT',
			body: isFormData ? body : JSON.stringify(body)
		});
	},

	/**
	 * @param {string} url
	 * @param {RequestInit} [options={}]
	 * @returns {Promise<{data: any|null, error: any|null}>}
	 */
	delete: (url, options = {}) => authenticatedFetch(url, { ...options, method: 'DELETE' }),

	/**
	 * @param {string} url
	 * @param {any} body
	 * @param {RequestInit} [options={}]
	 * @returns {Promise<{data: any|null, error: any|null}>}
	 */
	patch: (url, body, options = {}) => {
		const isFormData = body instanceof FormData;
		return authenticatedFetch(url, {
			...options,
			method: 'PATCH',
			body: isFormData ? body : JSON.stringify(body)
		});
	}
	// You can add other methods like patch, head etc. as needed
};
