<!-- src/lib/components/PropertySelector.svelte -->
<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { t, locale } from '$lib/i18n'; // Fixed import path
	import { getProperties } from '$lib/api/property';
	import { user } from '$lib/stores/user';
	import Button from '$lib/components/ui/Button.svelte';

	export let selectedPropertyId = null;
	export let error = '';

	const dispatch = createEventDispatcher();

	let properties = [];
	let loading = true;
	let propertiesError = '';
	let page = 1;
	let hasMore = false;

	onMount(async () => {
		await loadProperties();
	});

	async function loadProperties() {
		try {
			loading = true;
			propertiesError = '';

			// Filter by current user if not admin
			const filters = {
				page: page,
				limit: 9
			};

			if ($user && !$user.is_admin) {
				filters.owner = 'current';
			}

			const response = await getProperties({
				page,
				page_size: 10,
				is_active: true,
				exclude_auctioned: true
			});

			if (page === 1) {
				properties = response.results || [];
			} else {
				properties = [...properties, ...(response.results || [])];
			}

			hasMore = response.has_next || false;
		} catch (err) {
			propertiesError = err.message || $t('error.fetchFailed');
		} finally {
			loading = false;
		}
	}

	function loadMore() {
		if (hasMore) {
			page += 1;
			loadProperties();
		}
	}

	function selectProperty(property) {
		selectedPropertyId = property.id;
		dispatch('select', property);
	}
</script>

<div>
	{#if error}
		<div class="mb-4 rounded-md bg-red-50 p-4 dark:bg-red-900/30">
			<div class="flex">
				<div class="flex-shrink-0">
					<svg
						class="h-5 w-5 text-red-400"
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 20 20"
						fill="currentColor"
						aria-hidden="true"
					>
						<path
							fill-rule="evenodd"
							d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
				<div class="ml-3">
					<h3 class="text-sm font-medium text-red-800 dark:text-red-200">
						{error}
					</h3>
				</div>
			</div>
		</div>
	{/if}

	{#if loading && page === 1}
		<div class="flex justify-center py-12">
			<div
				class="border-primary-500 h-12 w-12 animate-spin rounded-full border-t-2 border-b-2"
			></div>
		</div>
	{:else if propertiesError}
		<div class="rounded-lg bg-red-50 py-12 text-center dark:bg-red-900/30">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="mx-auto mb-4 h-12 w-12 text-red-400"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
			<h3 class="mb-1 text-lg font-medium text-red-800 dark:text-red-200">{propertiesError}</h3>
			<Button variant="primary" onClick={loadProperties} class="mt-3">
				{$t('auction.tryAgain')}
			</Button>
		</div>
	{:else if properties.length === 0}
		<div class="rounded-lg bg-gray-50 py-12 text-center dark:bg-gray-700">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				class="mx-auto mb-4 h-12 w-12 text-gray-400 dark:text-gray-500"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
				/>
			</svg>
			<h3 class="mb-1 text-lg font-medium text-gray-900 dark:text-gray-100">
				{$t('auction.noProperties')}
			</h3>
			<p class="mb-4 text-gray-500 dark:text-gray-400">{$t('auction.noPropertiesDesc')}</p>
			<a
				href="/properties/create"
				class="bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 inline-flex items-center rounded-md border border-transparent px-4 py-2 text-sm font-medium text-white shadow-sm focus:ring-2 focus:ring-offset-2 focus:outline-none"
			>
				{$t('property.createProperty')}
			</a>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each properties as property}
				<div
					class={`cursor-pointer overflow-hidden rounded-lg border transition-shadow hover:shadow-md ${selectedPropertyId === property.id ? 'border-primary-500 ring-primary-500 ring-2' : 'border-gray-200 dark:border-gray-700'}`}
					on:click={() => selectProperty(property)}
					on:keypress={() => selectProperty(property)}
					role="button"
					tabindex="0"
				>
					<div class="h-40 bg-gray-200 dark:bg-gray-700">
						{#if property.main_image}
							<img
								src={property.main_image.url ||
									property.main_image ||
									'/images/property-placeholder.jpg'}
								alt={property.title}
								class="h-full w-full object-cover"
							/>
						{:else if property.media && property.media.length > 0}
							<img
								src={property.media[0].url ||
									property.media[0].file ||
									'/images/property-placeholder.jpg'}
								alt={property.title}
								class="h-full w-full object-cover"
							/>
						{:else}
							<div class="flex h-full items-center justify-center text-gray-400 dark:text-gray-500">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									class="h-12 w-12"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
									/>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
									/>
								</svg>
							</div>
						{/if}
					</div>
					<div class="p-4">
						<h3 class="font-medium text-gray-900 dark:text-white">{property.title}</h3>
						<p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
							{property.location?.address || property.address || ''},
							{property.location?.city || property.city || ''}
						</p>
						<div class="mt-2 flex items-baseline justify-between">
							<span
								class="inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-700 dark:bg-gray-700 dark:text-gray-300"
							>
								{property.property_type_display || property.property_type?.name || ''}
							</span>
							<span class="text-lg font-bold text-gray-900 dark:text-white">
								${property.market_value?.toLocaleString() || '0'}
							</span>
						</div>
					</div>
				</div>
			{/each}
		</div>

		{#if loading && page > 1}
			<div class="mt-6 flex justify-center">
				<div
					class="border-primary-500 h-8 w-8 animate-spin rounded-full border-t-2 border-b-2"
				></div>
			</div>
		{/if}

		{#if hasMore && !loading}
			<div class="mt-6 text-center">
				<Button variant="secondary" onClick={loadMore}>
					{$t('property.loadMore')}
				</Button>
			</div>
		{/if}
	{/if}
</div>
