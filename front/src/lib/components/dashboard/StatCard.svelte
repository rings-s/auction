<script>
	import { t } from '$lib/i18n';
	import { createEventDispatcher } from 'svelte';
	import { fade, scale } from 'svelte/transition';

	export let title = '';
	export let value = 0;
	export let change = null;
	export let icon = '';
	export let color = 'primary';
	export let loading = false;
	export let href = null;
	export let clickable = false;
	export let compact = false;
	export let trend = null; // 'up', 'down', 'stable'

	const dispatch = createEventDispatcher();

	// Enhanced color schemes with gradients
	const colorSchemes = {
		primary: {
			gradient: 'from-blue-500 to-indigo-600',
			background:
				'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20',
			border: 'border-blue-200 dark:border-blue-700',
			iconBg: 'bg-gradient-to-br from-blue-500 to-indigo-600',
			iconText: 'text-white',
			hoverShadow: 'hover:shadow-blue-500/25'
		},
		success: {
			gradient: 'from-emerald-500 to-green-600',
			background:
				'bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20',
			border: 'border-emerald-200 dark:border-emerald-700',
			iconBg: 'bg-gradient-to-br from-emerald-500 to-green-600',
			iconText: 'text-white',
			hoverShadow: 'hover:shadow-emerald-500/25'
		},
		warning: {
			gradient: 'from-amber-500 to-orange-600',
			background:
				'bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20',
			border: 'border-amber-200 dark:border-amber-700',
			iconBg: 'bg-gradient-to-br from-amber-500 to-orange-600',
			iconText: 'text-white',
			hoverShadow: 'hover:shadow-amber-500/25'
		},
		error: {
			gradient: 'from-red-500 to-rose-600',
			background:
				'bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20',
			border: 'border-red-200 dark:border-red-700',
			iconBg: 'bg-gradient-to-br from-red-500 to-rose-600',
			iconText: 'text-white',
			hoverShadow: 'hover:shadow-red-500/25'
		},
		info: {
			gradient: 'from-cyan-500 to-blue-600',
			background:
				'bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900/20 dark:to-blue-900/20',
			border: 'border-cyan-200 dark:border-cyan-700',
			iconBg: 'bg-gradient-to-br from-cyan-500 to-blue-600',
			iconText: 'text-white',
			hoverShadow: 'hover:shadow-cyan-500/25'
		}
	};

	$: currentScheme = colorSchemes[color] || colorSchemes.primary;

	// Trend icons
	const trendIcons = {
		up: `<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
			<path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
		</svg>`,
		down: `<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
			<path fill-rule="evenodd" d="M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
		</svg>`,
		stable: `<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
			<path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
		</svg>`
	};

	function handleClick() {
		if (clickable && !loading) {
			dispatch('click');
		}
	}

	function handleKeydown(event) {
		if (clickable && !loading && (event.key === 'Enter' || event.key === ' ')) {
			event.preventDefault();
			dispatch('click');
		}
	}

	function formatValue(val) {
		if (typeof val === 'number') {
			return val.toLocaleString();
		}
		return val;
	}

	// Determine interactive classes
	$: interactiveClasses =
		href || clickable
			? `transform transition-all duration-300 hover:scale-[1.02] hover:shadow-xl ${currentScheme.hoverShadow} cursor-pointer`
			: 'transition-shadow duration-200';

	$: baseCardClasses = `
		relative overflow-hidden rounded-xl border bg-white dark:bg-gray-800 
		${currentScheme.border} ${currentScheme.background}
		${compact ? 'p-4' : 'p-6'} 
		${interactiveClasses}
		backdrop-blur-sm
	`.trim();
</script>

