// src/lib/services/user.js
// خدمات المستخدم - User Services

import api from './api';

/**
 * خدمات المستخدم - توفر دوال للتعامل مع المستخدمين عبر واجهة برمجة التطبيقات
 * User services - provides functions for interacting with users via the API
 */
class UserService {
    /**
     * الحصول على بيانات الملف الشخصي للمستخدم الحالي
     * Get current user profile
     * 
     * @returns {Promise<Object>} وعد يحتوي على بيانات المستخدم
     */
    async getProfile() {
        try {
            const response = await api.get('accounts/profile/');
            return {
                success: true,
                data: response.user || response.data || {}
            };
        } catch (error) {
            console.error('Error fetching user profile:', error);
            return {
                success: false,
                error: error.message || 'Failed to fetch user profile'
            };
        }
    }

    /**
     * تحديث بيانات الملف الشخصي للمستخدم الحالي
     * Update current user profile
     * 
     * @param {Object} profileData - بيانات الملف الشخصي الجديدة
     * @param {boolean} partial - تحديث جزئي (PATCH) أو كلي (PUT)
     * @returns {Promise<Object>} وعد يحتوي على بيانات المستخدم المحدثة
     */
    async updateProfile(profileData, partial = true) {
        if (!profileData) {
            return {
                success: false,
                error: 'Profile data is required'
            };
        }

        try {
            const method = partial ? 'patch' : 'put';
            const response = await api[method]('accounts/profile/', profileData);
            return {
                success: true,
                data: response.user || response.data || {}
            };
        } catch (error) {
            console.error('Error updating user profile:', error);
            return {
                success: false,
                error: error.message || 'Failed to update user profile'
            };
        }
    }

    /**
     * الحصول على بيانات الملف الشخصي العام لمستخدم محدد
     * Get public profile for a specific user
     * 
     * @param {string} userId - معرف المستخدم
     * @returns {Promise<Object>} وعد يحتوي على بيانات المستخدم العامة
     */
    async getPublicProfile(userId) {
        if (!userId) {
            return {
                success: false,
                error: 'User ID is required'
            };
        }

        try {
            const response = await api.get(`accounts/profile/${userId}/`);
            return {
                success: true,
                data: response.user || response.data || {}
            };
        } catch (error) {
            console.error(`Error fetching public profile for user ${userId}:`, error);
            return {
                success: false,
                error: error.message || 'Failed to fetch public profile'
            };
        }
    }

    /**
     * تحديث صورة الملف الشخصي
     * Update profile avatar
     * 
     * @param {File} file - ملف الصورة
     * @param {Function} onProgress - دالة لتتبع تقدم الرفع (اختياري)
     * @returns {Promise<Object>} وعد يحتوي على نتيجة العملية
     */
    async updateAvatar(file, onProgress) {
        if (!file) {
            return {
                success: false,
                error: 'Avatar file is required'
            };
        }

        try {
            const response = await api.upload('accounts/profile/avatar/', file, onProgress);
            return {
                success: true,
                data: response.user || response.data || {}
            };
        } catch (error) {
            console.error('Error updating avatar:', error);
            return {
                success: false,
                error: error.message || 'Failed to update avatar'
            };
        }
    }

    /**
     * الحصول على بيانات لوحة تحكم المستخدم حسب الدور
     * Get user dashboard data based on role
     * 
     * @returns {Promise<Object>} وعد يحتوي على بيانات لوحة التحكم
     */
    async getDashboardData() {
        try {
            const response = await api.get('accounts/dashboard/role/');
            return {
                success: true,
                data: response || {}
            };
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            return {
                success: false,
                error: error.message || 'Failed to fetch dashboard data'
            };
        }
    }

    /**
     * تغيير كلمة المرور للمستخدم الحالي
     * Change password for current user
     * 
     * @param {string} currentPassword - كلمة المرور الحالية
     * @param {string} newPassword - كلمة المرور الجديدة
     * @param {string} confirmPassword - تأكيد كلمة المرور الجديدة
     * @returns {Promise<Object>} وعد يحتوي على نتيجة العملية
     */
    async changePassword(currentPassword, newPassword, confirmPassword) {
        if (!currentPassword || !newPassword || !confirmPassword) {
            return {
                success: false,
                error: 'All password fields are required'
            };
        }

        if (newPassword !== confirmPassword) {
            return {
                success: false,
                error: 'New passwords do not match'
            };
        }

        try {
            const response = await api.post('accounts/password/', {
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            });
            
            return {
                success: true,
                data: response || {},
                message: response.message || 'Password changed successfully'
            };
        } catch (error) {
            console.error('Error changing password:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to change password'
            };
        }
    }

