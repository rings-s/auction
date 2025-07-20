/**
 * @typedef {Object} ToastAction
 * @property {string} label - Button text
 * @property {Function} callback - Function to call when button is clicked
 */

/**
 * @typedef {Object} ToastMessage
 * @property {string} id
 * @property {string} message
 * @property {string} [title] - Optional title for the toast
 * @property {'info' | 'success' | 'warning' | 'error'} type
 * @property {number} duration - Duration in milliseconds (0 = persistent)
 * @property {boolean} [persistent] - Whether toast stays until manually dismissed
 * @property {ToastAction} [action] - Optional action button
 */

// Use Svelte 5 state rune for toasts
let toasts = $state([]);

// Create enhanced toast store with advanced functionality
function createToastStore() {
	return {
		// Getter for toasts
		get toasts() {
			return toasts;
		},

		/**
		 * Adds a new toast message.
		 * @param {Partial<ToastMessage> & { message: string }} toastDetails - The details for the toast.
		 * @returns {string} The ID of the added toast.
		 */
		add: (toastDetails) => {
			const id = toastDetails.id || Math.random().toString(36).substr(2, 9);
			const defaults = {
				id,
				type: /** @type {'info'} */ ('info'),
				duration: 5000,
				persistent: false
			};

			/** @type {ToastMessage} */
			const newToast = { ...defaults, ...toastDetails };

			toasts = [...toasts, newToast];

			// Auto-remove after duration (unless persistent or duration is 0)
			if (!newToast.persistent && newToast.duration > 0) {
				setTimeout(() => toastStore.remove(id), newToast.duration);
			}

			return id;
		},

		/**
		 * Removes a toast message by its ID.
		 * @param {string} id - The ID of the toast to remove.
		 */
		remove: (id) => {
			toasts = toasts.filter((t) => t.id !== id);
		},

		/**
		 * Clear all toasts
		 */
		clear: () => {
			toasts = [];
		},

		// Enhanced convenience methods with better defaults
		success: (message, options = {}) => {
			return toastStore.add({
				type: 'success',
				message,
				duration: 4000,
				...options
			});
		},

		error: (message, options = {}) => {
			return toastStore.add({
				type: 'error',
				message,
				duration: 8000, // Error toasts stay longer
				...options
			});
		},

		warning: (message, options = {}) => {
			return toastStore.add({
				type: 'warning',
				message,
				duration: 6000,
				...options
			});
		},

		info: (message, options = {}) => {
			return toastStore.add({
				type: 'info',
				message,
				duration: 5000,
				...options
			});
		},

		/**
		 * Create a toast with an action button
		 * @param {string} message
		 * @param {ToastAction} action
		 * @param {Partial<ToastMessage>} options
		 */
		withAction: (message, action, options = {}) => {
			return toastStore.add({
				message,
				action,
				persistent: true, // Action toasts don't auto-dismiss by default
				duration: 0,
				...options
			});
		}
	};
}

export const toastStore = createToastStore();

// Legacy compatibility exports
export function addToast(toastDetails) {
	return toastStore.add(toastDetails);
}

export function removeToast(id) {
	toastStore.remove(id);
}

// Enhanced convenience API
export const toast = {
	success: (message, options) => toastStore.success(message, options),
	error: (message, options) => toastStore.error(message, options),
	warning: (message, options) => toastStore.warning(message, options),
	info: (message, options) => toastStore.info(message, options),
	withAction: (message, action, options) => toastStore.withAction(message, action, options),
	add: (toastDetails) => toastStore.add(toastDetails),
	remove: (id) => toastStore.remove(id),
	clear: () => toastStore.clear()
};
