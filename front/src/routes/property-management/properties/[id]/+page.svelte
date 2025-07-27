<!-- src/routes/property-management/properties/[id]/+page.svelte -->
<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { t, locale } from '$lib/i18n';
	import { fade, slide } from 'svelte/transition';
	import { user } from '$lib/stores/user.svelte.js';
	import { getProperty } from '$lib/api/property.js';
	import { formatCurrency } from '$lib/utils/currency';

	import LoadingSpinner from '$lib/components/animations/LoadingSpinner.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	let propertyId = $derived($page.params.id);
	let isRTL = $derived($locale === 'ar');

	// State
	let property = $state(null);
	let loading = $state(true);
	let error = $state(null);
	let activeImageIndex = $state(0);
	let showImageModal = $state(false);

	// Permissions
	let canEdit = $derived(
		$user && ($user.is_superuser || $user.is_staff || ['owner', 'appraiser'].includes($user.role))
	);

	// Computed properties mapping actual backend data structure
	let primaryImage = $derived(
		property?.media?.find((m) => m.is_primary)?.file || property?.media?.[0]?.file
	);
	let propertyImages = $derived(property?.media?.filter((m) => m.media_type === 'image') || []);
	let propertyAddress = $derived(
		property?.location_data
			? `${property.location_data.city}, ${property.location_data.state}`
			: property?.address || '-'
	);
	let estimatedRent = $derived(
		property?.market_value ? Math.round((property.market_value * 0.08) / 12) : 0
	);
	let typeInfo = $derived(
		property?.property_type ? getPropertyTypeBadge(property.property_type) : null
	);

	onMount(() => {
		loadProperty();
	});

	async function loadProperty() {
		try {
			loading = true;
			error = null;

			const response = await getProperty(propertyId);
			property = response;
		} catch (err) {
			error = err.message || $t('error.fetchFailed');
			console.error('Failed to load property:', err);
		} finally {
			loading = false;
		}
	}

	function handleEdit() {
		goto(`/property-management/properties/${propertyId}/edit`);
	}

	function handleBack() {
		goto('/property-management/properties');
	}

	function openImageModal(index) {
		activeImageIndex = index;
		showImageModal = true;
	}

	function closeImageModal() {
		showImageModal = false;
	}

	function nextImage() {
		activeImageIndex = (activeImageIndex + 1) % propertyImages.length;
	}

	function previousImage() {
		activeImageIndex = (activeImageIndex - 1 + propertyImages.length) % propertyImages.length;
	}

	function getPropertyTypeBadge(type) {
		const typeMap = {
			apartment: {
				icon: '🏠',
				color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
			},
			villa: {
				icon: '🏡',
				color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
			},
			commercial: {
				icon: '🏢',
				color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
			},
			land: {
				icon: '🏞️',
				color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
			},
			warehouse: {
				icon: '🏭',
				color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
			}
		};
		return (
			typeMap[type] || {
				icon: '🏘️',
				color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
			}
		);
	}

	function formatDate(dateString) {
		if (!dateString) return '-';
		return new Date(dateString).toLocaleDateString($locale === 'ar' ? 'ar-SA' : 'en-US');
	}
</script>

<svelte:head>
	<title>
		{property?.title
			? `${property.title} - ${$t('propertyManagement.propertyDetails')}`
			: $t('propertyManagement.propertyDetails')}
	</title>
</svelte:head>

