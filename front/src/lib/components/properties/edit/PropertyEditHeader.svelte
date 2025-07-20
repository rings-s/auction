<script>
	import { t } from '$lib/i18n';

	export let property;
	export let currentStep;
	export let totalSteps;
	export const loading = false; // External reference only
	export let hasUnsavedChanges;

	const steps = [
		{ id: 1, key: 'basicInfo', icon: 'document' },
		{ id: 2, key: 'location', icon: 'map-pin' },
		{ id: 3, key: 'details', icon: 'home' },
		{ id: 4, key: 'financial', icon: 'currency' }
	];

	function getIcon(iconName) {
		switch (iconName) {
			case 'document':
				return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`;
			case 'map-pin':
				return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`;
			case 'home':
				return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>`;
			case 'currency':
				return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
			default:
				return '';
		}
	}

	function formatCurrency(value) {
		if (!value) return '$0';
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			maximumFractionDigits: 0
		}).format(value);
	}
</script>

<div class="rounded-t-xl bg-white shadow-md dark:bg-gray-800">
	<div class="p-6">
		<div class="flex flex-col justify-between gap-4 lg:flex-row">
			<div class="flex-grow">
				<!-- Status Badges -->
				<div class="mb-3 flex flex-wrap gap-2">
					<span
						class={`inline-flex items-center rounded-md px-2.5 py-0.5 text-sm font-medium 
            ${
							property?.status === 'available'
								? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
								: property?.status === 'under_contract'
									? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
									: property?.status === 'sold'
										? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
										: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
						}`}
					>
						{property?.status_display || $t('property.statusTypes.available')}
					</span>

					{#if property?.is_featured}
						<span
							class="inline-flex items-center rounded-md bg-amber-100 px-2.5 py-0.5 text-sm font-medium text-amber-800 dark:bg-amber-900 dark:text-amber-200"
						>
							<svg class="mr-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
								<path
									d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
								/>
							</svg>
							{$t('property.featured')}
						</span>
					{/if}

					{#if hasUnsavedChanges}
						<span
							class="inline-flex items-center rounded-md bg-orange-100 px-2.5 py-0.5 text-sm font-medium text-orange-800 dark:bg-orange-900 dark:text-orange-200"
						>
							<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
								/>
							</svg>
							{$t('property.unsavedChanges')}
						</span>
					{/if}
				</div>

				<h1 class="text-2xl font-bold text-gray-900 sm:text-3xl dark:text-white">
					{$t('property.editProperty')}: {property?.title || ''}
				</h1>

				<p class="mt-2 text-base text-gray-500 dark:text-gray-400">
					{#if currentStep === 1}
						{$t('property.basicInfoDesc')}
					{:else if currentStep === 2}
						{$t('property.locationDesc')}
					{:else if currentStep === 3}
						{$t('property.detailsDesc')}
					{:else if currentStep === 4}
						{$t('property.financialDesc')}
					{/if}
				</p>
			</div>

			<div class="flex flex-col items-start justify-center lg:items-end">
				<div class="flex flex-col items-center lg:items-end">
					<p class="text-sm text-gray-500 dark:text-gray-400">
						{$t('common.step')}
						{currentStep}
						{$t('common.of')}
						{totalSteps}
					</p>
					<p class="text-primary-600 dark:text-primary-400 text-lg font-semibold">
						{Math.round((currentStep / totalSteps) * 100)}% {$t('common.complete')}
					</p>
					{#if property?.market_value}
						<p class="mt-1 text-xl font-bold text-gray-900 dark:text-white">
							{formatCurrency(property.market_value)}
						</p>
					{/if}
				</div>
			</div>
		</div>
	</div>

	<div class="px-6 pb-6">
		<div class="h-2.5 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
			<div
				class="from-primary-500 to-secondary-500 dark:from-primary-600 dark:to-secondary-400 h-2.5 rounded-full bg-gradient-to-r transition-all duration-500 ease-out"
				style="width: {(currentStep / totalSteps) * 100}%"
			></div>
		</div>

		<div class="relative mt-6 flex justify-between">
			<div class="absolute top-4 right-0 left-0 -z-10 h-0.5 bg-gray-200 dark:bg-gray-700"></div>

			{#each steps as step}
				<div class="z-10 text-center">
					<div
						class={`mx-auto flex h-8 w-8 cursor-pointer items-center justify-center rounded-full 
                      border-2 text-xs font-medium transition-all duration-300 
                      ${
												currentStep > step.id
													? 'bg-primary-500 border-primary-500 dark:bg-primary-600 text-white'
													: currentStep === step.id
														? 'border-primary-500 text-primary-600 dark:text-primary-400 dark:border-primary-400 bg-white dark:bg-gray-800'
														: 'border-gray-300 bg-white text-gray-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400'
											}`}
					>
						{#if currentStep > step.id}
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M5 13l4 4L19 7"
								/>
							</svg>
						{:else}
							{step.id}
						{/if}
					</div>
					<div class="mt-2 hidden text-xs font-medium text-gray-500 sm:block dark:text-gray-400">
						{$t(`property.${step.key}`)}
					</div>
				</div>
			{/each}
		</div>
	</div>

	<div
		class="scrollbar-hide flex overflow-x-auto border-t border-gray-200 px-4 pt-1 dark:border-gray-700"
	>
		{#each steps as step}
			<button
				class={`flex items-center border-b-2 px-4 py-4 text-sm font-medium whitespace-nowrap
          ${
						currentStep === step.id
							? 'border-primary-500 text-primary-600 dark:text-primary-400'
							: 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-300'
					} transition-colors duration-200`}
				disabled={true}
				aria-selected={currentStep === step.id}
				role="tab"
			>
				{@html getIcon(step.icon)}
				<span class="ml-2">{$t(`property.${step.key}`)}</span>
			</button>
		{/each}
	</div>
</div>

<style>
	.scrollbar-hide {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}

	.scrollbar-hide::-webkit-scrollbar {
		display: none;
	}
</style>
