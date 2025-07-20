<!-- src/lib/components/auction/create/AuctionCreatePreview.svelte -->
<script>
	import { t } from '$lib/i18n';
	import AuctionPreview from '$lib/components/auction/AuctionPreview.svelte';

	export let previewData;
</script>

<div
	class="border-primary-200 dark:border-primary-800 overflow-hidden rounded-lg border bg-white shadow-sm dark:bg-gray-800"
>
	<div
		class="bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800 border-b px-6 py-3"
	>
		<div class="text-primary-700 dark:text-primary-300 flex items-center">
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
			<span class="text-sm font-medium">{$t('common.preview')}</span>
		</div>
	</div>

	<AuctionPreview auction={previewData} />
</div>
