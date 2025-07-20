<script>
	import { browser } from '$app/environment';

	// Breakpoint definitions
	const breakpoints = {
		xs: 0,
		sm: 640,
		md: 768,
		lg: 1024,
		xl: 1280,
		'2xl': 1536
	};

	// Reactive state for current breakpoint information
	export let currentBreakpoint = $state('xs');
	export let screenWidth = $state(0);
	export let screenHeight = $state(0);
	export let isMobile = $state(true);
	export let isTablet = $state(false);
	export let isDesktop = $state(false);
	export let orientation = $state('portrait');

	// Specific breakpoint states
	export let isXs = $state(true);
	export let isSm = $state(false);
	export let isMd = $state(false);
	export let isLg = $state(false);
	export let isXl = $state(false);
	export let is2xl = $state(false);

	// Responsive utilities
	export let smAndUp = $state(false);
	export let mdAndUp = $state(false);
	export let lgAndUp = $state(false);
	export let xlAndUp = $state(false);

	let resizeTimeout;

	$effect(() => {
		if (!browser) return;

		function updateBreakpoint() {
			const width = window.innerWidth;
			const height = window.innerHeight;

			// Update dimensions
			screenWidth = width;
			screenHeight = height;

			// Determine current breakpoint
			let current = 'xs';
			if (width >= breakpoints['2xl']) current = '2xl';
			else if (width >= breakpoints.xl) current = 'xl';
			else if (width >= breakpoints.lg) current = 'lg';
			else if (width >= breakpoints.md) current = 'md';
			else if (width >= breakpoints.sm) current = 'sm';

			currentBreakpoint = current;

			// Update individual breakpoint states
			isXs = width < breakpoints.sm;
			isSm = width >= breakpoints.sm && width < breakpoints.md;
			isMd = width >= breakpoints.md && width < breakpoints.lg;
			isLg = width >= breakpoints.lg && width < breakpoints.xl;
			isXl = width >= breakpoints.xl && width < breakpoints['2xl'];
			is2xl = width >= breakpoints['2xl'];

			// Update range states
			smAndUp = width >= breakpoints.sm;
			mdAndUp = width >= breakpoints.md;
			lgAndUp = width >= breakpoints.lg;
			xlAndUp = width >= breakpoints.xl;

			// Update device type states
			isMobile = width < breakpoints.md;
			isTablet = width >= breakpoints.md && width < breakpoints.lg;
			isDesktop = width >= breakpoints.lg;

			// Update orientation
			orientation = width > height ? 'landscape' : 'portrait';
		}

		function handleResize() {
			clearTimeout(resizeTimeout);
			resizeTimeout = setTimeout(updateBreakpoint, 150);
		}

		// Initial update
		updateBreakpoint();

		// Listen for resize events
		window.addEventListener('resize', handleResize);

		// Listen for orientation changes
		window.addEventListener('orientationchange', () => {
			setTimeout(updateBreakpoint, 500);
		});

		return () => {
			window.removeEventListener('resize', handleResize);
			window.removeEventListener('orientationchange', updateBreakpoint);
			clearTimeout(resizeTimeout);
		};
	});

	// Helper functions for use in components
	export function isBreakpoint(bp) {
		if (!browser) return false;
		return window.innerWidth >= breakpoints[bp];
	}

	export function isBreakpointRange(min, max) {
		if (!browser) return false;
		const width = window.innerWidth;
		return width >= breakpoints[min] && (max ? width < breakpoints[max] : true);
	}

	export function getBreakpointValue(values) {
		if (!browser)
			return values.xs || values.sm || values.md || values.lg || values.xl || values['2xl'];

		const width = window.innerWidth;

		if (width >= breakpoints['2xl'] && values['2xl'] !== undefined) return values['2xl'];
		if (width >= breakpoints.xl && values.xl !== undefined) return values.xl;
		if (width >= breakpoints.lg && values.lg !== undefined) return values.lg;
		if (width >= breakpoints.md && values.md !== undefined) return values.md;
		if (width >= breakpoints.sm && values.sm !== undefined) return values.sm;
		return values.xs;
	}

	// CSS class helpers
	export function getResponsiveClasses(classMap) {
		if (!browser) return '';

		const width = window.innerWidth;
		const classes = [];

		if (classMap.xs) classes.push(classMap.xs);
		if (width >= breakpoints.sm && classMap.sm) classes.push(classMap.sm);
		if (width >= breakpoints.md && classMap.md) classes.push(classMap.md);
		if (width >= breakpoints.lg && classMap.lg) classes.push(classMap.lg);
		if (width >= breakpoints.xl && classMap.xl) classes.push(classMap.xl);
		if (width >= breakpoints['2xl'] && classMap['2xl']) classes.push(classMap['2xl']);

		return classes.join(' ');
	}
</script>

<!-- Development helper (only shows in development mode) -->
{#if browser && import.meta.env.DEV}
	<div class="breakpoint-indicator">
		<div class="indicator-content">
			<span class="breakpoint-name">{$currentBreakpoint}</span>
			<span class="screen-size">{$screenWidth}×{$screenHeight}</span>
			<span class="device-type">
				{$isMobile ? 'Mobile' : $isTablet ? 'Tablet' : 'Desktop'}
			</span>
			<span class="orientation">{$orientation}</span>
		</div>
	</div>
{/if}

<style>
	.breakpoint-indicator {
		position: fixed;
		bottom: 1rem;
		right: 1rem;
		background: rgba(0, 0, 0, 0.8);
		color: white;
		padding: 0.5rem 0.75rem;
		border-radius: 0.5rem;
		font-family: monospace;
		font-size: 0.75rem;
		z-index: 10000;
		pointer-events: none;
		backdrop-filter: blur(4px);
	}

	.indicator-content {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		text-align: center;
	}

	.breakpoint-name {
		font-weight: bold;
		color: #10b981;
	}

	.screen-size {
		color: #60a5fa;
	}

	.device-type {
		color: #f59e0b;
	}

	.orientation {
		color: #ec4899;
	}

	/* Hide indicator on very small screens */
	@media (max-width: 480px) {
		.breakpoint-indicator {
			display: none;
		}
	}

	/* Print styles */
	@media print {
		.breakpoint-indicator {
			display: none;
		}
	}
</style>
