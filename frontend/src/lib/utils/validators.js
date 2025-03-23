// src/lib/utils/validators.js
// التحقق من صحة البيانات - Data Validation Utilities

/**
 * مجموعة من وظائف التحقق للتأكد من صحة البيانات المختلفة في النظام
 * Collection of validation functions to verify different data in the system
 */

// ========================
// التحقق العام - General Validation
// ========================

/**
 * التحقق من وجود قيمة (غير فارغة)
 * Check if a value is present (not empty)
 * 
 * @param {*} value - القيمة للتحقق منها
 * @returns {boolean} نتيجة التحقق
 */
export function isNotEmpty(value) {
    if (value === undefined || value === null) return false;
    if (typeof value === 'string') return value.trim().length > 0;
    if (typeof value === 'object') {
      if (Array.isArray(value)) return value.length > 0;
      return Object.keys(value).length > 0;
    }
    return true;
  }
  
  /**
   * التحقق من أن القيمة رقم صالح
   * Check if a value is a valid number
   * 
   * @param {*} value - القيمة للتحقق منها
   * @param {Object} options - خيارات إضافية
   * @param {number} options.min - الحد الأدنى (اختياري)
   * @param {number} options.max - الحد الأقصى (اختياري)
   * @param {boolean} options.allowZero - السماح بالصفر (اختياري)
   * @param {boolean} options.allowNegative - السماح بالأرقام السالبة (اختياري)
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidNumber(value, options = {}) {
    // Try to convert to number if it's a string
    if (typeof value === 'string') {
      value = parseFloat(value);
    }
    
    // Check if it's a valid number
    if (typeof value !== 'number' || isNaN(value)) {
      return false;
    }
    
    // Check minimum and maximum if provided
    if (options.min !== undefined && value < options.min) {
      return false;
    }
    if (options.max !== undefined && value > options.max) {
      return false;
    }
    
    // Check for zero
    if (value === 0 && options.allowZero === false) {
      return false;
    }
    
    // Check for negative values
    if (value < 0 && options.allowNegative === false) {
      return false;
    }
    
    return true;
  }
  
  /**
   * التحقق من صحة تنسيق البريد الإلكتروني
   * Validate email format
   * 
   * @param {string} email - البريد الإلكتروني للتحقق منه
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidEmail(email) {
    if (!email || typeof email !== 'string') return false;
    
    // Regular expression for basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  /**
   * التحقق من طول النص
   * Validate text length
   * 
   * @param {string} text - النص للتحقق منه
   * @param {Object} options - خيارات التحقق
   * @param {number} options.min - الحد الأدنى للطول (اختياري)
   * @param {number} options.max - الحد الأقصى للطول (اختياري)
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidLength(text, options = {}) {
    if (typeof text !== 'string') return false;
    
    const length = text.trim().length;
    
    if (options.min !== undefined && length < options.min) {
      return false;
    }
    if (options.max !== undefined && length > options.max) {
      return false;
    }
    
    return true;
  }
  
  /**
   * التحقق من تطابق القيم
   * Check if values match
   * 
   * @param {*} value1 - القيمة الأولى
   * @param {*} value2 - القيمة الثانية
   * @returns {boolean} نتيجة التحقق
   */
  export function doValuesMatch(value1, value2) {
    return value1 === value2;
  }
  
  /**
   * التحقق من صحة التاريخ
   * Validate date
   * 
   * @param {Date|string} date - التاريخ للتحقق منه
   * @param {Object} options - خيارات إضافية
   * @param {Date|string} options.minDate - الحد الأدنى للتاريخ (اختياري)
   * @param {Date|string} options.maxDate - الحد الأقصى للتاريخ (اختياري)
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidDate(date, options = {}) {
    let dateObj;
    
    // Convert to Date object if it's a string
    if (typeof date === 'string') {
      dateObj = new Date(date);
    } else if (date instanceof Date) {
      dateObj = date;
    } else {
      return false;
    }
    
    // Check if date is valid
    if (isNaN(dateObj.getTime())) {
      return false;
    }
    
    // Check minimum date if provided
    if (options.minDate) {
      const minDate = options.minDate instanceof Date 
        ? options.minDate 
        : new Date(options.minDate);
      
      if (isNaN(minDate.getTime()) || dateObj < minDate) {
        return false;
      }
    }
    
    // Check maximum date if provided
    if (options.maxDate) {
      const maxDate = options.maxDate instanceof Date 
        ? options.maxDate 
        : new Date(options.maxDate);
      
      if (isNaN(maxDate.getTime()) || dateObj > maxDate) {
        return false;
      }
    }
    
    return true;
  }
  
  // ========================
  // التحقق من العقارات - Property Validation
  // ========================
  
  /**
   * التحقق من صحة بيانات العقار الأساسية
   * Validate basic property data
   * 
   * @param {Object} property - بيانات العقار
   * @returns {Object} نتائج التحقق { isValid, errors }
   */
  export function validatePropertyBasics(property) {
    const errors = {};
    
    // Check required fields
    if (!isNotEmpty(property.title)) {
      errors.title = 'Property title is required';
    } else if (!isValidLength(property.title, { min: 3, max: 255 })) {
      errors.title = 'Property title must be between 3 and 255 characters';
    }
    
    if (!isNotEmpty(property.property_type)) {
      errors.property_type = 'Property type is required';
    }
    
    if (!isNotEmpty(property.address)) {
      errors.address = 'Address is required';
    }
    
    if (!isNotEmpty(property.city)) {
      errors.city = 'City is required';
    }
    
    if (!isNotEmpty(property.district)) {
      errors.district = 'District is required';
    }
    
    // Check numeric fields
    if (!isValidNumber(property.area, { min: 0.1 })) {
      errors.area = 'Property area must be a positive number';
    }
    
    if (property.estimated_value !== undefined && 
        !isValidNumber(property.estimated_value, { min: 1 })) {
      errors.estimated_value = 'Estimated value must be a positive number';
    }
    
    if (property.bedrooms !== undefined && 
        !isValidNumber(property.bedrooms, { min: 0, allowZero: true })) {
      errors.bedrooms = 'Bedrooms must be a non-negative number';
    }
    
    if (property.bathrooms !== undefined && 
        !isValidNumber(property.bathrooms, { min: 0, allowZero: true })) {
      errors.bathrooms = 'Bathrooms must be a non-negative number';
    }
    
    // Check coordinates if provided
    if (property.latitude !== undefined || property.longitude !== undefined) {
      if (!isValidCoordinates(property.latitude, property.longitude)) {
        errors.coordinates = 'Invalid coordinates';
      }
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }
  
  /**
   * التحقق من صحة الإحداثيات الجغرافية
   * Validate geographic coordinates
   * 
   * @param {number|string} latitude - خط العرض
   * @param {number|string} longitude - خط الطول
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidCoordinates(latitude, longitude) {
    // Convert to numbers if they are strings
    if (typeof latitude === 'string') latitude = parseFloat(latitude);
    if (typeof longitude === 'string') longitude = parseFloat(longitude);
    
    // Check if both are valid numbers
    if (typeof latitude !== 'number' || isNaN(latitude) ||
        typeof longitude !== 'number' || isNaN(longitude)) {
      return false;
    }
    
    // Check if within valid ranges
    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      return false;
    }
    
    return true;
  }
  
  /**
   * التحقق من صحة سعر العقار
   * Validate property price
   * 
   * @param {number|string} price - السعر
   * @param {Object} options - خيارات إضافية
   * @param {number} options.min - الحد الأدنى للسعر (اختياري)
   * @param {number} options.max - الحد الأقصى للسعر (اختياري)
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidPropertyPrice(price, options = {}) {
    return isValidNumber(price, { 
      min: options.min || 1, 
      max: options.max,
      allowZero: false,
      allowNegative: false
    });
  }
  
  // ========================
  // التحقق من المزادات - Auction Validation
  // ========================
  
  /**
   * التحقق من صحة بيانات المزاد الأساسية
   * Validate basic auction data
   * 
   * @param {Object} auction - بيانات المزاد
   * @returns {Object} نتائج التحقق { isValid, errors }
   */
  export function validateAuctionBasics(auction) {
    const errors = {};
    
    // Check required fields
    if (!isNotEmpty(auction.title)) {
      errors.title = 'Auction title is required';
    } else if (!isValidLength(auction.title, { min: 3, max: 255 })) {
      errors.title = 'Auction title must be between 3 and 255 characters';
    }
    
    if (!isNotEmpty(auction.property_id)) {
      errors.property_id = 'Property ID is required';
    }
    
    if (!isNotEmpty(auction.auction_type)) {
      errors.auction_type = 'Auction type is required';
    }
    
    // Check dates
    const now = new Date();
    
    if (!isNotEmpty(auction.start_date)) {
      errors.start_date = 'Start date is required';
    } else if (!isValidDate(auction.start_date)) {
      errors.start_date = 'Invalid start date';
    }
    
    if (!isNotEmpty(auction.end_date)) {
      errors.end_date = 'End date is required';
    } else if (!isValidDate(auction.end_date)) {
      errors.end_date = 'Invalid end date';
    }
    
    // Check start date is after now
    if (!errors.start_date && isValidDate(auction.start_date)) {
      const startDate = new Date(auction.start_date);
      if (startDate < now) {
        errors.start_date = 'Start date must be in the future';
      }
    }
    
    // Check end date is after start date
    if (!errors.start_date && !errors.end_date && 
        isValidDate(auction.start_date) && isValidDate(auction.end_date)) {
      const startDate = new Date(auction.start_date);
      const endDate = new Date(auction.end_date);
      if (endDate <= startDate) {
        errors.end_date = 'End date must be after start date';
      }
    }
    
    // Check numeric fields
    if (!isValidNumber(auction.starting_price, { min: 1 })) {
      errors.starting_price = 'Starting price must be a positive number';
    }
    
    if (auction.reserve_price !== undefined) {
      if (!isValidNumber(auction.reserve_price, { min: 1 })) {
        errors.reserve_price = 'Reserve price must be a positive number';
      } else if (auction.starting_price !== undefined && 
                 auction.reserve_price < auction.starting_price) {
        errors.reserve_price = 'Reserve price must be greater than or equal to starting price';
      }
    }
    
    if (!isValidNumber(auction.min_bid_increment, { min: 0.01 })) {
      errors.min_bid_increment = 'Minimum bid increment must be a positive number';
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }
  
  /**
   * التحقق من صحة قيمة المزايدة
   * Validate bid amount
   * 
   * @param {number|string} bidAmount - قيمة المزايدة
   * @param {number|string} currentBid - المزايدة الحالية
   * @param {number|string} minIncrement - الحد الأدنى للزيادة
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidBidAmount(bidAmount, currentBid, minIncrement) {
    // Convert to numbers if they are strings
    if (typeof bidAmount === 'string') bidAmount = parseFloat(bidAmount);
    if (typeof currentBid === 'string') currentBid = parseFloat(currentBid);
    if (typeof minIncrement === 'string') minIncrement = parseFloat(minIncrement);
    
    // Check if all are valid numbers
    if (typeof bidAmount !== 'number' || isNaN(bidAmount) ||
        typeof currentBid !== 'number' || isNaN(currentBid) ||
        typeof minIncrement !== 'number' || isNaN(minIncrement)) {
      return false;
    }
    
    // Check if bid amount is positive
    if (bidAmount <= 0) {
      return false;
    }
    
    // Check if bid amount is greater than current bid + minimum increment
    const minimumAllowedBid = currentBid + minIncrement;
    if (bidAmount < minimumAllowedBid) {
      return false;
    }
    
    return true;
  }
  
  /**
   * التحقق من إمكانية تعديل حالة المزاد
   * Check if auction status can be changed
   * 
   * @param {string} currentStatus - الحالة الحالية
   * @param {string} newStatus - الحالة الجديدة
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidAuctionStatusTransition(currentStatus, newStatus) {
    // Define valid status transitions
    const validTransitions = {
      'draft': ['pending', 'cancelled'],
      'pending': ['active', 'cancelled'],
      'active': ['extended', 'closed', 'cancelled'],
      'extended': ['closed', 'cancelled'],
      'closed': ['sold', 'cancelled'],
      'sold': [],  // No transitions allowed from sold
      'cancelled': []  // No transitions allowed from cancelled
    };
    
    // Check if current status exists in the valid transitions map
    if (!validTransitions.hasOwnProperty(currentStatus)) {
      return false;
    }
    
    // Check if new status is in the list of valid transitions for the current status
    return validTransitions[currentStatus].includes(newStatus);
  }
  
  // ========================
  // التحقق من الملفات - File Validation
  // ========================
  
  /**
   * التحقق من صحة الملف
   * Validate file
   * 
   * @param {File} file - الملف للتحقق منه
   * @param {Object} options - خيارات التحقق
   * @param {string[]} options.allowedTypes - أنواع الملفات المسموح بها (اختياري)
   * @param {number} options.maxSize - الحد الأقصى لحجم الملف بالبايت (اختياري)
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidFile(file, options = {}) {
    // Check if it's a valid File object
    if (!file || !(file instanceof File)) {
      return false;
    }
    
    // Check file type if allowedTypes is provided
    if (options.allowedTypes && options.allowedTypes.length > 0) {
      const fileType = file.type.toLowerCase();
      const fileExtension = file.name.split('.').pop().toLowerCase();
      
      // Check if the file type or extension is in the allowed types
      const isAllowedType = options.allowedTypes.some(type => {
        // Check MIME type (e.g., 'image/jpeg')
        if (fileType === type.toLowerCase()) {
          return true;
        }
        
        // Check extension (e.g., 'jpg', 'pdf')
        const extensionToCheck = type.startsWith('.') ? type.substring(1).toLowerCase() : type.toLowerCase();
        return fileExtension === extensionToCheck;
      });
      
      if (!isAllowedType) {
        return false;
      }
    }
    
    // Check file size if maxSize is provided
    if (options.maxSize && file.size > options.maxSize) {
      return false;
    }
    
    return true;
  }
  
  /**
   * التحقق من صحة ملف صورة
   * Validate image file
   * 
   * @param {File} file - ملف الصورة للتحقق منه
   * @param {Object} options - خيارات إضافية
   * @param {number} options.maxSize - الحد الأقصى لحجم الملف بالبايت (اختياري، الافتراضي 5MB)
   * @param {number} options.minWidth - الحد الأدنى للعرض بالبكسل (اختياري)
   * @param {number} options.minHeight - الحد الأدنى للارتفاع بالبكسل (اختياري)
   * @returns {Promise<Object>} وعد يحتوي على نتائج التحقق { isValid, error }
   */
  export function validateImageFile(file, options = {}) {
    return new Promise((resolve) => {
      // Set default max size to 5MB if not provided
      const maxSize = options.maxSize || 5 * 1024 * 1024;
      
      // Allowed image types
      const allowedTypes = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/svg+xml'
      ];
      
      // Basic file validation
      if (!isValidFile(file, { allowedTypes, maxSize })) {
        if (file.size > maxSize) {
          resolve({ isValid: false, error: 'Image size exceeds the maximum allowed size' });
        } else {
          resolve({ isValid: false, error: 'Invalid image file type' });
        }
        return;
      }
      
      // If min dimensions are specified, check image dimensions
      if (options.minWidth || options.minHeight) {
        const img = new Image();
        const objectUrl = URL.createObjectURL(file);
        
        img.onload = () => {
          URL.revokeObjectURL(objectUrl);
          
          if ((options.minWidth && img.width < options.minWidth) || 
              (options.minHeight && img.height < options.minHeight)) {
            resolve({
              isValid: false,
              error: `Image dimensions too small. Required minimum: ${options.minWidth || 0}x${options.minHeight || 0} pixels`
            });
          } else {
            resolve({ isValid: true });
          }
        };
        
        img.onerror = () => {
          URL.revokeObjectURL(objectUrl);
          resolve({ isValid: false, error: 'Invalid image file' });
        };
        
        img.src = objectUrl;
      } else {
        // No dimension requirements, so image is valid
        resolve({ isValid: true });
      }
    });
  }
  
  /**
   * التحقق من صحة ملف مستند
   * Validate document file
   * 
   * @param {File} file - ملف المستند للتحقق منه
   * @param {Object} options - خيارات إضافية
   * @param {number} options.maxSize - الحد الأقصى لحجم الملف بالبايت (اختياري، الافتراضي 10MB)
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidDocumentFile(file, options = {}) {
    // Set default max size to 10MB if not provided
    const maxSize = options.maxSize || 10 * 1024 * 1024;
    
    // Allowed document types
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/plain',
      'application/rtf',
      '.pdf',
      '.doc',
      '.docx',
      '.xls',
      '.xlsx',
      '.txt',
      '.rtf'
    ];
    
    return isValidFile(file, { allowedTypes, maxSize });
  }
  
  // ========================
  // تحقق من بيانات المستخدم - User Data Validation
  // ========================
  
  /**
   * التحقق من صحة بيانات المستخدم
   * Validate user data
   * 
   * @param {Object} userData - بيانات المستخدم
   * @returns {Object} نتائج التحقق { isValid, errors }
   */
  export function validateUserData(userData) {
    const errors = {};
    
    // Check required fields
    if (!isNotEmpty(userData.email)) {
      errors.email = 'Email is required';
    } else if (!isValidEmail(userData.email)) {
      errors.email = 'Invalid email format';
    }
    
    if (!isNotEmpty(userData.first_name)) {
      errors.first_name = 'First name is required';
    }
    
    if (!isNotEmpty(userData.last_name)) {
      errors.last_name = 'Last name is required';
    }
    
    // Check password if provided
    if (userData.password !== undefined) {
      if (!isValidLength(userData.password, { min: 8 })) {
        errors.password = 'Password must be at least 8 characters';
      }
      
      // Check password confirmation if provided
      if (userData.password_confirm !== undefined && 
          !doValuesMatch(userData.password, userData.password_confirm)) {
        errors.password_confirm = 'Passwords do not match';
      }
    }
    
    // Check phone number if provided
    if (userData.phone_number !== undefined && userData.phone_number !== '') {
      if (!isValidPhoneNumber(userData.phone_number)) {
        errors.phone_number = 'Invalid phone number format';
      }
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }
  
  /**
   * التحقق من صحة رقم الهاتف
   * Validate phone number
   * 
   * @param {string} phoneNumber - رقم الهاتف
   * @returns {boolean} نتيجة التحقق
   */
  export function isValidPhoneNumber(phoneNumber) {
    if (!phoneNumber || typeof phoneNumber !== 'string') return false;
    
    // Remove spaces, dashes, parentheses
    const cleaned = phoneNumber.replace(/\s+|-|\(|\)/g, '');
    
    // Check if it's numeric and has minimum length
    if (!/^\+?[0-9]{8,15}$/.test(cleaned)) {
      return false;
    }
    
    return true;
  }
  
  /**
   * التحقق من كلمة المرور وقوتها
   * Validate password and check strength
   * 
   * @param {string} password - كلمة المرور
   * @returns {Object} نتائج التحقق { isValid, strength, message }
   */
  export function validatePassword(password) {
    if (!password || typeof password !== 'string') {
      return {
        isValid: false,
        strength: 0,
        message: 'Password is required'
      };
    }
    
    // Check minimum length
    if (password.length < 8) {
      return {
        isValid: false,
        strength: 1,
        message: 'Password must be at least 8 characters'
      };
    }
    
    // Calculate password strength
    let strength = 0;
    
    // Has lowercase letters
    if (/[a-z]/.test(password)) strength++;
    
    // Has uppercase letters
    if (/[A-Z]/.test(password)) strength++;
    
    // Has numbers
    if (/[0-9]/.test(password)) strength++;
    
    // Has special characters
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    // Determine message based on strength
    let message;
    if (strength === 1) {
      message = 'Weak password';
    } else if (strength === 2) {
      message = 'Fair password';
    } else if (strength === 3) {
      message = 'Good password';
    } else {
      message = 'Strong password';
    }
    
    return {
      isValid: true,
      strength,
      message
    };
  }
  
  // ========================
  // وظائف إضافية - Additional Utilities
  // ========================
  
  /**
   * تنقية بيانات النموذج قبل الإرسال
   * Sanitize form data before submission
   * 
   * @param {Object} formData - بيانات النموذج
   * @returns {Object} البيانات المنقاة
   */
  export function sanitizeFormData(formData) {
    const sanitized = {};
    
    // Process each field
    for (const [key, value] of Object.entries(formData)) {
      // Skip null or undefined values
      if (value === null || value === undefined) continue;
      
      // Trim strings
      if (typeof value === 'string') {
        sanitized[key] = value.trim();
        continue;
      }
      
      // Convert empty strings to null for specific fields
      if (typeof value === 'string' && value.trim() === '' && 
          ['price', 'area', 'bedrooms', 'bathrooms'].includes(key)) {
        sanitized[key] = null;
        continue;
      }
      
      // Convert string numbers to actual numbers
      if (typeof value === 'string' && 
          ['price', 'area', 'bedrooms', 'bathrooms', 'starting_price', 'reserve_price', 'min_bid_increment'].includes(key) && 
          !isNaN(parseFloat(value))) {
        sanitized[key] = parseFloat(value);
        continue;
      }
      
      // Default: keep original value
      sanitized[key] = value;
    }
    
    return sanitized;
  }
  
  /**
   * تنسيق أخطاء التحقق لعرضها
   * Format validation errors for display
   * 
   * @param {Object} errors - أخطاء التحقق
   * @param {string} fieldPrefix - بادئة لحقول النموذج (اختياري)
   * @returns {Array} مصفوفة من رسائل الخطأ مع معرفات الحقول
   */
  export function formatValidationErrors(errors, fieldPrefix = '') {
    return Object.entries(errors).map(([field, message]) => ({
      field: fieldPrefix ? `${fieldPrefix}.${field}` : field,
      message
    }));
  }
  
  /**
   * دمج نتائج التحقق المتعددة
   * Merge multiple validation results
   * 
   * @param {...Object} validationResults - نتائج التحقق المراد دمجها
   * @returns {Object} نتائج التحقق المدمجة { isValid, errors }
   */
  export function mergeValidationResults(...validationResults) {
    const mergedErrors = {};
    let isValid = true;
    
    for (const result of validationResults) {
      if (!result.isValid) {
        isValid = false;
        
        // Merge error messages
        Object.assign(mergedErrors, result.errors);
      }
    }
    
    return {
      isValid,
      errors: mergedErrors
    };
  }