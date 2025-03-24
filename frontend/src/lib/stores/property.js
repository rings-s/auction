// src/lib/stores/property.js
// Property store with all necessary exports for the application

import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import propertyService from '$lib/services/property';
import { t } from '$lib/i18n';
import { toast } from '$lib/stores/toast';

// ==================== Initial States ====================

// Main property stores
const initialPropertiesState = {
    items: [],
    count: 0,
    totalPages: 0,
    currentPage: 1,
    pageSize: 12,
    hasMore: false,
    featured: []
};

const initialFiltersState = {
    property_type: '',
    status: '',
    bedrooms: '',
    bathrooms: '',
    city: '',
    district: '',
    min_price: '',
    max_price: '',
    min_area: '',
    max_area: '',
    sort_by: 'created_at',
    order: 'desc',
    search: ''
};

// ==================== Store Definitions ====================

// Primary stores
export const properties = writable({ ...initialPropertiesState });
export const currentProperty = writable(null);
export const propertyFilters = writable({ ...initialFiltersState });

// UI state stores
export const isLoadingProperties = writable(false);
export const isLoadingProperty = writable(false);
export const isLoadingMore = writable(false);
export const propertyError = writable(null);
export const favoriteProperties = writable([]);
export const recommendedProperties = writable([]);

// Export loading state for components that expect it (like AuctionGrid)
export const loading = isLoadingProperties;

// ==================== Derived Stores ====================

// Active filters count for UI feedback
export const activeFiltersCount = derived(propertyFilters, $filters => {
    return Object.entries($filters).filter(([key, value]) => {
        // Skip these fields when counting active filters
        if (key === 'sort_by' || key === 'order' || key === 'search') {
            return false;
        }
        // Otherwise, count non-empty values
        return value !== '' && value !== null && value !== undefined;
    }).length;
});

// Filter state for persisting in URL or localStorage
export const filtersQueryString = derived(propertyFilters, $filters => {
    const params = new URLSearchParams();
    
    Object.entries($filters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
            params.append(key, value);
        }
    });
    
    return params.toString();
});

// ==================== Action Functions ====================

/**
 * تحميل قائمة العقارات
 * Load the properties list
 * 
 * @param {Object} options - خيارات التحميل
 * @param {boolean} options.resetPage - إعادة ضبط الصفحة الحالية
 * @param {boolean} options.useCurrentFilters - استخدام معايير التصفية الحالية
 * @param {Object} options.filters - معايير تصفية مخصصة
 */
export async function loadProperties(options = {}) {
    const { resetPage = true, useCurrentFilters = true, filters = {} } = options;
    
    // Show loading state
    isLoadingProperties.set(true);
    propertyError.set(null);
    
    // Build filters parameter
    let requestFilters = { ...filters };
    
    // Use current filters if requested
    if (useCurrentFilters) {
        requestFilters = { 
            ...get(propertyFilters),
            ...requestFilters 
        };
    }
    
    // Reset to page 1 if requested
    if (resetPage) {
        requestFilters.page = 1;
    }
    
    // Set default page size
    if (!requestFilters.page_size) {
        requestFilters.page_size = get(properties).pageSize;
    }
    
    try {
        const response = await propertyService.getProperties(requestFilters);
        
        if (response.success) {
            const data = response.data;
            
            properties.update(state => ({
                items: data.results || [],
                count: data.count || 0,
                totalPages: data.total_pages || 0,
                currentPage: data.current_page || 1,
                pageSize: data.page_size || state.pageSize,
                hasMore: data.current_page < data.total_pages
            }));
            
            // If filters provided, update filter store
            if (Object.keys(filters).length > 0 && !useCurrentFilters) {
                propertyFilters.set({ 
                    ...get(propertyFilters),
                    ...filters 
                });
            }
        } else {
            propertyError.set(response.error || t('general.error'));
        }
    } catch (error) {
        console.error('Error loading properties:', error);
        propertyError.set(error.message || t('general.error'));
    } finally {
        isLoadingProperties.set(false);
    }
}

