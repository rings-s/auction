<!-- src/lib/components/properties/edit/PropertyEditFooter.svelte -->
<script>
	import { t } from '$lib/i18n';

	export let currentStep;
	export let totalSteps;
	export let loading;
	export let uploadingMedia;
	export let uploadProgress;
	export let hasUnsavedChanges;
	export let propertyId;
	export let onNext;
	export let onPrev;
	export let onSave;
	export let onCancel;
</script>

<div
	class="rounded-b-xl border-t border-gray-200 bg-white px-6 py-4 dark:border-gray-700 dark:bg-gray-800"
>
	<!-- Unsaved Changes Warning -->
	{#if hasUnsavedChanges}
		<div
			class="mb-4 rounded-md border border-orange-200 bg-orange-50 p-3 dark:border-orange-800 dark:bg-orange-900/20"
		>
			<div class="flex">
				<svg
					class="mr-2 h-5 w-5 flex-shrink-0 text-orange-400"
					fill="currentColor"
					viewBox="0 0 20 20"
				>
					<path
						fill-rule="evenodd"
						d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
						clip-rule="evenodd"
					/>
				</svg>
				<div>
					<p class="text-sm font-medium text-orange-800 dark:text-orange-200">
						{$t('property.unsavedChangesWarning')}
					</p>
					<p class="mt-1 text-xs text-orange-700 dark:text-orange-300">
						{$t('property.unsavedChangesDesc')}
					</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Form Navigation -->
	<div class="flex items-center justify-between">
		<div class="flex items-center space-x-3">
			<!-- Previous Button -->
			<button
				type="button"
				on:click={onPrev}
				disabled={currentStep === 1 || loading}
				class="focus:ring-primary-500 inline-flex transform items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-all duration-200 hover:-translate-x-1 hover:bg-gray-50 focus:ring-2 focus:ring-offset-2 focus:outline-none disabled:opacity-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"
					></path>
				</svg>
				{$t('common.previous')}
			</button>

			<!-- Cancel Button -->
			<button
				type="button"
				on:click={onCancel}
				disabled={loading}
				class="inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:outline-none disabled:opacity-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M6 18L18 6M6 6l12 12"
					></path>
				</svg>
				{$t('common.cancel')}
			</button>
		</div>

		<div class="flex items-center space-x-3">
			<!-- View Property Button -->
			<a
				href={`/properties/${propertyId}`}
				class="text-primary-600 bg-primary-50 hover:bg-primary-100 focus:ring-primary-500 border-primary-200 dark:bg-primary-900/20 dark:text-primary-400 dark:hover:bg-primary-900/30 dark:border-primary-800 inline-flex items-center rounded-md border px-4 py-2 text-sm font-medium shadow-sm transition-colors focus:ring-2 focus:ring-offset-2 focus:outline-none"
			>
				<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
					></path>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
					></path>
				</svg>
				{$t('property.viewProperty')}
			</a>

			{#if currentStep < totalSteps}
				<!-- Next Button -->
				<button
					type="button"
					on:click={onNext}
					class="btn-modern-primary ml-3 inline-flex transform items-center rounded-md px-4 py-2 text-sm font-medium shadow-sm transition-all duration-200 hover:translate-x-1"
				>
					{$t('common.next')}
					<svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"
						></path>
					</svg>
				</button>
			{:else}
				<!-- Save Button -->
				<button
					type="button"
					on:click={onSave}
					disabled={loading || uploadingMedia}
					class="btn-modern-primary ml-3 inline-flex items-center rounded-md px-4 py-2 text-sm font-medium shadow-sm transition-all duration-200 disabled:opacity-50"
				>
					{#if loading || uploadingMedia}
						<svg class="mr-2 -ml-1 h-4 w-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						{uploadingMedia
							? `${$t('mediaUploader.uploading')} (${uploadProgress}%)`
							: $t('common.saving')}
					{:else}
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M5 13l4 4L19 7"
							></path>
						</svg>
						{$t('property.saveChanges')}
					{/if}
				</button>
			{/if}
		</div>
	</div>
</div>
