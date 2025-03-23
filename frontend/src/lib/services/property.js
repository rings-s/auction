// src/lib/services/property.js
// خدمات العقارات - Property Services

import api from './api';

/**
 * خدمات العقارات - توفر دوال للتعامل مع العقارات عبر واجهة برمجة التطبيقات
 * Property services - provides functions for interacting with properties via the API
 */
class PropertyService {
    /**
     * الحصول على قائمة العقارات مع إمكانية التصفية
     * Get a list of properties with optional filtering
     * 
     * @param {Object} filters - معايير التصفية (اختياري)
     * @param {string} filters.property_type - نوع العقار
     * @param {string} filters.status - حالة العقار
     * @param {number} filters.min_price - الحد الأدنى للسعر
     * @param {number} filters.max_price - الحد الأقصى للسعر
     * @param {number} filters.min_area - الحد الأدنى للمساحة
     * @param {number} filters.max_area - الحد الأقصى للمساحة
     * @param {number} filters.bedrooms - عدد غرف النوم
     * @param {number} filters.bathrooms - عدد الحمامات
     * @param {string} filters.city - المدينة
     * @param {string} filters.district - الحي
     * @param {boolean} filters.has_auction - هل له مزاد
     * @param {boolean} filters.is_featured - هل العقار مميز
     * @param {number} filters.page - رقم الصفحة
     * @param {number} filters.page_size - عدد العناصر في الصفحة
     * @param {string} filters.sort_by - ترتيب حسب
     * @param {string} filters.order - ترتيب (asc, desc)
     * @returns {Promise<Object>} وعد يحتوي على بيانات العقارات
     */
    async getProperties(filters = {}) {
        try {
            const response = await api.get('properties/', filters);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching properties:', error);
            return {
                success: false,
                error: error.message || 'Failed to fetch properties'
            };
        }
    }

    /**
     * الحصول على تفاصيل عقار معين
     * Get details of a specific property
     * 
     * @param {string|number} propertyId - معرف العقار
     * @param {Object} options - خيارات إضافية
     * @param {boolean} options.include_auctions - تضمين المزادات
     * @param {boolean} options.include_documents - تضمين المستندات
     * @returns {Promise<Object>} وعد يحتوي على بيانات العقار
     */
    async getPropertyDetails(propertyId, options = {}) {
        if (!propertyId) {
            return {
                success: false,
                error: 'Property ID is required'
            };
        }

        try {
            const response = await api.get(`properties/${propertyId}/`, options);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error fetching property ${propertyId}:`, error);
            return {
                success: false,
                error: error.message || 'Failed to fetch property details'
            };
        }
    }

    /**
     * إنشاء عقار جديد
     * Create a new property
     * 
     * @param {Object} propertyData - بيانات العقار الجديد
     * @returns {Promise<Object>} وعد يحتوي على بيانات العقار الجديد
     */
    async createProperty(propertyData) {
        if (!propertyData?.title || !propertyData?.property_type) {
            return {
                success: false,
                error: 'Property title and type are required'
            };
        }

        try {
            const response = await api.post('properties/create/', propertyData);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error creating property:', error);
            return {
                success: false,
                error: error.message || 'Failed to create property'
            };
        }
    }

    /**
     * تحديث عقار موجود
     * Update an existing property
     * 
     * @param {string|number} propertyId - معرف العقار
     * @param {Object} updateData - بيانات التحديث
     * @param {boolean} partial - تحديث جزئي (PATCH) أو كلي (PUT)
     * @returns {Promise<Object>} وعد يحتوي على بيانات العقار المحدث
     */
    async updateProperty(propertyId, updateData, partial = true) {
        if (!propertyId) {
            return {
                success: false,
                error: 'Property ID is required'
            };
        }

        try {
            const method = partial ? 'patch' : 'put';
            const response = await api[method](`properties/${propertyId}/update/`, updateData);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error updating property ${propertyId}:`, error);
            return {
                success: false,
                error: error.message || 'Failed to update property'
            };
        }
    }

    /**
     * حذف عقار
     * Delete a property
     * 
     * @param {string|number} propertyId - معرف العقار
     * @returns {Promise<Object>} وعد يحتوي على نتيجة الحذف
     */
    async deleteProperty(propertyId) {
        if (!propertyId) {
            return {
                success: false,
                error: 'Property ID is required'
            };
        }

        try {
            const response = await api.delete(`properties/${propertyId}/delete/`);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error deleting property ${propertyId}:`, error);
            return {
                success: false,
                error: error.message || 'Failed to delete property'
            };
        }
    }

    /**
     * تغيير حالة العقار
     * Change property status
     * 
     * @param {string|number} propertyId - معرف العقار
     * @param {string} newStatus - الحالة الجديدة
     * @returns {Promise<Object>} وعد يحتوي على نتيجة تغيير الحالة
     */
    async changePropertyStatus(propertyId, newStatus) {
        if (!propertyId || !newStatus) {
            return {
                success: false,
                error: 'Property ID and new status are required'
            };
        }

        try {
            const response = await api.post(`properties/${propertyId}/status/`, { status: newStatus });
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error changing property ${propertyId} status:`, error);
            return {
                success: false,
                error: error.message || 'Failed to change property status'
            };
        }
    }

    /**
     * الحصول على مستندات العقار
     * Get property documents
     * 
     * @param {string|number} propertyId - معرف العقار
     * @param {Object} options - خيارات التصفية
     * @returns {Promise<Object>} وعد يحتوي على بيانات المستندات
     */
    async getPropertyDocuments(propertyId, options = {}) {
        if (!propertyId) {
            return {
                success: false,
                error: 'Property ID is required'
            };
        }

        try {
            const response = await api.get(`properties/${propertyId}/documents/`, options);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error fetching documents for property ${propertyId}:`, error);
            return {
                success: false,
                error: error.message || 'Failed to fetch property documents'
            };
        }
    }

    /**
     * الحصول على إحصائيات العقارات
     * Get property analytics
     * 
     * @param {Object} filters - معايير التصفية (اختياري)
     * @param {string} filters.start_date - تاريخ البدء للتحليل
     * @param {string} filters.end_date - تاريخ الانتهاء للتحليل
     * @param {string} filters.property_type - نوع العقار
     * @param {string} filters.status - حالة العقار
     * @param {string} filters.city - المدينة
     * @param {string} filters.format - تنسيق البيانات (json, csv)
     * @returns {Promise<Object>} وعد يحتوي على بيانات التحليل
     */
    async getPropertyAnalytics(filters = {}) {
        try {
            const response = await api.get('properties/analytics/', filters);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching property analytics:', error);
            return {
                success: false,
                error: error.message || 'Failed to fetch property analytics'
            };
        }
    }

    /**
     * البحث عن العقارات
     * Search for properties
     * 
     * @param {string} query - نص البحث
     * @param {Object} filters - معايير تصفية إضافية (اختياري)
     * @returns {Promise<Object>} وعد يحتوي على نتائج البحث
     */
    async searchProperties(query, filters = {}) {
        try {
            const params = {
                search: query,
                ...filters
            };
            const response = await api.get('properties/', params);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error searching properties with query "${query}":`, error);
            return {
                success: false,
                error: error.message || 'Failed to search properties'
            };
        }
    }
}

// Export a singleton instance
export default new PropertyService();