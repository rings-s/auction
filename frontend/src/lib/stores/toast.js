// src/lib/stores/toastStore.js
// مخزن الإشعارات - Toast Notification Store

import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

/**
 * أنواع الإشعارات
 * Toast notification types
 */
export const TOAST_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info'
};

/**
 * إنشاء مخزن الإشعارات
 * Create toast store
 */
function createToastStore() {
    // المخزن الأساسي: مصفوفة من الإشعارات
    // Base store: array of toasts
    const { subscribe, update } = writable([]);

    // معرف فريد للإشعارات
    // Unique ID counter for toasts
    let nextId = 1;

    /**
     * إضافة إشعار جديد
     * Add a new toast notification
     *
     * @param {Object} toastOptions - خيارات الإشعار
     * @param {string} toastOptions.message - نص الإشعار
     * @param {string} [toastOptions.type=TOAST_TYPES.INFO] - نوع الإشعار
     * @param {string} [toastOptions.title] - عنوان الإشعار (اختياري)
     * @param {number} [toastOptions.duration=5000] - مدة ظهور الإشعار بالمللي ثانية
     * @param {boolean} [toastOptions.dismissable=true] - هل يمكن إغلاق الإشعار يدويًا
     * @param {Object} [toastOptions.action] - إجراء يمكن تنفيذه من الإشعار (اختياري)
     * @param {string} toastOptions.action.text - نص الإجراء
     * @param {Function} toastOptions.action.callback - دالة ستنفذ عند النقر على الإجراء
     * @returns {number} معرف الإشعار
     */
    function add({ 
        message, 
        type = TOAST_TYPES.INFO, 
        title = null,
        duration = 5000, 
        dismissable = true,
        action = null
    }) {
        if (!message) {
            console.warn('Toast message is required');
            return -1;
        }

        const id = nextId++;
        const toast = {
            id,
            message,
            type,
            title,
            dismissable,
            action,
            createdAt: new Date()
        };

        update(toasts => [toast, ...toasts]);

        // إزالة الإشعار تلقائيًا بعد المدة المحددة
        // Auto-remove toast after specified duration
        if (duration > 0 && browser) {
            setTimeout(() => {
                remove(id);
            }, duration);
        }

        return id;
    }

    /**
     * إزالة إشعار بواسطة المعرف
     * Remove a toast by ID
     *
     * @param {number} id - معرف الإشعار
     */
    function remove(id) {
        update(toasts => toasts.filter(toast => toast.id !== id));
    }

    /**
     * إزالة جميع الإشعارات
     * Remove all toasts
     */
    function clear() {
        update(() => []);
    }

    /**
     * دوال مساعدة لإضافة أنواع مختلفة من الإشعارات
     * Helper functions for adding different types of toasts
     */
    
    /**
     * إضافة إشعار نجاح
     * Add a success toast
     */
    function success(message, options = {}) {
        return add({ message, type: TOAST_TYPES.SUCCESS, ...options });
    }

    /**
     * إضافة إشعار خطأ
     * Add an error toast
     */
    function error(message, options = {}) {
        return add({ message, type: TOAST_TYPES.ERROR, ...options });
    }

    /**
     * إضافة إشعار تحذير
     * Add a warning toast
     */
    function warning(message, options = {}) {
        return add({ message, type: TOAST_TYPES.WARNING, ...options });
    }

    /**
     * إضافة إشعار معلومات
     * Add an info toast
     */
    function info(message, options = {}) {
        return add({ message, type: TOAST_TYPES.INFO, ...options });
    }

    /**
     * إضافة إشعار لخطأ API استنادًا إلى استجابة الخطأ
     * Add a toast for API error based on error response
     */
    function apiError(error, fallbackMessage = 'An error occurred') {
        let message = fallbackMessage;
        
        if (error?.message) {
            message = error.message;
        } else if (typeof error === 'string') {
            message = error;
        }
        
        return add({ 
            message, 
            type: TOAST_TYPES.ERROR,
            dismissable: true,
            duration: 7000
        });
    }

    return {
        subscribe,
        add,
        remove,
        clear,
        success,
        error,
        warning,
        info,
        apiError
    };
}

/**
 * مخزن الإشعارات - يستخدم لإدارة وعرض الإشعارات في التطبيق
 * Toast store - used to manage and display toast notifications in the app
 */
export const toast = createToastStore();

/**
 * مخزن مشتق يحتوي فقط على الإشعارات المصنفة حسب النوع
 * Derived store with toasts categorized by type
 */
export const toastsByType = derived(toast, $toasts => {
    return {
        success: $toasts.filter(toast => toast.type === TOAST_TYPES.SUCCESS),
        error: $toasts.filter(toast => toast.type === TOAST_TYPES.ERROR),
        warning: $toasts.filter(toast => toast.type === TOAST_TYPES.WARNING),
        info: $toasts.filter(toast => toast.type === TOAST_TYPES.INFO)
    };
});

// Export the default toast store for easy importing
export default toast;