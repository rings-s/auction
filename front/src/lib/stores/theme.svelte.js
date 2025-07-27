// Theme store using Svelte 5 runes
import { browser } from '$app/environment';

// Get initial theme from localStorage
function getInitialTheme() {
	if (typeof localStorage !== 'undefined') {
		const savedTheme = localStorage.getItem('theme');
		if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
			return savedTheme;
		}
	}
	return 'light';
}

// Theme state using Svelte 5 runes
let currentTheme = $state(getInitialTheme());

// Create store object that provides subscribe method for $ syntax compatibility
function createThemeStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(currentTheme));
	}

	return {
		// Subscribe method for $ syntax compatibility
		subscribe(fn) {
			subscribers.add(fn);
			fn(currentTheme); // Call immediately with current value
			return () => subscribers.delete(fn);
		},

		// Getter for current theme
		get value() {
			return currentTheme;
		},

		// Setter for theme
		set(newTheme) {
			if (newTheme === 'light' || newTheme === 'dark') {
				currentTheme = newTheme;
				// Save to localStorage
				if (typeof localStorage !== 'undefined') {
					localStorage.setItem('theme', newTheme);
				}
				notify();
			}
		},

		// Toggle theme
		toggle() {
			const newTheme = currentTheme === 'light' ? 'dark' : 'light';
			currentTheme = newTheme;
			// Save to localStorage
			if (typeof localStorage !== 'undefined') {
				localStorage.setItem('theme', newTheme);
			}
			notify();
		}
	};
}

export const theme = createThemeStore();
