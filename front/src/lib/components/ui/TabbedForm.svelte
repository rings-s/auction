<!-- src/lib/components/ui/TabbedForm.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';
	import MobileTabNavigation from './MobileTabNavigation.svelte';

	// Props
	export let tabs = [];
	export let currentTab = 0;
	export let validationErrors = {};
	export let showProgressBar = true;
	export let allowFreeNavigation = false;
	export let completedTabs = [];
	export let disabledTabs = [];

	const dispatch = createEventDispatcher();

	// Reactive values
	$: totalTabs = tabs.length;
	$: progressPercentage = ((currentTab + 1) / totalTabs) * 100;

	// Navigation functions
	function goToTab(index) {
		if (allowFreeNavigation || canNavigateToTab(index)) {
			currentTab = index;
			dispatch('tabChange', { tab: index, tabData: tabs[index] });
		}
	}

	function canNavigateToTab(index) {
		// Can always go back to previous tabs
		if (index < currentTab) return true;
		
		// Can only go forward if current tab is completed or no validation errors
		if (index === currentTab + 1) {
			return completedTabs.includes(currentTab) || !hasValidationErrors(currentTab);
		}
		
		return false;
	}

	function hasValidationErrors(tabIndex) {
		const tab = tabs[tabIndex];
		if (!tab?.fields) return false;
		
		return tab.fields.some(field => validationErrors[field]);
	}

	function getTabStatus(index) {
		if (completedTabs.includes(index)) return 'completed';
		if (hasValidationErrors(index)) return 'error';
		if (index === currentTab) return 'active';
		if (disabledTabs.includes(index)) return 'disabled';
		return 'pending';
	}

	function getTabIcon(tab, status) {
		if (status === 'completed') {
			return '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
		}
		if (status === 'error') {
			return '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>';
		}
		return tab.icon || '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle></svg>';
	}

	function handleTabChange(event) {
		currentTab = event.detail.tab;
		dispatch('tabChange', event.detail);
	}
</script>

<div class="w-full">
	<!-- Mobile Navigation -->
	<MobileTabNavigation
		{tabs}
		{currentTab}
		{completedTabs}
		{validationErrors}
		{disabledTabs}
		on:tabChange={handleTabChange}
	>
		<!-- Desktop Navigation -->
		<div class="hidden sm:block">
			<!-- Progress Bar -->
			{#if showProgressBar}
				<div class="mb-6">
					<div class="flex items-center justify-between mb-2">
						<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
							{$t('form.progress', 'Progress')}
						</span>
						<span class="text-sm text-gray-500 dark:text-gray-400">
							{currentTab + 1} {$t('form.of', 'of')} {totalTabs}
						</span>
					</div>
					<div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
						<div 
							class="bg-primary-600 h-2 rounded-full transition-all duration-300 ease-in-out" 
							style="width: {progressPercentage}%"
						></div>
					</div>
				</div>
			{/if}

			<!-- Desktop Tab Navigation -->
			<div class="border-b border-gray-200 dark:border-gray-700 mb-6">
				<nav class="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs" role="tablist">
					{#each tabs as tab, index}
						{@const status = getTabStatus(index)}
						{@const isClickable = allowFreeNavigation || canNavigateToTab(index)}
						
						<button
							type="button"
							role="tab"
							aria-selected={index === currentTab}
							aria-controls="tab-panel-{index}"
							tabindex={index === currentTab ? 0 : -1}
							class="flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 {
								status === 'active' 
									? 'border-primary-500 text-primary-600 dark:text-primary-400' 
									: status === 'completed'
									? 'border-transparent text-green-600 hover:text-green-800 hover:border-green-300 dark:text-green-400 dark:hover:text-green-300'
									: status === 'error'
									? 'border-transparent text-red-600 hover:text-red-800 hover:border-red-300 dark:text-red-400 dark:hover:text-red-300'
									: status === 'disabled'
									? 'border-transparent text-gray-400 cursor-not-allowed dark:text-gray-600'
									: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
							} {isClickable ? 'cursor-pointer' : 'cursor-not-allowed'}"
							on:click={() => isClickable && goToTab(index)}
							disabled={!isClickable}
						>
							<span 
								class="flex-shrink-0" 
								class:text-green-500={status === 'completed'} 
								class:text-red-500={status === 'error'}
								aria-hidden="true"
							>
								{@html getTabIcon(tab, status)}
							</span>
							<span>{tab.label}</span>
							{#if tab.badge}
								<span class="ml-2 bg-gray-100 text-gray-900 py-0.5 px-2 rounded-full text-xs font-medium dark:bg-gray-800 dark:text-gray-100">
									{tab.badge}
								</span>
							{/if}
						</button>
					{/each}
				</nav>
			</div>
		</div>
	</MobileTabNavigation>

	<!-- Tab Content -->
	<div class="tab-content" role="tabpanel" id="tab-panel-{currentTab}" aria-labelledby="tab-{currentTab}">
		<slot {currentTab} {tabs} />
	</div>
</div>

<style>
	.tab-content {
		min-height: 300px;
	}
	
	/* Mobile responsive adjustments */
	@media (max-width: 640px) {
		.tab-content {
			min-height: 250px;
			padding-top: 1rem;
		}
	}

	/* Focus styles for accessibility */
	nav button:focus {
		outline: 2px solid transparent;
		outline-offset: 2px;
	}

	/* High contrast mode support */
	@media (prefers-contrast: high) {
		nav button {
			border-width: 2px;
		}
	}

	/* Reduced motion support */
	@media (prefers-reduced-motion: reduce) {
		nav button {
			transition: none;
		}
		
		.bg-primary-600 {
			transition: none;
		}
	}
</style>