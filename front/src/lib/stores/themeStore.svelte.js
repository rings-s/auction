// Advanced theme store using Svelte 5 runes
import { browser } from '$app/environment';

// Theme states using Svelte 5 runes
let currentTheme = $state('system'); // 'light', 'dark', 'system'
let systemTheme = $state('light');

// Derived store for the effective theme using $derived as variable declaration
const effectiveThemeValue = $derived(() => {
	return currentTheme === 'system' ? systemTheme : currentTheme;
});

// Export function that returns current effective theme
export function getEffectiveTheme() {
	return effectiveThemeValue;
}

// Theme configuration state
let config = $state({
	enableTransitions: true,
	transitionDuration: 300,
	persistPreference: true,
	followSystemChanges: true,
	applyToDocument: true
});

// Create store objects that provide subscribe method for $ syntax compatibility
function createThemeStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(currentTheme));
	}

	return {
		subscribe(fn) {
			subscribers.add(fn);
			fn(currentTheme);
			return () => subscribers.delete(fn);
		},
		get value() {
			return currentTheme;
		},
		set(newTheme) {
			if (['light', 'dark', 'system'].includes(newTheme)) {
				currentTheme = newTheme;
				if (browser) {
					localStorage.setItem('theme', newTheme);
				}
				notify();
			}
		}
	};
}

function createSystemThemeStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(systemTheme));
	}

	return {
		subscribe(fn) {
			subscribers.add(fn);
			fn(systemTheme);
			return () => subscribers.delete(fn);
		},
		get value() {
			return systemTheme;
		},
		set(newSystemTheme) {
			systemTheme = newSystemTheme;
			notify();
		}
	};
}

function createEffectiveThemeStore() {
	const subscribers = new Set();

	function notify() {
		const effective = effectiveThemeValue;
		subscribers.forEach((fn) => fn(effective));
	}

	return {
		subscribe(fn) {
			subscribers.add(fn);
			fn(effectiveThemeValue);
			return () => subscribers.delete(fn);
		},
		get value() {
			return effectiveThemeValue;
		}
	};
}

function createThemeConfigStore() {
	const subscribers = new Set();

	function notify() {
		subscribers.forEach((fn) => fn(config));
	}

	return {
		subscribe(fn) {
			subscribers.add(fn);
			fn(config);
			return () => subscribers.delete(fn);
		},
		get value() {
			return config;
		},
		set(newConfig) {
			config = newConfig;
			notify();
		},
		update(updater) {
			config = updater(config);
			notify();
		}
	};
}

// Export theme stores
export const theme = createThemeStore();
export const systemThemeStore = createSystemThemeStore();
export const effectiveThemeStore = createEffectiveThemeStore();
export const themeConfig = createThemeConfigStore();

// Initialize theme system
export function initializeTheme() {
	if (!browser) return;

	// Detect system theme preference
	const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
	systemTheme = mediaQuery.matches ? 'dark' : 'light';

	// Listen for system theme changes
	const handleSystemThemeChange = (e) => {
		systemTheme = e.matches ? 'dark' : 'light';
		// Apply theme when system theme changes
		applyThemeToDocument(effectiveThemeValue);
	};

	mediaQuery.addEventListener('change', handleSystemThemeChange);

	// Load saved theme preference
	const savedTheme = localStorage.getItem('theme');
	if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
		currentTheme = savedTheme;
	}

	// Apply theme to document initially
	applyThemeToDocument(effectiveThemeValue);

	// Cleanup function
	return () => {
		mediaQuery.removeEventListener('change', handleSystemThemeChange);
	};
}

// Apply theme to document
function applyThemeToDocument(themeName) {
	if (!browser) return;

	const root = document.documentElement;

	// Set data attribute for CSS targeting
	root.setAttribute('data-theme', themeName);

	// Set color-scheme for better browser integration
	root.style.colorScheme = themeName;

	// Update meta theme-color for mobile browsers
	updateMetaThemeColor(themeName);
}

// Update meta theme-color
function updateMetaThemeColor(themeName) {
	if (!browser) return;

	const colors = {
		light: '#ffffff',
		dark: '#0f172a'
	};

	let metaThemeColor = document.querySelector('meta[name="theme-color"]');
	if (!metaThemeColor) {
		metaThemeColor = document.createElement('meta');
		metaThemeColor.name = 'theme-color';
		document.head.appendChild(metaThemeColor);
	}

	metaThemeColor.content = colors[themeName] || colors.light;
}

// Theme control functions
export function setTheme(newTheme) {
	if (!['light', 'dark', 'system'].includes(newTheme)) {
		console.warn(`Invalid theme: ${newTheme}`);
		return;
	}

	currentTheme = newTheme;

	if (browser) {
		localStorage.setItem('theme', newTheme);
	}
}

export function toggleTheme() {
	const themes = ['light', 'dark', 'system'];
	const currentIndex = themes.indexOf(currentTheme);
	const nextIndex = (currentIndex + 1) % themes.length;
	const newTheme = themes[nextIndex];

	currentTheme = newTheme;

	if (browser) {
		localStorage.setItem('theme', newTheme);
	}
}

export function toggleBetweenLightAndDark() {
	const newTheme = currentTheme === 'light' ? 'dark' : 'light';
	currentTheme = newTheme;

	if (browser) {
		localStorage.setItem('theme', newTheme);
	}
}

// Utility functions
export function getThemeColors(themeName) {
	const themes = {
		light: {
			background: '#ffffff',
			foreground: '#0f172a',
			card: '#ffffff',
			cardForeground: '#0f172a',
			popover: '#ffffff',
			popoverForeground: '#0f172a',
			primary: '#3b82f6',
			primaryForeground: '#f8fafc',
			secondary: '#f1f5f9',
			secondaryForeground: '#0f172a',
			muted: '#f1f5f9',
			mutedForeground: '#64748b',
			accent: '#f1f5f9',
			accentForeground: '#0f172a',
			destructive: '#ef4444',
			destructiveForeground: '#f8fafc',
			border: '#e2e8f0',
			input: '#e2e8f0',
			ring: '#3b82f6',
			success: '#10b981',
			warning: '#f59e0b',
			info: '#3b82f6'
		},
		dark: {
			background: '#0f172a',
			foreground: '#f8fafc',
			card: '#1e293b',
			cardForeground: '#f8fafc',
			popover: '#1e293b',
			popoverForeground: '#f8fafc',
			primary: '#3b82f6',
			primaryForeground: '#f8fafc',
			secondary: '#1e293b',
			secondaryForeground: '#f8fafc',
			muted: '#1e293b',
			mutedForeground: '#94a3b8',
			accent: '#1e293b',
			accentForeground: '#f8fafc',
			destructive: '#ef4444',
			destructiveForeground: '#f8fafc',
			border: '#334155',
			input: '#334155',
			ring: '#3b82f6',
			success: '#10b981',
			warning: '#f59e0b',
			info: '#3b82f6'
		}
	};

	return themes[themeName] || themes.light;
}

export function isDarkTheme(themeName) {
	return themeName === 'dark';
}

export function isLightTheme(themeName) {
	return themeName === 'light';
}

export function isSystemTheme(themeName) {
	return themeName === 'system';
}

// Create a reactive theme class helper
export function createThemeClass() {
	const effective = getEffectiveTheme();
	return {
		'theme-light': effective === 'light',
		'theme-dark': effective === 'dark'
	};
}

// Auto-initialize theme system if in browser
if (browser) {
	initializeTheme();
}
