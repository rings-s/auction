// src/lib/i18n.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Available languages
export const languageNames = {
	en: 'English',
	ar: 'العربية'
};

// Default translations - minimal implementation
// In real app, these would be loaded from separate JSON files
const translations = {
	en: {
		general: {
			app_name: 'Real Estate Auction Platform',
			loading: 'Loading...',
			required: 'Required'
		},
		navigation: {
			home: 'Home',
			auctions: 'Auctions',
			properties: 'Properties',
			login: 'Login',
			register: 'Sign Up',
			dashboard: 'Dashboard',
			profile: 'Profile',
			settings: 'Settings',
			notifications: 'Notifications',
			logout: 'Logout',
			about: 'About Us',
			contact: 'Contact Us',
			rights: 'All Rights Reserved'
		},
		auth: {
			login: 'Login',
			register: 'Sign Up',
			email: 'Email',
			password: 'Password',
			password_confirm: 'Confirm Password',
			first_name: 'First Name',
			last_name: 'Last Name',
			phone_number: 'Phone Number',
			verification_code: 'Verification Code',
			verify_account: 'Verify Account',
			resend_code: 'Resend Code',
			forgot_password: 'Forgot Password?',
			request_reset: 'Request Reset',
			reset_password: 'Reset Password',
			new_password: 'New Password',
			enter_code: 'Enter Code',
			update_profile: 'Update Profile',
			already_have_account: 'Already have an account?',
			dont_have_account: "Don't have an account?",
			already_have_code: 'Already have a code?',
			remember_me: 'Remember me',
			bio: 'Bio',
			bio_placeholder: 'Tell us about yourself',
			address: 'Address',
			city: 'City',
			country: 'Country',
			verification_sent: 'Verification email has been sent',
			profile_updated: 'Profile updated successfully',
			avatar: 'Profile Picture',
			roles: {
				title: 'Role',
				buyer: 'Buyer',
				seller: 'Seller',
				agent: 'Agent'
			},
			errors: {
				email_required: 'Email is required',
				email_invalid: 'Invalid email format',
				password_required: 'Password is required',
				password_length: 'Password must be at least 8 characters',
				passwords_not_match: 'Passwords do not match',
				name_required: 'Name is required',
				phone_required: 'Phone number is required',
				avatar_too_large: 'Avatar file too large. Maximum size is 2MB',
				avatar_invalid_type: 'Invalid file type. Allowed types: JPEG, PNG, GIF'
			}
		},
		system_messages: {
			error_occurred: 'An error occurred',
			login_failure: 'Failed to login. Please check your credentials',
			verification_failure: 'Failed to verify email',
			register_success: 'Registration successful. Please check your email for verification',
			password_reset_failure: 'Failed to reset password',
			password_reset_sent: 'Password reset instructions have been sent to your email',
			password_reset_success: 'Password reset successfully'
		}
	},
	ar: {
		general: {
			app_name: 'منصة مزادات العقارات',
			loading: 'جاري التحميل...',
			required: 'مطلوب'
		},
		navigation: {
			home: 'الرئيسية',
			auctions: 'المزادات',
			properties: 'العقارات',
			login: 'تسجيل الدخول',
			register: 'إنشاء حساب',
			dashboard: 'لوحة التحكم',
			profile: 'الملف الشخصي',
			settings: 'الإعدادات',
			notifications: 'الإشعارات',
			logout: 'تسجيل الخروج',
			about: 'من نحن',
			contact: 'اتصل بنا',
			rights: 'جميع الحقوق محفوظة'
		},
		auth: {
			login: 'تسجيل الدخول',
			register: 'إنشاء حساب',
			email: 'البريد الإلكتروني',
			password: 'كلمة المرور',
			password_confirm: 'تأكيد كلمة المرور',
			first_name: 'الاسم الأول',
			last_name: 'اسم العائلة',
			phone_number: 'رقم الهاتف',
			verification_code: 'رمز التحقق',
			verify_account: 'تأكيد الحساب',
			resend_code: 'إعادة إرسال الرمز',
			forgot_password: 'نسيت كلمة المرور؟',
			request_reset: 'طلب إعادة تعيين',
			reset_password: 'إعادة تعيين كلمة المرور',
			new_password: 'كلمة المرور الجديدة',
			enter_code: 'إدخال الرمز',
			update_profile: 'تحديث الملف الشخصي',
			already_have_account: 'لديك حساب بالفعل؟',
			dont_have_account: 'ليس لديك حساب؟',
			already_have_code: 'لديك رمز بالفعل؟',
			remember_me: 'تذكرني',
			bio: 'نبذة شخصية',
			bio_placeholder: 'أخبرنا عن نفسك',
			address: 'العنوان',
			city: 'المدينة',
			country: 'الدولة',
			verification_sent: 'تم إرسال رسالة التحقق إلى بريدك الإلكتروني',
			profile_updated: 'تم تحديث الملف الشخصي بنجاح',
			avatar: 'الصورة الشخصية',
			roles: {
				title: 'الدور',
				buyer: 'مشتري',
				seller: 'بائع',
				agent: 'وكيل عقاري'
			},
			errors: {
				email_required: 'البريد الإلكتروني مطلوب',
				email_invalid: 'صيغة البريد الإلكتروني غير صحيحة',
				password_required: 'كلمة المرور مطلوبة',
				password_length: 'يجب أن تكون كلمة المرور 8 أحرف على الأقل',
				passwords_not_match: 'كلمات المرور غير متطابقة',
				name_required: 'الاسم مطلوب',
				phone_required: 'رقم الهاتف مطلوب',
				avatar_too_large: 'حجم الصورة كبير جدًا. الحد الأقصى هو 2 ميجابايت',
				avatar_invalid_type: 'نوع الملف غير صالح. الأنواع المسموح بها: JPEG، PNG، GIF'
			}
		},
		system_messages: {
			error_occurred: 'حدث خطأ',
			login_failure: 'فشل تسجيل الدخول. يرجى التحقق من بيانات الاعتماد الخاصة بك',
			verification_failure: 'فشل التحقق من البريد الإلكتروني',
			register_success: 'تم التسجيل بنجاح. يرجى التحقق من بريدك الإلكتروني للتحقق',
			password_reset_failure: 'فشل إعادة تعيين كلمة المرور',
			password_reset_sent: 'تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني',
			password_reset_success: 'تم إعادة تعيين كلمة المرور بنجاح'
		}
	}
};