    /**
     * طلب إعادة تعيين كلمة المرور
     * Request password reset
     * 
     * @param {string} email - البريد الإلكتروني للمستخدم
     * @returns {Promise<Object>} وعد يحتوي على نتيجة العملية
     */
    async requestPasswordReset(email) {
        if (!email) {
            return {
                success: false,
                error: 'Email is required'
            };
        }

        try {
            const response = await api.post('accounts/password/reset/', { email });
            return {
                success: true,
                data: response || {},
                message: response.message || 'Password reset instructions have been sent to your email'
            };
        } catch (error) {
            console.error('Error requesting password reset:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to request password reset'
            };
        }
    }

    /**
     * التحقق من صحة رمز إعادة تعيين كلمة المرور
     * Verify password reset code
     * 
     * @param {string} email - البريد الإلكتروني للمستخدم
     * @param {string} resetCode - رمز إعادة التعيين
     * @returns {Promise<Object>} وعد يحتوي على نتيجة التحقق
     */
    async verifyResetCode(email, resetCode) {
        if (!email || !resetCode) {
            return {
                success: false,
                error: 'Email and reset code are required'
            };
        }

        try {
            const response = await api.post('accounts/password/reset/verify/', {
                email,
                reset_code: resetCode
            });
            
            return {
                success: true,
                data: response || {},
                message: response.message || 'Reset code is valid'
            };
        } catch (error) {
            console.error('Error verifying reset code:', error);
            return {
                success: false,
                error: error.message || error.error || 'Invalid or expired reset code'
            };
        }
    }

    /**
     * إعادة تعيين كلمة المرور باستخدام الرمز
     * Reset password using code
     * 
     * @param {string} email - البريد الإلكتروني للمستخدم
     * @param {string} resetCode - رمز إعادة التعيين
     * @param {string} newPassword - كلمة المرور الجديدة
     * @param {string} confirmPassword - تأكيد كلمة المرور الجديدة
     * @returns {Promise<Object>} وعد يحتوي على نتيجة العملية
     */
    async resetPassword(email, resetCode, newPassword, confirmPassword) {
        if (!email || !resetCode || !newPassword || !confirmPassword) {
            return {
                success: false,
                error: 'All fields are required'
            };
        }

        if (newPassword !== confirmPassword) {
            return {
                success: false,
                error: 'Passwords do not match'
            };
        }

        try {
            const response = await api.post('accounts/password/reset/confirm/', {
                email,
                reset_code: resetCode,
                new_password: newPassword,
                confirm_password: confirmPassword
            });
            
            return {
                success: true,
                data: response || {},
                tokens: {
                    refresh: response.refresh,
                    access: response.access
                },
                message: response.message || 'Password reset successfully'
            };
        } catch (error) {
            console.error('Error resetting password:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to reset password'
            };
        }
    }

    /**
     * إعادة إرسال رمز التحقق من البريد الإلكتروني
     * Resend email verification code
     * 
     * @param {string} email - البريد الإلكتروني للمستخدم
     * @returns {Promise<Object>} وعد يحتوي على نتيجة العملية
     */
    async resendVerification(email) {
        if (!email) {
            return {
                success: false,
                error: 'Email is required'
            };
        }

        try {
            const response = await api.post('accounts/resend-verification/', { email });
            return {
                success: true,
                data: response || {},
                message: response.message || 'Verification email has been sent'
            };
        } catch (error) {
            console.error('Error resending verification email:', error);
            return {
                success: false,
                error: error.message || error.error || 'Failed to resend verification email'
            };
        }
    }

    /**
     * التحقق من البريد الإلكتروني باستخدام الرمز
     * Verify email using code
     * 
     * @param {string} email - البريد الإلكتروني للمستخدم
     * @param {string} verificationCode - رمز التحقق
     * @returns {Promise<Object>} وعد يحتوي على نتيجة التحقق
     */
    async verifyEmail(email, verificationCode) {
        if (!email || !verificationCode) {
            return {
                success: false,
                error: 'Email and verification code are required'
            };
        }

        try {
            const response = await api.post('accounts/verify-email/', {
                email,
                verification_code: verificationCode
            });
            
            return {
                success: true,
                data: response || {},
                tokens: {
                    refresh: response.refresh,
                    access: response.access
                },
                message: response.message || 'Email verified successfully'
            };
        } catch (error) {
            console.error('Error verifying email:', error);
            return {
                success: false,
                error: error.message || error.error || 'Invalid or expired verification code'
            };
        }
    }
}

// Export a singleton instance
export default new UserService();