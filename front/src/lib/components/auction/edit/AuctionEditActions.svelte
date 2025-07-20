<!-- src/lib/components/auction/edit/AuctionEditActions.svelte -->
<script>
	import { t } from '$lib/i18n';
	import Button from '$lib/components/ui/Button.svelte';

	export let auction;
	export let saving = false;
	export let canDelete = false;
	export let onSave;
	export let onCancel;
	export let onDelete;
</script>

<div class="rounded-lg bg-white p-6 shadow-sm dark:bg-gray-800">
	<div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
		<!-- Primary Actions -->
		<div class="flex flex-wrap gap-3">
			<Button
				variant="primary"
				size="default"
				on:click={onSave}
				disabled={saving}
				loading={saving}
				class="inline-flex items-center"
			>
				<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M5 13l4 4L19 7"
					/>
				</svg>
				{saving ? $t('common.saving') : $t('common.saveChanges')}
			</Button>

			<Button
				variant="outline"
				size="default"
				on:click={onCancel}
				disabled={saving}
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

			<!-- View Auction Link -->
			{#if auction && auction.slug}
				<Button
					variant="secondary"
					size="default"
					href={`/auctions/${auction.slug}`}
					disabled={saving}
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
					{$t('auction.viewAuction')}
				</Button>
			{/if}
		</div>

		<!-- Danger Zone -->
		{#if canDelete}
			<div class="flex items-center">
				<div class="ml-4 border-l border-neutral-200 pl-4 dark:border-neutral-700">
					<Button
						variant="danger"
						size="default"
						on:click={onDelete}
						disabled={saving}
						class="inline-flex items-center"
					>
						<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
							/>
						</svg>
						{$t('auction.delete')}
					</Button>
				</div>
			</div>
		{/if}
	</div>

	<!-- Warning for Active Auctions -->
	{#if auction && (auction.status === 'live' || auction.status === 'scheduled')}
		<div
			class="bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800 mt-4 rounded-lg border p-3"
		>
			<div class="flex items-start">
				<svg
					class="text-warning-500 mt-0.5 mr-2 h-5 w-5 flex-shrink-0"
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
					<h4 class="text-warning-800 dark:text-warning-200 text-sm font-semibold">
						{$t('auction.editWarningTitle')}
					</h4>
					<p class="text-warning-700 dark:text-warning-300 mt-1 text-sm">
						{auction.status === 'live'
							? $t('auction.editLiveWarning')
							: $t('auction.editScheduledWarning')}
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