/**
 * تحميل المزيد من العقارات (للصفحة التالية)
 * Load more properties (for the next page)
 */
export async function loadMoreProperties() {
    const currentState = get(properties);
    
    // Stop if already loading or no more data
    if (get(isLoadingMore) || !currentState.hasMore) {
        return;
    }
    
    isLoadingMore.set(true);
    
    try {
        const currentFilters = get(propertyFilters);
        const nextPage = currentState.currentPage + 1;
        
        const response = await propertyService.getProperties({
            ...currentFilters,
            page: nextPage,
            page_size: currentState.pageSize
        });
        
        if (response.success) {
            const data = response.data;
            
            properties.update(state => ({
                items: [...state.items, ...(data.results || [])],
                count: data.count || state.count,
                totalPages: data.total_pages || state.totalPages,
                currentPage: nextPage,
                pageSize: state.pageSize,
                hasMore: nextPage < (data.total_pages || state.totalPages)
            }));
        } else {
            toast.error(response.error || t('general.error_loading_more'));
        }
    } catch (error) {
        console.error('Error loading more properties:', error);
        toast.error(error.message || t('general.error_loading_more'));
    } finally {
        isLoadingMore.set(false);
    }
}

/**
 * تحميل عقار محدد بواسطة المعرف
 * Load a specific property by ID
 * 
 * @param {string|number} propertyId - معرف العقار
 * @param {Object} options - خيارات إضافية
 * @param {boolean} options.includeAuctions - تضمين بيانات المزادات
 * @param {boolean} options.includeDocuments - تضمين المستندات
 */
export async function loadProperty(propertyId, options = {}) {
    if (!propertyId) {
        propertyError.set(t('properties.id_required'));
        return;
    }
    
    isLoadingProperty.set(true);
    propertyError.set(null);
    
    try {
        const requestOptions = {
            include_auctions: options.includeAuctions !== false,
            include_documents: options.includeDocuments !== false
        };
        
        const response = await propertyService.getPropertyDetails(propertyId, requestOptions);
        
        if (response.success && response.data.property) {
            currentProperty.set(response.data.property);
            
            // Load recommended properties in parallel if they exist in response
            if (response.data.recommended_properties) {
                recommendedProperties.set(response.data.recommended_properties);
            } else {
                // Load recommended properties separately
                loadRecommendedProperties(propertyId);
            }
        } else {
            propertyError.set(response.error || t('properties.not_found'));
            currentProperty.set(null);
        }
    } catch (error) {
        console.error(`Error loading property ${propertyId}:`, error);
        propertyError.set(error.message || t('general.error'));
        currentProperty.set(null);
    } finally {
        isLoadingProperty.set(false);
    }
}

/**
 * تحميل العقارات المشابهة الموصى بها
 * Load recommended/similar properties
 * 
 * @param {string|number} propertyId - معرف العقار
 * @param {number} limit - عدد العقارات المطلوبة
 */
export async function loadRecommendedProperties(propertyId, limit = 4) {
    if (!propertyId) return;
    
    try {
        const response = await propertyService.getRecommendedProperties(propertyId, limit);
        
        if (response.success && response.data.properties) {
            recommendedProperties.set(response.data.properties);
        } else {
            recommendedProperties.set([]);
        }
    } catch (error) {
        console.error(`Error loading recommended properties for ${propertyId}:`, error);
        recommendedProperties.set([]);
    }
}

/**
 * تطبيق معايير تصفية جديدة
 * Apply new filters to the properties list
 * 
 * @param {Object} newFilters - معايير التصفية الجديدة
 * @param {boolean} resetPage - إعادة ضبط الصفحة الحالية
 */
export function applyFilters(newFilters, resetPage = true) {
    propertyFilters.update(filters => ({ ...filters, ...newFilters }));
    
    // Reload properties with new filters
    loadProperties({
        resetPage,
        useCurrentFilters: true
    });
}

/**
 * إعادة ضبط معايير التصفية
 * Reset filters to initial state
 */