<div
	class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-blue-900 dark:to-indigo-900"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
		<!-- Back Button -->
		<div class="mb-6">
			<button
				onclick={handleBack}
				class="group inline-flex items-center text-sm font-medium text-blue-600 transition-colors hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
			>
				<svg
					class="h-4 w-4 {isRTL
						? 'ml-2 rotate-180'
						: 'mr-2'} transition-transform group-hover:scale-110"
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
				{$t('propertyManagement.backToProperties')}
			</button>
		</div>

		<!-- Loading State -->
		{#if loading && !property}
			<div class="flex flex-col items-center justify-center py-20">
				<LoadingSpinner size="lg" color="blue" />
				<p class="mt-4 text-gray-500 dark:text-gray-400">{$t('common.loading')}</p>
			</div>

			<!-- Error State -->
		{:else if error && !property}
			<div
				class="mx-auto max-w-3xl rounded-2xl border border-red-200 bg-red-50 p-8 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200"
			>
				<div class="flex items-center">
					<svg
						class="mr-3 h-8 w-8 text-red-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
						/>
					</svg>
					<div>
						<h2 class="mb-2 text-xl font-semibold">{$t('error.title')}</h2>
						<p class="text-base">{error}</p>
					</div>
				</div>
				<div class="mt-6 flex space-x-4">
					<Button variant="primary" onclick={loadProperty}>
						<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						{$t('common.retry')}
					</Button>
					<Button variant="outline" onclick={handleBack}>
						{$t('propertyManagement.backToProperties')}
					</Button>
				</div>
			</div>

			<!-- Property Content -->
		{:else if property}
			<div class="space-y-8">
				<!-- Property Header -->
				<div
					class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-700 dark:bg-gray-800"
				>
					<div class="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 p-8 text-white">
						<div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
							<!-- Property Info -->
							<div class="flex-1">
								<div class="mb-4 flex items-center">
									<h1 class="mr-4 text-3xl font-bold text-white">{property.title}</h1>
									{#if typeInfo}
										<span class="rounded-full px-3 py-1 text-sm font-medium {typeInfo.color}">
											{typeInfo.icon}
											{$t(`property.type.${property.property_type}`)}
										</span>
									{/if}
								</div>
								<div class="flex items-center space-x-4 text-white/90">
									<div class="flex items-center">
										<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
											/>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
											/>
										</svg>
										<span class="text-sm">{propertyAddress}</span>
									</div>
									{#if property.size_sqm}
										<div class="flex items-center">
											<svg
												class="mr-1 h-4 w-4"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
												/>
											</svg>
											<span class="text-sm">{property.size_sqm} {$t('property.sqm')}</span>
										</div>
									{/if}
									{#if property.year_built}
										<div class="flex items-center">
											<svg
												class="mr-1 h-4 w-4"
												fill="none"
												stroke="currentColor"
												viewBox="0 0 24 24"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													stroke-width="2"
													d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
												/>
											</svg>
											<span class="text-sm">{property.year_built}</span>
										</div>
									{/if}
								</div>
							</div>

							<!-- Action Buttons -->
							<div class="flex flex-wrap gap-3 lg:flex-col lg:items-end">
								{#if canEdit}
									<Button
										variant="outline"
										class="border-white/20 bg-white/10 text-white transition-all duration-300 hover:bg-white/20"
										onclick={handleEdit}
									>
										<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
											/>
										</svg>
										{$t('common.edit')}
									</Button>
								{/if}
								<Button
									variant="outline"
									class="border-white/20 bg-white/10 text-white transition-all duration-300 hover:bg-white/20"
									onclick={() => goto(`/properties/${property.slug || property.id}`)}
								>
									<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
									{$t('property.viewPublic')}
								</Button>
							</div>
						</div>
					</div>

					<!-- Quick Stats Bar -->
					<div
						class="border-b border-gray-200 bg-gray-50 p-6 dark:border-gray-600 dark:bg-gray-700"
					>
						<div class="grid grid-cols-2 gap-6 md:grid-cols-4">
							<div class="text-center">
								<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
									{formatCurrency(property.market_value || 0)}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">
									{$t('property.marketValue')}
								</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-green-600 dark:text-green-400">
									{formatCurrency(estimatedRent)}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">
									{$t('rental.estimatedRent')}
								</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
									{property.rooms?.length || 0}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">{$t('property.rooms')}</div>
							</div>
							<div class="text-center">
								<div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
									{property.floors || 1}
								</div>
								<div class="text-sm text-gray-600 dark:text-gray-400">{$t('property.floors')}</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Property Content Grid -->
				<div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
					<!-- Main Content -->
					<div class="space-y-8 lg:col-span-2">
						<!-- Property Images -->
						{#if propertyImages.length > 0}
							<div
								class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
							>
								<h3 class="mb-6 text-xl font-semibold text-gray-900 dark:text-gray-100">
									{$t('property.images')}
								</h3>

								<!-- Main Image -->
								<div class="mb-4">
									<img
										src={propertyImages[0]?.file}
										alt={property.title}
										class="h-96 w-full cursor-pointer rounded-xl object-cover transition-opacity hover:opacity-90"
										onclick={() => openImageModal(0)}
									/>
								</div>

								<!-- Thumbnail Grid -->
								{#if propertyImages.length > 1}
									<div class="grid grid-cols-4 gap-2">
										{#each propertyImages.slice(1, 5) as image, index}
											<img
												src={image.file}
												alt={`${property.title} - ${index + 2}`}
												class="h-20 w-full cursor-pointer rounded-lg object-cover transition-opacity hover:opacity-90"
												onclick={() => openImageModal(index + 1)}
											/>
										{/each}
										{#if propertyImages.length > 5}
											<div
												class="flex h-20 w-full cursor-pointer items-center justify-center rounded-lg bg-gray-100 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600"
												onclick={() => openImageModal(5)}
											>
												<span class="text-sm font-medium text-gray-600 dark:text-gray-400">
													+{propertyImages.length - 5}
												</span>
											</div>
										{/if}
									</div>
								{/if}
							</div>
						{/if}

						<!-- Property Description -->
						{#if property.description}
							<div
								class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
							>
								<h3 class="mb-4 text-xl font-semibold text-gray-900 dark:text-gray-100">
									{$t('property.description')}
								</h3>
								<div class="prose prose-gray dark:prose-invert max-w-none">
									<p class="leading-relaxed text-gray-700 dark:text-gray-300">
										{property.description}
									</p>
								</div>
							</div>
						{/if}

						<!-- Rooms Information -->
						{#if property.rooms && property.rooms.length > 0}
							<div
								class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
							>
								<h3 class="mb-6 text-xl font-semibold text-gray-900 dark:text-gray-100">
									{$t('property.rooms')} ({property.rooms.length})
								</h3>
								<div class="grid grid-cols-1 gap-4 md:grid-cols-2">
									{#each property.rooms as room}
										<div class="rounded-xl border border-gray-200 p-4 dark:border-gray-600">
											<h4 class="mb-2 font-medium text-gray-900 dark:text-gray-100">
												{room.name || room.room_type}
											</h4>
											<div class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
												{#if room.area_sqm}
													<p>🏠 {room.area_sqm} {$t('property.sqm')}</p>
												{/if}
												{#if room.floor}
													<p>🏢 {$t('property.floor')} {room.floor}</p>
												{/if}
												{#if room.description}
													<p class="mt-2 text-xs">{room.description}</p>
												{/if}
											</div>
										</div>
									{/each}
								</div>
							</div>
						{/if}
					</div>

					<!-- Sidebar -->
					<div class="space-y-6">
						<!-- Property Details -->
						<div
							class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
						>
							<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
								{$t('property.details')}
							</h3>
							<dl class="space-y-3">
								<div>
									<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
										{$t('property.id')}
									</dt>
									<dd class="text-sm text-gray-900 dark:text-gray-100">#{property.id}</dd>
								</div>
								<div>
									<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
										{$t('property.type')}
									</dt>
									<dd class="text-sm text-gray-900 dark:text-gray-100">
										{$t(`property.type.${property.property_type}`)}
									</dd>
								</div>
								{#if property.size_sqm}
									<div>
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.area')}
										</dt>
										<dd class="text-sm text-gray-900 dark:text-gray-100">
											{property.size_sqm}
											{$t('property.sqm')}
										</dd>
									</div>
								{/if}
								{#if property.floors}
									<div>
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.floors')}
										</dt>
										<dd class="text-sm text-gray-900 dark:text-gray-100">{property.floors}</dd>
									</div>
								{/if}
								{#if property.year_built}
									<div>
										<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
											{$t('property.yearBuilt')}
										</dt>
										<dd class="text-sm text-gray-900 dark:text-gray-100">{property.year_built}</dd>
									</div>
								{/if}
								<div>
									<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
										{$t('property.status')}
									</dt>
									<dd class="text-sm">
										<span
											class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium
											{property.is_featured
												? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
												: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'}"
										>
											{property.is_featured ? $t('property.featured') : $t('property.regular')}
										</span>
									</dd>
								</div>
								<div>
									<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
										{$t('property.created')}
									</dt>
									<dd class="text-sm text-gray-900 dark:text-gray-100">
										{formatDate(property.created_at)}
									</dd>
								</div>
								<div>
									<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
										{$t('property.updated')}
									</dt>
									<dd class="text-sm text-gray-900 dark:text-gray-100">
										{formatDate(property.updated_at)}
									</dd>
								</div>
							</dl>
						</div>

						<!-- Location Details -->
						{#if property.location_data}
							<div
								class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
							>
								<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
									{$t('property.location')}
								</h3>
								<dl class="space-y-3">
									{#if property.location_data.city}
										<div>
											<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
												{$t('property.city')}
											</dt>
											<dd class="text-sm text-gray-900 dark:text-gray-100">
												{property.location_data.city}
											</dd>
										</div>
									{/if}
									{#if property.location_data.state}
										<div>
											<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
												{$t('property.state')}
											</dt>
											<dd class="text-sm text-gray-900 dark:text-gray-100">
												{property.location_data.state}
											</dd>
										</div>
									{/if}
									{#if property.location_data.country}
										<div>
											<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
												{$t('property.country')}
											</dt>
											<dd class="text-sm text-gray-900 dark:text-gray-100">
												{property.location_data.country}
											</dd>
										</div>
									{/if}
									{#if property.location_data.postal_code}
										<div>
											<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
												{$t('property.postalCode')}
											</dt>
											<dd class="text-sm text-gray-900 dark:text-gray-100">
												{property.location_data.postal_code}
											</dd>
										</div>
									{/if}
									{#if property.location_data.latitude && property.location_data.longitude}
										<div>
											<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
												{$t('property.coordinates')}
											</dt>
											<dd class="text-xs text-gray-900 dark:text-gray-100">
												{property.location_data.latitude}, {property.location_data.longitude}
											</dd>
										</div>
									{/if}
								</dl>
							</div>
						{/if}

						<!-- Quick Actions -->
						<div
							class="rounded-2xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800"
						>
							<h3 class="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
								{$t('propertyManagement.quickActions')}
							</h3>
							<div class="space-y-3">
								<Button
									variant="outline"
									class="w-full justify-start"
									onclick={() => goto(`/property-management/tenants?property=${propertyId}`)}
								>
									<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
										/>
									</svg>
									{$t('rental.manageTenants')}
								</Button>
								<Button
									variant="outline"
									class="w-full justify-start"
									onclick={() => goto(`/property-management/maintenance?property=${propertyId}`)}
								>
									<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
										/>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
										/>
									</svg>
									{$t('maintenance.manageMaintenance')}
								</Button>
								<Button
									variant="outline"
									class="w-full justify-start"
									onclick={() => goto(`/property-management/expenses?property=${propertyId}`)}
								>
									<svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
										/>
									</svg>
									{$t('expenses.manageExpenses')}
								</Button>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>

<!-- Image Modal -->
{#if showImageModal && propertyImages.length > 0}
	<div
		class="bg-opacity-90 fixed inset-0 z-50 flex items-center justify-center bg-black"
		transition:fade={{ duration: 200 }}
	>
		<!-- Close Button -->
		<button
			class="absolute top-4 right-4 z-10 p-2 text-white transition-colors hover:text-gray-300"
			onclick={closeImageModal}
		>
			<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M6 18L18 6M6 6l12 12"
				/>
			</svg>
		</button>

		<!-- Navigation Buttons -->
		{#if propertyImages.length > 1}
			<button
				class="absolute left-4 p-2 text-white transition-colors hover:text-gray-300"
				onclick={previousImage}
			>
				<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M15 19l-7-7 7-7"
					/>
				</svg>
			</button>
			<button
				class="absolute right-4 p-2 text-white transition-colors hover:text-gray-300"
				onclick={nextImage}
			>
				<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
				</svg>
			</button>
		{/if}

		<!-- Main Image -->
		<img
			src={propertyImages[activeImageIndex]?.file}
			alt={property?.title}
			class="max-h-full max-w-full object-contain"
		/>

		<!-- Image Counter -->
		{#if propertyImages.length > 1}
			<div
				class="bg-opacity-50 absolute bottom-4 left-1/2 -translate-x-1/2 transform rounded-full bg-black px-3 py-1 text-sm text-white"
			>
				{activeImageIndex + 1} / {propertyImages.length}
			</div>
		{/if}
	</div>
{/if}

<style>
	/* Enhanced animations for property detail theme */
	:global(.property-detail-theme) {
		--primary-gradient: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
		--accent-color: #3b82f6;
		--accent-light: #dbeafe;
		--accent-dark: #1d4ed8;
	}

	/* Smooth transitions for better UX */
	* {
		transition: all 0.2s ease-in-out;
	}

	/* Custom gradient animations */
	@keyframes gradient-shift {
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
		animation: gradient-shift 6s ease infinite;
	}
</style>
