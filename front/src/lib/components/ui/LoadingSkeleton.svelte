<!-- src/lib/components/LoadingSkeleton.svelte -->
<script>
	export let type = 'default'; // 'default', 'text', 'rect', 'circle', 'auctionCard', 'auctionHeader', 'auctionContent', 'auctionSidebar', 'auctionForm', 'propertyCard'
	export let width = '100%';
	export let height = '1rem';
	export let borderRadius = '0.25rem';
	export let class_ = '';

	// Export class as class_ because "class" is a reserved word
	export { class_ as class };

	// Helper function to generate skeleton items
	function renderItems(count) {
		return Array(count).fill(null);
	}
</script>

<div class={`skeleton-wrapper ${class_}`}>
	{#if type === 'auctionCard'}
		<div
			class="h-full animate-pulse overflow-hidden rounded-lg bg-white shadow-md dark:bg-gray-800"
		>
			<div class="h-56 w-full bg-gray-200 dark:bg-gray-700"></div>
			<div class="p-4">
				<div class="mb-3 flex justify-between">
					<div class="h-6 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-6 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="mb-2 h-5 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="mb-4 h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="mb-3 h-16 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="flex items-center justify-between">
					<div class="h-4 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-1/3 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>
		</div>
	{:else if type === 'auctionHeader'}
		<div class="animate-pulse rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
			<div class="flex flex-wrap justify-between">
				<div class="w-3/4">
					<div class="mb-3 flex space-x-2">
						<div class="h-6 w-20 rounded-md bg-gray-200 dark:bg-gray-700"></div>
						<div class="h-6 w-32 rounded-md bg-gray-200 dark:bg-gray-700"></div>
					</div>
					<div class="mb-2 h-8 w-full max-w-md rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-48 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="flex w-1/4 justify-end">
					<div class="h-10 w-32 rounded-md bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>
		</div>
	{:else if type === 'auctionContent'}
		<div class="animate-pulse space-y-6">
			<div class="overflow-hidden rounded-lg bg-white shadow-md dark:bg-gray-800">
				<div class="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-700"></div>
			</div>

			<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
				<div class="mb-4 h-6 w-48 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="space-y-2">
					<div class="h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>

				<div class="mt-8 grid grid-cols-2 gap-4">
					<div>
						<div class="mb-3 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
						<div class="grid grid-cols-2 gap-2">
							{#each renderItems(4) as _, i}
								<div class="h-3 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-3 rounded bg-gray-200 dark:bg-gray-700"></div>
							{/each}
						</div>
					</div>
					<div>
						<div class="mb-3 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
						<div class="grid grid-cols-2 gap-2">
							{#each renderItems(3) as _, i}
								<div class="h-3 rounded bg-gray-200 dark:bg-gray-700"></div>
								<div class="h-3 rounded bg-gray-200 dark:bg-gray-700"></div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		</div>
	{:else if type === 'auctionSidebar'}
		<div class="animate-pulse space-y-6">
			<div class="rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
				<div class="mb-3 h-5 w-40 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="mb-4 grid grid-cols-4 gap-2 rounded-lg bg-gray-100 p-3 dark:bg-gray-700">
					{#each renderItems(4) as _, i}
						<div class="flex flex-col items-center">
							<div class="mb-1 h-8 w-12 rounded bg-gray-200 dark:bg-gray-600"></div>
							<div class="h-3 w-8 rounded bg-gray-200 dark:bg-gray-600"></div>
						</div>
					{/each}
				</div>

				<div class="mb-4 border-t border-gray-200 pt-4 dark:border-gray-700">
					<div class="mb-2 flex justify-between">
						<div class="h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
						<div class="h-6 w-20 rounded bg-gray-200 dark:bg-gray-700"></div>
					</div>
					<div class="mb-4 h-4 w-24 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>

			<div class="overflow-hidden rounded-lg bg-white shadow-md dark:bg-gray-800">
				<div class="h-40 bg-gray-200 dark:bg-gray-700"></div>
				<div class="p-4">
					<div class="mb-3 h-5 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="mb-4 grid grid-cols-2 gap-2">
						{#each renderItems(4) as _, i}
							<div class="h-3 rounded bg-gray-200 dark:bg-gray-700"></div>
							<div class="h-3 rounded bg-gray-200 dark:bg-gray-700"></div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	{:else if type === 'auctionForm'}
		<div class="animate-pulse space-y-6">
			<div class="mb-4 h-7 w-48 rounded bg-gray-200 dark:bg-gray-700"></div>

			<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
				<div class="space-y-4">
					<div class="mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="space-y-4">
					<div class="mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>

			<div class="space-y-4">
				<div class="mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="h-32 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
			</div>

			<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
				<div class="space-y-4">
					<div class="mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="space-y-4">
					<div class="mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="space-y-4">
					<div class="mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>

			<div class="h-48 w-full rounded bg-gray-200 dark:bg-gray-700"></div>

			<div class="flex justify-end space-x-4">
				<div class="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700"></div>
			</div>
		</div>
	{:else if type === 'propertyCard'}
		<div
			class="h-full animate-pulse overflow-hidden rounded-lg bg-white shadow-md dark:bg-gray-800"
		>
			<div class="h-48 w-full bg-gray-200 dark:bg-gray-700"></div>
			<div class="p-4">
				<div class="mb-3 flex justify-between">
					<div class="h-5 w-1/3 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-5 w-1/4 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
				<div class="mb-2 h-6 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="mb-4 h-4 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
				<div class="mb-3 grid grid-cols-2 gap-2">
					<div class="h-4 rounded bg-gray-200 dark:bg-gray-700"></div>
					<div class="h-4 rounded bg-gray-200 dark:bg-gray-700"></div>
				</div>
			</div>
		</div>
	{:else if type === 'default' || type === 'rect'}
		<div
			class="animate-pulse rounded bg-gray-200 dark:bg-gray-700"
			style="width: {width}; height: {height}; border-radius: {borderRadius};"
		></div>
	{:else if type === 'circle'}
		<div
			class="animate-pulse rounded-full bg-gray-200 dark:bg-gray-700"
			style="width: {width}; height: {height};"
		></div>
	{:else if type === 'text'}
		<div class="animate-pulse space-y-2">
			<div class="h-4 w-5/6 rounded bg-gray-200 dark:bg-gray-700"></div>
			<div class="h-4 rounded bg-gray-200 dark:bg-gray-700"></div>
			<div class="h-4 w-4/6 rounded bg-gray-200 dark:bg-gray-700"></div>
		</div>
	{/if}
</div>

<style>
	.skeleton-wrapper {
		display: block;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	.animate-pulse {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}
</style>
