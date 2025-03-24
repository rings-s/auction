// src/lib/stores/propertyStore.js
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
 * Load the properties list
 * 
 * @param {Object} options - Options for loading
 * @param {boolean} options.resetPage - Reset the current page
 * @param {boolean} options.useCurrentFilters - Use current filter criteria
 * @param {Object} options.filters - Custom filter criteria
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
 * Create a new property
 * 
 * @param {Object} propertyData - Property data
 * @returns {Promise<Object>} The newly created property
 */
export async function createProperty(propertyData) {
    isLoadingProperty.set(true);
    propertyError.set(null);
    
    try {
        const response = await propertyService.createProperty(propertyData);
        
        if (response.success) {
            // Show success message
            toast.success(t('properties.create.success') || 'Property created successfully');
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
 * Update a property
 * 
 * @param {string|number} propertyId - Property ID
 * @param {Object} updateData - Update data
 * @param {boolean} partial - Partial (PATCH) or full (PUT) update
 * @returns {Promise<Object>} The updated property
 */
export async function updateProperty(propertyId, updateData, partial = true) {
    if (!propertyId) {
        toast.error(t('properties.id_required') || 'Property ID is required');
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
            toast.success(t('properties.updated_successfully') || 'Property updated successfully');
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

// Export the store object as a singleton
export const propertyStore = {
    // Stores
    properties,
    currentProperty,
    propertyFilters,
    isLoadingProperties,
    isLoadingProperty,
    isLoadingMore,
    propertyError,
    favoriteProperties,
    recommendedProperties,
    activeFiltersCount,
    filtersQueryString,
    
    // Methods
    loadProperties,
    createProperty,
    updateProperty,
    
    // Re-export functions from the propertyStore.js
    loadProperty: propertyService.getPropertyDetails,
    loadMoreProperties: propertyService.getProperties,
    searchProperties: propertyService.searchProperties,
    deleteProperty: propertyService.deleteProperty,
    toggleFavorite: propertyService.toggleFavoriteProperty
};

export default propertyStore;