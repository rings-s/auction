<!-- src/lib/components/ui/MobileTabNavigation.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';

	// Props
	export let tabs = [];
	export let currentTab = 0;
	export let completedTabs = [];
	export let validationErrors = {};
	export let disabledTabs = [];

	const dispatch = createEventDispatcher();

	function getTabStatus(index) {
		if (completedTabs.includes(index)) return 'completed';
		if (hasValidationErrors(index)) return 'error';
		if (index === currentTab) return 'active';
		if (disabledTabs.includes(index)) return 'disabled';
		return 'pending';
	}

	function hasValidationErrors(tabIndex) {
		const tab = tabs[tabIndex];
		if (!tab?.fields) return false;
		return tab.fields.some(field => validationErrors[field]);
	}

	function handleTabClick(index) {
		if (!disabledTabs.includes(index)) {
			dispatch('tabChange', { tab: index, tabData: tabs[index] });
		}
	}

	function getStatusIcon(status) {
		switch (status) {
			case 'completed':
				return '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>';
			case 'error':
				return '<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
			case 'active':
				return '<div class="w-2 h-2 bg-current rounded-full animate-pulse"></div>';
			default:
				return '<div class="w-2 h-2 bg-current rounded-full opacity-50"></div>';
		}
	}

	function getStatusClasses(status) {
		const baseClasses = 'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-all duration-200';
		
		switch (status) {
			case 'completed':
				return `${baseClasses} bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300`;
			case 'error':
				return `${baseClasses} bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300`;
			case 'active':
				return `${baseClasses} bg-primary-100 text-primary-600 ring-2 ring-primary-600 ring-offset-2 dark:bg-primary-900 dark:text-primary-300`;
			case 'disabled':
				return `${baseClasses} bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600 cursor-not-allowed`;
			default:
				return `${baseClasses} bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700`;
		}
	}
</script>

<!-- Mobile Tab Navigation -->
<div class="block sm:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
	<!-- Current Tab Info -->
	<div class="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
		<div class="flex items-center justify-between">
			<div>
				<h3 class="text-sm font-medium text-gray-900 dark:text-gray-100">
					{tabs[currentTab]?.label}
				</h3>
				<p class="text-xs text-gray-500 dark:text-gray-400">
					{$t('form.step')} {currentTab + 1} {$t('form.of')} {tabs.length}
				</p>
			</div>
			<div class="flex items-center space-x-2">
				{#if getTabStatus(currentTab) === 'completed'}
					<span class="text-green-600 dark:text-green-400">
						{@html getStatusIcon('completed')}
					</span>
				{:else if getTabStatus(currentTab) === 'error'}
					<span class="text-red-600 dark:text-red-400">
						{@html getStatusIcon('error')}
					</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- Horizontal Scroll Tabs -->
	<div class="overflow-x-auto scrollbar-hide">
		<div class="flex space-x-1 px-4 py-2" style="min-width: max-content;">
			{#each tabs as tab, index}
				{@const status = getTabStatus(index)}
				{@const isClickable = !disabledTabs.includes(index)}
				
				<button
					type="button"
					class="flex-shrink-0 flex flex-col items-center space-y-1 px-3 py-2 rounded-md transition-all duration-200 {
						status === 'active' 
							? 'bg-primary-50 text-primary-600 dark:bg-primary-900/20 dark:text-primary-400' 
							: 'text-gray-500 hover:text-gray-700 hover:bg-gray-50 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:bg-gray-700'
					} {isClickable ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'}"
					on:click={() => isClickable && handleTabClick(index)}
					disabled={!isClickable}
					aria-current={index === currentTab ? 'step' : undefined}
				>
					<!-- Icon/Status Indicator -->
					<div class={getStatusClasses(status)}>
						{@html getStatusIcon(status)}
					</div>
					
					<!-- Tab Label -->
					<span class="text-xs font-medium whitespace-nowrap">
						{tab.label}
					</span>
				</button>
			{/each}
		</div>
	</div>
</div>

<!-- Desktop Tab Navigation (Hidden on Mobile) -->
<div class="hidden sm:block">
	<slot />
</div>

<style>
	/* Hide scrollbar but keep functionality */
	.scrollbar-hide {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
	
	.scrollbar-hide::-webkit-scrollbar {
		display: none;
	}

	/* Smooth scroll behavior */
	.overflow-x-auto {
		scroll-behavior: smooth;
	}

	/* Ensure proper touch scrolling on iOS */
	.overflow-x-auto {
		-webkit-overflow-scrolling: touch;
	}
</style>