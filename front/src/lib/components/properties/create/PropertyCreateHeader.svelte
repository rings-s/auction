<script>
	import { t } from '$lib/i18n';

	export let currentStep;
	export let totalSteps;
	export const loading = false; // External reference only

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
</script>

<div class="rounded-t-xl bg-white shadow-md dark:bg-gray-800">
	<div class="p-6">
		<div class="flex flex-col justify-between gap-4 lg:flex-row">
			<div class="flex-grow">
				<h1 class="text-2xl font-bold text-gray-900 sm:text-3xl dark:text-white">
					{$t('property.createProperty')}
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
