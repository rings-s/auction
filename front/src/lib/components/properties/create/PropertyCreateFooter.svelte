<!-- src/lib/components/properties/create/PropertyCreateFooter.svelte -->
<script>
	import { t } from '$lib/i18n';

	export let currentStep;
	export let totalSteps;
	export let loading;
	export let uploadingMedia;
	export let uploadProgress;
	export let onNext;
	export let onPrev;
	export let onSubmit;
</script>

<div
	class="rounded-b-xl border-t border-gray-200 bg-white px-6 py-4 dark:border-gray-700 dark:bg-gray-800"
>
	<!-- Form Navigation -->
	<div class="flex items-center justify-between">
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

		{#if currentStep < totalSteps}
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
			<button
				type="button"
				on:click={onSubmit}
				disabled={loading || uploadingMedia}
				class="btn-modern-primary ml-3 inline-flex items-center rounded-md px-4 py-2 text-sm font-medium shadow-sm transition-all duration-200 disabled:opacity-50"
			>
				{#if loading || uploadingMedia}
					<svg class="mr-2 -ml-1 h-4 w-4 animate-spin text-white" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
						></circle>
						<path
							class="opacity-75"
							fill="currentColor"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
						></path>
					</svg>
					{uploadingMedia
						? `${$t('mediaUploader.uploading')} (${uploadProgress}%)`
						: $t('common.processing')}
				{:else}
					<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"
						></path>
					</svg>
					{$t('property.create')}
				{/if}
			</button>
		{/if}
	</div>
</div>
