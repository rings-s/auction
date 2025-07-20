<script>
	import { browser } from '$app/environment';

	// Theme state using Svelte 5 runes
	let themeState = $state('light');
	let systemThemeState = $state('light');
	let effectiveThemeState = $state('light');

	/** @type {'light' | 'dark' | 'system'} */
	let defaultTheme = $props('system');
	/** @type {boolean} */
	let enableTransitions = $props(true);
	/** @type {number} */
	let transitionDuration = $props(300);

	let mounted = $state(false);
	let mediaQuery = $state();

	// Color schemes for different themes
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

	$effect(() => {
		mounted = true;

		// Initialize system theme detection
		if (browser) {
			mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

			// Set initial system theme
			systemThemeState = mediaQuery.matches ? 'dark' : 'light';

			// Listen for system theme changes
			const handleChange = (e) => {
				systemThemeState = e.matches ? 'dark' : 'light';
			};

			mediaQuery.addEventListener('change', handleChange);

			// Load saved theme preference
			const savedTheme = localStorage.getItem('theme');
			if (savedTheme && ['light', 'dark', 'system'].includes(savedTheme)) {
				themeState = savedTheme;
			} else {
				themeState = defaultTheme;
			}

			return () => {
				mediaQuery.removeEventListener('change', handleChange);
			};
		}
	});

	// Update effective theme based on theme setting and system preference
	$effect(() => {
		if (themeState === 'system') {
			effectiveThemeState = systemThemeState;
		} else {
			effectiveThemeState = themeState;
		}
	});

	// Apply theme to document
	$effect(() => {
		if (mounted && browser) {
			applyTheme(effectiveThemeState);
		}
	});

	function applyTheme(themeName) {
		if (!browser || !document.documentElement) return;

		const root = document.documentElement;
		const themeColors = themes[themeName];

		// Add transition class if enabled
		if (enableTransitions) {
			root.classList.add('theme-transition');
			root.style.setProperty('--theme-transition-duration', `${transitionDuration}ms`);
		}

		// Set theme attribute
		root.setAttribute('data-theme', themeName);

		// Apply CSS custom properties
		Object.entries(themeColors).forEach(([key, value]) => {
			root.style.setProperty(`--color-${key}`, value);
		});

		// Update meta theme-color for mobile browsers
		let metaThemeColor = document.querySelector('meta[name="theme-color"]');
		if (!metaThemeColor) {
			metaThemeColor = document.createElement('meta');
			metaThemeColor.name = 'theme-color';
			document.head.appendChild(metaThemeColor);
		}
		metaThemeColor.content = themeColors.background;

		// Remove transition class after transition completes
		if (enableTransitions) {
			setTimeout(() => {
				root.classList.remove('theme-transition');
			}, transitionDuration);
		}
	}

	// Theme switching functions
	export function setTheme(newTheme) {
		if (!['light', 'dark', 'system'].includes(newTheme)) return;

		themeState = newTheme;

		if (browser) {
			localStorage.setItem('theme', newTheme);
		}
	}

	export function toggleTheme() {
		if (themeState === 'light') {
			setTheme('dark');
		} else if (themeState === 'dark') {
			setTheme('system');
		} else {
			setTheme('light');
		}
	}

	export function getThemeColors(themeName = effectiveThemeState) {
		return themes[themeName] || themes.light;
	}

	// Create store-like objects for backward compatibility
	export const theme = {
		get value() {
			return themeState;
		},
		set: (value) => {
			themeState = value;
		},
		subscribe: (fn) => {
			fn(themeState);
			return () => {};
		}
	};

	export const systemTheme = {
		get value() {
			return systemThemeState;
		},
		subscribe: (fn) => {
			fn(systemThemeState);
			return () => {};
		}
	};

	export const effectiveTheme = {
		get value() {
			return effectiveThemeState;
		},
		subscribe: (fn) => {
			fn(effectiveThemeState);
			return () => {};
		}
	};
