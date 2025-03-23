// src/lib/utils/formatters.js
// تنسيق البيانات (تاريخ، عملة، إلخ) - Data formatting utilities

import { get } from 'svelte/store';
import { language } from '$lib/i18n';

/**
 * تنسيق الرقم كعملة
 * Format a number as currency
 * 
 * @param {number} amount - المبلغ المراد تنسيقه
 * @param {string} currencyCode - رمز العملة (الافتراضي: SAR)
 * @param {string} locale - اللغة المستخدمة للتنسيق (الافتراضي: اللغة الحالية)
 * @returns {string} النص المنسق
 */
export function formatCurrency(amount, currencyCode = 'SAR', locale = null) {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '-';
  }

  try {
    // Get current language or use provided locale
    const currentLang = locale || get(language);
    const localeString = currentLang === 'ar' ? 'ar-SA' : 'en-US';

    return new Intl.NumberFormat(localeString, {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  } catch (error) {
    console.error('Error formatting currency:', error);
    return `${amount} ${currencyCode}`;
  }
}

/**
 * تنسيق الرقم
 * Format a number
 * 
 * @param {number} number - الرقم المراد تنسيقه
 * @param {Object} options - خيارات التنسيق
 * @param {number} options.minimumFractionDigits - الحد الأدنى لخانات الكسور العشرية
 * @param {number} options.maximumFractionDigits - الحد الأقصى لخانات الكسور العشرية
 * @param {string} locale - اللغة المستخدمة للتنسيق (الافتراضي: اللغة الحالية)
 * @returns {string} النص المنسق
 */
export function formatNumber(number, options = {}, locale = null) {
  if (number === null || number === undefined || isNaN(number)) {
    return '-';
  }

  try {
    // Get current language or use provided locale
    const currentLang = locale || get(language);
    const localeString = currentLang === 'ar' ? 'ar-SA' : 'en-US';

    // Default options
    const defaultOptions = {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    };

    // Merge options
    const formatOptions = { ...defaultOptions, ...options };

    return new Intl.NumberFormat(localeString, formatOptions).format(number);
  } catch (error) {
    console.error('Error formatting number:', error);
    return number.toString();
  }
}

/**
 * تنسيق التاريخ
 * Format a date
 * 
 * @param {Date|string|number} date - التاريخ المراد تنسيقه
 * @param {Object} options - خيارات التنسيق
 * @param {string} options.dateStyle - نمط عرض التاريخ (full, long, medium, short)
 * @param {string} options.timeStyle - نمط عرض الوقت (full, long, medium, short)
 * @param {boolean} options.showTime - عرض الوقت
 * @param {string} locale - اللغة المستخدمة للتنسيق (الافتراضي: اللغة الحالية)
 * @returns {string} النص المنسق
 */
export function formatDate(date, options = {}, locale = null) {
  if (!date) return '-';

  try {
    // Convert to Date object if it's not already
    const dateObj = date instanceof Date ? date : new Date(date);
    
    // Check if date is valid
    if (isNaN(dateObj.getTime())) {
      return '-';
    }

    // Get current language or use provided locale
    const currentLang = locale || get(language);
    const localeString = currentLang === 'ar' ? 'ar-SA' : 'en-US';

    // Default options
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };

    // Add time if showTime is true
    if (options.showTime) {
      defaultOptions.hour = 'numeric';
      defaultOptions.minute = 'numeric';
    }

    // If dateStyle is provided, use it instead of individual options
    if (options.dateStyle) {
      delete defaultOptions.year;
      delete defaultOptions.month;
      delete defaultOptions.day;
      defaultOptions.dateStyle = options.dateStyle;
    }

    // If timeStyle is provided, use it instead of individual time options
    if (options.timeStyle) {
      delete defaultOptions.hour;
      delete defaultOptions.minute;
      defaultOptions.timeStyle = options.timeStyle;
    }

    // Merge options
    const formatOptions = { ...defaultOptions, ...options };

    return new Intl.DateTimeFormat(localeString, formatOptions).format(dateObj);
  } catch (error) {
    console.error('Error formatting date:', error);
    return String(date);
  }
}

/**
 * تنسيق المساحة
 * Format an area measurement
 * 
 * @param {number} area - المساحة المراد تنسيقها
 * @param {string} unit - وحدة المساحة (الافتراضي: m²)
 * @param {number} fractionDigits - عدد الخانات العشرية (الافتراضي: 2)
 * @returns {string} النص المنسق
 */
