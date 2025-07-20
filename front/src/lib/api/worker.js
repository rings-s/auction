// src/lib/api/worker.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const WORKER_URL = `${API_BASE_URL}/workers`;
const WORKER_CATEGORY_URL = `${API_BASE_URL}/workers/categories`;

/**
 * Enhanced API request handler with authentication and error handling
 */
async function apiRequest(url, options = {}) {
	const token = localStorage.getItem('accessToken');

	const defaultHeaders = {
		'Content-Type': 'application/json',
		...(token ? { Authorization: `Bearer ${token}` } : {})
	};

	const requestOptions = {
		...options,
		headers: {
			...defaultHeaders,
			...options.headers
		}
	};

	try {
		let response = await fetch(url, requestOptions);

		// Handle token refresh for 401 responses
		if (response.status === 401 && token) {
			try {
				const newToken = await refreshToken();
				requestOptions.headers.Authorization = `Bearer ${newToken}`;
				response = await fetch(url, requestOptions);
			} catch (refreshError) {
				throw new Error('Your session has expired. Please log in again.');
			}
		}

		// Parse response data
		let data;
		const contentType = response.headers.get('content-type');

		if (contentType && contentType.includes('application/json')) {
			data = await response.json();
		} else {
			data = await response.text();
		}

		// Handle error responses
		if (!response.ok) {
			const errorMessage = extractErrorMessage(data, response.status);
			throw new Error(errorMessage);
		}

		return data;
	} catch (error) {
		throw error;
	}
}

/**
 * Extract error message from different response formats
 */
function extractErrorMessage(data, status) {
	if (typeof data === 'string') {
		return data || `HTTP Error ${status}`;
	}

	if (data && typeof data === 'object') {
		if (data.error && data.error.message) {
			return data.error.message;
		}

		if (data.error && typeof data.error === 'string') {
			return data.error;
		}

		if (data.detail) {
			return data.detail;
		}

		if (data.message) {
			return data.message;
		}

		// Handle validation errors
		const validationErrors = [];
		for (const [field, messages] of Object.entries(data)) {
			if (field !== 'error' && field !== 'message' && field !== 'detail') {
				if (Array.isArray(messages)) {
					validationErrors.push(`${field}: ${messages.join(', ')}`);
				} else if (typeof messages === 'string') {
					validationErrors.push(`${field}: ${messages}`);
				}
			}
		}

		if (validationErrors.length > 0) {
			return validationErrors.join('; ');
		}
	}

	return `HTTP Error ${status}`;
}

// ========================
// WORKER CATEGORY METHODS
// ========================

/**
 * Get all worker categories
 */
export async function getWorkerCategories() {
	const response = await apiRequest(`${WORKER_CATEGORY_URL}/`, { method: 'GET' });
	return response.categories || response.results || [];
}

/**
 * Create a new worker category
 */
export async function createWorkerCategory(categoryData) {
	const response = await apiRequest(`${WORKER_CATEGORY_URL}/`, {
		method: 'POST',
		body: JSON.stringify(categoryData)
	});
	return response.category || response;
}

/**
 * Update a worker category
 */
export async function updateWorkerCategory(id, categoryData) {
	const response = await apiRequest(`${WORKER_CATEGORY_URL}/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(categoryData)
	});
	return response.category || response;
}

/**
 * Delete a worker category
 */
export async function deleteWorkerCategory(id) {
	await apiRequest(`${WORKER_CATEGORY_URL}/${id}/`, { method: 'DELETE' });
	return true;
}

// ==================
// WORKER METHODS
// ==================

/**
 * Get all workers with optional filtering
 */
export async function getWorkers(filters = {}) {
	const queryParams = new URLSearchParams();

	Object.entries(filters).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== '') {
			if (Array.isArray(value)) {
				value.forEach(item => queryParams.append(key, item));
			} else {
				queryParams.append(key, value);
			}
		}
	});

	const url = `${WORKER_URL}/?${queryParams.toString()}`;
	const response = await apiRequest(url, { method: 'GET' });
	return response.workers || response.results || [];
}

/**
 * Get a specific worker by ID
 */
export async function getWorker(id) {
	const response = await apiRequest(`${WORKER_URL}/${id}/`, { method: 'GET' });
	return response.worker || response;
}

/**
 * Create a new worker
 */
export async function createWorker(workerData) {
	const response = await apiRequest(`${WORKER_URL}/`, {
		method: 'POST',
		body: JSON.stringify(workerData)
	});
	return response.worker || response;
}

/**
 * Update an existing worker
 */
export async function updateWorker(id, workerData) {
	const response = await apiRequest(`${WORKER_URL}/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(workerData)
	});
	return response.worker || response;
}

