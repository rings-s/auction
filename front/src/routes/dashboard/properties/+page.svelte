<!-- src/routes/dashboard/properties/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { t } from '$lib/i18n';
	import { user } from '$lib/stores/user.svelte.js';
	import {
		dashboardProperties,
		dashboardLoading,
		dashboardFilters
	} from '$lib/stores/dashboard.svelte.js';
	import { getDashboardProperties } from '$lib/api/dashboard';
	import { toast } from '$lib/stores/toastStore.svelte.js';

	// Components
	import Button from '$lib/components/ui/Button.svelte';
	import FormField from '$lib/components/ui/FormField.svelte';
	import LoadingSkeleton from '$lib/components/ui/LoadingSkeleton.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import Breadcrumb from '$lib/components/ui/Breadcrumb.svelte';

	let searchQuery = '';
	let statusFilter = '';
	let verifiedFilter = '';
	let currentPage = 1;
	let totalPages = 1;
	let totalProperties = 0;

	// Breadcrumb items
	$: breadcrumbItems = [
		{ label: $t('nav.home'), href: '/' },
		{ label: $t('dashboard.title'), href: '/dashboard' },
		{ label: $t('dashboard.properties'), href: '/dashboard/properties', active: true }
	];

	// Status options
	const statusOptions = [
		{ value: '', label: $t('common.all') },
		{ value: 'published', label: $t('property.statusTypes.published') },
		{ value: 'draft', label: $t('property.statusTypes.draft') },
		{ value: 'available', label: $t('property.statusTypes.available') },
		{ value: 'sold', label: $t('property.statusTypes.sold') }
	];

	const verifiedOptions = [
		{ value: '', label: $t('common.all') },
		{ value: 'true', label: $t('dashboard.verified') },
		{ value: 'false', label: $t('dashboard.unverified') }
	];

	// Load properties
	async function loadProperties() {
		dashboardLoading.set(true);

		try {
			const filters = {
				page: currentPage,
				search: searchQuery || undefined,
				status: statusFilter || undefined,
				verified: verifiedFilter || undefined
			};

			const response = await getDashboardProperties(filters);

			dashboardProperties.set(response.results || []);
			totalPages = Math.ceil(response.count / 10);
			totalProperties = response.count || 0;
		} catch (error) {
			console.error('Failed to load properties:', error);
			toast.error($t('dashboard.loadPropertiesError'));
		} finally {
			dashboardLoading.set(false);
		}
	}

	// Handle search
	function handleSearch() {
		currentPage = 1;
		loadProperties();
	}

	// Handle filter change
	function handleFilterChange() {
		currentPage = 1;
		loadProperties();
	}

	// Handle pagination
	function handlePageChange(page) {
		currentPage = page;
		loadProperties();
	}

	onMount(() => {
		loadProperties();
	});

	$: properties = $dashboardProperties;
	$: isLoading = $dashboardLoading;
</script>

