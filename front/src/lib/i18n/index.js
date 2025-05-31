// lib/i18n/index.js
import { derived } from 'svelte/store';
import { browser } from '$app/environment';
import { locale } from './config.js';
import { translations } from './translations/index.js';
import { 
  getFeatureKey, 
  getAmenityKey, 
  getRoomTypeKey, 
  FEATURE_MAPPING,
  AMENITY_MAPPING,
  ROOM_TYPE_MAPPING 
} from './mappings.js';

// Safe object property access
function getNestedProperty(obj, path) {
  return path.split('.').reduce((current, property) => {
    return current && Object.prototype.hasOwnProperty.call(current, property) 
      ? current[property] 
      : null;
  }, obj);
}

// Parameter interpolation
function interpolateParams(text, params = {}) {
  if (!text || typeof text !== 'string') return text;
  
  return text.replace(/{(\w+)}/g, (match, key) => {
    return Object.prototype.hasOwnProperty.call(params, key) 
      ? params[key] 
      : match;
  });
}

// Main translation function
export const t = derived(
  locale,
  ($locale) => (key, params = {}) => {
    if (!key || typeof key !== 'string') {
      return key || '';
    }
    
    const translation = translations[$locale];
    if (!translation) {
      return key;
    }
    
    const result = getNestedProperty(translation, key);
    if (result === null) {
      return key;
    }
    
    return interpolateParams(result, params);
  }
);

// Helper function for direct translation (for SSR/non-reactive contexts)
export function translateKey(key, params = {}, targetLocale = null) {
  let currentLocale = targetLocale;
  
  if (!currentLocale) {
    if (browser) {
      const saved = localStorage.getItem('app-locale');
      const browserLang = navigator.language?.split('-')[0];
      currentLocale = saved || browserLang || 'en';
    } else {
      currentLocale = 'en';
    }
  }
  
  // Ensure locale is supported
  if (!translations[currentLocale]) {
    currentLocale = 'en';
  }
  
  const translation = translations[currentLocale];
  if (!translation) return key;
  
  const result = getNestedProperty(translation, key);
  if (result === null) return key;
  
  return interpolateParams(result, params);
}

// Feature translation helpers
export function translateFeature(feature, targetLocale = null) {
  if (!feature) return '';
  
  const mappedKey = getFeatureKey(feature);
  if (!mappedKey) return feature;
  
  return translateKey(`property.featureItems.${mappedKey}`, {}, targetLocale) || feature;
}

export function translateAmenity(amenity, targetLocale = null) {
  if (!amenity) return '';
  
  const mappedKey = getAmenityKey(amenity);
  if (!mappedKey) return amenity;
  
  return translateKey(`property.amenityItems.${mappedKey}`, {}, targetLocale) || amenity;
}

export function translateRoomType(roomType, targetLocale = null) {
  if (!roomType) return '';
  
  const mappedKey = getRoomTypeKey(roomType);
  if (!mappedKey) return roomType;
  
  return translateKey(`property.roomTypes.${mappedKey}`, {}, targetLocale) || roomType;
}

// Batch translation helpers
export function translateFeatures(features = [], targetLocale = null) {
  return features.map(feature => translateFeature(feature, targetLocale));
}

export function translateAmenities(amenities = [], targetLocale = null) {
  return amenities.map(amenity => translateAmenity(amenity, targetLocale));
}

// Export everything for easy access
export * from './config.js';
export * from './mappings.js';
export { translations };