// src/lib/store/lang.js
/**
 * مدير الترجمة وإعدادات اللغة المحسن
 * Enhanced internationalization and language management
 */
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { dictionary, languageNames } from './dictionary';

/**
 * تحديد اللغة الأولية من المتصفح أو التخزين المحلي
 * Determine initial language from browser or localStorage
 * @returns {string} رمز اللغة - language code
 */
const getInitialLanguage = () => {
	if (!browser) return 'ar'; // Default to Arabic on server

	try {
		// Check localStorage first
		const storedLang = localStorage.getItem('language');
		if (storedLang && ['ar', 'en'].includes(storedLang)) return storedLang;

		// Check browser language
		const browserLang = navigator.language?.split('-')[0];
		return browserLang === 'en' ? 'en' : 'ar'; // Default to Arabic if not English
	} catch (error) {
		console.warn('Error accessing browser language settings:', error);
		return 'ar'; // Fallback to Arabic
	}
};

/**
 * مخزن اللغة الحالية
 * Current language store
 */
export const language = writable(getInitialLanguage());

/**
 * تعيين اللغة في واجهة المستخدم عند تغييرها
 * Update UI language settings when language changes
 */
if (browser) {
	language.subscribe((lang) => {
		try {
			// Store in localStorage
			localStorage.setItem('language', lang);

			// Update HTML attributes
			document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
			document.documentElement.lang = lang;

			// Update meta tags
			const htmlLangMeta = document.querySelector('meta[property="og:locale"]');
			if (htmlLangMeta) {
				htmlLangMeta.setAttribute('content', lang === 'ar' ? 'ar_SA' : 'en_US');
			}
		} catch (error) {
			console.error('Error updating language settings:', error);
		}
	});
}

/**
 * دالة الترجمة المشتقة
 * Derived translation function
 */
export const t = derived(language, ($language) => (key, replacements = {}) => {
	if (!key) return '';

	try {
		// Split key path by dots
		const keys = key.split('.');
		let value = dictionary[$language];

		// Navigate through the dictionary
		for (const k of keys) {
			if (value && value[k] !== undefined) {
				value = value[k];
			} else {
				console.warn(`Translation key not found: ${key}`);
				return key; // Return the key as fallback
			}
		}

		// Handle string replacements
		if (typeof value === 'string' && Object.keys(replacements).length > 0) {
			return Object.entries(replacements).reduce(
				(str, [placeholder, replacement]) =>
					str.replace(new RegExp(`{${placeholder}}`, 'g'), replacement),
				value
			);
		}

		return value;
	} catch (error) {
		console.error(`Translation error for key: ${key}`, error);
		return key;
	}
});

/**
 * تغيير اللغة الحالية
 * Change the current language
 * @param {string} lang - رمز اللغة (ar أو en)
 * @returns {boolean} نجاح التغيير - success flag
 */
export const changeLanguage = (lang) => {
	if (lang === 'ar' || lang === 'en') {
		language.set(lang);
		return true;
	} else {
		console.warn(`Unsupported language: ${lang}. Supported languages are 'ar' and 'en'.`);
		return false;
	}
};

/**
 * التحقق إذا كانت اللغة الحالية من اليمين إلى اليسار
 * Check if the current language is RTL
 * @returns {boolean} هل اللغة من اليمين إلى اليسار
 */
export const isRTL = () => get(language) === 'ar';

/**
 * الحصول على اتجاه النص
 * Get the text direction
 * @returns {string} rtl أو ltr
 */
export const getDirection = () => (isRTL() ? 'rtl' : 'ltr');

/**
 * الحصول على كلاس الاتجاه
 * Get direction class
 * @returns {string} dir-rtl أو dir-ltr
 */
export const getDirectionClass = () => `dir-${getDirection()}`;

/**
 * تنسيق التاريخ حسب اللغة الحالية
 * Format a date according to the current language
 * @param {Date|string|number} date - التاريخ
 * @param {Object} options - خيارات التنسيق
 * @returns {string} التاريخ المنسق
 */
export function formatDate(date, options = {}) {
	if (!date) return '';

	try {
		const dateObj = date instanceof Date ? date : new Date(date);
		const currentLang = get(language);

		// Check if date is valid
		if (isNaN(dateObj.getTime())) {
			console.warn('Invalid date provided to formatDate:', date);
			return String(date);
		}

		// Default options
		const defaultOptions = {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			...options
		};

		return new Intl.DateTimeFormat(currentLang === 'ar' ? 'ar-SA' : 'en-US', defaultOptions).format(
			dateObj
		);
	} catch (error) {
		console.error('Error formatting date:', error);
		return String(date);
	}
}

/**
 * تنسيق الرقم حسب اللغة الحالية
 * Format a number according to the current language
 * @param {number} number - الرقم
 * @param {Object} options - خيارات التنسيق
 * @returns {string} الرقم المنسق
 */
