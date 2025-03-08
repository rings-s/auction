// /src/lib/stores/uiStore.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

// Initialize theme from localStorage or system preference
let initialTheme = 'light';

if (browser) {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    initialTheme = savedTheme;
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    initialTheme = 'dark';
  }
}

// Create stores
export const theme = writable(initialTheme);
export const searchOpen = writable(false);
export const sidebarOpen = writable(false);
export const notifications = writable([]);
export const unreadNotificationsCount = derived(
  notifications,
  $notifications => $notifications.filter(n => !n.read).length
);

// Toast notifications
const toastStore = writable([]);
export const toasts = {
  subscribe: toastStore.subscribe,
  
  /**
   * Add a toast notification
   * @param {string} message - Toast message
   * @param {string} type - Toast type (success, error, warning, info)
   * @param {number} duration - Auto-dismiss duration in milliseconds
   */
  add: (message, type = 'info', duration = 5000) => {
    const id = Date.now().toString();
    
    toastStore.update(all => [
      {
        id,
        message,
        type,
        timestamp: new Date(),
      },
      ...all,
    ]);
    
    if (duration) {
      setTimeout(() => {
        toastStore.update(all => all.filter(t => t.id !== id));
      }, duration);
    }
    
    return id;
  },
  
  /**
   * Remove a toast notification
   * @param {string} id - Toast ID
   */
  remove: (id) => {
    toastStore.update(all => all.filter(t => t.id !== id));
  },
  
  /**
   * Clear all toast notifications
   */
  clear: () => {
    toastStore.set([]);
  },
};

// Modal system
export const modalStore = writable({
  isOpen: false,
  component: null,
  props: {},
});

// Update theme in localStorage when it changes
if (browser) {
  theme.subscribe(value => {
    localStorage.setItem('theme', value);
    
    // Apply theme to document
    if (value === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  });
}

/**
 * Toggle theme between light and dark
 */
export function toggleTheme() {
  theme.update(current => (current === 'light' ? 'dark' : 'light'));
}

/**
 * Open the global search overlay
 */
export function openSearch() {
  searchOpen.set(true);
}

/**
 * Close the global search overlay
 */
export function closeSearch() {
  searchOpen.set(false);
}

/**
 * Toggle the main sidebar
 */
export function toggleSidebar() {
  sidebarOpen.update(value => !value);
}

/**
 * Mark notification as read
 * @param {string} id - Notification ID
 */
export function markNotificationAsRead(id) {
  notifications.update(all => 
    all.map(n => (n.id === id ? { ...n, read: true } : n))
  );
}

/**
 * Add a new notification
 * @param {Object} notification - Notification object
 */
export function addNotification(notification) {
  notifications.update(all => [
    {
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false,
      ...notification
    },
    ...all
  ]);
}

/**
 * Open a modal with the specified component
 * @param {Object} component - Svelte component to render in the modal
 * @param {Object} props - Props to pass to the component
 */
export function openModal(component, props = {}) {
  modalStore.set({
    isOpen: true,
    component,
    props
  });
}

/**
 * Close the currently open modal
 */
export function closeModal() {
  modalStore.update(state => ({
    ...state,
    isOpen: false
  }));
}