// src/lib/services/auction.js
// خدمات المزادات - Auction Services

import api from './api';

/**
 * خدمات المزادات - توفر دوال للتعامل مع المزادات عبر واجهة برمجة التطبيقات
 * Auction services - provides functions for interacting with auctions via the API
 */
class AuctionService {
    /**
     * الحصول على قائمة المزادات مع إمكانية التصفية
     * Get a list of auctions with optional filtering
     * 
     * @param {Object} filters - معايير التصفية (اختياري)
     * @param {string} filters.status - حالة المزاد (active, pending, closed, etc.)
     * @param {string} filters.auction_type - نوع المزاد
     * @param {string} filters.property_type - نوع العقار
     * @param {number} filters.min_price - الحد الأدنى للسعر
     * @param {number} filters.max_price - الحد الأقصى للسعر
     * @param {string} filters.city - المدينة
     * @param {string} filters.district - الحي
     * @param {string} filters.start_date_from - تاريخ بداية المزاد (من)
     * @param {string} filters.start_date_to - تاريخ بداية المزاد (إلى)
     * @param {string} filters.end_date_from - تاريخ نهاية المزاد (من)
     * @param {string} filters.end_date_to - تاريخ نهاية المزاد (إلى)
     * @param {boolean} filters.is_featured - هل المزاد مميز
     * @param {boolean} filters.is_published - هل المزاد منشور
     * @param {string} filters.bidder_id - معرف المزايد (للتصفية حسب المزايد)
     * @param {string} filters.owner_id - معرف المالك (للتصفية حسب مالك العقار)
     * @param {string} filters.auctioneer_id - معرف منظم المزاد
     * @param {boolean} filters.has_bids - هل هناك مزايدات
     * @param {number} filters.min_bid_count - الحد الأدنى لعدد المزايدات
     * @param {string} filters.search - بحث عبر العنوان والوصف
     * @param {string} filters.sort_by - ترتيب حسب (start_date, current_bid, etc.)
     * @param {string} filters.order - ترتيب (asc, desc)
     * @param {string} filters.fields - الحقول المطلوبة (قائمة مفصولة بفواصل)
     * @param {number} filters.page - رقم الصفحة
     * @param {number} filters.page_size - عدد العناصر في الصفحة
     * @returns {Promise<Object>} وعد يحتوي على بيانات المزادات
     */
    async getAuctions(filters = {}) {
        try {
            const response = await api.get('auctions/', filters);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching auctions:', error);
            return {
                success: false,
                error: error.message || 'Failed to fetch auctions'
            };
        }
    }