export function resetFilters() {
    propertyFilters.set({ ...initialFiltersState });
    
    // Reload properties with reset filters
    loadProperties({
        resetPage: true,
        useCurrentFilters: true
    });
}

/**
 * تحميل العقارات المميزة
 * Load featured properties
 * 
 * @param {number} limit - عدد العقارات المطلوبة
 */
export async function loadFeaturedProperties(limit = 6) {
    isLoadingProperties.set(true);
    
    try {
        const response = await propertyService.getProperties({
            is_featured: true,
            page_size: limit,
            sort_by: 'created_at',
            order: 'desc'
        });
        
        if (response.success) {
            properties.update(state => ({
                ...state,
                featured: response.data.results || []
            }));
        }
    } catch (error) {
        console.error('Error loading featured properties:', error);
    } finally {
        isLoadingProperties.set(false);
    }
}

/**
 * البحث عن العقارات
 * Search for properties
 * 
 * @param {string} query - نص البحث
 */
export async function searchProperties(query) {
    if (!query) {
        return resetFilters();
    }
    
    propertyFilters.update(filters => ({ 
        ...filters, 
        search: query 
    }));
    
    // Load properties with search query
    loadProperties({
        resetPage: true,
        useCurrentFilters: true
    });
}

/**
 * تحميل العقارات المفضلة
 * Load favorite properties
 */
export async function loadFavoriteProperties() {
    try {
        const response = await propertyService.getFavoriteProperties();
        
        if (response.success) {
            favoriteProperties.set(response.data.results || []);
        } else {
            favoriteProperties.set([]);
        }
    } catch (error) {
        console.error('Error loading favorite properties:', error);
        favoriteProperties.set([]);
    }
}

/**
 * تبديل حالة العقار المفضل
 * Toggle property favorite status
 * 
 * @param {string|number} propertyId - معرف العقار
 * @returns {Promise<boolean>} حالة المفضلة بعد التبديل
 */
export async function toggleFavorite(propertyId) {
    if (!propertyId) {
        toast.error(t('properties.id_required'));
        return false;
    }
    
    try {
        const response = await propertyService.toggleFavoriteProperty(propertyId);
        
        if (response.success) {
            // Update favorite properties list
            loadFavoriteProperties();
            
            // Show success message
            const message = response.data.is_favorite 
                ? t('properties.added_to_favorites')
                : t('properties.removed_from_favorites');
            
            toast.success(message);
            return response.data.is_favorite;
        } else {
            toast.error(response.error || t('general.error'));
            return false;
        }
    } catch (error) {
        console.error(`Error toggling favorite for property ${propertyId}:`, error);
        toast.error(error.message || t('general.error'));
        return false;
    }
}

/**
 * تحديث بيانات عقار
 * Update a property
 * 
 * @param {string|number} propertyId - معرف العقار
 * @param {Object} updateData - بيانات التحديث
 * @param {boolean} partial - تحديث جزئي (PATCH) أو كلي (PUT)
 * @returns {Promise<Object>} العقار المحدث
 */
export async function updateProperty(propertyId, updateData, partial = true) {
    if (!propertyId) {
        toast.error(t('properties.id_required'));
        return null;
    }
    
    try {
        const response = await propertyService.updateProperty(propertyId, updateData, partial);
        
        if (response.success) {
            // Update current property if we're viewing it
            const current = get(currentProperty);
            if (current && current.id === propertyId) {
                currentProperty.set(response.data.property);
            }
            
            // Show success message
            toast.success(t('properties.updated_successfully'));
            return response.data.property;
        } else {
            toast.error(response.error || t('general.error'));
            return null;
        }
    } catch (error) {
        console.error(`Error updating property ${propertyId}:`, error);
        toast.error(error.message || t('general.error'));
        return null;
    }
}

