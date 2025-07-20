// front/src/lib/utils/currency.js
import { get } from 'svelte/store';
import { locale } from '$lib/i18n/config.js';

/**
 * Format currency based on current locale
 * @param {number} amount - The amount to format
 * @param {string} targetLocale - Optional locale override
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, targetLocale = null) {
	// Handle invalid/null amounts
	if (amount === null || amount === undefined || isNaN(amount)) {
		return targetLocale === 'ar' ? '0 ريال' : 'SAR 0';
	}

	// Ensure amount is a number
	const numericAmount = typeof amount === 'string' ? parseFloat(amount) : amount;

	if (isNaN(numericAmount)) {
		return targetLocale === 'ar' ? '0 ريال' : 'SAR 0';
	}

	const currentLocale = targetLocale || get(locale);

	try {
		if (currentLocale === 'ar') {
			// Arabic formatting with Saudi Riyal
			return new Intl.NumberFormat('ar-SA', {
				style: 'currency',
				currency: 'SAR',
				minimumFractionDigits: 0,
				maximumFractionDigits: 0
			}).format(numericAmount);
		} else {
			// English formatting with Saudi Riyal
			return new Intl.NumberFormat('en-SA', {
				style: 'currency',
				currency: 'SAR',
				minimumFractionDigits: 0,
				maximumFractionDigits: 0
			}).format(numericAmount);
		}
	} catch (error) {
		// Fallback formatting
		const formattedNumber = numericAmount.toLocaleString();
		return currentLocale === 'ar' ? `${formattedNumber} ر.س` : `SAR ${formattedNumber}`;
	}
}

/**
 * Parse currency input to number
 * @param {string|number} input - Currency input to parse
 * @returns {number} Parsed number or 0 if invalid
 */
export function parseCurrencyInput(input) {
	if (input === null || input === undefined || input === '') {
		return 0;
	}

	// Convert to string and remove currency symbols and spaces
	const cleanInput = String(input)
		.replace(/[^\d.-]/g, '') // Remove all non-numeric characters except dots and minus
		.trim();

	if (cleanInput === '' || cleanInput === '-') {
		return 0;
	}

	const parsed = parseFloat(cleanInput);
	return isNaN(parsed) ? 0 : parsed;
}

/**
 * Validate bid amount
 * @param {string|number} bidAmount - Bid amount to validate
 * @param {number} minimumBid - Minimum required bid
 * @returns {object} Validation result with isValid and error message
 */
export function validateBidAmount(bidAmount, minimumBid) {
	const parsedAmount = parseCurrencyInput(bidAmount);

	if (parsedAmount <= 0) {
		return {
			isValid: false,
			error: 'bidAmountRequired' // Translation key
		};
	}

	if (parsedAmount < minimumBid) {
		return {
			isValid: false,
			error: 'bidTooLow', // Translation key
			params: { amount: formatCurrency(minimumBid) }
		};
	}

	return {
		isValid: true,
		error: null
	};
}