// Detect browser language or get from localStorage
function getBrowserLanguage() {
	if (!browser) return 'en';

	// Try to get from localStorage first
	const storedLang = localStorage.getItem('language');
	if (storedLang && ['en', 'ar'].includes(storedLang)) {
		return storedLang;
	}

	// Detect from browser
	const lang = navigator.language?.substring(0, 2);
	return lang === 'ar' ? 'ar' : 'en'; // Default to English for all except Arabic
}

// Create the language store
export const language = writable(getBrowserLanguage());

// Create a derived store for translations
const translationStore = derived(
	language,
	($language) => translations[$language] || translations.en
);

// Create a translation function store
export const t = derived(translationStore, ($translations) => (key) => {
	// Split the key by dots
	const keys = key.split('.');
	let result = $translations;

	// Traverse the translation object
	for (const k of keys) {
		if (result && result[k] !== undefined) {
			result = result[k];
		} else {
			// Return the key if translation is missing
			return key;
		}
	}

	return result;
});

// Function to change language
export function changeLanguage(newLanguage) {
	if (!['en', 'ar'].includes(newLanguage)) {
		console.warn(`Language '${newLanguage}' is not supported. Using 'en' as fallback.`);
		newLanguage = 'en';
	}

	language.set(newLanguage);

	if (browser) {
		// Store in localStorage
		localStorage.setItem('language', newLanguage);

		// Update HTML attributes
		document.documentElement.lang = newLanguage;
		document.documentElement.dir = newLanguage === 'ar' ? 'rtl' : 'ltr';
	}
}

// Initialize language on load
if (browser) {
	// Update HTML attributes when language changes
	language.subscribe((lang) => {
		document.documentElement.lang = lang;
		document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
	});
}

export default { t, language, changeLanguage, languageNames };
