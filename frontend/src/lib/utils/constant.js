// src/lib/utils/constants.js
// ملف القيم الثابتة والدوال المساعدة - Constants and utilities file

/**
 * حالات العقارات
 * Property statuses
 */
export const PROPERTY_STATUS = {
    DRAFT: 'draft',               // مسودة
    PENDING_APPROVAL: 'pending_approval', // في انتظار الموافقة
    ACTIVE: 'active',             // نشط
    UNDER_CONTRACT: 'under_contract', // تحت التعاقد
    SOLD: 'sold',                 // مباع
    INACTIVE: 'inactive',         // غير نشط
    REJECTED: 'rejected',         // مرفوض
  };
  
  /**
   * أنواع العقارات
   * Property types
   */
  export const PROPERTY_TYPES = {
    LAND: 'land',                 // أرض
    APARTMENT: 'apartment',       // شقة
    VILLA: 'villa',               // فيلا
    COMMERCIAL: 'commercial',     // تجاري
    BUILDING: 'building',         // مبنى
    FARM: 'farm',                 // مزرعة
    INDUSTRIAL: 'industrial',     // صناعي
    OFFICE: 'office',             // مكتب
    RETAIL: 'retail',             // محل تجاري
    MIXED_USE: 'mixed_use',       // متعدد الاستخدامات
  };
  
  /**
   * حالات المزادات
   * Auction statuses
   */
  export const AUCTION_STATUS = {
    DRAFT: 'draft',               // مسودة
    PENDING: 'pending',           // قيد الانتظار
    ACTIVE: 'active',             // مفتوح
    EXTENDED: 'extended',         // ممدد
    CLOSED: 'closed',             // مغلق
    SOLD: 'sold',                 // مُباع
    CANCELLED: 'cancelled',       // ملغي
  };
  
  /**
   * أنواع المزادات
   * Auction types
   */
  export const AUCTION_TYPES = {
    PUBLIC: 'public',             // عام
    PRIVATE: 'private',           // خاص
    ONLINE: 'online',             // إلكتروني
    ONSITE: 'onsite',             // حضوري
    HYBRID: 'hybrid',             // مختلط
  };
  
  /**
   * حالات العطاءات (المزايدات)
   * Bid statuses
   */
  export const BID_STATUS = {
    PENDING: 'pending',           // معلق
    ACCEPTED: 'accepted',         // مقبول
    REJECTED: 'rejected',         // مرفوض
    WINNING: 'winning',           // فائز
    OUTBID: 'outbid',             // تم تجاوزه
    CANCELLED: 'cancelled',       // ملغي
  };
  
  /**
   * حالات العقود
   * Contract statuses
   */
  export const CONTRACT_STATUS = {
    DRAFT: 'draft',               // مسودة
    PENDING_REVIEW: 'pending_review', // قيد المراجعة
    PENDING_BUYER: 'pending_buyer', // بانتظار المشتري
    PENDING_SELLER: 'pending_seller', // بانتظار البائع
    PENDING_PAYMENT: 'pending_payment', // بانتظار الدفع
    SIGNED: 'signed',             // موقع
    ACTIVE: 'active',             // نشط
    COMPLETED: 'completed',       // مكتمل
    CANCELLED: 'cancelled',       // ملغى
    DISPUTED: 'disputed',         // متنازع عليه
  };
  
  /**
   * أنواع المستندات
   * Document types
   */
  export const DOCUMENT_TYPES = {
    DEED: 'deed',                 // صك ملكية
    INSPECTION: 'inspection',     // تقرير فحص
    APPRAISAL: 'appraisal',       // تقرير تقييم
    COASTAL_ASSESSMENT: 'coastal_assessment', // تقييم ساحلي
    LEGAL: 'legal',               // مستند قانوني
    CONTRACT: 'contract',         // عقد
    IDENTITY: 'identity',         // إثبات هوية
    FINANCIAL: 'financial',       // مستند مالي
    OTHER: 'other',               // أخرى
  };
  
  /**
   * حالات التحقق من المستندات
   * Document verification statuses
   */
  export const VERIFICATION_STATUS = {
    PENDING: 'pending',           // معلق
    VERIFIED: 'verified',         // تم التحقق
    REJECTED: 'rejected',         // مرفوض
  };
  
  /**
   * طرق الدفع
   * Payment methods
   */
  export const PAYMENT_METHODS = {
    BANK_TRANSFER: 'bank_transfer', // تحويل بنكي
    CASH: 'cash',                 // نقدي
    CHECK: 'check',               // شيك
    INSTALLMENT: 'installment',   // تقسيط
    ESCROW: 'escrow',             // ضمان
  };
  
  /**
   * الاستخدامات
   * Usage types
   */
  export const USAGE_TYPES = {
    RESIDENTIAL: 'residential',   // سكني
    COMMERCIAL: 'commercial',     // تجاري
    MIXED: 'mixed',               // مختلط
    INDUSTRIAL: 'industrial',     // صناعي
    AGRICULTURAL: 'agricultural', // زراعي
  };
  
  /**
   * الاتجاهات
   * Facing directions
   */
  export const FACING_DIRECTIONS = {
    NORTH: 'north',               // شمال
    EAST: 'east',                 // شرق
    SOUTH: 'south',               // جنوب
    WEST: 'west',                 // غرب
    NORTHEAST: 'northeast',       // شمال شرق
    SOUTHEAST: 'southeast',       // جنوب شرق
    SOUTHWEST: 'southwest',       // جنوب غرب
    NORTHWEST: 'northwest',       // شمال غرب
  };
  
  /**
   * حالات العقار
   * Property conditions
   */
  export const PROPERTY_CONDITIONS = {
    EXCELLENT: 'excellent',       // ممتاز
    VERY_GOOD: 'very_good',       // جيد جدا
    GOOD: 'good',                 // جيد
    FAIR: 'fair',                 // مقبول
    POOR: 'poor',                 // سيئ
    UNDER_CONSTRUCTION: 'under_construction', // تحت الإنشاء
    NEW: 'new',                   // جديد
  };
  
  /**
   * إعدادات التصفح (الصفحات)
   * Pagination settings
   */
  export const PAGINATION = {
    DEFAULT_PAGE_SIZE: 10,        // حجم الصفحة الافتراضي
    MAX_PAGE_SIZE: 50,            // أقصى حجم للصفحة
    DEFAULT_PAGE: 1,              // رقم الصفحة الافتراضي
  };
  
  /**
   * ألوان الحالات - لواجهة المستخدم
   * Status colors - for UI
   */
  export const STATUS_COLORS = {
    // Property & Auction Status Colors
    [PROPERTY_STATUS.ACTIVE]: 'status-success',
    [PROPERTY_STATUS.PENDING_APPROVAL]: 'status-warning',
    [PROPERTY_STATUS.UNDER_CONTRACT]: 'status-info',
    [PROPERTY_STATUS.SOLD]: 'cosmos-text-dim',
    [PROPERTY_STATUS.INACTIVE]: 'status-error',
    [PROPERTY_STATUS.REJECTED]: 'status-error',
    [PROPERTY_STATUS.DRAFT]: 'cosmos-text-muted',
    
    [AUCTION_STATUS.ACTIVE]: 'status-success',
    [AUCTION_STATUS.PENDING]: 'status-warning',
    [AUCTION_STATUS.EXTENDED]: 'primary-light',
    [AUCTION_STATUS.CLOSED]: 'cosmos-text-dim',
    [AUCTION_STATUS.SOLD]: 'status-success',
    [AUCTION_STATUS.CANCELLED]: 'status-error',
    [AUCTION_STATUS.DRAFT]: 'cosmos-text-muted',
    
    // Bid Status Colors
    [BID_STATUS.WINNING]: 'status-success',
    [BID_STATUS.OUTBID]: 'status-warning',
    [BID_STATUS.PENDING]: 'status-info',
    [BID_STATUS.ACCEPTED]: 'status-success',
    [BID_STATUS.REJECTED]: 'status-error',
    [BID_STATUS.CANCELLED]: 'cosmos-text-dim',
    
    // Contract Status Colors
    [CONTRACT_STATUS.ACTIVE]: 'status-success',
    [CONTRACT_STATUS.SIGNED]: 'status-success',
    [CONTRACT_STATUS.PENDING_REVIEW]: 'status-warning',
    [CONTRACT_STATUS.PENDING_BUYER]: 'status-info',
    [CONTRACT_STATUS.PENDING_SELLER]: 'status-info',
    [CONTRACT_STATUS.PENDING_PAYMENT]: 'status-warning',
    [CONTRACT_STATUS.COMPLETED]: 'status-success',
    [CONTRACT_STATUS.CANCELLED]: 'status-error',
    [CONTRACT_STATUS.DISPUTED]: 'status-error',
    [CONTRACT_STATUS.DRAFT]: 'cosmos-text-muted',
  };
  
  /**
   * أقصى حجم مسموح للملفات المرفوعة (بالبايت)
   * Maximum allowed file sizes for uploads (in bytes)
   */
  export const FILE_SIZE_LIMITS = {
    IMAGE: 5 * 1024 * 1024,       // صور: 5 ميجابايت
    DOCUMENT: 10 * 1024 * 1024,   // مستندات: 10 ميجابايت
    VIDEO: 100 * 1024 * 1024,     // فيديوهات: 100 ميجابايت
  };
  
  /**
   * أنواع الملفات المسموح بها
   * Allowed file types
   */
  export const ALLOWED_FILE_TYPES = {
    IMAGE: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    DOCUMENT: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    VIDEO: ['video/mp4', 'video/webm', 'video/quicktime'],
  };
  
  /**
   * القيم الافتراضية للتصفية
   * Default filter values
   */
  export const DEFAULT_FILTERS = {
    PROPERTIES: {
      status: PROPERTY_STATUS.ACTIVE,
      sort_by: 'created_at',
      order: 'desc',
      page: 1,
      page_size: PAGINATION.DEFAULT_PAGE_SIZE,
    },
    AUCTIONS: {
      status: AUCTION_STATUS.ACTIVE,
      sort_by: 'start_date',
      order: 'asc',
      page: 1,
      page_size: PAGINATION.DEFAULT_PAGE_SIZE,
    },
  };
  
  /**
   * خرائط المسارات الصحيحة للحالات
   * Valid status transition maps
   */
  export const VALID_STATUS_TRANSITIONS = {
    PROPERTY: {
      [PROPERTY_STATUS.DRAFT]: [PROPERTY_STATUS.PENDING_APPROVAL, PROPERTY_STATUS.INACTIVE],
      [PROPERTY_STATUS.PENDING_APPROVAL]: [PROPERTY_STATUS.ACTIVE, PROPERTY_STATUS.REJECTED],
      [PROPERTY_STATUS.ACTIVE]: [PROPERTY_STATUS.UNDER_CONTRACT, PROPERTY_STATUS.INACTIVE],
      [PROPERTY_STATUS.UNDER_CONTRACT]: [PROPERTY_STATUS.SOLD, PROPERTY_STATUS.ACTIVE],
      [PROPERTY_STATUS.INACTIVE]: [PROPERTY_STATUS.ACTIVE, PROPERTY_STATUS.DRAFT],
      [PROPERTY_STATUS.REJECTED]: [PROPERTY_STATUS.DRAFT],
      [PROPERTY_STATUS.SOLD]: [],
    },
    AUCTION: {
      [AUCTION_STATUS.DRAFT]: [AUCTION_STATUS.PENDING, AUCTION_STATUS.CANCELLED],
      [AUCTION_STATUS.PENDING]: [AUCTION_STATUS.ACTIVE, AUCTION_STATUS.CANCELLED],
      [AUCTION_STATUS.ACTIVE]: [AUCTION_STATUS.EXTENDED, AUCTION_STATUS.CLOSED, AUCTION_STATUS.CANCELLED],
      [AUCTION_STATUS.EXTENDED]: [AUCTION_STATUS.CLOSED, AUCTION_STATUS.CANCELLED],
      [AUCTION_STATUS.CLOSED]: [AUCTION_STATUS.SOLD, AUCTION_STATUS.CANCELLED],
      [AUCTION_STATUS.SOLD]: [],
      [AUCTION_STATUS.CANCELLED]: [],
    },
    CONTRACT: {
      [CONTRACT_STATUS.DRAFT]: [CONTRACT_STATUS.PENDING_REVIEW, CONTRACT_STATUS.CANCELLED],
      [CONTRACT_STATUS.PENDING_REVIEW]: [CONTRACT_STATUS.PENDING_BUYER, CONTRACT_STATUS.PENDING_SELLER, CONTRACT_STATUS.CANCELLED],
      [CONTRACT_STATUS.PENDING_BUYER]: [CONTRACT_STATUS.PENDING_SELLER, CONTRACT_STATUS.SIGNED, CONTRACT_STATUS.CANCELLED],
      [CONTRACT_STATUS.PENDING_SELLER]: [CONTRACT_STATUS.PENDING_BUYER, CONTRACT_STATUS.SIGNED, CONTRACT_STATUS.CANCELLED],
      [CONTRACT_STATUS.SIGNED]: [CONTRACT_STATUS.PENDING_PAYMENT, CONTRACT_STATUS.ACTIVE, CONTRACT_STATUS.DISPUTED],
      [CONTRACT_STATUS.PENDING_PAYMENT]: [CONTRACT_STATUS.ACTIVE, CONTRACT_STATUS.CANCELLED],
      [CONTRACT_STATUS.ACTIVE]: [CONTRACT_STATUS.COMPLETED, CONTRACT_STATUS.DISPUTED],
      [CONTRACT_STATUS.COMPLETED]: [CONTRACT_STATUS.DISPUTED],
      [CONTRACT_STATUS.DISPUTED]: [CONTRACT_STATUS.ACTIVE, CONTRACT_STATUS.CANCELLED, CONTRACT_STATUS.COMPLETED],
      [CONTRACT_STATUS.CANCELLED]: [],
    },
  };
  
  /**
   * وحدات القياس
   * Measurement units
   */
  export const UNITS = {
    AREA: 'm²',                   // متر مربع
    CURRENCY: 'SAR',              // ريال سعودي
    DISTANCE: 'km',               // كيلومتر
  };
  
  /**
   * مخطط أيقونات حالات العقارات
   * Property status icon map
   */
  export const PROPERTY_STATUS_ICONS = {
    [PROPERTY_STATUS.DRAFT]: 'pencil-square',
    [PROPERTY_STATUS.PENDING_APPROVAL]: 'clock',
    [PROPERTY_STATUS.ACTIVE]: 'check-circle',
    [PROPERTY_STATUS.UNDER_CONTRACT]: 'document-text',
    [PROPERTY_STATUS.SOLD]: 'badge-check',
    [PROPERTY_STATUS.INACTIVE]: 'x-circle',
    [PROPERTY_STATUS.REJECTED]: 'ban',
  };
  
  /**
   * مخطط أيقونات أنواع العقارات
   * Property type icon map
   */
  export const PROPERTY_TYPE_ICONS = {
    [PROPERTY_TYPES.LAND]: 'map',
    [PROPERTY_TYPES.APARTMENT]: 'office-building',
    [PROPERTY_TYPES.VILLA]: 'home',
    [PROPERTY_TYPES.COMMERCIAL]: 'shopping-bag',
    [PROPERTY_TYPES.BUILDING]: 'office-building',
    [PROPERTY_TYPES.FARM]: 'globe',
    [PROPERTY_TYPES.INDUSTRIAL]: 'cube',
    [PROPERTY_TYPES.OFFICE]: 'desktop-computer',
    [PROPERTY_TYPES.RETAIL]: 'shopping-cart',
    [PROPERTY_TYPES.MIXED_USE]: 'collection',
  };
  
  /**
   * مخطط أيقونات حالات المزادات
   * Auction status icon map
   */
  export const AUCTION_STATUS_ICONS = {
    [AUCTION_STATUS.DRAFT]: 'pencil-square',
    [AUCTION_STATUS.PENDING]: 'clock',
    [AUCTION_STATUS.ACTIVE]: 'play',
    [AUCTION_STATUS.EXTENDED]: 'clock',
    [AUCTION_STATUS.CLOSED]: 'lock-closed',
    [AUCTION_STATUS.SOLD]: 'badge-check',
    [AUCTION_STATUS.CANCELLED]: 'x-circle',
  };
  
  /**
   * مخطط الخصائص للعقارات
   * Property features icon map
   */
  export const FEATURE_ICONS = {
    bedrooms: 'bed',
    bathrooms: 'bath',
    area: 'area',
    parking: 'car',
    air_conditioning: 'sun',
    heating: 'fire',
    pool: 'water',
    garden: 'leaf',
    elevator: 'elevator',
    security_system: 'shield-check',
    balcony: 'view',
    terrace: 'outdoor',
    fireplace: 'fire',
    storage: 'archive',
    furnished: 'home',
    pet_friendly: 'paw',
    gym: 'exercise',
    wifi: 'wifi',
    washing_machine: 'laundry',
    dishwasher: 'dish',
    microwave: 'microwave',
    refrigerator: 'fridge',
    oven: 'oven',
  };
  
  /**
   * التنسيقات الزمنية
   * Date/time formats
   */
  export const DATE_FORMATS = {
    FULL_DATE: { day: 'numeric', month: 'long', year: 'numeric' },
    SHORT_DATE: { day: 'numeric', month: 'short', year: 'numeric' },
    TIME_ONLY: { hour: '2-digit', minute: '2-digit' },
    DATE_TIME: { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' },
    RELATIVE: 'relative',
  };
  
  /**
   * تنسيقات العملة
   * Currency formats
   */
  export const CURRENCY_FORMATS = {
    DEFAULT: { style: 'currency', currency: UNITS.CURRENCY, minimumFractionDigits: 0, maximumFractionDigits: 0 },
    WITH_DECIMALS: { style: 'currency', currency: UNITS.CURRENCY, minimumFractionDigits: 2, maximumFractionDigits: 2 },
    COMPACT: { style: 'currency', currency: UNITS.CURRENCY, notation: 'compact', minimumFractionDigits: 0, maximumFractionDigits: 1 },
  };
  
  // ====================
  // دوال مساعدة - Utility Functions
  // ====================
  
  /**
   * التحقق من صحة انتقال الحالة
   * Validate status transition
   * 
   * @param {string} entityType - نوع الكيان (PROPERTY, AUCTION, CONTRACT)
   * @param {string} currentStatus - الحالة الحالية
   * @param {string} newStatus - الحالة الجديدة
   * @returns {boolean} صحة الانتقال
   */
  export function isValidStatusTransition(entityType, currentStatus, newStatus) {
    if (!VALID_STATUS_TRANSITIONS[entityType]) {
      return false;
    }
    
    if (!VALID_STATUS_TRANSITIONS[entityType][currentStatus]) {
      return false;
    }
    
    return VALID_STATUS_TRANSITIONS[entityType][currentStatus].includes(newStatus);
  }
  
  /**
   * الحصول على لون الحالة
   * Get status color
   * 
   * @param {string} status - الحالة
   * @returns {string} لون CSS للحالة
   */
  export function getStatusColor(status) {
    return STATUS_COLORS[status] || 'cosmos-text-muted';
  }
  
  /**
   * الحصول على اسم أيقونة الحالة
   * Get status icon name
   * 
   * @param {string} entityType - نوع الكيان (PROPERTY, AUCTION)
   * @param {string} status - الحالة
   * @returns {string} اسم الأيقونة
   */
  export function getStatusIcon(entityType, status) {
    if (entityType === 'PROPERTY') {
      return PROPERTY_STATUS_ICONS[status] || 'question-mark-circle';
    } else if (entityType === 'AUCTION') {
      return AUCTION_STATUS_ICONS[status] || 'question-mark-circle';
    }
    return 'question-mark-circle';
  }
  
  /**
   * الحصول على اسم أيقونة نوع العقار
   * Get property type icon name
   * 
   * @param {string} propertyType - نوع العقار
   * @returns {string} اسم الأيقونة
   */
  export function getPropertyTypeIcon(propertyType) {
    return PROPERTY_TYPE_ICONS[propertyType] || 'home';
  }
  
  /**
   * الحصول على اسم أيقونة الخاصية
   * Get feature icon name
   * 
   * @param {string} feature - الخاصية
   * @returns {string} اسم الأيقونة
   */
  export function getFeatureIcon(feature) {
    return FEATURE_ICONS[feature] || 'plus-circle';
  }
  
  /**
   * التحقق من صحة نوع الملف
   * Validate file type
   * 
   * @param {File} file - الملف
   * @param {string} type - نوع الملف (IMAGE, DOCUMENT, VIDEO)
   * @returns {boolean} صحة نوع الملف
   */
  export function isValidFileType(file, type) {
    if (!file || !file.type) return false;
    return ALLOWED_FILE_TYPES[type]?.includes(file.type) || false;
  }
  
  /**
   * التحقق من صحة حجم الملف
   * Validate file size
   * 
   * @param {File} file - الملف
   * @param {string} type - نوع الملف (IMAGE, DOCUMENT, VIDEO)
   * @returns {boolean} صحة حجم الملف
   */
  export function isValidFileSize(file, type) {
    if (!file || typeof file.size !== 'number') return false;
    return file.size <= FILE_SIZE_LIMITS[type];
  }
  
  /**
   * الحصول على الوقت المتبقي بتنسيق مقروء
   * Get formatted remaining time
   * 
   * @param {number} seconds - الثواني المتبقية
   * @returns {string} الوقت المتبقي بتنسيق مقروء
   */
  export function formatRemainingTime(seconds) {
    if (seconds <= 0) return '00:00:00';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    
    if (days > 0) {
      return `${days}d ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
  
  /**
   * تقصير النص مع إضافة علامات الحذف
   * Truncate text with ellipsis
   * 
   * @param {string} text - النص
   * @param {number} maxLength - الحد الأقصى للطول
   * @returns {string} النص المقتصر
   */
  export function truncateText(text, maxLength = 100) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }
  
  /**
   * تنسيق المساحة
   * Format area
   * 
   * @param {number} area - المساحة
   * @param {boolean} withUnit - إضافة وحدة القياس
   * @returns {string} المساحة المنسقة
   */
  export function formatArea(area, withUnit = true) {
    if (area === null || area === undefined) return '';
    return withUnit ? `${area} ${UNITS.AREA}` : `${area}`;
  }
  
  /**
   * تحويل سلسلة snake_case إلى Title Case
   * Convert snake_case to Title Case
   * 
   * @param {string} text - النص بتنسيق snake_case
   * @returns {string} النص بتنسيق Title Case
   */
  export function formatDisplayName(text) {
    if (!text) return '';
    return text
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  /**
   * الحصول على فئة العمر للعقار
   * Get property age category
   * 
   * @param {number} yearBuilt - سنة البناء
   * @returns {string} فئة العمر
   */
  export function getPropertyAgeCategory(yearBuilt) {
    if (!yearBuilt) return 'unknown';
    
    const currentYear = new Date().getFullYear();
    const age = currentYear - yearBuilt;
    
    if (age <= 1) return 'new';
    if (age <= 5) return 'recent';
    if (age <= 10) return 'established';
    if (age <= 20) return 'mature';
    if (age <= 50) return 'old';
    return 'historic';
  }
  
  /**
   * اسم الملف ليكون آمنًا في URL
   * Make filename URL-safe
   * 
   * @param {string} filename - اسم الملف
   * @returns {string} اسم الملف الآمن
   */
  export function safeFilename(filename) {
    if (!filename) return '';
    return filename
      .toLowerCase()
      .replace(/[^a-z0-9.]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }
  
  export default {
    PROPERTY_STATUS,
    PROPERTY_TYPES,
    AUCTION_STATUS,
    AUCTION_TYPES,
    BID_STATUS,
    CONTRACT_STATUS,
    DOCUMENT_TYPES,
    VERIFICATION_STATUS,
    PAYMENT_METHODS,
    USAGE_TYPES,
    FACING_DIRECTIONS,
    PROPERTY_CONDITIONS,
    PAGINATION,
    STATUS_COLORS,
    FILE_SIZE_LIMITS,
    ALLOWED_FILE_TYPES,
    DEFAULT_FILTERS,
    VALID_STATUS_TRANSITIONS,
    UNITS,
    PROPERTY_STATUS_ICONS,
    PROPERTY_TYPE_ICONS,
    AUCTION_STATUS_ICONS,
    FEATURE_ICONS,
    DATE_FORMATS,
    CURRENCY_FORMATS,
    isValidStatusTransition,
    getStatusColor,
    getStatusIcon,
    getPropertyTypeIcon,
    getFeatureIcon,
    isValidFileType,
    isValidFileSize,
    formatRemainingTime,
    truncateText,
    formatArea,
    formatDisplayName,
    getPropertyAgeCategory,
    safeFilename,
  };