<svelte:head>
	<title>{$t('dashboard.properties')} - {$t('dashboard.title')} - {$t('app.name')}</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-6">
		<Breadcrumb items={breadcrumbItems} class="mb-4" />

		<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
			<div>
				<h1 class="text-xl font-semibold text-gray-900">
					{$t('dashboard.properties')}
				</h1>
				<p class="mt-1 text-sm text-gray-600">
					{$t('dashboard.manageProperties')}
				</p>
			</div>

			<div class="mt-4 sm:mt-0">
				<Button variant="primary" size="compact" href="/properties/create">
					{$t('dashboard.addProperty')}
				</Button>
			</div>
		</div>
	</div>

	<!-- Filters -->
	<div class="mb-6 rounded-lg border border-gray-200 bg-white p-4">
		<div class="grid grid-cols-1 gap-4 md:grid-cols-4">
			<FormField
				type="text"
				placeholder={$t('common.search')}
				bind:value={searchQuery}
				on:input={handleSearch}
			/>

			<FormField
				type="select"
				options={statusOptions}
				bind:value={statusFilter}
				on:change={handleFilterChange}
			/>

			<FormField
				type="select"
				options={verifiedOptions}
				bind:value={verifiedFilter}
				on:change={handleFilterChange}
			/>

			<Button
				variant="outline"
				size="default"
				onClick={() => {
					searchQuery = '';
					statusFilter = '';
					verifiedFilter = '';
					handleFilterChange();
				}}
			>
				{$t('search.clear')}
			</Button>
		</div>
	</div>

	<!-- Properties List -->
	{#if isLoading}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(6) as _}
				<LoadingSkeleton type="propertyCard" />
			{/each}
		</div>
	{:else if properties.length === 0}
		<EmptyState
			icon="property"
			title={$t('dashboard.noProperties')}
			description={$t('dashboard.noPropertiesDesc')}
			actionLabel={$t('dashboard.addProperty')}
			actionUrl="/properties/create"
		/>
	{:else}
		<div class="space-y-4">
			<!-- Properties Grid -->
			<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
				{#each properties as property (property.id)}
					<div
						class="overflow-hidden rounded-lg border border-gray-200 bg-white transition-shadow hover:shadow-md"
					>
						<!-- Property Image -->
						<div class="aspect-w-16 aspect-h-9 bg-gray-200">
							{#if property.main_image}
								<img
									src={property.main_image.url}
									alt={property.title}
									class="h-full w-full object-cover"
								/>
							{:else}
								<div class="flex items-center justify-center">
									<svg
										class="h-12 w-12 text-gray-400"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
										/>
									</svg>
								</div>
							{/if}
						</div>

						<!-- Property Info -->
						<div class="p-4">
							<div class="mb-2 flex items-start justify-between">
								<h3 class="flex-1 truncate text-sm font-medium text-gray-900">
									{property.title}
								</h3>

								<div class="ml-2 flex items-center space-x-1">
									{#if property.is_featured}
										<span
											class="inline-flex items-center rounded bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800"
										>
											{$t('property.featured')}
										</span>
									{/if}

									{#if property.is_verified}
										<span
											class="inline-flex items-center rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800"
										>
											{$t('dashboard.verified')}
										</span>
									{/if}
								</div>
							</div>

							<p class="mb-2 text-xs text-gray-600">
								{property.location_display || $t('property.noLocationData')}
							</p>

							<div class="mb-3 flex items-center justify-between text-xs text-gray-500">
								<span>{property.property_type_display}</span>
								<span>{property.days_since_created} {$t('common.daysAgo')}</span>
							</div>

							<div class="flex items-center justify-between">
								<div class="text-sm">
									<span class="font-medium text-gray-900">
										${property.market_value?.toLocaleString() || 0}
									</span>
									<span class="ml-1 text-gray-500">
										• {property.size_sqm}
										{$t('property.sqm')}
									</span>
								</div>

								<div class="flex items-center space-x-2">
									<Button variant="outline" size="compact" href="/properties/{property.slug}">
										{$t('common.view')}
									</Button>

									<Button variant="ghost" size="compact" href="/properties/{property.id}/edit">
										{$t('common.edit')}
									</Button>
								</div>
							</div>
						</div>
					</div>
				{/each}
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
				<div
					class="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-3"
				>
					<div class="flex items-center">
						<p class="text-sm text-gray-700">
							{$t('dashboard.showing')}
							<span class="font-medium">{(currentPage - 1) * 10 + 1}</span>
							{$t('common.to')}
							<span class="font-medium">{Math.min(currentPage * 10, totalProperties)}</span>
							{$t('common.of')}
							<span class="font-medium">{totalProperties}</span>
							{$t('dashboard.properties')}
						</p>
					</div>

					<div class="flex items-center space-x-2">
						<Button
							variant="outline"
							size="compact"
							disabled={currentPage === 1}
							onClick={() => handlePageChange(currentPage - 1)}
						>
							{$t('common.previous')}
						</Button>

						<span class="text-sm text-gray-700">
							{currentPage} / {totalPages}
						</span>

						<Button
							variant="outline"
							size="compact"
							disabled={currentPage === totalPages}
							onClick={() => handlePageChange(currentPage + 1)}
						>
							{$t('common.next')}
						</Button>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
