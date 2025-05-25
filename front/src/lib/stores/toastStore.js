import { writable } from 'svelte/store';

/**
 * @typedef {Object} ToastMessage
 * @property {string} id
 * @property {string} message
 * @property {'info' | 'success' | 'warning' | 'error'} type
 * @property {number} duration - Duration in milliseconds.
 */

/** @type {import('svelte/store').Writable<ToastMessage[]>} */
export const toasts = writable([]);

/**
 * Adds a new toast message.
 * @param {Partial<ToastMessage> & { message: string }} toastDetails - The details for the toast.
 * @returns {string} The ID of the added toast.
 */
export function addToast(toastDetails) {
  const id = toastDetails.id || Math.random().toString(36).substr(2, 9);
  const defaults = {
    id,
    type: /** @type {'info'} */ ('info'), // Default type
    duration: 3000,
  };
  /** @type {ToastMessage} */
  const newToast = { ...defaults, ...toastDetails, message: toastDetails.message };

  toasts.update((all) => [newToast, ...all]);

  if (newToast.duration > 0) { // Ensure duration is positive
    setTimeout(() => removeToast(id), newToast.duration);
  }
  return id;
}

/**
 * Removes a toast message by its ID.
 * @param {string} id - The ID of the toast to remove.
 */
export function removeToast(id) {
  toasts.update((all) => all.filter((t) => t.id !== id));
}

// Convenience functions for different toast types
/**
 * Creates a function that adds a toast of a specific type.
 * @param {'info' | 'success' | 'warning' | 'error'} type - The type of toast.
 * @returns {(message: string, options?: Partial<Omit<ToastMessage, 'message' | 'type' | 'id'>>) => string} A function to add a toast of the specified type.
 */
const createTypedToast = (type) => 
  /**
   * @param {string} message
   * @param {Partial<Omit<ToastMessage, 'message' | 'type' | 'id'>>} [options]
   * @returns {string}
   */
  (message, options = {}) => addToast({ message, type, ...options });

export const toast = {
  info: createTypedToast('info'),
  success: createTypedToast('success'),
  warning: createTypedToast('warning'),
  error: createTypedToast('error'),
  add: addToast, // expose the generic addToast
  remove: removeToast, // expose removeToast
};
