// src/lib/api/bankAccount.js
import { API_BASE_URL } from '$lib/constants';
import { refreshToken } from './auth';

const BANK_ACCOUNT_URL = `${API_BASE_URL}/bank-accounts`;

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
 * Get all bank accounts for the current user
 */
export async function getBankAccounts() {
	const response = await apiRequest(`${BANK_ACCOUNT_URL}/`, { method: 'GET' });
	return response.bank_accounts || [];
}

/**
 * Get a specific bank account by ID
 */
export async function getBankAccount(id) {
	const response = await apiRequest(`${BANK_ACCOUNT_URL}/${id}/`, { method: 'GET' });
	return response.bank_account || response;
}

/**
 * Create a new bank account
 */
export async function createBankAccount(bankAccountData) {
	const response = await apiRequest(`${BANK_ACCOUNT_URL}/`, {
		method: 'POST',
		body: JSON.stringify(bankAccountData)
	});
	return response.bank_account || response;
}

/**
 * Update an existing bank account
 */
export async function updateBankAccount(id, bankAccountData) {
	const response = await apiRequest(`${BANK_ACCOUNT_URL}/${id}/`, {
		method: 'PUT',
		body: JSON.stringify(bankAccountData)
	});
	return response.bank_account || response;
}

/**
 * Delete a bank account
 */
export async function deleteBankAccount(id) {
	await apiRequest(`${BANK_ACCOUNT_URL}/${id}/`, { method: 'DELETE' });
	return true;
}

/**
 * Set a bank account as primary
 */
export async function setPrimaryBankAccount(id) {
	const response = await apiRequest(`${BANK_ACCOUNT_URL}/${id}/`, {
		method: 'PUT',
		body: JSON.stringify({ is_primary: true })
	});
	return response.bank_account || response;
}

/**
 * Validate IBAN number format
 */
export function validateIBAN(iban) {
	if (!iban || typeof iban !== 'string') {
		return { valid: false, error: 'IBAN is required' };
	}

	// Remove spaces and convert to uppercase
	const cleanIban = iban.replace(/\s/g, '').toUpperCase();

	// Basic format validation (starts with 2 letters, followed by 2 digits, then alphanumeric)
	const ibanRegex = /^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$/;

	if (!ibanRegex.test(cleanIban)) {
		return {
			valid: false,
			error:
				'Invalid IBAN format. Must start with 2 letters, followed by 2 digits and alphanumeric characters.'
		};
	}

	// Length validation (most IBANs are between 15-34 characters)
	if (cleanIban.length < 15 || cleanIban.length > 34) {
		return {
			valid: false,
			error: 'IBAN length must be between 15 and 34 characters.'
		};
	}

	return { valid: true, cleanIban };
}

/**
 * Format IBAN for display (add spaces every 4 characters)
 */
export function formatIBAN(iban) {
	if (!iban) return '';

	const cleanIban = iban.replace(/\s/g, '').toUpperCase();
	return cleanIban.replace(/(.{4})/g, '$1 ').trim();
}

/**
 * Get bank account types
 */
export function getBankAccountTypes() {
	return [
		{ value: 'checking', label: 'Checking Account' },
		{ value: 'savings', label: 'Savings Account' },
		{ value: 'business', label: 'Business Account' },
		{ value: 'investment', label: 'Investment Account' }
	];
}

/**
 * Validate bank account form data
 */
export function validateBankAccountData(data) {
	const errors = {};

	// Validate bank account name
	if (!data.bank_account_name || data.bank_account_name.trim().length < 2) {
		errors.bank_account_name = 'Account holder name must be at least 2 characters';
	}

	// Validate bank name
	if (!data.bank_name || data.bank_name.trim().length < 2) {
		errors.bank_name = 'Bank name must be at least 2 characters';
	}

	// Validate IBAN
	const ibanValidation = validateIBAN(data.iban_number);
	if (!ibanValidation.valid) {
		errors.iban_number = ibanValidation.error;
	}

	// Validate account number (optional but if provided, must be valid)
	if (data.account_number && data.account_number.trim().length < 5) {
		errors.account_number = 'Account number must be at least 5 characters';
	}

	// Validate SWIFT code (optional but if provided, must be 8 or 11 characters)
	if (data.swift_code && data.swift_code.length !== 8 && data.swift_code.length !== 11) {
		errors.swift_code = 'SWIFT code must be 8 or 11 characters';
	}

	return {
		isValid: Object.keys(errors).length === 0,
		errors
	};
}

/**
 * Get bank account summary statistics
 */
export async function getBankAccountSummary() {
	try {
		const accounts = await getBankAccounts();

		return {
			total: accounts.length,
			primary: accounts.filter((account) => account.is_primary).length,
			verified: accounts.filter((account) => account.is_verified).length,
			unverified: accounts.filter((account) => !account.is_verified).length,
			business: accounts.filter((account) => account.account_type === 'business').length,
			personal: accounts.filter((account) => account.account_type !== 'business').length
		};
	} catch (error) {
		throw error;
	}
}
