// src/lib/api/payment.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const PAYMENT_URL = `${API_BASE_URL}/payments`;

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

/**
 * Get all payments for the current user with optional filtering
 */
export async function getPayments(filters = {}) {
	const queryParams = new URLSearchParams();

	Object.entries(filters).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== '') {
			queryParams.append(key, value);
		}
	});

	const url = `${PAYMENT_URL}/?${queryParams.toString()}`;
	const response = await apiRequest(url, { method: 'GET' });
	return response.payments || [];
}

/**
 * Get a specific payment by ID
 */
export async function getPayment(id) {
	const response = await apiRequest(`${PAYMENT_URL}/${id}/`, { method: 'GET' });
	return response.payment || response;
}

/**
 * Create a new payment record
 */
export async function createPayment(paymentData) {
	const response = await apiRequest(`${PAYMENT_URL}/`, {
		method: 'POST',
		body: JSON.stringify(paymentData)
	});
	return response.payment || response;
}

/**
 * Update an existing payment
 */
export async function updatePayment(id, paymentData) {
	const response = await apiRequest(`${PAYMENT_URL}/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(paymentData)
	});
	return response.payment || response;
}

/**
 * Delete a payment record
 */
export async function deletePayment(id) {
	await apiRequest(`${PAYMENT_URL}/${id}/`, { method: 'DELETE' });
	return true;
}

/**
 * Get payment types
 */
export function getPaymentTypes() {
	return [
		{ value: 'rent', label: 'Rent Payment' },
		{ value: 'maintenance', label: 'Maintenance Fee' },
		{ value: 'deposit', label: 'Security Deposit' },
		{ value: 'utilities', label: 'Utilities' },
		{ value: 'insurance', label: 'Insurance' },
		{ value: 'tax', label: 'Property Tax' },
		{ value: 'service', label: 'Service Fee' },
		{ value: 'other', label: 'Other' }
	];
}

/**
 * Get payment status options
 */
export function getPaymentStatuses() {
	return [
		{ value: 'pending', label: 'Pending', color: 'yellow' },
		{ value: 'processing', label: 'Processing', color: 'blue' },
		{ value: 'completed', label: 'Completed', color: 'green' },
		{ value: 'failed', label: 'Failed', color: 'red' },
		{ value: 'cancelled', label: 'Cancelled', color: 'gray' },
		{ value: 'refunded', label: 'Refunded', color: 'purple' }
	];
}

/**
 * Validate payment form data
 */
export function validatePaymentData(data) {
	const errors = {};

	// Validate payment ID
	if (!data.payment_id || data.payment_id.trim().length < 3) {
		errors.payment_id = 'Payment ID must be at least 3 characters';
	}

	// Validate amount
	if (!data.amount || parseFloat(data.amount) <= 0) {
		errors.amount = 'Amount must be greater than 0';
	}

	// Validate payment type
	const validTypes = getPaymentTypes().map((type) => type.value);
	if (!data.payment_type || !validTypes.includes(data.payment_type)) {
		errors.payment_type = 'Please select a valid payment type';
	}

	// Validate due date (if provided)
	if (data.due_date && new Date(data.due_date) < new Date()) {
		errors.due_date = 'Due date cannot be in the past';
	}

	// Validate payment date (if provided)
	if (data.payment_date && new Date(data.payment_date) > new Date()) {
		errors.payment_date = 'Payment date cannot be in the future';
	}

	return {
		isValid: Object.keys(errors).length === 0,
		errors
	};
}

/**
 * Calculate payment statistics
 */
export function calculatePaymentStats(payments) {
	const stats = {
		total: payments.length,
		completed: 0,
		pending: 0,
		overdue: 0,
		totalAmount: 0,
		completedAmount: 0,
		pendingAmount: 0,
		overdueAmount: 0,
		byType: {},
		byMonth: {}
	};

	const today = new Date();

	payments.forEach((payment) => {
		const amount = parseFloat(payment.amount) || 0;
		stats.totalAmount += amount;

		// Count by status
		if (payment.status === 'completed') {
			stats.completed++;
			stats.completedAmount += amount;
		} else if (payment.status === 'pending') {
			stats.pending++;
			stats.pendingAmount += amount;

			// Check if overdue
			if (payment.due_date && new Date(payment.due_date) < today) {
				stats.overdue++;
				stats.overdueAmount += amount;
			}
		}

		// Count by type
		if (!stats.byType[payment.payment_type]) {
			stats.byType[payment.payment_type] = { count: 0, amount: 0 };
		}
		stats.byType[payment.payment_type].count++;
		stats.byType[payment.payment_type].amount += amount;

		// Count by month
		const monthKey = payment.payment_date
			? new Date(payment.payment_date).toISOString().slice(0, 7)
			: new Date().toISOString().slice(0, 7);

		if (!stats.byMonth[monthKey]) {
			stats.byMonth[monthKey] = { count: 0, amount: 0 };
		}
		stats.byMonth[monthKey].count++;
		stats.byMonth[monthKey].amount += amount;
	});

	return stats;
}

/**
 * Generate payment report data
 */
export async function generatePaymentReport(filters = {}) {
	try {
		const payments = await getPayments(filters);
		const stats = calculatePaymentStats(payments);

		return {
			payments,
			statistics: stats,
			summary: {
				totalPayments: stats.total,
				totalAmount: stats.totalAmount,
				completionRate: stats.total > 0 ? ((stats.completed / stats.total) * 100).toFixed(1) : 0,
				overdueRate: stats.total > 0 ? ((stats.overdue / stats.total) * 100).toFixed(1) : 0,
				averageAmount: stats.total > 0 ? (stats.totalAmount / stats.total).toFixed(2) : 0
			},
			generatedAt: new Date().toISOString()
		};
	} catch (error) {
		throw error;
	}
}

/**
 * Get overdue payments
 */
export async function getOverduePayments() {
	const today = new Date().toISOString().split('T')[0];
	return await getPayments({
		status: 'pending',
		due_date__lt: today
	});
}

/**
 * Get upcoming payments (due in next 7 days)
 */
export async function getUpcomingPayments() {
	const today = new Date();
	const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

	return await getPayments({
		status: 'pending',
		due_date__gte: today.toISOString().split('T')[0],
		due_date__lte: nextWeek.toISOString().split('T')[0]
	});
}

/**
 * Format currency amount
 */
export function formatCurrency(amount, currency = 'USD') {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: currency
	}).format(amount);
}

/**
 * Format payment date
 */
export function formatPaymentDate(dateString) {
	if (!dateString) return 'N/A';

	return new Intl.DateTimeFormat('en-US', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	}).format(new Date(dateString));
}

/**
 * Get payment status color
 */
export function getPaymentStatusColor(status) {
	const statusColors = {
		pending: 'yellow',
		processing: 'blue',
		completed: 'green',
		failed: 'red',
		cancelled: 'gray',
		refunded: 'purple'
	};

	return statusColors[status] || 'gray';
}