    /**
     * الحصول على تفاصيل مزاد معين
     * Get details of a specific auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @param {Object} options - خيارات إضافية
     * @param {boolean} options.include_bids - تضمين المزايدات
     * @param {boolean} options.include_property - تضمين تفاصيل العقار
     * @param {boolean} options.include_documents - تضمين المستندات
     * @returns {Promise<Object>} وعد يحتوي على بيانات المزاد
     */
    async getAuctionDetails(auctionId, options = {}) {
        if (!auctionId) {
            return {
                success: false,
                error: 'Auction ID is required'
            };
        }

        try {
            const response = await api.get(`auctions/${auctionId}/`, options);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error fetching auction ${auctionId}:`, error);
            return {
                success: false,
                error: error.message || 'Failed to fetch auction details'
            };
        }
    }

    /**
     * إنشاء مزاد جديد
     * Create a new auction
     * 
     * @param {Object} auctionData - بيانات المزاد الجديد
     * @param {string|number} auctionData.property_id - معرف العقار
     * @param {string} auctionData.title - عنوان المزاد
     * @param {string} auctionData.description - وصف المزاد (اختياري)
     * @param {string} auctionData.auction_type - نوع المزاد
     * @param {string} auctionData.status - حالة المزاد (default: draft)
     * @param {Date|string} auctionData.start_date - تاريخ البدء
     * @param {Date|string} auctionData.end_date - تاريخ الانتهاء
     * @param {number} auctionData.starting_price - سعر البدء
     * @param {number} auctionData.reserve_price - السعر الاحتياطي
     * @param {number} auctionData.min_bid_increment - الحد الأدنى للزيادة (default: 100)
     * @param {boolean} auctionData.auto_extend - التمديد التلقائي (default: true)
     * @param {number} auctionData.extension_minutes - دقائق التمديد (default: 10)
     * @param {number} auctionData.deposit_amount - مبلغ التأمين (اختياري)
     * @param {boolean} auctionData.deposit_required - هل مطلوب تأمين (default: false)
     * @param {number} auctionData.buyer_premium_percent - نسبة عمولة المشتري (default: 5.0)
     * @param {number} auctionData.seller_commission_percent - نسبة عمولة البائع (default: 2.5)
     * @returns {Promise<Object>} وعد يحتوي على بيانات المزاد الجديد
     */
    async createAuction(auctionData) {
        if (!auctionData?.property_id) {
            return {
                success: false,
                error: 'Property ID is required'
            };
        }

        // Ensure required fields are present
        const requiredFields = ['title', 'start_date', 'end_date', 'starting_price', 'reserve_price'];
        for (const field of requiredFields) {
            if (!auctionData[field]) {
                return {
                    success: false,
                    error: `${field} is required`
                };
            }
        }

        try {
            const response = await api.post('auctions/create/', auctionData);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error creating auction:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to create auction'
            };
        }
    }

    /**
     * تحديث مزاد موجود
     * Update an existing auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @param {Object} updateData - بيانات التحديث
     * @param {boolean} partial - تحديث جزئي (PATCH) أو كلي (PUT)
     * @returns {Promise<Object>} وعد يحتوي على بيانات المزاد المحدث
     */
    async updateAuction(auctionId, updateData, partial = true) {
        if (!auctionId) {
            return {
                success: false,
                error: 'Auction ID is required'
            };
        }

        try {
            const method = partial ? 'patch' : 'put';
            const response = await api[method](`auctions/${auctionId}/update/`, updateData);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error updating auction ${auctionId}:`, error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to update auction'
            };
        }
    }

    /**
     * حذف مزاد
     * Delete an auction
     * 
     * @param {string|number} auctionId - معرف المزاد
     * @returns {Promise<Object>} وعد يحتوي على نتيجة الحذف
     */
    async deleteAuction(auctionId) {
        if (!auctionId) {
            return {
                success: false,
                error: 'Auction ID is required'
            };
        }

        try {
            const response = await api.delete(`auctions/${auctionId}/delete/`);
            return {
                success: true,
                data: response.data || {},
                message: response.message || 'Auction deleted successfully'
            };
        } catch (error) {
            console.error(`Error deleting auction ${auctionId}:`, error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to delete auction'
            };
        }
    }

    /**
     * تقديم مزايدة على مزاد
     * Place a bid on an auction
     * 
     * @param {Object} bidData - بيانات المزايدة
     * @param {string|number} bidData.auction - معرف المزاد
     * @param {number} bidData.bid_amount - قيمة المزايدة
     * @param {boolean} bidData.is_auto_bid - هل هي مزايدة تلقائية (اختياري)
     * @param {number} bidData.max_bid_amount - الحد الأقصى للمزايدة التلقائية (مطلوب إذا كانت is_auto_bid صحيحة)
     * @returns {Promise<Object>} وعد يحتوي على نتيجة المزايدة
     */
    async placeBid(bidData) {
        if (!bidData?.auction || !bidData?.bid_amount) {
            return {
                success: false,
                error: 'Auction ID and bid amount are required'
            };
        }

        // Validate auto-bid data
        if (bidData.is_auto_bid && !bidData.max_bid_amount) {
            return {
                success: false,
                error: 'Max bid amount is required for auto bidding'
            };
        }

        try {
            const response = await api.post('bids/place/', bidData);
            return {
                success: true,
                data: response.data || {},
                message: response.message || 'Bid placed successfully'
            };
        } catch (error) {
            console.error('Error placing bid:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to place bid'
            };
        }
    }

    /**
     * الحصول على قائمة المزايدات مع إمكانية التصفية
     * Get a list of bids with optional filtering
     * 
     * @param {Object} filters - معايير التصفية (اختياري)
     * @param {string} filters.auction_id - معرف المزاد
     * @param {string} filters.bidder_id - معرف المزايد
     * @param {string} filters.status - حالة المزايدة
     * @param {number} filters.min_bid_amount - الحد الأدنى لقيمة المزايدة
     * @param {number} filters.max_bid_amount - الحد الأقصى لقيمة المزايدة
     * @param {string} filters.start_date - تاريخ البدء للتصفية
     * @param {string} filters.end_date - تاريخ الانتهاء للتصفية
     * @param {boolean} filters.is_auto_bid - هل هي مزايدة تلقائية
     * @param {string} filters.sort_by - ترتيب حسب
     * @param {string} filters.order - ترتيب (asc, desc)
     * @returns {Promise<Object>} وعد يحتوي على بيانات المزايدات
     */
    async getBids(filters = {}) {
        try {
            const response = await api.get('bids/', filters);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching bids:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch bids'
            };
        }
    }

    /**
     * الحصول على إحصائيات المزادات
     * Get auction analytics
     * 
     * @param {Object} filters - معايير التصفية (اختياري)
     * @param {string} filters.start_date - تاريخ البدء للتحليل
     * @param {string} filters.end_date - تاريخ الانتهاء للتحليل
     * @param {string} filters.auction_type - نوع المزاد
     * @param {string} filters.status - حالة المزاد
     * @param {string} filters.format - تنسيق البيانات (json, csv)
     * @returns {Promise<Object>} وعد يحتوي على بيانات التحليل
     */
    async getAuctionAnalytics(filters = {}) {
        try {
            const response = await api.get('auctions/analytics/', filters);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching auction analytics:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch auction analytics'
            };
        }
    }
    
    /**
     * الحصول على إحصائيات المزايدات
     * Get bid analytics
     * 
     * @param {Object} filters - معايير التصفية (اختياري)
     * @param {string} filters.auction_id - معرف المزاد
     * @param {string} filters.bidder_id - معرف المزايد
     * @param {string} filters.start_date - تاريخ البدء للتحليل
     * @param {string} filters.end_date - تاريخ الانتهاء للتحليل
     * @param {string} filters.format - تنسيق البيانات (json, csv)
     * @returns {Promise<Object>} وعد يحتوي على بيانات التحليل
     */
    async getBidAnalytics(filters = {}) {
        try {
            const response = await api.get('bids/analytics/', filters);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching bid analytics:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch bid analytics'
            };
        }
    }
    
    /**
     * الحصول على بيانات لوحة التحكم الرئيسية
     * Get dashboard overview data
     * 
     * @returns {Promise<Object>} وعد يحتوي على بيانات لوحة التحكم
     */
    async getDashboardOverview() {
        try {
            const response = await api.get('dashboard/overview/');
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching dashboard overview:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch dashboard overview'
            };
        }
    }
    
    /**
     * الحصول على معلومات قسم معين في لوحة التحكم
     * Get dashboard section data
     * 
     * @param {string} section - اسم القسم (properties, auctions, etc.)
     * @returns {Promise<Object>} وعد يحتوي على بيانات القسم
     */
    async getDashboardSection(section) {
        if (!section) {
            return {
                success: false,
                error: 'Section name is required'
            };
        }
        
        try {
            const response = await api.get(`dashboard/section/${section}/`);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error fetching dashboard section ${section}:`, error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch dashboard section'
            };
        }
    }
    
    /**
     * الحصول على بيانات رسم بياني في لوحة التحكم
     * Get dashboard chart data
     * 
     * @param {string} chartType - نوع الرسم البياني
     * @returns {Promise<Object>} وعد يحتوي على بيانات الرسم البياني
     */
    async getDashboardChart(chartType) {
        if (!chartType) {
            return {
                success: false,
                error: 'Chart type is required'
            };
        }
        
        try {
            const response = await api.get(`dashboard/chart/${chartType}/`);
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error(`Error fetching dashboard chart ${chartType}:`, error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch dashboard chart'
            };
        }
    }
    
    /**
     * الحصول على الإحصائيات السريعة للوحة التحكم
     * Get dashboard quick statistics
     * 
     * @returns {Promise<Object>} وعد يحتوي على الإحصائيات السريعة
     */
    async getDashboardQuickStats() {
        try {
            const response = await api.get('dashboard/quick-stats/');
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching dashboard quick stats:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch dashboard quick stats'
            };
        }
    }
    
    /**
     * الحصول على النشاطات الأخيرة في لوحة التحكم
     * Get dashboard recent activity
     * 
     * @returns {Promise<Object>} وعد يحتوي على النشاطات الأخيرة
     */
    async getDashboardRecentActivity() {
        try {
            const response = await api.get('dashboard/recent-activity/');
            return {
                success: true,
                data: response.data || {}
            };
        } catch (error) {
            console.error('Error fetching dashboard recent activity:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to fetch dashboard recent activity'
            };
        }
    }
}

// Export a singleton instance
export default new AuctionService();