/**
 * Delete a worker
 */
export async function deleteWorker(id) {
	await apiRequest(`${WORKER_URL}/${id}/`, { method: 'DELETE' });
	return true;
}

/**
 * Get available workers (not at max capacity)
 */
export async function getAvailableWorkers(categoryId = null) {
	const filters = { is_available: true, status: 'active' };
	if (categoryId) {
		filters.categories = [categoryId];
	}
	return await getWorkers(filters);
}

/**
 * Assign worker to a job/task
 */
export async function assignWorker(workerId, jobData) {
	const response = await apiRequest(`${WORKER_URL}/${workerId}/assign/`, {
		method: 'POST',
		body: JSON.stringify(jobData)
	});
	return response;
}

/**
 * Complete a job for a worker
 */
export async function completeWorkerJob(workerId, jobId, completionData) {
	const response = await apiRequest(`${WORKER_URL}/${workerId}/jobs/${jobId}/complete/`, {
		method: 'POST',
		body: JSON.stringify(completionData)
	});
	return response;
}

// =======================
// UTILITY FUNCTIONS
// =======================

/**
 * Get employment types
 */
export function getEmploymentTypes() {
	return [
		{ value: 'full_time', label: 'Full Time' },
		{ value: 'part_time', label: 'Part Time' },
		{ value: 'contract', label: 'Contract' },
		{ value: 'freelance', label: 'Freelance' },
		{ value: 'temporary', label: 'Temporary' }
	];
}

/**
 * Get worker statuses
 */
export function getWorkerStatuses() {
	return [
		{ value: 'active', label: 'Active', color: 'green' },
		{ value: 'inactive', label: 'Inactive', color: 'gray' },
		{ value: 'suspended', label: 'Suspended', color: 'red' },
		{ value: 'on_leave', label: 'On Leave', color: 'yellow' }
	];
}

/**
 * Get skill levels
 */
export function getSkillLevels() {
	return [
		{ value: 'beginner', label: 'Beginner', rating: 1 },
		{ value: 'intermediate', label: 'Intermediate', rating: 2 },
		{ value: 'advanced', label: 'Advanced', rating: 3 },
		{ value: 'expert', label: 'Expert', rating: 4 }
	];
}

/**
 * Validate worker form data
 */
export function validateWorkerData(data) {
	const errors = {};

	// Validate basic information
	if (!data.first_name || data.first_name.trim().length < 2) {
		errors.first_name = 'First name must be at least 2 characters';
	}

	if (!data.last_name || data.last_name.trim().length < 2) {
		errors.last_name = 'Last name must be at least 2 characters';
	}

	if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
		errors.email = 'Please enter a valid email address';
	}

	if (!data.phone || data.phone.trim().length < 10) {
		errors.phone = 'Phone number must be at least 10 digits';
	}

	// Validate employment information
	const validEmploymentTypes = getEmploymentTypes().map(type => type.value);
	if (!data.employment_type || !validEmploymentTypes.includes(data.employment_type)) {
		errors.employment_type = 'Please select a valid employment type';
	}

	if (!data.hourly_rate || parseFloat(data.hourly_rate) <= 0) {
		errors.hourly_rate = 'Hourly rate must be greater than 0';
	}

	if (!data.categories || data.categories.length === 0) {
		errors.categories = 'Please select at least one skill category';
	}

	// Validate dates
	if (data.hire_date && new Date(data.hire_date) > new Date()) {
		errors.hire_date = 'Hire date cannot be in the future';
	}

	if (data.date_of_birth) {
		const age = (new Date() - new Date(data.date_of_birth)) / (365.25 * 24 * 60 * 60 * 1000);
		if (age < 16) {
			errors.date_of_birth = 'Worker must be at least 16 years old';
		}
		if (age > 100) {
			errors.date_of_birth = 'Please enter a valid date of birth';
		}
	}

	// Validate numeric fields
	if (data.max_concurrent_jobs && (parseFloat(data.max_concurrent_jobs) < 1 || parseFloat(data.max_concurrent_jobs) > 10)) {
		errors.max_concurrent_jobs = 'Max concurrent jobs must be between 1 and 10';
	}

	return {
		isValid: Object.keys(errors).length === 0,
		errors
	};
}

