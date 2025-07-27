// User store using Svelte 5 runes
let currentUser = $state(null);

// Derived values using $derived as variable declarations
const isAuthenticatedValue = $derived(() => currentUser !== null);
const roleValue = $derived(() => currentUser?.role || null);
const isStaffValue = $derived(() => currentUser?.is_staff || false);
const isSuperuserValue = $derived(() => currentUser?.is_superuser || false);

// Export functions that return current derived values
export function isAuthenticated() {
	return isAuthenticatedValue;
}

export function role() {
	return roleValue;
}

export function isStaff() {
	return isStaffValue;
}

export function isSuperuser() {
	return isSuperuserValue;
}

// Create store object that provides subscribe method for $ syntax compatibility
function createUserStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(currentUser));
	}

	return {
		// Subscribe method for $ syntax compatibility
		subscribe(fn) {
			subscribers.add(fn);
			fn(currentUser); // Call immediately with current value
			return () => subscribers.delete(fn);
		},

		// Getter for current user value
		get value() {
			return currentUser;
		},

		// Setter for the current user
		set(newUser) {
			currentUser = newUser;
			notify();
		},

		// Update method for partial updates
		update(updater) {
			currentUser = updater(currentUser);
			notify();
		},

		// Clear user data
		clear() {
			currentUser = null;
			notify();
		}
	};
}

export const userStore = createUserStore();
export const user = userStore;