</script>

<!-- Theme Provider Component -->
<div class="theme-provider" data-theme={effectiveThemeState}>
	<slot />
</div>

<style>
	:global(html) {
		/* CSS Custom Properties for theming */
		--color-background: #ffffff;
		--color-foreground: #0f172a;
		--color-card: #ffffff;
		--color-card-foreground: #0f172a;
		--color-popover: #ffffff;
		--color-popover-foreground: #0f172a;
		--color-primary: #3b82f6;
		--color-primary-foreground: #f8fafc;
		--color-secondary: #f1f5f9;
		--color-secondary-foreground: #0f172a;
		--color-muted: #f1f5f9;
		--color-muted-foreground: #64748b;
		--color-accent: #f1f5f9;
		--color-accent-foreground: #0f172a;
		--color-destructive: #ef4444;
		--color-destructive-foreground: #f8fafc;
		--color-border: #e2e8f0;
		--color-input: #e2e8f0;
		--color-ring: #3b82f6;
		--color-success: #10b981;
		--color-warning: #f59e0b;
		--color-info: #3b82f6;

		/* Transition duration for smooth theme changes */
		--theme-transition-duration: 300ms;
	}

	:global(.theme-transition) {
		transition:
			background-color var(--theme-transition-duration) ease-out,
			color var(--theme-transition-duration) ease-out,
			border-color var(--theme-transition-duration) ease-out,
			box-shadow var(--theme-transition-duration) ease-out;
	}

	:global(.theme-transition *) {
		transition:
			background-color var(--theme-transition-duration) ease-out,
			color var(--theme-transition-duration) ease-out,
			border-color var(--theme-transition-duration) ease-out,
			box-shadow var(--theme-transition-duration) ease-out,
			fill var(--theme-transition-duration) ease-out,
			stroke var(--theme-transition-duration) ease-out;
	}

	.theme-provider {
		min-height: 100vh;
		background-color: var(--color-background);
		color: var(--color-foreground);
	}

	/* Theme-specific styles */
	:global([data-theme='light']) {
		color-scheme: light;
	}

	:global([data-theme='dark']) {
		color-scheme: dark;
	}

	/* Scrollbar theming */
	:global([data-theme='light'] ::-webkit-scrollbar) {
		background: #f1f5f9;
	}

	:global([data-theme='light'] ::-webkit-scrollbar-thumb) {
		background: #cbd5e1;
	}

	:global([data-theme='dark'] ::-webkit-scrollbar) {
		background: #1e293b;
	}

	:global([data-theme='dark'] ::-webkit-scrollbar-thumb) {
		background: #475569;
	}

	/* Selection colors */
	:global([data-theme='light'] ::selection) {
		background: rgba(59, 130, 246, 0.2);
		color: #1e40af;
	}

	:global([data-theme='dark'] ::selection) {
		background: rgba(59, 130, 246, 0.3);
		color: #93c5fd;
	}

	/* Focus ring colors */
	:global([data-theme='light'] :focus-visible) {
		outline: 2px solid var(--color-ring);
		outline-offset: 2px;
	}

	:global([data-theme='dark'] :focus-visible) {
		outline: 2px solid var(--color-ring);
		outline-offset: 2px;
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		:global(.theme-transition),
		:global(.theme-transition *) {
			transition: none !important;
		}
	}

	/* High contrast mode adjustments */
	@media (prefers-contrast: high) {
		:global([data-theme='light']) {
			--color-border: #000000;
			--color-foreground: #000000;
			--color-background: #ffffff;
		}

		:global([data-theme='dark']) {
			--color-border: #ffffff;
			--color-foreground: #ffffff;
			--color-background: #000000;
		}
	}

	/* Print styles */
	@media print {
		.theme-provider {
			background: white !important;
			color: black !important;
		}

		:global(*) {
			background: transparent !important;
			color: black !important;
			box-shadow: none !important;
		}
	}
</style>