export function formatNumber(number, options = {}) {
	if (number === undefined || number === null) return '';

	try {
		const num = Number(number);
		if (isNaN(num)) {
			console.warn('Invalid number provided to formatNumber:', number);
			return String(number);
		}

		const currentLang = get(language);

		return new Intl.NumberFormat(currentLang === 'ar' ? 'ar-SA' : 'en-US', options).format(num);
	} catch (error) {
		console.error('Error formatting number:', error);
		return String(number);
	}
}

/**
 * تنسيق المبلغ المالي حسب اللغة الحالية
 * Format a currency amount according to the current language
 * @param {number} amount - المبلغ
 * @param {string} currency - رمز العملة (SAR افتراضيًا)
 * @param {Object} options - خيارات إضافية
 * @returns {string} المبلغ المنسق
 */
export function formatCurrency(amount, currency = 'SAR', options = {}) {
	if (amount === undefined || amount === null) return '';

	try {
		const num = Number(amount);
		if (isNaN(num)) {
			console.warn('Invalid amount provided to formatCurrency:', amount);
			return String(amount);
		}

		return formatNumber(amount, {
			style: 'currency',
			currency,
			minimumFractionDigits: 0,
			maximumFractionDigits: 2,
			...options
		});
	} catch (error) {
		console.error('Error formatting currency:', error);
		return String(amount);
	}
}

/**
 * تنسيق النسبة المئوية
 * Format a percentage
 * @param {number} value - القيمة
 * @param {Object} options - خيارات التنسيق
 * @returns {string} النسبة المئوية المنسقة
 */
export function formatPercent(value, options = {}) {
	if (value === undefined || value === null) return '';

	try {
		const num = Number(value);
		if (isNaN(num)) {
			console.warn('Invalid value provided to formatPercent:', value);
			return String(value);
		}

		return formatNumber(value, {
			style: 'percent',
			minimumFractionDigits: 0,
			maximumFractionDigits: 2,
			...options
		});
	} catch (error) {
		console.error('Error formatting percentage:', error);
		return String(value);
	}
}

/**
 * تنسيق وقت نسبي (منذ..)
 * Format relative time (X ago, in X)
 * @param {Date|string|number} date - التاريخ
 * @param {Object} options - خيارات التنسيق
 * @returns {string} النص المنسق
 */
export function formatRelativeTime(date, options = {}) {
	if (!date) return '';

	try {
		const dateObj = date instanceof Date ? date : new Date(date);
		const currentLang = get(language);

		// Check if date is valid
		if (isNaN(dateObj.getTime())) {
			console.warn('Invalid date provided to formatRelativeTime:', date);
			return String(date);
		}

		const now = new Date();
		const diffMs = dateObj.getTime() - now.getTime();
		const diffSec = Math.round(diffMs / 1000);
		const diffMin = Math.round(diffSec / 60);
		const diffHour = Math.round(diffMin / 60);
		const diffDay = Math.round(diffHour / 24);
		const diffMonth = Math.round(diffDay / 30);
		const diffYear = Math.round(diffDay / 365);

		const rtf = new Intl.RelativeTimeFormat(currentLang === 'ar' ? 'ar-SA' : 'en-US', {
			numeric: 'auto',
			...options
		});

		if (Math.abs(diffSec) < 60) {
			return rtf.format(diffSec, 'second');
		} else if (Math.abs(diffMin) < 60) {
			return rtf.format(diffMin, 'minute');
		} else if (Math.abs(diffHour) < 24) {
			return rtf.format(diffHour, 'hour');
		} else if (Math.abs(diffDay) < 30) {
			return rtf.format(diffDay, 'day');
		} else if (Math.abs(diffMonth) < 12) {
			return rtf.format(diffMonth, 'month');
		} else {
			return rtf.format(diffYear, 'year');
		}
	} catch (error) {
		console.error('Error formatting relative time:', error);
		return String(date);
	}
}

/**
 * تحويل النص من camelCase إلى Title Case
 * Convert text from camelCase to Title Case
 * @param {string} text - النص
 * @returns {string} النص المحول
 */
export function formatTitleCase(text) {
	if (!text) return '';

	try {
		return text
			.replace(/([A-Z])/g, ' $1') // Insert space before capital letters
			.replace(/_/g, ' ') // Replace underscores with spaces
			.replace(/^\w/, (c) => c.toUpperCase()) // Capitalize first letter
			.trim();
	} catch (error) {
		console.error('Error formatting title case:', error);
		return text;
	}
}

/**
 * جلب أسماء اللغات المتاحة
 * Get available language names
 * @returns {Object} أسماء اللغات
 */
export function getAvailableLanguages() {
	return { ...languageNames };
}

/**
 * جلب اللغة الحالية
 * Get current language
 * @returns {string} رمز اللغة الحالية
 */
export function getCurrentLanguage() {
	return get(language);
}

/**
 * جلب قائمة اللغات المدعومة
 * Get supported languages list
 * @returns {Array} قائمة اللغات المدعومة
 */
export function getSupportedLanguages() {
	return Object.entries(languageNames).map(([code, name]) => ({
		code,
		name
	}));
}

// Export language names and dictionary
export { languageNames, dictionary };