/**
 * رفع صورة للعقار
 * Upload an image for a property
 * 
 * @param {string|number} propertyId - معرف العقار
 * @param {File} file - ملف الصورة
 * @param {Object} options - خيارات إضافية
 * @param {boolean} options.isPrimary - هل هي الصورة الرئيسية
 * @param {Function} options.onProgress - دالة لتتبع تقدم الرفع
 * @returns {Promise<Object>} بيانات الصورة المرفوعة
 */
export async function uploadPropertyImage(propertyId, file, options = {}) {
    if (!propertyId || !file) {
        toast.error(t('properties.id_and_file_required'));
        return null;
    }
    
    try {
        const metadata = {
            is_primary: options.isPrimary === true
        };
        
        const response = await propertyService.uploadPropertyImage(
            propertyId,
            file,
            metadata,
            options.onProgress
        );
        
        if (response.success) {
            // Refresh current property to show the new image
            if (get(currentProperty)?.id === propertyId) {
                loadProperty(propertyId);
            }
            
            // Show success message
            toast.success(t('properties.image_uploaded'));
            return response.data;
        } else {
            toast.error(response.error || t('general.error'));
            return null;
        }
    } catch (error) {
        console.error(`Error uploading image for property ${propertyId}:`, error);
        toast.error(error.message || t('general.error'));
        return null;
    }
}

/**
 * إنشاء عقار جديد
 * Create a new property
 * 
 * @param {Object} propertyData - بيانات العقار الجديد
 * @returns {Promise<Object>} العقار الجديد
 */
export async function createProperty(propertyData) {
    isLoadingProperty.set(true);
    propertyError.set(null);
    
    try {
        const response = await propertyService.createProperty(propertyData);
        
        if (response.success) {
            // Show success message
            toast.success(t('properties.created_successfully'));
            return response.data.property;
        } else {
            propertyError.set(response.error || t('general.error'));
            toast.error(response.error || t('general.error'));
            return null;
        }
    } catch (error) {
        console.error('Error creating property:', error);
        propertyError.set(error.message || t('general.error'));
        toast.error(error.message || t('general.error'));
        return null;
    } finally {
        isLoadingProperty.set(false);
    }
}

/**
 * تغيير حالة العقار
 * Change property status
 * 
 * @param {string|number} propertyId - معرف العقار
 * @param {string} newStatus - الحالة الجديدة
 * @returns {Promise<boolean>} نجاح العملية
 */
export async function changePropertyStatus(propertyId, newStatus) {
    if (!propertyId || !newStatus) {
        toast.error(t('properties.id_and_status_required'));
        return false;
    }
    
    try {
        const response = await propertyService.changePropertyStatus(propertyId, newStatus);
        
        if (response.success) {
            // Update current property if we're viewing it
            const current = get(currentProperty);
            if (current && current.id === propertyId) {
                currentProperty.update(prop => ({
                    ...prop,
                    status: newStatus,
                    status_display: response.data.property?.status_display || newStatus
                }));
            }
            
            // Show success message
            toast.success(t('properties.status_updated'));
            return true;
        } else {
            toast.error(response.error || t('general.error'));
            return false;
        }
    } catch (error) {
        console.error(`Error changing status for property ${propertyId}:`, error);
        toast.error(error.message || t('general.error'));
        return false;
    }
}

// Initialize data on browser if needed
if (browser) {
    // Load favorites if user is logged in
    if (localStorage.getItem('accessToken')) {
        loadFavoriteProperties();
    }
}

// Export single object for use as "property" in existing code
export const property = {
    properties,
    currentProperty,
    propertyFilters,
    isLoadingProperties,
    isLoadingProperty,
    isLoadingMore,
    loading,
    propertyError,
    favoriteProperties,
    recommendedProperties,
    activeFiltersCount,
    filtersQueryString,
    loadProperties,
    loadMoreProperties,
    loadProperty,
    loadRecommendedProperties,
    applyFilters,
    resetFilters,
    loadFeaturedProperties,
    searchProperties,
    loadFavoriteProperties,
    toggleFavorite,
    updateProperty,
    createProperty,
    changePropertyStatus,
    uploadPropertyImage
};

// Export default object for default imports
export default property;