export function formatArea(area, unit = 'm²', fractionDigits = 2) {
  if (area === null || area === undefined || isNaN(area)) {
    return '-';
  }

  try {
    const formattedNumber = formatNumber(area, {
      minimumFractionDigits: 0,
      maximumFractionDigits: fractionDigits
    });

    return `${formattedNumber} ${unit}`;
  } catch (error) {
    console.error('Error formatting area:', error);
    return `${area} ${unit}`;
  }
}

/**
 * تنسيق رقم الهاتف
 * Format a phone number
 * 
 * @param {string} phoneNumber - رقم الهاتف المراد تنسيقه
 * @param {string} countryCode - رمز الدولة (الافتراضي: SA)
 * @returns {string} النص المنسق
 */
export function formatPhoneNumber(phoneNumber, countryCode = 'SA') {
  if (!phoneNumber) return '-';

  try {
    // Remove non-digit characters
    const digitsOnly = String(phoneNumber).replace(/\D/g, '');
    
    // Handle Saudi Arabia phone numbers
    if (countryCode === 'SA') {
      // Saudi mobile numbers format
      if (digitsOnly.length === 9 && (digitsOnly.startsWith('5'))) {
        return `+966 ${digitsOnly.slice(0, 2)} ${digitsOnly.slice(2, 5)} ${digitsOnly.slice(5)}`;
      }
      // Saudi landline numbers
      else if (digitsOnly.length === 9) {
        return `+966 ${digitsOnly.slice(0, 2)} ${digitsOnly.slice(2)}`;
      }
      // Already has country code
      else if (digitsOnly.length === 12 && digitsOnly.startsWith('966')) {
        return `+${digitsOnly.slice(0, 3)} ${digitsOnly.slice(3, 5)} ${digitsOnly.slice(5, 8)} ${digitsOnly.slice(8)}`;
      }
    }
    
    // Default formatting for other countries or formats
    if (digitsOnly.length > 7) {
      return `${digitsOnly.slice(0, 3)} ${digitsOnly.slice(3, 6)} ${digitsOnly.slice(6)}`;
    }
    
    // Return as is if no formatting rules apply
    return phoneNumber;
  } catch (error) {
    console.error('Error formatting phone number:', error);
    return phoneNumber;
  }
}

/**
 * تنسيق المدة الزمنية بتنسيق إنساني
 * Format a time duration in a human-readable format
 * 
 * @param {number} seconds - عدد الثواني
 * @param {Object} options - خيارات التنسيق
 * @param {boolean} options.compact - عرض مختصر
 * @param {boolean} options.includeSeconds - تضمين الثواني
 * @returns {string} النص المنسق
 */
export function formatDuration(seconds, options = {}) {
  if (seconds === null || seconds === undefined || isNaN(seconds) || seconds < 0) {
    return '-';
  }

  try {
    const currentLang = get(language);
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    // Get the correct terms based on language
    const terms = {
      days: currentLang === 'ar' ? 'يوم' : 'day',
      daysPlural: currentLang === 'ar' ? 'أيام' : 'days',
      hours: currentLang === 'ar' ? 'ساعة' : 'hour',
      hoursPlural: currentLang === 'ar' ? 'ساعات' : 'hours',
      minutes: currentLang === 'ar' ? 'دقيقة' : 'minute',
      minutesPlural: currentLang === 'ar' ? 'دقائق' : 'minutes',
      seconds: currentLang === 'ar' ? 'ثانية' : 'second',
      secondsPlural: currentLang === 'ar' ? 'ثوان' : 'seconds',
      and: currentLang === 'ar' ? 'و' : 'and'
    };
    
    // Compact format just shows the two largest units
    if (options.compact) {
      if (days > 0) {
        const daysTerm = days === 1 ? terms.days : terms.daysPlural;
        const hoursTerm = hours === 1 ? terms.hours : terms.hoursPlural;
        return `${days} ${daysTerm} ${hours} ${hoursTerm}`;
      } else if (hours > 0) {
        const hoursTerm = hours === 1 ? terms.hours : terms.hoursPlural;
        const minutesTerm = minutes === 1 ? terms.minutes : terms.minutesPlural;
        return `${hours} ${hoursTerm} ${minutes} ${minutesTerm}`;
      } else {
        const minutesTerm = minutes === 1 ? terms.minutes : terms.minutesPlural;
        const secondsTerm = remainingSeconds ===.1 ? terms.seconds : terms.secondsPlural;
        return `${minutes} ${minutesTerm} ${remainingSeconds} ${secondsTerm}`;
      }
    }
    
    // Full format
    const parts = [];
    
    if (days > 0) {
      const term = days === 1 ? terms.days : terms.daysPlural;
      parts.push(`${days} ${term}`);
    }
    
    if (hours > 0) {
      const term = hours === 1 ? terms.hours : terms.hoursPlural;
      parts.push(`${hours} ${term}`);
    }
    
    if (minutes > 0) {
      const term = minutes === 1 ? terms.minutes : terms.minutesPlural;
      parts.push(`${minutes} ${term}`);
    }
    
    if ((remainingSeconds > 0 && options.includeSeconds) || parts.length === 0) {
      const term = remainingSeconds === 1 ? terms.seconds : terms.secondsPlural;
      parts.push(`${remainingSeconds} ${term}`);
    }
    
    if (parts.length === 1) {
      return parts[0];
    } else {
      const lastPart = parts.pop();
      return `${parts.join(', ')} ${terms.and} ${lastPart}`;
    }
  } catch (error) {
    console.error('Error formatting duration:', error);
    return `${seconds}s`;
  }
}

