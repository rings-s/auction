// src/lib/api/media.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const MEDIA_URL = `${API_BASE_URL}/media`;

/**
 * Upload media file to server
 */
export async function uploadMedia(file, contentType, objectId, options = {}) {
	const token = localStorage.getItem('accessToken');

	if (!token) {
		throw new Error('Authentication required');
	}

	const formData = new FormData();
	formData.append('file', file);
	formData.append('content_type_str', contentType);
	formData.append('object_id', objectId);
	formData.append('media_type', options.mediaType || 'image');
	formData.append('is_primary', options.isPrimary || false);

	if (options.name) {
		formData.append('name', options.name);
	}

	try {
		let response = await fetch(`${MEDIA_URL}/`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${token}`
			},
			body: formData
		});

		// Handle token refresh for 401 responses
		if (response.status === 401) {
			try {
				const newToken = await refreshToken();
				response = await fetch(`${MEDIA_URL}/`, {
					method: 'POST',
					headers: {
						Authorization: `Bearer ${newToken}`
					},
					body: formData
				});
			} catch (refreshError) {
				throw new Error('Your session has expired. Please log in again.');
			}
		}

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.message || `Upload failed: ${response.statusText}`);
		}

		return await response.json();
	} catch (error) {
		throw error;
	}
}

/**
 * Upload multiple media files
 */
export async function uploadMultipleMedia(files, contentType, objectId, options = {}) {
	const uploadPromises = Array.from(files).map((file, index) =>
		uploadMedia(file, contentType, objectId, {
			...options,
			name: file.name,
			isPrimary: index === 0 && options.makeFirstPrimary, // Make first image primary if requested
			mediaType: file.type.startsWith('image/') ? 'image' : 'document'
		})
	);

	return await Promise.all(uploadPromises);
}

/**
 * Delete media file
 */
export async function deleteMedia(mediaId) {
	const token = localStorage.getItem('accessToken');

	if (!token) {
		throw new Error('Authentication required');
	}

	try {
		let response = await fetch(`${MEDIA_URL}/${mediaId}/`, {
			method: 'DELETE',
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		if (response.status === 401) {
			try {
				const newToken = await refreshToken();
				response = await fetch(`${MEDIA_URL}/${mediaId}/`, {
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${newToken}`
					}
				});
			} catch (refreshError) {
				throw new Error('Your session has expired. Please log in again.');
			}
		}

		if (!response.ok) {
			throw new Error(`Delete failed: ${response.statusText}`);
		}

		return true;
	} catch (error) {
		throw error;
	}
}

/**
 * Update media (e.g., set as primary)
 */
export async function updateMedia(mediaId, updates) {
	const token = localStorage.getItem('accessToken');

	if (!token) {
		throw new Error('Authentication required');
	}

	try {
		let response = await fetch(`${MEDIA_URL}/${mediaId}/`, {
			method: 'PATCH',
			headers: {
				Authorization: `Bearer ${token}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(updates)
		});

		if (response.status === 401) {
			try {
				const newToken = await refreshToken();
				response = await fetch(`${MEDIA_URL}/${mediaId}/`, {
					method: 'PATCH',
					headers: {
						Authorization: `Bearer ${newToken}`,
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(updates)
				});
			} catch (refreshError) {
				throw new Error('Your session has expired. Please log in again.');
			}
		}

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.message || `Update failed: ${response.statusText}`);
		}

		return await response.json();
	} catch (error) {
		throw error;
	}
}
