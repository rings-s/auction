<script>
	import { t } from '$lib/i18n';
	import { createEventDispatcher } from 'svelte';

	export let title = '';
	export let value = 0;
	export let change = null;
	export let icon = '';
	export let color = 'primary';
	export let loading = false;
	export let href = null;
	export let clickable = false;
	export let compact = false;

	const dispatch = createEventDispatcher();

	const colorClasses = {
		primary:
			'text-primary-600 bg-primary-50 border-primary-100 dark:text-primary-400 dark:bg-primary-900/20 dark:border-primary-800',
		success:
			'text-success-600 bg-success-50 border-success-100 dark:text-success-400 dark:bg-success-900/20 dark:border-success-800',
		warning:
			'text-warning-600 bg-warning-50 border-warning-100 dark:text-warning-400 dark:bg-warning-900/20 dark:border-warning-800',
		danger:
			'text-danger-600 bg-danger-50 border-danger-100 dark:text-danger-400 dark:bg-danger-900/20 dark:border-danger-800',
		info: 'text-primary-600 bg-primary-50 border-primary-100 dark:text-primary-400 dark:bg-primary-900/20 dark:border-primary-800'
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
</script>

{#if href}
	<a
		{href}
		class="block rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 {compact
			? 'p-3'
			: 'p-4'} focus:ring-primary-500 transition-shadow duration-200 hover:shadow-md focus:ring-2 focus:ring-offset-2 focus:outline-none"
	>
		<div class="flex items-center">
			{#if icon}
				<div
					class="flex-shrink-0 {compact
						? 'h-8 w-8'
						: 'h-10 w-10'} flex items-center justify-center rounded-lg {colorClasses[color]}"
				>
					{@html icon}
				</div>
			{/if}

			<div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
				<p class="truncate text-xs font-medium text-gray-600 dark:text-gray-400">{title}</p>

				{#if loading}
					<div class="mt-1 h-6 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
				{:else}
					<div class="flex items-baseline">
						<p class="text-lg font-semibold text-gray-900 dark:text-white">
							{formatValue(value)}
						</p>

						{#if change}
							<span
								class="ml-2 text-xs font-medium {change.type === 'increase'
									? 'text-success-600 dark:text-success-400'
									: 'text-danger-600 dark:text-danger-400'}"
							>
								{change.type === 'increase' ? '+' : ''}{change.value}%
							</span>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</a>
{:else if clickable}
	<button
		type="button"
		class="w-full rounded-lg border border-gray-200 bg-white text-left dark:border-gray-700 dark:bg-gray-800 {compact
			? 'p-3'
			: 'p-4'} focus:ring-primary-500 transition-shadow duration-200 hover:shadow-md focus:ring-2 focus:ring-offset-2 focus:outline-none"
		on:click={handleClick}
		on:keydown={handleKeydown}
		disabled={loading}
		aria-label={title}
	>
		<div class="flex items-center">
			{#if icon}
				<div
					class="flex-shrink-0 {compact
						? 'h-8 w-8'
						: 'h-10 w-10'} flex items-center justify-center rounded-lg {colorClasses[color]}"
				>
					{@html icon}
				</div>
			{/if}

			<div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
				<p class="truncate text-xs font-medium text-gray-600 dark:text-gray-400">{title}</p>

				{#if loading}
					<div class="mt-1 h-6 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
				{:else}
					<div class="flex items-baseline">
						<p class="text-lg font-semibold text-gray-900 dark:text-white">
							{formatValue(value)}
						</p>

						{#if change}
							<span
								class="ml-2 text-xs font-medium {change.type === 'increase'
									? 'text-success-600 dark:text-success-400'
									: 'text-danger-600 dark:text-danger-400'}"
							>
								{change.type === 'increase' ? '+' : ''}{change.value}%
							</span>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</button>
{:else}
	<div
		class="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 {compact
			? 'p-3'
			: 'p-4'} transition-shadow duration-200"
		role="presentation"
	>
		<div class="flex items-center">
			{#if icon}
				<div
					class="flex-shrink-0 {compact
						? 'h-8 w-8'
						: 'h-10 w-10'} flex items-center justify-center rounded-lg {colorClasses[color]}"
				>
					{@html icon}
				</div>
			{/if}

			<div class="flex-1 {icon ? (compact ? 'ml-3' : 'ml-4') : ''}">
				<p class="truncate text-xs font-medium text-gray-600 dark:text-gray-400">{title}</p>

				{#if loading}
					<div class="mt-1 h-6 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
				{:else}
					<div class="flex items-baseline">
						<p class="text-lg font-semibold text-gray-900 dark:text-white">
							{formatValue(value)}
						</p>

						{#if change}
							<span
								class="ml-2 text-xs font-medium {change.type === 'increase'
									? 'text-success-600 dark:text-success-400'
									: 'text-danger-600 dark:text-danger-400'}"
							>
								{change.type === 'increase' ? '+' : ''}{change.value}%
							</span>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
