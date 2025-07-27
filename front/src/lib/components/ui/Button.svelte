<!-- src/lib/components/ui/Button.svelte -->
<script>
	// Props with enhanced gradient variants
	let {
		/** @type {'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost' | 'auction' | 'property'} */
		variant = 'primary',
		/** @type {'sm' | 'default' | 'large'} */
		size = 'default',
		/** @type {'button' | 'submit' | 'reset'} */
		type = 'button',
		disabled = false,
		loading = false,
		fullWidth = false,
		href = null,
		target = null,
		rel = null,
		onClick = null,
		class: class_ = '',
		rounded = 'default', // 'default' | 'full'
		gradientEffect = true, // Enable vibrant gradients
		shimmerEffect = false, // Enable shimmer animation
		glowEffect = false, // Enable glow effect on hover
		onclick,
		children
	} = $props();

	// Enhanced gradient variant classes with vibrant designs
	const variants = {
		primary: gradientEffect
			? `
      bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600
      hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700
      active:from-blue-800 active:via-purple-800 active:to-indigo-800
      text-white border border-transparent
      shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40
      focus:outline-none focus:ring-4 focus:ring-blue-500/50 focus:ring-offset-2
      dark:shadow-blue-400/20 dark:hover:shadow-blue-400/30
    `
			: `
      bg-primary-600 hover:bg-primary-700 
      text-white border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      dark:bg-primary-600 dark:hover:bg-primary-700
    `,
		secondary: gradientEffect
			? `
      bg-gradient-to-r from-gray-600 via-slate-600 to-gray-700
      hover:from-gray-700 hover:via-slate-700 hover:to-gray-800
      active:from-gray-800 active:via-slate-800 active:to-gray-900
      text-white border border-transparent
      shadow-lg shadow-gray-500/30 hover:shadow-xl hover:shadow-gray-500/40
      focus:outline-none focus:ring-4 focus:ring-gray-500/50 focus:ring-offset-2
      dark:shadow-gray-400/20 dark:hover:shadow-gray-400/30
    `
			: `
      bg-white hover:bg-gray-50 
      text-gray-700 border border-gray-300
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-300 dark:border-gray-600
    `,
		outline: `
      bg-transparent hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50
      text-blue-600 hover:text-blue-700 
      border-2 border-blue-300 hover:border-blue-400
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500
      dark:text-blue-400 dark:border-blue-500 dark:hover:bg-gradient-to-r 
      dark:hover:from-blue-950/50 dark:hover:to-purple-950/50
    `,
		danger: gradientEffect
			? `
      bg-gradient-to-r from-red-500 via-pink-500 to-rose-600
      hover:from-red-600 hover:via-pink-600 hover:to-rose-700
      active:from-red-700 active:via-pink-700 active:to-rose-800
      text-white border border-transparent
      shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40
      focus:outline-none focus:ring-4 focus:ring-red-500/50 focus:ring-offset-2
      dark:shadow-red-400/20 dark:hover:shadow-red-400/30
    `
			: `
      bg-red-600 hover:bg-red-700 
      text-white border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500
      dark:bg-red-600 dark:hover:bg-red-700
    `,
		success: gradientEffect
			? `
      bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600
      hover:from-green-600 hover:via-emerald-600 hover:to-teal-700
      active:from-green-700 active:via-emerald-700 active:to-teal-800
      text-white border border-transparent
      shadow-lg shadow-green-500/30 hover:shadow-xl hover:shadow-green-500/40
      focus:outline-none focus:ring-4 focus:ring-green-500/50 focus:ring-offset-2
      dark:shadow-green-400/20 dark:hover:shadow-green-400/30
    `
			: `
      bg-green-600 hover:bg-green-700 
      text-white border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500
      dark:bg-green-600 dark:hover:bg-green-700
    `,
		ghost: `
      bg-transparent hover:bg-gradient-to-r hover:from-gray-50 hover:to-slate-50
      text-gray-700 hover:text-gray-900
      border border-transparent
      focus:outline-none focus:ring-4 focus:ring-gray-500/20
      dark:hover:from-gray-800/50 dark:hover:to-slate-800/50
      dark:text-gray-300 dark:hover:text-white
    `,
		auction: gradientEffect
			? `
      bg-gradient-to-r from-orange-500 via-red-500 to-pink-600
      hover:from-orange-600 hover:via-red-600 hover:to-pink-700
      active:from-orange-700 active:via-red-700 active:to-pink-800
      text-white border border-transparent
      shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40
      focus:outline-none focus:ring-4 focus:ring-orange-500/50 focus:ring-offset-2
      dark:shadow-orange-400/20 dark:hover:shadow-orange-400/30
    `
			: `
      bg-orange-600 hover:bg-orange-700 
      text-white border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500
      dark:bg-orange-600 dark:hover:bg-orange-700
    `,
		property: gradientEffect
			? `
      bg-gradient-to-r from-emerald-500 via-green-500 to-lime-600
      hover:from-emerald-600 hover:via-green-600 hover:to-lime-700
      active:from-emerald-700 active:via-green-700 active:to-lime-800
      text-white border border-transparent
      shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40
      focus:outline-none focus:ring-4 focus:ring-emerald-500/50 focus:ring-offset-2
      dark:shadow-emerald-400/20 dark:hover:shadow-emerald-400/30
    `
			: `
      bg-emerald-600 hover:bg-emerald-700 
      text-white border border-transparent
      shadow-sm hover:shadow-md
      focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500
      dark:bg-emerald-600 dark:hover:bg-emerald-700
    `
	};

	// Simplified size classes
	const sizes = {
		sm: `
      px-3 py-1.5 
      text-sm font-medium
    `,
		default: `
      px-4 py-2.5 
      text-sm font-medium
    `,
		large: `
      px-6 py-3 
      text-base font-medium
    `
	};

	// Border radius options
	const roundedStyles = {
		default: 'rounded-lg',
		full: 'rounded-full'
	};

	// Base classes with enhanced animations
	const baseClasses = `
    inline-flex items-center justify-center
    font-semibold
    transition-all duration-300 ease-out
    relative overflow-hidden
    ${gradientEffect ? 'transform-gpu' : ''}
  `;

	// Enhanced state classes with animations
	let stateClasses = $derived(
		(() => {
			if (disabled || loading) {
				return 'opacity-50 cursor-not-allowed transform-none';
			}
			return `transform hover:scale-[1.02] hover:-translate-y-0.5 active:scale-95 
			${glowEffect ? 'hover:shadow-2xl' : ''}`;
		})()
	);

	// Generate glow class for gradient variants
	let glowClass = $derived(glowEffect && gradientEffect ? getGlowClass(variant) : '');

	function getGlowClass(variant) {
		const glowMap = {
			primary: 'hover:shadow-blue-500/25',
			secondary: 'hover:shadow-gray-500/25',
			danger: 'hover:shadow-red-500/25',
			success: 'hover:shadow-green-500/25',
			auction: 'hover:shadow-orange-500/25',
			property: 'hover:shadow-emerald-500/25'
		};
		return glowMap[variant] || 'hover:shadow-blue-500/25';
	}

	// Generate final class string with enhanced effects
	let buttonClass = $derived(
		[
			baseClasses,
			sizes[size] || sizes.default,
			variants[variant] || variants.primary,
			roundedStyles[rounded] || roundedStyles.default,
			fullWidth ? 'w-full' : '',
			stateClasses,
			glowClass,
			class_
		]
			.filter(Boolean)
			.join(' ')
			.trim()
	);

	// Handle click events
	function handleClick(event) {
		if (disabled || loading) {
			event.preventDefault();
			return;
		}

		if (onClick) {
			onClick(event);
		}

		if (onclick) {
			onclick(event);
		}
	}
