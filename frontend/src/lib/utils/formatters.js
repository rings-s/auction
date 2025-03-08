// /src/lib/utils/formatters.js

/**
 * Format a date string to a readable format
 * @param {string} dateStr - ISO date string
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date string
 */
export function formatDate(dateStr, options = {}) {
  if (!dateStr) return '';
  
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  
  // Default options
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: undefined,
    minute: undefined,
    second: undefined
  };
  
  // Merge options
  const mergedOptions = { ...defaultOptions, ...options };
  
  return new Intl.DateTimeFormat('en-US', mergedOptions).format(date);
}

/**
 * Format a date with time
 * @param {string} dateStr - ISO date string
 * @returns {string} - Formatted date and time
 */
export function formatDateTime(dateStr) {
  return formatDate(dateStr, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

/**
 * Format a currency amount
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code
 * @returns {string} - Formatted currency string
 */
export function formatCurrency(amount, currency = 'USD') {
  if (amount === undefined || amount === null) return '';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}

/**
 * Format a number with commas
 * @param {number} num - Number to format
 * @returns {string} - Formatted number
 */
export function formatNumber(num) {
  if (num === undefined || num === null) return '';
  
  return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Format a string to title case
 * @param {string} str - String to format
 * @returns {string} - Title case string
 */
export function toTitleCase(str) {
  if (!str) return '';
  
  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Format a time difference as relative time (e.g., "5 minutes ago")
 * @param {string} dateStr - ISO date string
 * @returns {string} - Relative time string
 */
export function formatRelativeTime(dateStr) {
  if (!dateStr) return '';
  
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  
  if (diffSec < 60) return 'just now';
  
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
  
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
  
  const diffDay = Math.floor(diffHour / 24);
  if (diffDay < 7) return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
  
  const diffWeek = Math.floor(diffDay / 7);
  if (diffWeek < 4) return `${diffWeek} week${diffWeek !== 1 ? 's' : ''} ago`;
  
  const diffMonth = Math.floor(diffDay / 30);
  if (diffMonth < 12) return `${diffMonth} month${diffMonth !== 1 ? 's' : ''} ago`;
  
  const diffYear = Math.floor(diffDay / 365);
  return `${diffYear} year${diffYear !== 1 ? 's' : ''} ago`;
}

/**
 * Format a time ago string (e.g., "5 minutes ago")
 * @param {string} dateStr - ISO date string
 * @returns {string} - Time ago string
 */
export function formatTimeAgo(dateStr) {
  return formatRelativeTime(dateStr);
}

/**
 * Format a time remaining string for auctions
 * @param {Object} remaining - Object with remaining time values
 * @returns {string} - Formatted remaining time
 */
export function formatTimeRemaining(remaining) {
  if (!remaining) return 'No time remaining';
  
  if (remaining.total_seconds <= 0) {
    return 'Ended';
  }
  
  if (remaining.days > 0) {
    return `${remaining.days}d ${remaining.hours}h ${remaining.minutes}m`;
  }
  
  if (remaining.hours > 0) {
    return `${remaining.hours}h ${remaining.minutes}m ${remaining.seconds}s`;
  }
  
  return `${remaining.minutes}m ${remaining.seconds}s`;
}

/**
 * Format a file size in bytes to a human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Get a readable string from an enum/constant value
 * @param {string} value - The constant value (e.g., "REAL_ESTATE")
 * @returns {string} - Human-readable string (e.g., "Real Estate")
 */
export function readableConstant(value) {
  if (!value) return '';
  
  return value
    .toString()
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.toLowerCase().slice(1))
    .join(' ');
}