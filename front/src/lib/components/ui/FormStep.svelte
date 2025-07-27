<!-- src/lib/components/ui/FormStep.svelte -->
<script>
	import { createEventDispatcher } from 'svelte';
	import { t } from '$lib/i18n';

	// Props
	export let step = {};
	export let isActive = false;
	export let isCompleted = false;
	export let hasError = false;
	export let canProceed = true;
	export let isFirstStep = false;
	export let isLastStep = false;
	export let showNavigation = true;
	export let loading = false;

	const dispatch = createEventDispatcher();

	function handleNext() {
		dispatch('next');
	}

	function handlePrevious() {
		dispatch('previous');
	}

	function handleSubmit() {
		dispatch('submit');
	}
</script>

{#if isActive}
	<div class="form-step" data-step={step.id}>
		<!-- Step Header -->
		<div class="mb-6">
			<h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
				{step.title}
			</h2>
			{#if step.description}
				<p class="text-sm text-gray-600 dark:text-gray-400">
					{step.description}
				</p>
			{/if}
		</div>

		<!-- Step Content -->
		<div class="step-content mb-8">
			<slot />
		</div>

		<!-- Navigation Controls -->
		{#if showNavigation}
			<div class="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
				<div>
					{#if !isFirstStep}
						<button
							type="button"
							class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
							on:click={handlePrevious}
							disabled={loading}
						>
							<svg class="mr-2 -ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
							</svg>
							{$t('form.previous', 'Previous')}
						</button>
					{/if}
				</div>

				<div class="flex space-x-3">
					{#if !isLastStep}
						<button
							type="button"
							class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
							on:click={handleNext}
							disabled={!canProceed || loading}
							class:opacity-50={!canProceed}
						>
							{loading ? $t('form.processing', 'Processing...') : $t('form.next', 'Next')}
							{#if !loading}
								<svg class="ml-2 -mr-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
								</svg>
							{:else}
								<svg class="ml-2 -mr-1 w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
							{/if}
						</button>
					{:else}
						<button
							type="button"
							class="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
							on:click={handleSubmit}
							disabled={!canProceed || loading}
							class:opacity-50={!canProceed}
						>
							{#if loading}
								<svg class="mr-2 -ml-1 w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
								</svg>
								{step.submitLoadingText || $t('form.submitting', 'Submitting...')}
							{:else}
								<svg class="mr-2 -ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
								</svg>
								{step.submitText || $t('form.submit', 'Submit')}
							{/if}
						</button>
					{/if}
				</div>
			</div>
		{/if}
	</div>
{/if}

<style>
	.form-step {
		animation: fadeIn 0.3s ease-in-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.step-content {
		min-height: 200px;
	}

	/* Mobile responsive adjustments */
	@media (max-width: 640px) {
		.flex.items-center.justify-between {
			flex-direction: column;
			align-items: stretch;
			gap: 1rem;
		}
		
		.flex.space-x-3 {
			justify-content: center;
		}
	}
</style>