// src/lib/i18n/index.js
// مدير الترجمة

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { dictionary, languageNames } from './dictionary';

// Get user's preferred language from browser or localStorage
const getInitialLanguage = () => {
  if (!browser) return 'ar'; // Default to Arabic on server
  
  // Check localStorage first
  const storedLang = localStorage.getItem('language');
  if (storedLang) return storedLang;
  
  // Check browser language
  const browserLang = navigator.language.split('-')[0];
  return browserLang === 'en' ? 'en' : 'ar'; // Default to Arabic if not English
};

// Create a writable store for the active language
export const language = writable(getInitialLanguage());

// When language changes, update localStorage
if (browser) {
  language.subscribe(lang => {
    localStorage.setItem('language', lang);
    // Update HTML dir attribute for RTL/LTR
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
  });
}

// Create a translation function
export const t = derived(language, $language => (key) => {
  // Split the key by dots to access nested properties
  const keys = key.split('.');
  let value = dictionary[$language];
  
  // Navigate through the dictionary
  for (const k of keys) {
    if (value && value[k] !== undefined) {
      value = value[k];
    } else {
      console.warn(`Translation key not found: ${key}`);
      return key; // Return the key if translation not found
    }
  }
  
  return value;
});

// Function to change language
export const changeLanguage = (lang) => {
  if (lang === 'ar' || lang === 'en') {
    language.set(lang);
  } else {
    console.warn(`Unsupported language: ${lang}`);
  }
};

// Format utilities

/**
 * Format a date according to the current language
 * @param {Date|string|number} date - Date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(date, options = {}) {
  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    const currentLang = get(language);
    
    // Default options
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      ...options
    };
    
    return new Intl.DateTimeFormat(
      currentLang === 'ar' ? 'ar-SA' : 'en-US', 
      defaultOptions
    ).format(dateObj);
  } catch (error) {
    console.error('Error formatting date:', error);
    return String(date);
  }
}

/**
 * Format a number according to the current language
 * @param {number} number - Number to format
 * @param {object} options - Intl.NumberFormat options
 * @returns {string} Formatted number string
 */
export function formatNumber(number, options = {}) {
  try {
    const currentLang = get(language);
    
    return new Intl.NumberFormat(
      currentLang === 'ar' ? 'ar-SA' : 'en-US', 
      options
    ).format(number);
  } catch (error) {
    console.error('Error formatting number:', error);
    return String(number);
  }
}

/**
 * Format a currency amount according to the current language
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: SAR for Saudi Riyal)
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, currency = 'SAR') {
  return formatNumber(amount, {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  });
}

/**
 * Get direction string (rtl/ltr) based on current language
 * @returns {string} 'rtl' for Arabic, 'ltr' otherwise
 */
export function getDirection() {
  return get(language) === 'ar' ? 'rtl' : 'ltr';
}

/**
 * Check if current language is RTL
 * @returns {boolean} true if language is Arabic
 */
export function isRTL() {
  return get(language) === 'ar';
}

// Export language names and dictionary
export { languageNames, dictionary };