</script>

{#if href}
	<a
		{href}
		{target}
		{rel}
		class={buttonClass}
		aria-disabled={disabled || loading}
		tabindex={disabled || loading ? -1 : 0}
		onclick={handleClick}
		role="button"
	>
		<!-- Shimmer effect overlay -->
		{#if shimmerEffect && gradientEffect && !disabled}
			<div
				class="pointer-events-none absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 hover:translate-x-full"
			></div>
		{/if}

		<!-- Button content -->
		<div class="relative flex items-center justify-center">
			{#if loading}
				<svg
					class="h-4 w-4 animate-spin {children ? 'mr-2' : ''}"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
				>
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
					></circle>
					<path
						class="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
			{/if}
			{@render children()}
		</div>
	</a>
{:else}
	<button
		{type}
		{disabled}
		class={buttonClass}
		aria-disabled={disabled || loading}
		onclick={handleClick}
	>
		<!-- Shimmer effect overlay -->
		{#if shimmerEffect && gradientEffect && !disabled}
			<div
				class="pointer-events-none absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 hover:translate-x-full"
			></div>
		{/if}

		<!-- Button content -->
		<div class="relative flex items-center justify-center">
			{#if loading}
				<svg
					class="h-4 w-4 animate-spin {children ? 'mr-2' : ''}"
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
				>
					<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
					></circle>
					<path
						class="opacity-75"
						fill="currentColor"
						d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
					></path>
				</svg>
			{/if}
			{@render children()}
		</div>
	</button>
{/if}

<style>
	/* RTL support for loading spinner */
	:global([dir='rtl']) .mr-2 {
		margin-right: 0;
		margin-left: 0.5rem;
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		:global(button),
		:global(a[role='button']) {
			transition: none !important;
		}

		:global(button:hover),
		:global(a[role='button']:hover) {
			transform: none !important;
		}

		:global(.animate-spin) {
			animation: none !important;
		}
	}
</style>
