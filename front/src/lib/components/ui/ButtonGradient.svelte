<!-- Enhanced Gradient Button Component for Real Estate Auction App -->
<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	// Props with enhanced gradient variants
	export let variant = 'primary'; // primary, secondary, success, danger, warning, info, auction, property
	export let size = 'md'; // xs, sm, md, lg, xl
	export let type = 'button';
	export let disabled = false;
	export let loading = false;
	export let fullWidth = false;
	export let icon = null;
	export let iconPosition = 'left'; // left, right
	export let animateOnHover = true;
	export let glowEffect = false;
	export let pulseOnClick = true;

	// Enhanced gradient variant configurations
	const variants = {
		primary: {
			base: 'bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600',
			hover: 'hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700',
			active: 'active:from-blue-800 active:via-purple-800 active:to-indigo-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40',
			glow: 'before:bg-gradient-to-r before:from-blue-400 before:via-purple-400 before:to-indigo-400'
		},
		secondary: {
			base: 'bg-gradient-to-r from-gray-600 via-slate-600 to-gray-700',
			hover: 'hover:from-gray-700 hover:via-slate-700 hover:to-gray-800',
			active: 'active:from-gray-800 active:via-slate-800 active:to-gray-900',
			text: 'text-white',
			shadow: 'shadow-lg shadow-gray-500/30 hover:shadow-xl hover:shadow-gray-500/40',
			glow: 'before:bg-gradient-to-r before:from-gray-400 before:via-slate-400 before:to-gray-500'
		},
		success: {
			base: 'bg-gradient-to-r from-green-500 via-emerald-500 to-teal-600',
			hover: 'hover:from-green-600 hover:via-emerald-600 hover:to-teal-700',
			active: 'active:from-green-700 active:via-emerald-700 active:to-teal-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-green-500/30 hover:shadow-xl hover:shadow-green-500/40',
			glow: 'before:bg-gradient-to-r before:from-green-300 before:via-emerald-300 before:to-teal-400'
		},
		danger: {
			base: 'bg-gradient-to-r from-red-500 via-pink-500 to-rose-600',
			hover: 'hover:from-red-600 hover:via-pink-600 hover:to-rose-700',
			active: 'active:from-red-700 active:via-pink-700 active:to-rose-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40',
			glow: 'before:bg-gradient-to-r before:from-red-300 before:via-pink-300 before:to-rose-400'
		},
		warning: {
			base: 'bg-gradient-to-r from-yellow-500 via-orange-500 to-amber-600',
			hover: 'hover:from-yellow-600 hover:via-orange-600 hover:to-amber-700',
			active: 'active:from-yellow-700 active:via-orange-700 active:to-amber-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-yellow-500/30 hover:shadow-xl hover:shadow-yellow-500/40',
			glow: 'before:bg-gradient-to-r before:from-yellow-300 before:via-orange-300 before:to-amber-400'
		},
		info: {
			base: 'bg-gradient-to-r from-cyan-500 via-blue-500 to-sky-600',
			hover: 'hover:from-cyan-600 hover:via-blue-600 hover:to-sky-700',
			active: 'active:from-cyan-700 active:via-blue-700 active:to-sky-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-cyan-500/30 hover:shadow-xl hover:shadow-cyan-500/40',
			glow: 'before:bg-gradient-to-r before:from-cyan-300 before:via-blue-300 before:to-sky-400'
		},
		auction: {
			base: 'bg-gradient-to-r from-orange-500 via-red-500 to-pink-600',
			hover: 'hover:from-orange-600 hover:via-red-600 hover:to-pink-700',
			active: 'active:from-orange-700 active:via-red-700 active:to-pink-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40',
			glow: 'before:bg-gradient-to-r before:from-orange-300 before:via-red-300 before:to-pink-400'
		},
		property: {
			base: 'bg-gradient-to-r from-emerald-500 via-green-500 to-lime-600',
			hover: 'hover:from-emerald-600 hover:via-green-600 hover:to-lime-700',
			active: 'active:from-emerald-700 active:via-green-700 active:to-lime-800',
			text: 'text-white',
			shadow: 'shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40',
			glow: 'before:bg-gradient-to-r before:from-emerald-300 before:via-green-300 before:to-lime-400'
		}
	};

	// Size configurations
	const sizes = {
		xs: 'px-3 py-1.5 text-xs',
		sm: 'px-4 py-2 text-sm',
		md: 'px-6 py-3 text-base',
		lg: 'px-8 py-4 text-lg',
		xl: 'px-10 py-5 text-xl'
	};

	// Get current variant styles
	$: variantStyles = variants[variant] || variants.primary;
	$: sizeStyles = sizes[size] || sizes.md;

	// Handle click with pulse animation
	function handleClick(event) {
		if (disabled || loading) return;

		dispatch('click', event);

		if (pulseOnClick) {
			event.currentTarget.classList.add('animate-pulse-soft');
			setTimeout(() => {
				event.currentTarget.classList.remove('animate-pulse-soft');
			}, 200);
		}
	}
</script>

<button
	{type}
	{disabled}
	class="
		relative transform overflow-hidden rounded-xl font-semibold transition-all duration-300 ease-out
		{variantStyles.base}
		{variantStyles.hover}
		{variantStyles.active}
		{variantStyles.text}
		{variantStyles.shadow}
		{sizeStyles}
		{fullWidth ? 'w-full' : ''}
		{animateOnHover ? 'hover:-translate-y-0.5 hover:scale-[1.02]' : ''}
		{disabled ? 'transform-none cursor-not-allowed opacity-50' : 'cursor-pointer'}
		{loading ? 'cursor-wait' : ''}
		{glowEffect
		? `before:absolute before:inset-0 before:rounded-xl before:opacity-0 before:transition-opacity before:duration-300 hover:before:opacity-20 ${variantStyles.glow}`
		: ''}
		focus:ring-opacity-50 focus:ring-4 focus:ring-offset-2 focus:outline-none
		active:scale-95
	"
	on:click={handleClick}
	{...$$restProps}
>
	<!-- Shimmer overlay effect -->
	<div
		class="absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-1000 hover:translate-x-full"
	></div>

	<!-- Button content -->
	<div class="relative flex items-center justify-center space-x-2">
		{#if loading}
			<svg class="mr-2 -ml-1 h-4 w-4 animate-spin text-current" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
				></circle>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				></path>
			</svg>
		{:else if icon && iconPosition === 'left'}
			<span class="flex-shrink-0">
				{@html icon}
			</span>
		{/if}

		<span class="truncate">
			<slot />
		</span>

		{#if icon && iconPosition === 'right' && !loading}
			<span class="flex-shrink-0">
				{@html icon}
			</span>
		{/if}
	</div>

	<!-- Ripple effect on click -->
	{#if pulseOnClick}
		<div
			class="pointer-events-none absolute inset-0 rounded-xl bg-white/10 opacity-0 transition-opacity"
		></div>
	{/if}
</button>

<style>
	/* Enhanced animations */
	@keyframes pulse-soft {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.8;
		}
	}

	.animate-pulse-soft {
		animation: pulse-soft 0.2s ease-in-out;
	}

	/* Glow effect */
	button:hover::before {
		animation: shimmer 2s infinite;
	}

	@keyframes shimmer {
		0% {
			transform: translateX(-100%) skewX(-12deg);
		}
		100% {
			transform: translateX(200%) skewX(-12deg);
		}
	}
</style>