/**
 * Calculate worker performance metrics
 */
export function calculateWorkerPerformance(worker) {
	const metrics = {
		completionRate: 0,
		averageRating: worker.rating || 0,
		totalJobs: worker.total_jobs || 0,
		completedJobs: worker.completed_jobs || 0,
		activeJobs: worker.active_jobs_count || 0,
		efficiency: 0,
		status: worker.status || 'inactive'
	};

	// Calculate completion rate
	if (metrics.totalJobs > 0) {
		metrics.completionRate = (metrics.completedJobs / metrics.totalJobs * 100).toFixed(1);
	}

	// Calculate efficiency based on jobs completed vs capacity
	if (worker.max_concurrent_jobs && worker.max_concurrent_jobs > 0) {
		metrics.efficiency = Math.min(100, (metrics.activeJobs / worker.max_concurrent_jobs * 100)).toFixed(1);
	}

	return metrics;
}

/**
 * Get worker analytics summary
 */
export async function getWorkerAnalytics() {
	try {
		const workers = await getWorkers();
		const categories = await getWorkerCategories();
		
		const analytics = {
			total: workers.length,
			active: workers.filter(w => w.status === 'active').length,
			available: workers.filter(w => w.is_available && w.status === 'active').length,
			totalCapacity: workers.reduce((sum, w) => sum + (w.max_concurrent_jobs || 0), 0),
			utilizationRate: 0,
			averageRating: 0,
			byCategory: {},
			byEmploymentType: {},
			performance: []
		};

		// Calculate utilization rate
		const totalActiveJobs = workers.reduce((sum, w) => sum + (w.active_jobs_count || 0), 0);
		if (analytics.totalCapacity > 0) {
			analytics.utilizationRate = (totalActiveJobs / analytics.totalCapacity * 100).toFixed(1);
		}

		// Calculate average rating
		const workersWithRating = workers.filter(w => w.rating && w.rating > 0);
		if (workersWithRating.length > 0) {
			analytics.averageRating = (workersWithRating.reduce((sum, w) => sum + w.rating, 0) / workersWithRating.length).toFixed(1);
		}

		// Group by category
		categories.forEach(category => {
			const categoryWorkers = workers.filter(w => 
				w.categories && w.categories.some(c => c.id === category.id)
			);
			analytics.byCategory[category.name] = {
				count: categoryWorkers.length,
				active: categoryWorkers.filter(w => w.status === 'active').length,
				averageRate: categoryWorkers.length > 0 ? 
					(categoryWorkers.reduce((sum, w) => sum + (w.hourly_rate || 0), 0) / categoryWorkers.length).toFixed(2) : 0
			};
		});

		// Group by employment type
		getEmploymentTypes().forEach(type => {
			const typeWorkers = workers.filter(w => w.employment_type === type.value);
			analytics.byEmploymentType[type.label] = {
				count: typeWorkers.length,
				active: typeWorkers.filter(w => w.status === 'active').length
			};
		});

		// Calculate individual performance
		analytics.performance = workers.map(worker => ({
			id: worker.id,
			name: `${worker.first_name} ${worker.last_name}`,
			...calculateWorkerPerformance(worker)
		}));

		return analytics;
	} catch (error) {
		throw error;
	}
}

/**
 * Format worker display name
 */
export function formatWorkerName(worker) {
	return `${worker.first_name} ${worker.last_name}`.trim();
}

/**
 * Get worker status color
 */
export function getWorkerStatusColor(status) {
	const statusColors = {
		active: 'green',
		inactive: 'gray',
		suspended: 'red',
		on_leave: 'yellow'
	};
	
	return statusColors[status] || 'gray';
}

/**
 * Format hourly rate
 */
export function formatHourlyRate(rate, currency = 'USD') {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: currency
	}).format(rate);
}