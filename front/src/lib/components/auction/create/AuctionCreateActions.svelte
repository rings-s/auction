<!-- src/lib/components/auction/create/AuctionCreateActions.svelte -->
<script>
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';

	export let isPreview = false;
	export let submitting = false;
	export let onCancel;
	export let onTogglePreview;
	export let onSubmit;
	export let onBackToForm;
</script>

<div class="flex justify-end space-x-3">
	{#if isPreview}
		<!-- Preview Actions -->
		<Button variant="outline" size="sm" on:click={onBackToForm} class="inline-flex items-center">
			<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M11 17l-5-5m0 0l5-5m-5 5h12"
				/>
			</svg>
			{$t('common.edit')}
		</Button>

		<Button
			variant="primary"
			size="sm"
			on:click={onSubmit}
			loading={submitting}
			disabled={submitting}
			class="inline-flex items-center"
		>
			<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
			</svg>
			{submitting ? $t('common.creating') : $t('auction.create')}
		</Button>
	{:else}
		<!-- Form Actions -->
		<Button
			variant="outline"
			size="sm"
			on:click={onCancel}
			disabled={submitting}
			class="inline-flex items-center"
		>
			<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
			{$t('common.cancel')}
		</Button>

		<Button
			variant="secondary"
			size="sm"
			on:click={onTogglePreview}
			disabled={submitting}
			class="inline-flex items-center"
		>
			<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
				/>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
				/>
			</svg>
			{$t('auction.preview')}
		</Button>

		<Button
			variant="primary"
			size="sm"
			on:click={onSubmit}
			loading={submitting}
			disabled={submitting}
			class="inline-flex items-center"
		>
			<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
			</svg>
			{submitting ? $t('common.creating') : $t('auction.create')}
		</Button>
	{/if}
</div>
