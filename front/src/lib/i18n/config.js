// lib/i18n/config.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Supported locales configuration
export const LOCALES = {
  en: { code: 'en', name: 'English', dir: 'ltr' },
  ar: { code: 'ar', name: 'العربية', dir: 'rtl' }
};

export const DEFAULT_LOCALE = 'en';
export const SUPPORTED_LOCALES = Object.keys(LOCALES);

// Store for available locales
export const locales = writable(LOCALES);

// Initial locale detection with better fallback
function detectInitialLocale() {
  if (!browser) return DEFAULT_LOCALE;
  
  try {
    // Check localStorage first
    const saved = localStorage.getItem('app-locale');
    if (saved && SUPPORTED_LOCALES.includes(saved)) return saved;
    
    // Check browser language
    const browserLang = navigator.language.split('-')[0];
    if (SUPPORTED_LOCALES.includes(browserLang)) return browserLang;
    
    // Check Accept-Language header preference
    const languages = navigator.languages || [];
    for (const lang of languages) {
      const code = lang.split('-')[0];
      if (SUPPORTED_LOCALES.includes(code)) return code;
    }
  } catch (error) {
    console.warn('Locale detection failed:', error);
  }
  
  return DEFAULT_LOCALE;
}

// Current locale store
export const locale = writable(detectInitialLocale());

// Subscribe to locale changes and apply DOM updates
if (browser) {
  locale.subscribe((value) => {
    try {
      localStorage.setItem('app-locale', value);
      const config = LOCALES[value];
      if (config) {
        document.documentElement.lang = value;
        document.documentElement.dir = config.dir;
        document.documentElement.classList.remove('ltr', 'rtl');
        document.documentElement.classList.add(config.dir);
      }
    } catch (error) {
      console.warn('Failed to update locale settings:', error);
    }
  });
}