<!-- Enhanced Modern StatCard Template -->
{#if href}
	<a {href} class={baseCardClasses} in:scale={{ duration: 200, delay: 100 }}>
		<div class="relative z-10">
			<!-- Decorative gradient element -->
			<div
				class="absolute -top-1 -right-1 h-16 w-16 bg-gradient-to-br {currentScheme.gradient} rounded-full opacity-5 blur-xl"
			></div>

			<div class="flex items-start justify-between">
				<div class="flex-1">
					<div class="mb-3 flex items-center justify-between">
						<h3 class="truncate text-sm font-medium text-gray-600 dark:text-gray-400">
							{title}
						</h3>
						{#if trend && trendIcons[trend]}
							<div
								class="flex items-center space-x-1 text-{trend === 'up'
									? 'emerald'
									: trend === 'down'
										? 'red'
										: 'gray'}-500"
							>
								{@html trendIcons[trend]}
							</div>
						{/if}
					</div>

					{#if loading}
						<div class="space-y-2">
							<div class="h-8 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-4 w-2/3 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
						</div>
					{:else}
						<div class="space-y-1">
							<div class="flex items-baseline space-x-2">
								<span class="text-2xl font-bold text-gray-900 dark:text-white">
									{formatValue(value)}
								</span>
								{#if change}
									<span
										class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium {change.type ===
										'increase'
											? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-400'
											: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'}"
									>
										{change.type === 'increase' ? '+' : ''}{change.value}%
									</span>
								{/if}
							</div>
						</div>
					{/if}
				</div>

				{#if icon}
					<div class="ml-4 flex-shrink-0">
						<div
							class="h-12 w-12 rounded-xl {currentScheme.iconBg} {currentScheme.iconText} flex items-center justify-center shadow-lg"
						>
							{@html icon}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</a>
{:else if clickable}
	<button
		type="button"
		class={baseCardClasses}
		on:click={handleClick}
		on:keydown={handleKeydown}
		disabled={loading}
		aria-label={title}
		in:scale={{ duration: 200, delay: 100 }}
	>
		<div class="relative z-10 text-left">
			<!-- Decorative gradient element -->
			<div
				class="absolute -top-1 -right-1 h-16 w-16 bg-gradient-to-br {currentScheme.gradient} rounded-full opacity-5 blur-xl"
			></div>

			<div class="flex items-start justify-between">
				<div class="flex-1">
					<div class="mb-3 flex items-center justify-between">
						<h3 class="truncate text-sm font-medium text-gray-600 dark:text-gray-400">
							{title}
						</h3>
						{#if trend && trendIcons[trend]}
							<div
								class="flex items-center space-x-1 text-{trend === 'up'
									? 'emerald'
									: trend === 'down'
										? 'red'
										: 'gray'}-500"
							>
								{@html trendIcons[trend]}
							</div>
						{/if}
					</div>

					{#if loading}
						<div class="space-y-2">
							<div class="h-8 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-4 w-2/3 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
						</div>
					{:else}
						<div class="space-y-1">
							<div class="flex items-baseline space-x-2">
								<span class="text-2xl font-bold text-gray-900 dark:text-white">
									{formatValue(value)}
								</span>
								{#if change}
									<span
										class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium {change.type ===
										'increase'
											? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-400'
											: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'}"
									>
										{change.type === 'increase' ? '+' : ''}{change.value}%
									</span>
								{/if}
							</div>
						</div>
					{/if}
				</div>

				{#if icon}
					<div class="ml-4 flex-shrink-0">
						<div
							class="h-12 w-12 rounded-xl {currentScheme.iconBg} {currentScheme.iconText} flex items-center justify-center shadow-lg"
						>
							{@html icon}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</button>
{:else}
	<div class={baseCardClasses} role="presentation" in:scale={{ duration: 200, delay: 100 }}>
		<div class="relative z-10">
			<!-- Decorative gradient element -->
			<div
				class="absolute -top-1 -right-1 h-16 w-16 bg-gradient-to-br {currentScheme.gradient} rounded-full opacity-5 blur-xl"
			></div>

			<div class="flex items-start justify-between">
				<div class="flex-1">
					<div class="mb-3 flex items-center justify-between">
						<h3 class="truncate text-sm font-medium text-gray-600 dark:text-gray-400">
							{title}
						</h3>
						{#if trend && trendIcons[trend]}
							<div
								class="flex items-center space-x-1 text-{trend === 'up'
									? 'emerald'
									: trend === 'down'
										? 'red'
										: 'gray'}-500"
							>
								{@html trendIcons[trend]}
							</div>
						{/if}
					</div>

					{#if loading}
						<div class="space-y-2">
							<div class="h-8 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-4 w-2/3 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
						</div>
					{:else}
						<div class="space-y-1">
							<div class="flex items-baseline space-x-2">
								<span class="text-2xl font-bold text-gray-900 dark:text-white">
									{formatValue(value)}
								</span>
								{#if change}
									<span
										class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium {change.type ===
										'increase'
											? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-400'
											: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'}"
									>
										{change.type === 'increase' ? '+' : ''}{change.value}%
									</span>
								{/if}
							</div>
						</div>
					{/if}
				</div>

				{#if icon}
					<div class="ml-4 flex-shrink-0">
						<div
							class="h-12 w-12 rounded-xl {currentScheme.iconBg} {currentScheme.iconText} flex items-center justify-center shadow-lg"
						>
							{@html icon}
						</div>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
