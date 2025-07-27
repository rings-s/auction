<script>
	import { createEventDispatcher } from 'svelte';
	import { t, locale } from '$lib/i18n';
	import { formatCurrency } from '$lib/utils/currency';
	import Button from '$lib/components/ui/Button.svelte';

	const dispatch = createEventDispatcher();

	/** @type {{ property: Object }} */
	let { property } = $props();

	let isRTL = $derived($locale === 'ar');

	// Computed properties with proper backend mapping
	let primaryImage = $derived(
		property?.media?.find((m) => m.is_primary)?.file ||
			property?.media?.[0]?.file ||
			'/images/property-placeholder.jpg'
	);
	let propertyAddress = $derived(
		property?.location_data
			? `${property.location_data.city}, ${property.location_data.state}`
			: property?.address || '-'
	);
	let statusInfo = $derived(getStatusBadge(property?.property_status));
	let typeInfo = $derived(getPropertyTypeBadge(property?.property_type));

	function handleView() {
		dispatch('view', { property });
	}

	function handleEdit() {
		dispatch('edit', { property });
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

	function getStatusBadge(status) {
		const statusMap = {
			available: {
				color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
				text: $t('property.status.available')
			},
			sold: {
				color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
				text: $t('property.status.sold')
			},
			pending: {
				color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
				text: $t('property.status.pending')
			},
			off_market: {
				color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
				text: $t('property.status.offMarket')
			}
		};
		return statusMap[status] || statusMap.available;
	}
</script>

<div
	class="group overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-xl transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl dark:border-gray-700 dark:bg-gray-800"
	dir={isRTL ? 'rtl' : 'ltr'}
>
	<!-- Property Image -->
	<div class="relative h-48 overflow-hidden">
		<img
			src={primaryImage}
			alt={property.title}
			class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
			loading="lazy"
		/>

		<!-- Status Badge -->
		<div class="absolute top-3 left-3">
			<span class="rounded-full px-2 py-1 text-xs font-medium {statusInfo.color}">
				{statusInfo.text}
			</span>
		</div>

		<!-- Featured Badge -->
		{#if property.is_featured}
			<div class="absolute top-3 right-3">
				<span
					class="rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
				>
					⭐ {$t('property.featured')}
				</span>
			</div>
		{/if}

		<!-- Property Type Badge -->
		<div class="absolute bottom-3 left-3">
			<span class="rounded-full px-2 py-1 text-xs font-medium {typeInfo.color}">
				{typeInfo.icon}
				{$t(`property.type.${property.property_type}`)}
			</span>
		</div>
	</div>

	<!-- Property Content -->
	<div class="p-6">
		<!-- Title and Location -->
		<div class="mb-4">
			<h3
				class="mb-2 line-clamp-2 text-lg font-semibold text-gray-900 transition-colors group-hover:text-blue-600 dark:text-white dark:group-hover:text-blue-400"
			>
				{property.title}
			</h3>
			<div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
				<svg
					class="mr-1 h-4 w-4 flex-shrink-0"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
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
				<span class="truncate">{propertyAddress}</span>
			</div>
		</div>

		<!-- Property Details -->
		<div class="mb-4 grid grid-cols-3 gap-3 text-sm">
			{#if property.size_sqm}
				<div class="rounded-xl bg-gray-50 p-2 text-center dark:bg-gray-700">
					<div class="text-lg font-semibold text-gray-900 dark:text-white">{property.size_sqm}</div>
					<div class="text-xs text-gray-600 dark:text-gray-400">{$t('property.sqm')}</div>
				</div>
			{/if}

			{#if property.bedrooms}
				<div class="rounded-xl bg-gray-50 p-2 text-center dark:bg-gray-700">
					<div class="text-lg font-semibold text-gray-900 dark:text-white">{property.bedrooms}</div>
					<div class="text-xs text-gray-600 dark:text-gray-400">{$t('property.bedrooms')}</div>
				</div>
			{/if}

			{#if property.bathrooms}
				<div class="rounded-xl bg-gray-50 p-2 text-center dark:bg-gray-700">
					<div class="text-lg font-semibold text-gray-900 dark:text-white">
						{property.bathrooms}
					</div>
					<div class="text-xs text-gray-600 dark:text-gray-400">{$t('property.bathrooms')}</div>
				</div>
			{/if}
		</div>

		<!-- Market Value -->
		{#if property.market_value}
			<div class="mb-4">
				<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
					{formatCurrency(property.market_value)}
				</div>
				<div class="text-xs text-gray-500 dark:text-gray-400">
					{$t('property.marketValue')}
				</div>
			</div>
		{/if}

		<!-- Additional Info -->
		<div class="mb-4 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
			{#if property.year_built}
				<span>{$t('property.built')} {property.year_built}</span>
			{/if}
			{#if property.floors}
				<span>{property.floors} {$t('property.floors')}</span>
			{/if}
			{#if property.parking_spaces}
				<span>{property.parking_spaces} {$t('property.parking')}</span>
			{/if}
		</div>

		<!-- Action Buttons -->
		<div class="flex gap-2">
			<Button variant="outline" size="sm" class="flex-1" onclick={handleView}>
				<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
				{$t('common.view')}
			</Button>

			<Button
				variant="primary"
				size="sm"
				class="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
				onclick={handleEdit}
			>
				<svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
					/>
				</svg>
				{$t('common.edit')}
			</Button>
		</div>
	</div>
</div>

<style>
	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* Enhanced hover effects */
	.group:hover .transition-transform {
		transform: scale(1.05);
	}

	/* Custom gradient animations */
	@keyframes shimmer {
		0% {
			background-position: -200% 0;
		}
		100% {
			background-position: 200% 0;
		}
	}

	.group:hover {
		background: linear-gradient(45deg, rgba(59, 130, 246, 0.05) 0%, rgba(99, 102, 241, 0.05) 100%);
	}
</style>