/**
 * تنسيق العنوان بطريقة متناسقة
 * Format an address consistently
 * 
 * @param {Object} addressParts - أجزاء العنوان
 * @param {string} addressParts.address - العنوان التفصيلي
 * @param {string} addressParts.district - الحي
 * @param {string} addressParts.city - المدينة
 * @param {string} addressParts.postalCode - الرمز البريدي
 * @param {string} addressParts.country - الدولة
 * @returns {string} العنوان المنسق
 */
export function formatAddress(addressParts) {
  if (!addressParts) return '-';
  
  try {
    const { address, district, city, postalCode, country } = addressParts;
    const parts = [];
    
    if (address) parts.push(address);
    if (district) parts.push(district);
    
    const locationParts = [];
    if (city) locationParts.push(city);
    if (postalCode) locationParts.push(postalCode);
    if (locationParts.length > 0) parts.push(locationParts.join(' '));
    
    if (country) parts.push(country);
    
    return parts.join(', ');
  } catch (error) {
    console.error('Error formatting address:', error);
    return Object.values(addressParts).filter(Boolean).join(', ');
  }
}

/**
 * تنسيق النص مع إضافة علامات الاقتباس
 * Format text with quotes
 * 
 * @param {string} text - النص المراد تنسيقه
 * @param {string} quoteStyle - نمط علامات الاقتباس
 * @returns {string} النص المنسق
 */
export function formatWithQuotes(text, quoteStyle = 'standard') {
  if (!text) return '';
  
  const quotes = {
    standard: { open: '"', close: '"' },
    arabic: { open: '"', close: '"' },
    french: { open: '«', close: '»' },
    german: { open: '„', close: '"' },
    single: { open: "'", close: "'" }
  };
  
  const currentLang = get(language);
  const defaultStyle = currentLang === 'ar' ? 'arabic' : 'standard';
  const style = quotes[quoteStyle] || quotes[defaultStyle];
  
  return `${style.open}${text}${style.close}`;
}

/**
 * تنسيق حجم الملف بطريقة إنسانية
 * Format file size in a human-readable format
 * 
 * @param {number} bytes - حجم الملف بالبايت
 * @param {number} decimals - عدد الخانات العشرية (الافتراضي: 2)
 * @returns {string} الحجم المنسق
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  if (!bytes || isNaN(bytes)) return '-';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * تنسيق نص رقمي مع إضافة أصفار في البداية
 * Format a number with leading zeros
 * 
 * @param {number} num - الرقم
 * @param {number} size - الطول المطلوب
 * @returns {string} النص المنسق
 */
export function padNumber(num, size = 2) {
  let s = String(num);
  while (s.length < size) s = '0' + s;
  return s;
}

/**
 * تنسيق النسبة المئوية
 * Format a percentage
 * 
 * @param {number} value - القيمة
 * @param {number} decimals - عدد الخانات العشرية (الافتراضي: 1)
 * @param {boolean} includeSymbol - تضمين علامة النسبة المئوية
 * @returns {string} النسبة المئوية المنسقة
 */
export function formatPercentage(value, decimals = 1, includeSymbol = true) {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }
  
  try {
    const formattedValue = value.toFixed(decimals);
    return includeSymbol ? `${formattedValue}%` : formattedValue;
  } catch (error) {
    console.error('Error formatting percentage:', error);
    return `${value}${includeSymbol ? '%' : ''}`;
  }
}