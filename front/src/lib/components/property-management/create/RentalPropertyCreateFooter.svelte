<!-- src/lib/components/property-management/create/RentalPropertyCreateFooter.svelte -->
<script>
	import { t, locale } from '$lib/i18n';
	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';

	let {
		currentStep,
		totalSteps,
		loading = false,
		uploadingMedia = false,
		uploadProgress = 0,
		onNext,
		onPrev,
		onSubmit
	} = $props();

	let isRTL = $derived($locale === 'ar');
	let isFirstStep = $derived(currentStep === 1);
	let isLastStep = $derived(currentStep === totalSteps);

	// Handle navigation
	function handleNext() {
		if (onNext) {
			onNext();
		}
	}

	function handlePrev() {
		if (onPrev) {
			onPrev();
		}
	}

	function handleSubmit() {
		if (onSubmit) {
			onSubmit();
		}
	}

	// Get next button text
	let nextButtonText = $derived(
		isLastStep ? $t('propertyManagement.createProperty') : $t('common.next')
	);

	// Get button state classes
	function getButtonClasses(variant = 'primary', disabled = false) {
		const baseClasses =
			'inline-flex items-center px-6 py-3 rounded-lg font-medium text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

		if (variant === 'primary') {
			return `${baseClasses} bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-lg hover:from-teal-700 hover:to-cyan-700 hover:shadow-xl focus:ring-teal-500 transform hover:scale-105 disabled:transform-none disabled:hover:shadow-lg`;
		} else if (variant === 'secondary') {
			return `${baseClasses} bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 focus:ring-gray-500`;
		}

		return baseClasses;
	}
</script>

<div
	class="rounded-b-2xl border border-t-0 border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<!-- Progress Bar -->
	<div class="px-8 pt-6">
		<div class="h-2 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
			<div
				class="h-2 rounded-full bg-gradient-to-r from-teal-500 to-cyan-500 transition-all duration-500 ease-out"
				style="width: {(currentStep / totalSteps) * 100}%"
			></div>
		</div>
		<div class="mt-2 flex justify-between text-xs text-gray-500 dark:text-gray-400">
			<span
				>{$t('propertyManagement.create.step')} {currentStep} {$t('common.of')} {totalSteps}</span
			>
			<span>{Math.round((currentStep / totalSteps) * 100)}% {$t('common.complete')}</span>
		</div>
	</div>

	<!-- Action Buttons -->
	<div class="flex items-center justify-between p-8">
		<!-- Previous Button -->
		<div class="flex-1">
			{#if !isFirstStep}
				<button
					type="button"
					on:click={handlePrev}
					disabled={loading || uploadingMedia}
					class={getButtonClasses('secondary')}
				>
					<svg
						class="h-4 w-4 {isRTL ? 'ml-2 rotate-180' : 'mr-2'}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M10 19l-7-7m0 0l7-7m-7 7h18"
						/>
					</svg>
					{$t('common.previous')}
				</button>
			{/if}
		</div>

		<!-- Step Indicator -->
		<div class="flex items-center space-x-2 px-4">
			{#each Array(totalSteps) as _, index}
				{@const stepNumber = index + 1}
				<div
					class="h-2 w-2 rounded-full transition-all duration-300
						{stepNumber <= currentStep
						? 'bg-gradient-to-r from-teal-500 to-cyan-500'
						: 'bg-gray-300 dark:bg-gray-600'}
						{stepNumber === currentStep ? 'scale-150' : ''}"
				></div>
			{/each}
		</div>

		<!-- Next/Submit Button -->
		<div class="flex flex-1 justify-end">
			{#if isLastStep}
				<button
					type="button"
					on:click={handleSubmit}
					disabled={loading || uploadingMedia}
					class={getButtonClasses('primary', loading || uploadingMedia)}
				>
					{#if loading}
						<LoadingSpinner size="sm" color="white" className="mr-2" />
						{$t('propertyManagement.creating')}
					{:else if uploadingMedia}
						<div class="flex items-center">
							<div class="mr-2 h-4 w-4">
								<svg
									class="h-4 w-4 animate-spin"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
									/>
								</svg>
							</div>
							{$t('mediaUploader.uploading')} ({uploadProgress}%)
						</div>
					{:else}
						<svg
							class="h-4 w-4 {isRTL ? 'ml-2' : 'mr-2'}"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M5 13l4 4L19 7"
							/>
						</svg>
						{nextButtonText}
					{/if}
				</button>
			{:else}
				<button
					type="button"
					on:click={handleNext}
					disabled={loading}
					class={getButtonClasses('primary')}
				>
					{nextButtonText}
					<svg
						class="h-4 w-4 {isRTL ? 'mr-2 rotate-180' : 'ml-2'}"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 5l7 7-7 7"
						/>
					</svg>
				</button>
			{/if}
		</div>
	</div>

	<!-- Upload Progress (when uploading media) -->
	{#if uploadingMedia}
		<div class="px-8 pb-6">
			<div
				class="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20"
			>
				<div class="mb-2 flex items-center justify-between">
					<div class="flex items-center">
						<svg
							class="mr-2 h-5 w-5 text-blue-500"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
							/>
						</svg>
						<span class="text-sm font-medium text-blue-700 dark:text-blue-300">
							{$t('mediaUploader.uploadingFiles')}
						</span>
					</div>
					<span class="text-sm text-blue-600 dark:text-blue-400">
						{uploadProgress}%
					</span>
				</div>
				<div class="h-2 w-full rounded-full bg-blue-200 dark:bg-blue-800">
					<div
						class="h-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
						style="width: {uploadProgress}%"
					></div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Tips Section -->
	{#if currentStep < totalSteps}
		<div
			class="border-t border-gray-200 bg-gradient-to-r from-gray-50 to-teal-50 px-8 py-4 dark:border-gray-700 dark:from-gray-800 dark:to-teal-900/20"
		>
			<div class="flex items-start">
				<svg
					class="mt-0.5 mr-3 h-5 w-5 flex-shrink-0 text-teal-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<div>
					<p class="mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
						{$t('propertyManagement.create.tip')}
					</p>
					<p class="text-xs text-gray-600 dark:text-gray-400">
						{#if currentStep === 1}
							{$t('propertyManagement.create.tip1')}
						{:else if currentStep === 2}
							{$t('propertyManagement.create.tip2')}
						{:else if currentStep === 3}
							{$t('propertyManagement.create.tip3')}
						{:else if currentStep === 4}
							{$t('propertyManagement.create.tip4')}
						{/if}
					</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Auto-save Indicator -->
	<div class="flex items-center justify-center bg-gray-50 py-3 dark:bg-gray-800/50">
		<div class="flex items-center text-xs text-gray-500 dark:text-gray-400">
			<svg class="mr-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
			{$t('propertyManagement.create.autoSave')}
		</div>
	</div>
</div>

<style>
	/* Enhanced button animations */
	button:not(:disabled):hover {
		transform: translateY(-1px);
	}

	button:not(:disabled):active {
		transform: translateY(0);
	}

	/* Gradient animations */
	@keyframes gradient-flow {
		0%,
		100% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
	}

	.bg-gradient-to-r {
		background-size: 200% 200%;
		animation: gradient-flow 6s ease infinite;
	}

	/* Progress bar smooth transitions */
	.transition-all {
		transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
	}

	/* Step indicator animations */
	@keyframes pulse-scale {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.1);
		}
	}

	.scale-150 {
		animation: pulse-scale 2s ease-in-out infinite;
	}
</style>
